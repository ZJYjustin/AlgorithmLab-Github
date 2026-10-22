"""Build a VS 2022 VSIX with Microsoft's official SDK packaging task.

A generic ZIP with extension.vsixmanifest is not a modern VSIX v3 package.
The SDK also generates catalog.json and manifest.json. SDK binaries remain
build-only dependencies and are never copied into the extension payload.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import tempfile
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

SDK_VERSION = '17.14.2142'
SDK_SHA256 = '92526da94f2834b9ad48d8bed80edae83f522e73640ce40259366e917f1ef6b2'
SDK_URL = f'https://api.nuget.org/v3-flatcontainer/microsoft.vssdk.buildtools/{SDK_VERSION}/microsoft.vssdk.buildtools.{SDK_VERSION}.nupkg'


def find_sdk(home=None):
    if home:
        root = Path(home).resolve()
        if (root / 'tools/vssdk').is_dir():
            root = root / 'tools/vssdk'
    else:
        cache = Path(__file__).resolve().parent / '.tools/vssdk-buildtools' / SDK_VERSION
        root = cache / 'tools/vssdk'
        if not (root / 'bin/VsixUtil.exe').is_file():
            cache.mkdir(parents=True, exist_ok=True)
            package = cache / 'sdk.nupkg'
            print('Downloading Microsoft.VSSDK.BuildTools', SDK_VERSION, flush=True)
            with urllib.request.urlopen(SDK_URL, timeout=60) as response:
                content = response.read()
            if hashlib.sha256(content).hexdigest() != SDK_SHA256:
                raise RuntimeError('VSSDK build tool download checksum mismatch.')
            package.write_bytes(content)
            with zipfile.ZipFile(package) as archive:
                for name in archive.namelist():
                    destination = (cache / name).resolve()
                    if not destination.is_relative_to(cache.resolve()):
                        raise RuntimeError('Unsafe SDK archive member: ' + name)
                archive.extractall(cache)
    if not (root / 'bin/VsixUtil.exe').is_file():
        raise FileNotFoundError('Pass the extracted Microsoft.VSSDK.BuildTools directory with --vssdk-home.')
    return root


def validate_layout(package, expected_payload=()):
    with zipfile.ZipFile(package) as archive:
        names = set(archive.namelist())
        required = {'extension.vsixmanifest', '[Content_Types].xml', 'manifest.json', 'catalog.json'}
        if not required.issubset(names):
            raise ValueError('Not a modern VSIX package; missing: ' + ', '.join(sorted(required - names)))
        for metadata in ('manifest.json', 'catalog.json'):
            json.loads(archive.read(metadata))
        for path in expected_payload:
            if path not in names:
                raise ValueError('Missing VSIX payload at expected path: ' + path)
        if any('/runtime/' in name for name in names if name.startswith('runtime/')):
            raise ValueError('Duplicate runtime path prefix in VSIX.')


def package_vsix(stage, output, visual_studio, sdk_home=None):
    stage, output, visual_studio = Path(stage).resolve(), Path(output).resolve(), Path(visual_studio).resolve()
    sdk = find_sdk(sdk_home)
    output.parent.mkdir(parents=True, exist_ok=True)
    source_manifest = stage / 'extension.vsixmanifest'
    excluded = {'[Content_Types].xml', 'extension.vsixmanifest', 'manifest.json', 'catalog.json'}
    payload = [p for p in sorted(stage.rglob('*')) if p.is_file()
               and p.relative_to(stage).as_posix() not in excluded and '__pycache__' not in p.parts]
    with tempfile.TemporaryDirectory(prefix='vsix-build-', dir=output.parent, ignore_cleanup_errors=True) as temp:
        temp = Path(temp)
        files = {'files': [{'path': str(p), 'targetPath': str(p.relative_to(stage)), 'vsixSubPath': '',
                            'culture': '', 'installRoot': '', 'ngen': None} for p in payload]}
        files_path = temp / 'files.json'
        files_path.write_text(json.dumps(files), encoding='utf-8')
        project = ET.Element('Project', ToolsVersion='Current', DefaultTargets='Build',
                             xmlns='http://schemas.microsoft.com/developer/msbuild/2003')
        ET.SubElement(project, 'UsingTask', TaskName='VsixUtil',
                      AssemblyFile=str(sdk / 'Microsoft.VisualStudio.Sdk.BuildTasks.17.0.dll'))
        target = ET.SubElement(project, 'Target', Name='Build')
        ET.SubElement(target, 'VsixUtil', Command='package', SourceManifest=str(source_manifest),
                      ZipPackage=str(output), FilesManifest=str(files_path), ToolPath=str(sdk / 'bin'),
                      VsixSchemaPath=str(sdk / 'schemas'), Is64BitBuild='true',
                      SetupProductArch='amd64', CompressionLevel='Normal')
        project_path = temp / 'PackageVsix.proj'
        ET.ElementTree(project).write(project_path, encoding='utf-8', xml_declaration=True)
        subprocess.run([str(visual_studio / 'MSBuild/Current/Bin/MSBuild.exe'), str(project_path),
                        '/nologo', '/v:minimal'], check=True)
    validate_layout(output, [p.relative_to(stage).as_posix() for p in payload])
    return output

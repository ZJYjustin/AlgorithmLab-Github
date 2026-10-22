"""Build native launchers with installed IDE libraries and official VSIX tools.

Only the launcher is IDE-specific. Both packages embed the same Python engine.
"""
from pathlib import Path
import argparse
import os
import shutil
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET

BASE = Path(__file__).resolve().parent


def runtime(target):
    target.mkdir(parents=True, exist_ok=True)
    for filename in ('lab.py', 'worker.py', 'protocol.py', 'algorithm_lab.py', 'viewer.html', 'README.md', 'LICENSE', 'THIRD_PARTY.md'):
        if (BASE / filename).exists():
            shutil.copy2(BASE / filename, target / filename)
    (target / 'python.path').write_text('python.exe', encoding='utf-8')
    for folder in ('include', 'examples'):
        shutil.copytree(BASE / folder, target / folder, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns('__pycache__', '.git', '*.pyc'))


def zip_tree(source, output, prefix=''):
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in source.rglob('*'):
            if path.is_file():
                archive.write(path, prefix + path.relative_to(source).as_posix())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pycharm', default=os.environ.get('PYCHARM_HOME'), help='PyCharm 2025.2 installation directory')
    parser.add_argument('--visual-studio', default=os.environ.get('VSINSTALLDIR'), help='Visual Studio 2022 installation directory')
    parser.add_argument('--only', choices=['all', 'pycharm'], default='all')
    parser.add_argument('--vssdk-home', default=os.environ.get('VSSDK_BUILDTOOLS_HOME'), help='Extracted Microsoft.VSSDK.BuildTools directory; downloaded to .tools if omitted')
    args = parser.parse_args()
    if not args.pycharm:
        parser.error('Pass --pycharm or set PYCHARM_HOME to the installed IDE directory.')
    pycharm = Path(args.pycharm)
    if args.only == 'all' and not args.visual_studio:
        from lab import find_msvc
        args.visual_studio = str(find_msvc().parents[3])
    vs = Path(args.visual_studio) if args.visual_studio else None
    scratch = BASE / '.build'
    dist = BASE / 'dist'
    scratch.mkdir(exist_ok=True); dist.mkdir(exist_ok=True)
    version = ET.parse(BASE / 'plugins/pycharm/plugin.xml').getroot().findtext('version')
    pypkg = scratch / ('pycharm-' + version) / 'AlgorithmLab'
    classes = scratch / ('pycharm-' + version) / 'classes'
    classes.mkdir(parents=True, exist_ok=True)
    javac, jar = pycharm / 'jbr/bin/javac.exe', pycharm / 'jbr/bin/jar.exe'
    subprocess.run([str(javac), '--release', '21', '-encoding', 'UTF-8', '-cp', str(pycharm / 'lib/*'),
                    '-d', str(classes)] + [str(p) for p in sorted((BASE / 'plugins/pycharm/src').rglob('*.java'))], check=True)
    (classes / 'META-INF').mkdir(exist_ok=True)
    shutil.copy2(BASE / 'plugins/pycharm/plugin.xml', classes / 'META-INF/plugin.xml')
    (pypkg / 'lib').mkdir(parents=True, exist_ok=True)
    zip_tree(classes, pypkg / 'lib/AlgorithmLab.jar')
    runtime(pypkg / 'runtime')
    zip_tree(pypkg, dist / ('AlgorithmLab-PyCharm-' + version + '.zip'), 'AlgorithmLab/')
    if args.only == 'pycharm':
        print('Built PyCharm plugin', version, 'in', dist)
        return

    vspkg = scratch / 'visual-studio'
    vspkg.mkdir(exist_ok=True)
    editor = vs / 'Common7/IDE/CommonExtensions/Microsoft/Editor'
    framework = Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Microsoft.NET/Framework64/v4.0.30319'
    refs = [framework / 'System.dll', framework / 'System.Core.dll', framework / 'System.ComponentModel.Composition.dll',
            framework / 'WPF/PresentationFramework.dll', framework / 'WPF/PresentationCore.dll',
            framework / 'WPF/WindowsBase.dll', framework / 'WPF/System.Xaml.dll']
    if not refs[-1].exists(): refs[-1] = framework / 'System.Xaml.dll'
    refs += [editor / name for name in ('Microsoft.VisualStudio.CoreUtility.dll', 'Microsoft.VisualStudio.Text.Data.dll',
              'Microsoft.VisualStudio.Text.Logic.dll', 'Microsoft.VisualStudio.Text.UI.dll', 'Microsoft.VisualStudio.Text.UI.Wpf.dll')]
    csc = vs / 'MSBuild/Current/Bin/Roslyn/csc.exe'
    subprocess.run([str(csc), '/nologo', '/target:library', '/platform:anycpu', '/langversion:latest',
                    '/out:' + str(vspkg / 'AlgorithmLab.VisualStudio.dll')] + ['/reference:' + str(r) for r in refs] +
                    [str(BASE / 'plugins/visual-studio/AlgorithmMargin.cs')], check=True)
    shutil.copy2(BASE / 'plugins/visual-studio/extension.vsixmanifest', vspkg / 'extension.vsixmanifest')
    runtime(vspkg / 'runtime')
    from package_vsix import package_vsix
    vs_version = ET.parse(BASE / 'plugins/visual-studio/extension.vsixmanifest').getroot().find('{*}Metadata/{*}Identity').attrib['Version']
    package_vsix(vspkg, dist / ('AlgorithmLab-VisualStudio2022-' + vs_version + '.vsix'), vs, args.vssdk_home)
    print('Built native plugin packages in', dist)


if __name__ == '__main__':
    main()

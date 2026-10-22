"""Local runner shared by the PyCharm and Visual Studio launchers.

Usage: python lab.py examples/banker.py [--mode auto|lines] [--no-browser]
"""
import argparse
from datetime import datetime
import html
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import uuid
import webbrowser

from protocol import replay

BASE = Path(__file__).resolve().parent


def python_executable():
    configured = os.environ.get('ALGORITHM_LAB_PYTHON')
    path = BASE / 'python.path'
    candidate = configured or (path.read_text(encoding='utf-8-sig').strip() if path.exists() else sys.executable)
    if not Path(candidate).is_file():
        candidate = sys.executable
    # pythonw is unsuitable for child stdout/stderr capture.
    if Path(candidate).name.lower() == 'pythonw.exe':
        candidate = str(Path(candidate).with_name('python.exe'))
    return candidate


def run(command, cwd, timeout, env=None):
    options = {'creationflags': subprocess.CREATE_NO_WINDOW} if os.name == 'nt' else {}
    return subprocess.run(command, cwd=cwd, timeout=timeout, env=env, stdin=subprocess.DEVNULL,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, **options)


def decode(data):
    try:
        return data.decode('utf-8')
    except UnicodeDecodeError:
        return data.decode('gb18030', errors='replace')


def find_msvc():
    vswhere = Path(os.environ.get('ProgramFiles(x86)', 'C:/Program Files (x86)')) / 'Microsoft Visual Studio/Installer/vswhere.exe'
    if not vswhere.is_file():
        raise RuntimeError('找不到 Visual Studio C/C++ 编译器。请安装“使用 C++ 的桌面开发”工作负载。')
    found = run([str(vswhere), '-latest', '-products', '*', '-requires', 'Microsoft.VisualStudio.Component.VC.Tools.x86.x64',
                 '-property', 'installationPath'], BASE, 15)
    install = decode(found.stdout).strip()
    if not install:
        raise RuntimeError('Visual Studio 尚未安装 MSVC C/C++ 工具。')
    return Path(install) / 'VC/Auxiliary/Build/vcvars64.bat'


def compile_native(source, scratch):
    is_c = source.suffix.lower() == '.c'
    compiler = shutil.which('cl.exe')
    exe = scratch / 'program.exe'
    args = ['/nologo', '/utf-8', '/W3', '/TC' if is_c else '/TP',
            '/I' + str(BASE / 'include'),
            str(source), '/Fe:' + str(exe), '/Fo:' + str(scratch / 'program.obj')]
    if not is_c:
        args[3:3] = ['/EHsc', '/std:c++17']
    if compiler:
        result = run([compiler] + args, scratch, 60)
    else:
        vcvars = find_msvc()
        # subprocess.list2cmdline quotes the argument vector for Windows.
        # Reject cmd metacharacters that remain active inside batch expansion.
        paths = [str(vcvars), str(source), str(scratch), str(BASE)]
        if any(any(char in path for char in '%!&|<>^\r\n') for path in paths):
            raise RuntimeError('C/C++ 编译路径含命令解释器特殊字符，请换到普通目录后再运行。')
        batch = scratch / 'compile.cmd'
        batch.write_text('@echo off\ncall "' + str(vcvars) + '" >nul\n' +
                         'if errorlevel 1 exit /b 1\ncl.exe ' + subprocess.list2cmdline(args) + '\n', encoding='utf-8')
        result = run([os.environ.get('COMSPEC', 'cmd.exe'), '/d', '/c', str(batch)], scratch, 60)
    if result.returncode:
        raise RuntimeError(decode(result.stdout) + decode(result.stderr))
    return exe


def build_report(source, mode='auto', timeout=20, program_args=None):
    source = Path(source).resolve()
    if not source.is_file():
        raise ValueError('找不到文件：' + str(source))
    if source.suffix.lower() not in ('.py', '.c', '.cpp', '.cc', '.cxx'):
        raise ValueError('第一版支持 .py、.c、.cpp、.cc、.cxx 文件。')
    code = source.read_text(encoding='utf-8-sig')
    payload = {'name': source.name, 'source': code, 'path': str(source), 'frames': [],
               'error': '', 'warnings': [], 'stdout': '', 'mode': '', 'created': datetime.now().isoformat(timespec='seconds')}
    scratch_root = BASE / '.scratch'
    scratch_root.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='run-', dir=scratch_root, ignore_cleanup_errors=True) as tmp:
        scratch = Path(tmp)
        try:
            if source.suffix.lower() == '.py':
                result_path = scratch / 'result.json'
                result = run([python_executable(), str(BASE / 'worker.py'), str(source), str(result_path),
                              str(scratch), mode] + (program_args or []), scratch, timeout)
                if not result_path.exists():
                    raise RuntimeError(decode(result.stderr) or '执行进程未生成记录。')
                data = json.loads(result_path.read_text(encoding='utf-8'))
                payload['error'] = data['error']
                if data['visual_frames'] and mode != 'lines':
                    payload['frames'] = data['visual_frames']
                    payload['mode'] = '算法动画 · 执行记录回放'
                else:
                    payload['frames'] = data['frames']
                    payload['mode'] = 'Python 逐行 · 高亮行执行前的状态'
                    if data['truncated']:
                        payload['warnings'].append('仅保留前 4000 步；列表每层最多 40 项、最多 4 层、字符串最多 1000 字。')
            else:
                exe = compile_native(source, scratch)
                env = dict(os.environ, ALGORITHM_LAB_TRACE=str(scratch / 'visualization.json'))
                result = run([str(exe)] + (program_args or []), source.parent, timeout, env)
                trace_path = scratch / 'visualization.json'
                if not trace_path.exists():
                    raise RuntimeError('程序已运行，但没有可视化记录。C/C++ 需要调用记录接口；请先参考 examples 中的示例。\n' + decode(result.stdout) + decode(result.stderr))
                payload['frames'], payload['warnings'] = replay(json.loads(trace_path.read_text(encoding='utf-8')))
                payload['mode'] = 'C/C++ 算法动画 · 执行记录回放'
                if result.returncode:
                    payload['error'] = f'程序退出码：{result.returncode}\n' + decode(result.stderr)
            payload['stdout'] = (decode(result.stdout) + decode(result.stderr))[-100000:]
        except subprocess.TimeoutExpired:
            payload['error'] = f'运行超过 {timeout} 秒，已停止本次执行。可通过 --timeout 修改时限。'
        except Exception as exc:
            payload['error'] = str(exc)
    if not payload['frames']:
        payload['frames'] = [{'line': None, 'panels': []}]
    return payload


def write_report(payload, output):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(payload, ensure_ascii=False, allow_nan=False).replace('<', '\\u003c').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
    template = (BASE / 'viewer.html').read_text(encoding='utf-8')
    output.write_text(template.replace('/*__REPORT_DATA__*/', serialized), encoding='utf-8')
    return output


def main():
    parser = argparse.ArgumentParser(description='在本地回放 Python / C / C++ 的执行过程')
    parser.add_argument('file')
    parser.add_argument('--mode', choices=['auto', 'lines'], default='auto')
    parser.add_argument('--output')
    parser.add_argument('--timeout', type=int, default=20)
    parser.add_argument('--no-browser', action='store_true')
    parser.add_argument('--json', action='store_true', help='同时输出可检查的运行数据')
    args, program_args = parser.parse_known_args()
    if program_args and program_args[0] == '--':
        program_args = program_args[1:]
    payload = build_report(args.file, args.mode, args.timeout, program_args)
    output = Path(args.output).resolve() if args.output else BASE / 'reports' / (Path(args.file).stem + '-' + datetime.now().strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:6] + '.html')
    write_report(payload, output)
    if args.json:
        output.with_suffix('.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    if not args.no_browser:
        webbrowser.open(output.as_uri())
    if sys.stdout:
        print(output)
    return 1 if payload['error'] else 0


if __name__ == '__main__':
    raise SystemExit(main())

"""Run a Python file in a child process; record state without evaluating repr()."""
import json
import os
from pathlib import Path
import runpy
import sys
import traceback
import types

BASE = Path(__file__).resolve().parent


def clean(value, depth=0):
    if value is None or type(value) in (bool, int, str):
        return value[:1000] if type(value) is str else value
    if type(value) is float:
        return value if value == value and abs(value) != float('inf') else str(value)
    if depth > 3:
        return '<nested>'
    if type(value) in (list, tuple):
        return [clean(x, depth + 1) for x in value[:40]]
    if type(value) is dict:
        return {str(k): clean(v, depth + 1) for k, v in list(value.items())[:40]
                if type(k) in (str, int, float, bool)}
    if isinstance(value, (types.ModuleType, types.FunctionType, type)):
        return None
    return '<' + type(value).__name__ + '>'


def main():
    source, result_path, trace_dir, mode = sys.argv[1:5]
    target = str(Path(source).resolve())
    sys.argv = [source] + sys.argv[5:]
    os.chdir(Path(source).parent)
    # Load this project's own recorder from the engine directory.
    sys.path.insert(0, str(BASE))
    sys.path.insert(0, str(Path(source).parent))
    frames, error, truncated = [], '', False
    max_frames = 4000
    previous = None

    def snapshot(frame, line, label):
        nonlocal truncated
        if len(frames) >= max_frames:
            truncated = True
            return
        values = {}
        for k, v in list(frame.f_locals.items())[:100]:
            if k.startswith('__') or isinstance(v, (types.ModuleType, types.FunctionType, type)):
                continue
            values[k] = clean(v)
        frames.append({'line': line, 'function': frame.f_code.co_name, 'event': label,
                       'variables': values, 'panels': []})

    def trace(frame, event, arg):
        nonlocal previous
        if frame.f_code.co_filename != target:
            return trace
        if event == 'line':
            # Python line events occur BEFORE the highlighted line executes.
            snapshot(frame, frame.f_lineno, 'before')
            previous = frame.f_lineno
        elif event == 'return':
            snapshot(frame, frame.f_lineno, 'return')
        elif event == 'exception':
            snapshot(frame, frame.f_lineno, 'exception')
        return trace

    try:
        sys.settrace(trace)
        runpy.run_path(target, run_name='__main__')
    except SystemExit as exc:
        if exc.code not in (None, 0):
            error = f'SystemExit: {exc.code}'
    except BaseException:
        error = traceback.format_exc()
    finally:
        sys.settrace(None)
        recorder = sys.modules.get('algorithm_lab')
        visual_frames = recorder.export_frames() if recorder else []
        if 'ModuleNotFoundError' in error and 'algorithm_visualizer' in error:
            error += '\n公开版使用 algorithm_lab。旧版银行家示例请按 docs/MIGRATION.md 迁移。'
        payload = {'frames': frames, 'visual_frames': visual_frames, 'error': error, 'truncated': truncated}
        Path(result_path).write_text(json.dumps(payload, ensure_ascii=False), encoding='utf-8')
    return 1 if error else 0


if __name__ == '__main__':
    raise SystemExit(main())

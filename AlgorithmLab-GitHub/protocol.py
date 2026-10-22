"""Turn Algorithm Visualizer commands into reversible playback snapshots.

The upstream protocol is {key, method, args}; a delay closes one frame.
This deliberately supports array/log tracers, not all upstream graph renderers.
"""
from copy import deepcopy

CONSTRUCTORS = {'Array1DTracer', 'Array2DTracer', 'ChartTracer', 'LogTracer'}


def replay(commands):
    objects, frames, warnings = {}, [], []
    dirty = False
    for command in commands:
        key, method, args = command['key'], command['method'], command.get('args', [])
        if key is None and method == 'delay':
            frames.append({'line': args[0] if args else None, 'panels': deepcopy(list(objects.values()))})
            dirty = False
            continue
        if method in CONSTRUCTORS:
            objects[key] = {'key': key, 'kind': method, 'title': args[0] if args else method,
                            'data': '' if method == 'LogTracer' else [], 'selected': [], 'patched': []}
            dirty = True
            continue
        if key not in objects:
            if method in ('HorizontalLayout', 'VerticalLayout', 'setRoot', 'add', 'remove', 'removeAll', 'destroy'):
                continue
            if method not in warnings:
                warnings.append(method)
            continue
        obj = objects[key]
        dirty = True
        is_log = obj['kind'] == 'LogTracer'
        is_2d = obj['kind'] == 'Array2DTracer'
        if method == 'set':
            obj['data'] = deepcopy(args[0]) if args else ('' if is_log else [])
            obj['selected'], obj['patched'] = [], []
        elif method == 'reset':
            obj['selected'], obj['patched'] = [], []
        elif is_log and method in ('print', 'println', 'printf'):
            if method == 'printf':
                try:
                    message = str(args[0]) % tuple(args[1:])
                except (TypeError, ValueError):
                    message = ' '.join(map(str, args))
            else:
                message = str(args[0]) + ('\n' if method == 'println' else '')
            obj['data'] = (str(obj['data']) + message)[-100000:]
        elif method in ('patch', 'depatch'):
            coords = args[:2] if is_2d else args[:1]
            cell = ':'.join(map(str, coords))
            if method == 'patch':
                if cell not in obj['patched']:
                    obj['patched'].append(cell)
                if len(args) > len(coords):
                    try:
                        if is_2d:
                            obj['data'][coords[0]][coords[1]] = deepcopy(args[2])
                        else:
                            obj['data'][coords[0]] = deepcopy(args[1])
                    except (IndexError, TypeError):
                        warnings.append('patch index outside array')
            elif cell in obj['patched']:
                obj['patched'].remove(cell)
        elif method in ('select', 'deselect', 'selectRow', 'deselectRow', 'selectCol', 'deselectCol'):
            remove = method.startswith('deselect')
            cells = []
            if is_2d:
                if method.endswith('Row'):
                    cells = [f'{args[0]}:{c}' for c in range(args[1], args[2] + 1)]
                elif method.endswith('Col'):
                    cells = [f'{r}:{args[0]}' for r in range(args[1], args[2] + 1)]
                elif len(args) >= 2:
                    er, ec = args[2:4] if len(args) >= 4 else args[:2]
                    cells = [f'{r}:{c}' for r in range(args[0], er + 1) for c in range(args[1], ec + 1)]
            elif args:
                cells = [str(c) for c in range(args[0], (args[1] if len(args) > 1 else args[0]) + 1)]
            for cell in cells:
                if remove and cell in obj['selected']:
                    obj['selected'].remove(cell)
                elif not remove and cell not in obj['selected']:
                    obj['selected'].append(cell)
        elif method == 'destroy':
            objects.pop(key, None)
        elif method not in ('chart',):
            warnings.append(method)
    if dirty or not frames:
        frames.append({'line': None, 'panels': deepcopy(list(objects.values()))})
    return frames, sorted(set(warnings))

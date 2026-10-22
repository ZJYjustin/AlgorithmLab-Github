"""Small local recording API authored for this project.

No algorithm-visualizer tracer code, network requests, or exit hooks are used.
Views hold plain data; step() copies the complete state into a replay frame.
"""
from copy import deepcopy
import inspect

_views = {}
_frames = []
_dirty = False


def _changed():
    global _dirty
    _dirty = True


class ArrayView:
    """One-dimensional teaching view. Values are copied, not referenced."""
    kind = 'Array1DTracer'  # Existing local viewer's panel tag.

    def __init__(self, title, values):
        self.key = 'view-' + str(len(_views) + 1)
        self.state = {'key': self.key, 'kind': self.kind, 'title': title,
                      'data': deepcopy(values), 'selected': [], 'patched': []}
        _views[self.key] = self.state
        _changed()

    def replace(self, values):
        self.state['data'] = deepcopy(values)
        self.state['selected'] = []
        self.state['patched'] = []
        _changed()

    def update(self, index, value):
        self.state['data'][index] = deepcopy(value)
        marker = str(index)
        if marker not in self.state['patched']:
            self.state['patched'].append(marker)
        _changed()

    def clear_updates(self):
        self.state['patched'] = []
        _changed()

    def clear_focus(self):
        self.state['selected'] = []
        _changed()


class MatrixView(ArrayView):
    kind = 'Array2DTracer'

    def update(self, row, column, value):
        self.state['data'][row][column] = deepcopy(value)
        marker = f'{row}:{column}'
        if marker not in self.state['patched']:
            self.state['patched'].append(marker)
        _changed()

    def focus_row(self, row):
        self.state['selected'] = [f'{row}:{column}' for column in range(len(self.state['data'][row]))]
        _changed()


class Journal(ArrayView):
    kind = 'LogTracer'

    def __init__(self, title):
        super().__init__(title, '')

    def write(self, text):
        self.state['data'] = (self.state['data'] + str(text) + '\n')[-100000:]
        _changed()


def step(line=None):
    """Copy a state after the preceding visualization calls have completed."""
    global _dirty
    if len(_frames) >= 4000:
        raise RuntimeError('Animation exceeds the 4000-frame teaching limit.')
    if line is None:
        caller = inspect.currentframe()
        try:
            line = caller.f_back.f_lineno
        finally:
            del caller
    _frames.append({'line': line, 'panels': deepcopy(list(_views.values()))})
    _dirty = False


def export_frames():
    """Called by the local worker once the user's program has finished."""
    if _views and (_dirty or not _frames) and len(_frames) < 4000:
        step(line=0)
    return deepcopy(_frames)

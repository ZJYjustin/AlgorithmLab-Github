import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
from lab import build_report, write_report, find_msvc
from protocol import replay


def native_available():
    if os.name != 'nt':
        return False
    try:
        return bool(shutil.which('cl.exe') or find_msvc().is_file())
    except Exception:
        return False


class RuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (BASE / '.scratch').mkdir(exist_ok=True)

    def run_python(self, code, **options):
        with tempfile.TemporaryDirectory(dir=BASE / '.scratch') as directory:
            source = Path(directory) / 'sample.py'
            source.write_text(code, encoding='utf-8')
            return build_report(source, **options)

    def test_python_banker_safe_sequence(self):
        report = build_report(BASE / 'examples/banker.py')
        self.assertEqual(report['error'], '')
        self.assertEqual(len(report['frames']), 14)
        panels = report['frames'][-1]['panels']
        self.assertEqual(next(p['data'] for p in panels if p['title'].startswith('安全序列')), [1,3,4,0,2])
        self.assertEqual(next(p['data'] for p in panels if p['title'].startswith('Work')), [10,5,7])

    def test_python_banker_unsafe_state(self):
        code = (BASE / 'examples/banker.py').read_text(encoding='utf-8').replace('available = [3, 3, 2]', 'available = [0, 0, 0]')
        report = self.run_python(code)
        self.assertEqual(report['error'], '')
        self.assertIn("'safe': False", report['stdout'])
        self.assertEqual(next(p['data'] for p in report['frames'][-1]['panels'] if p['title'].startswith('安全序列')), [])

    def test_plain_python_before_line_state(self):
        report = self.run_python('x = [3, 1]\nx.sort()\nresult = x[:]\n')
        self.assertEqual(report['error'], '')
        before = next(f for f in report['frames'] if f['line'] == 2 and f['event'] == 'before')
        self.assertEqual(before['variables']['x'], [3,1])
        self.assertEqual(report['frames'][-1]['variables']['result'], [1,3])

    def test_forcing_lines_mode_changes_view_only(self):
        report = build_report(BASE / 'examples/banker.py', mode='lines')
        self.assertEqual(report['error'], '')
        self.assertTrue(report['frames'][-1]['variables']['safe'])
        self.assertEqual(report['frames'][-1]['panels'], [])
        self.assertIn('逐行', report['mode'])

    def test_snapshots_are_copies_and_step_gets_caller_line(self):
        code = 'from algorithm_lab import ArrayView, step\na=[1]\nv=ArrayView("A",a)\nstep()\na[0]=7\nv.update(0,7)\nstep()\n'
        report = self.run_python(code)
        self.assertEqual(report['frames'][0]['line'], 4)
        self.assertEqual(report['frames'][0]['panels'][0]['data'], [1])
        self.assertEqual(report['frames'][1]['panels'][0]['data'], [7])

    def test_matrix_focus_and_journal(self):
        code = 'from algorithm_lab import MatrixView,Journal,step\nm=MatrixView("M",[[1,2],[3,4]])\nj=Journal("J")\nm.focus_row(1)\nm.update(1,0,8)\nj.write("done")\nstep()\n'
        report = self.run_python(code)
        panels = report['frames'][0]['panels']
        self.assertEqual(panels[0]['selected'], ['1:0','1:1'])
        self.assertEqual(panels[0]['data'][1][0], 8)
        self.assertEqual(panels[1]['data'], 'done\n')

    def test_runtime_error_preserves_prior_frames(self):
        report = self.run_python('x = 7\ny = 1 / 0\n')
        self.assertIn('ZeroDivisionError', report['error'])
        self.assertTrue(any(f.get('variables',{}).get('x') == 7 for f in report['frames']))

    def test_timeout_is_reported(self):
        report = self.run_python('while True:\n    pass\n', timeout=1)
        self.assertIn('已停止', report['error'])

    def test_html_embedded_source_is_escaped(self):
        report = self.run_python('text="</script><script>alert(1)</script>"\n')
        with tempfile.TemporaryDirectory(dir=BASE / '.scratch') as directory:
            path = write_report(report, Path(directory) / 'report.html')
            self.assertNotIn('</script><script>alert(1)', path.read_text(encoding='utf-8'))

    def test_c_command_replay_uses_independent_snapshots(self):
        commands = [{'key':'a','method':'Array1DTracer','args':['A']}, {'key':'a','method':'set','args':[[1]]},
                    {'key':None,'method':'delay','args':[1]}, {'key':'a','method':'patch','args':[0,7]},
                    {'key':None,'method':'delay','args':[2]}]
        frames,warnings = replay(commands)
        self.assertFalse(warnings)
        self.assertEqual(frames[0]['panels'][0]['data'],[1])
        self.assertEqual(frames[1]['panels'][0]['data'],[7])

    def test_old_tracer_import_explains_migration(self):
        report = self.run_python('from algorithm_visualizer import Tracer\n')
        self.assertIn('MIGRATION.md',report['error'])

    @unittest.skipUnless(native_available(), 'Requires Windows and MSVC')
    def test_c_and_cpp_match_python_safety_result(self):
        for extension in ('c','cpp'):
            with self.subTest(language=extension):
                report = build_report(BASE / 'examples' / ('banker.'+extension))
                self.assertEqual(report['error'],'')
                panels = report['frames'][-1]['panels']
                self.assertEqual(next(p['data'] for p in panels if p['title'].startswith('安全序列')), [1,3,4,0,2])

    @unittest.skipUnless(native_available(), 'Requires Windows and MSVC')
    def test_c_and_cpp_unsafe_input_changes_execution(self):
        for extension in ('c','cpp'):
            with self.subTest(language=extension), tempfile.TemporaryDirectory(dir=BASE / '.scratch') as directory:
                code = (BASE / 'examples' / ('banker.'+extension)).read_text(encoding='utf-8').replace('work[3]={3,3,2}', 'work[3]={0,0,0}')
                source = Path(directory) / ('unsafe.'+extension)
                source.write_text(code,encoding='utf-8')
                report = build_report(source)
                self.assertEqual(report['error'],'')
                self.assertEqual(next(p['data'] for p in report['frames'][-1]['panels'] if p['title'].startswith('安全序列')), [])


if __name__ == '__main__':
    unittest.main(verbosity=2)

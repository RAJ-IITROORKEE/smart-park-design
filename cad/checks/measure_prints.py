"""Measure the exact final print meshes; preserve complete tool reports."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess, sys, json

ROOT = Path(__file__).resolve().parents[1]
TOOL = Path('C:/Users/rajra/.codex/plugins/cache/openai-curated-remote/text-to-cad/0.7.10/skills/dfam-check/scripts/dfam_tool.py')

def measure(job):
    name, mode = job
    args = [sys.executable, str(TOOL), mode, str(ROOT/'STL'/f'{name}.stl'), '--angle-limit', '45']
    if mode == 'measure':
        args += ['--samples', '2500']
    result = subprocess.run(args, capture_output=True, text=True, encoding='utf-8')
    suffix = '' if mode == 'measure' else '-orientations'
    output = ROOT/'checks'/f'dfam-{name}{suffix}.json'
    output.write_text(result.stdout, encoding='utf-8')
    assert result.returncode == 0, (name, mode, result.returncode, result.stderr, result.stdout)
    assert isinstance(json.loads(result.stdout), dict)
    print(name, mode, 'measured', flush=True)

if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(measure, [(name, mode) for name in ('base', 'lid') for mode in ('measure', 'orientations')]))

#!/usr/bin/env python
"""Rebuild frozen tables and plots in an external scratch directory, then diff them."""
import argparse
import csv
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def sensitivity(before, after, out):
    fields = ['subset', 'method', 'n_tasks', 'correct_count', 'correct_rate', 'mean_regret']
    with Path(out).open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator='\n')
        writer.writeheader()
        for label, rows in [('pre_fix', before), ('post_fix', after)]:
            for method in ['B0', 'B1', 'B2', 'B3', 'B4', 'B5']:
                subset = [r for r in rows if r['cell'] == 'ST-F' and r['method'] == method]
                n = len(subset)
                if not n:
                    raise ValueError(f'Missing sensitivity units: {label}/{method}')
                correct = sum(r['correct'] for r in subset)
                writer.writerow(dict(subset=label, method=method, n_tasks=n,
                                     correct_count=correct, correct_rate=correct/n,
                                     mean_regret=sum(r['regret'] for r in subset)/n))


def differences(reference, candidate, names):
    return [str(name) for name in names if not (candidate/name).is_file()
            or (reference/name).read_bytes() != (candidate/name).read_bytes()]


def run(scratch):
    scratch = Path(scratch).resolve()
    if scratch == ROOT or ROOT in scratch.parents:
        raise ValueError('Scratch must be outside the repository')
    if scratch.exists() and any(scratch.iterdir()):
        raise ValueError('Scratch must be empty or new')
    scratch.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, PYTHONPATH='', PYTHONDONTWRITEBYTECODE='1', MPLBACKEND='Agg')
    env['MPLCONFIGDIR'] = str(scratch/'mplconfig')
    def command(script, *args, cwd=scratch):
        cmd = [sys.executable, str(ROOT/script), *map(str, args)]
        print('RUN', ' '.join(cmd), flush=True)
        subprocess.run(cmd, cwd=cwd, env=env, check=True)
    raw = ROOT/'results/raw'
    command('analysis/make_figures.py', raw/'qwen.jsonl')
    before = [json.loads(line) for line in (raw/'qwen_pre_fix.jsonl').read_text().splitlines()]
    after = [json.loads(line) for line in (raw/'qwen.jsonl').read_text().splitlines()]
    sensitivity(before, after, scratch/'results/tables/st_f_sensitivity.csv')
    command('analysis/derive.py', raw/'qwen.jsonl', '--out', scratch/'results/derived_v1')
    v2 = scratch/'results/v2'
    v2.mkdir()
    command('analysis/make_figures.py', raw/'qwen_v2.jsonl', cwd=v2)
    command('analysis/derive.py', raw/'qwen_v2.jsonl', '--out', v2/'derived')
    command('analysis/compare_versions.py', '--v1', raw/'qwen.jsonl', '--v2', raw/'qwen_v2.jsonl',
            '--ablation', raw/'qwen_v2_ablation.jsonl', '--out', v2)
    command('analysis/plot_derived.py', raw/'qwen_v2.jsonl', '--out', v2/'figures')
    demo = scratch/'demo'
    command('scripts/make_reel.py', '--jsonl', raw/'qwen.jsonl', '--out', demo/'reel.mp4', '--res', '640x360')
    for method in ['B0', 'B5']:
        command('scripts/replay.py', '--jsonl', raw/'qwen.jsonl', '--task', 't06', '--cell', 'PAR-F',
                '--method', method, '--res', '640x360', '--video', demo/f't06_PAR-F_{method}.mp4')
    import imageio.v2 as iio
    from PIL import Image
    samples = {'reel.mp4': {'replay_150': 150, 'replay_400': 400, 'replay_700': 700},
               't06_PAR-F_B0.mp4': {'t06_PAR-F_B0_fail': 245, 't06_PAR-F_B0_final': 734},
               't06_PAR-F_B5.mp4': {'t06_PAR-F_B5_fail': 177, 't06_PAR-F_B5_final': 531}}
    for video, frames in samples.items():
        reader = iio.get_reader(demo/video)
        for name, frame in frames.items():
            Image.fromarray(reader.get_data(frame)).save(scratch/'figures'/f'{name}.png')
        reader.close()
    contrast = Image.new('RGB', (1290, 360), (30, 30, 35))
    contrast.paste(Image.open(scratch/'figures/t06_PAR-F_B0_fail.png'), (0, 0))
    contrast.paste(Image.open(scratch/'figures/t06_PAR-F_B5_final.png'), (650, 0))
    contrast.save(scratch/'figures/replay_contrast.png')
    names = [p.relative_to(ROOT) for d in ['results/tables', 'results/derived_v1', 'results/v2', 'figures']
             for p in sorted((ROOT/d).rglob('*')) if p.is_file()]
    changed = differences(ROOT, scratch, names)
    (scratch/'diff.json').write_text(json.dumps({'compared':len(names), 'different':changed}, indent=2)+'\n')
    print(f'ARTIFACT DIFF: {len(names)} files compared; {len(changed)} different', flush=True)
    for name in changed:
        print('DIFFERENT', name)
    return not changed


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scratch', type=Path, required=True)
    args = parser.parse_args()
    sys.exit(0 if run(args.scratch) else 1)

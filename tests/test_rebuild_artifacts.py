import csv
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('rebuild_artifacts', ROOT/'scripts/rebuild_artifacts.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_sensitivity_known_answers(tmp_path):
    rows = [dict(cell='ST-F', method=f'B{i}', correct=j == 0, regret=j*2)
            for i in range(6) for j in range(2)]
    out = tmp_path/'table.csv'
    module.sensitivity(rows, rows, out)
    result = list(csv.DictReader(out.open()))
    assert len(result) == 12
    assert all(r['correct_rate'] == '0.5' and r['mean_regret'] == '1.0' for r in result)


def test_sensitivity_rejects_missing_units(tmp_path):
    with pytest.raises(ValueError, match='Missing sensitivity units'):
        module.sensitivity([], [], tmp_path/'table.csv')


def test_diff_detects_changed_missing_and_identical(tmp_path):
    a, b = tmp_path/'a', tmp_path/'b'
    a.mkdir(); b.mkdir()
    for name in ['same', 'changed', 'missing']:
        (a/name).write_text('x')
    (b/'same').write_text('x'); (b/'changed').write_text('y')
    assert module.differences(a, b, ['same', 'changed', 'missing']) == ['changed', 'missing']


def test_scratch_cannot_overwrite_repo():
    with pytest.raises(ValueError, match='outside the repository'):
        module.run(ROOT/'results/v2')

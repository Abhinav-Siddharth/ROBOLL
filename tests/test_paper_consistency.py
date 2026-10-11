import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_v1_paper_table_matches_saved_metrics():
    text = (ROOT/'paper/notes/results.md').read_text()
    for row in csv.DictReader((ROOT/'results/tables/overall.csv').open()):
        cells = [row['method']] + [f"{float(row[k]):.3f}" for k in
                 ['correct', 'regret', 'loop', 'human_queries', 'tokens', 'latency_s']]
        assert '| '+' | '.join(cells)+' |' in text
    assert 'no_human_correct' in text
    assert 'autonomous_solvable_or_permanent_correct' in text


def test_claim_does_not_attribute_context_bundle_to_history_alone():
    text = (ROOT/'paper/claim.md').read_text()
    assert 'context bundle' in text
    assert 'ST regimes are observable' in text
    assert 'purely autonomous correctness (+19.5%' not in text
    assert 'only the failure history can tell them apart' not in text


def test_oracle_and_registration_disclosure_are_explicit():
    assert 'forced initial attempt' in (ROOT/'paper/notes/method.md').read_text()
    text = (ROOT/'paper/prereg.md').read_text()
    assert 'f2a2bb0c8591cd4c4593e714b978f3b08b0392ef' in text
    assert 'not a recovered original registration timestamp' in text
    assert 'Unknown' in text


def test_bibliography_contains_verified_metadata():
    text = (ROOT/'paper/refs.bib').read_text()
    assert text.count('@misc{') >= 7
    for arxiv in ['2211.09935', '2608.11977', '2606.01416', '2604.11378',
                  '2606.05806', '2609.22538', '2602.21198']:
        assert f'eprint = {{{arxiv}}}' in text

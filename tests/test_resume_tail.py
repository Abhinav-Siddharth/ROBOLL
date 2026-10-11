import json
from pfr.logging_utils import log_episode, load_done_ids


def test_resume_quarantines_partial_tail_before_append(tmp_path):
    path = tmp_path/'run.jsonl'
    good = json.dumps({'episode_id': 'done'})+'\n'
    tail = b'{"episode_id":"interrupted"'
    path.write_bytes(good.encode()+tail)
    assert load_done_ids(str(path)) == {'done'}
    log_episode({'episode_id': 'next'}, str(path))
    assert [json.loads(l)['episode_id'] for l in path.read_text().splitlines()] == ['done', 'next']
    assert next(tmp_path.glob('run.jsonl.partial-*')).read_bytes() == tail


def test_resume_preserves_valid_record_without_final_newline(tmp_path):
    path = tmp_path/'run.jsonl'
    path.write_text(json.dumps({'episode_id': 'done'}))
    log_episode({'episode_id': 'next'}, str(path))
    assert [json.loads(l)['episode_id'] for l in path.read_text().splitlines()] == ['done', 'next']
    assert not list(tmp_path.glob('*.partial-*'))

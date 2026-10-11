"""Metrics derived from traces, without changing archived runner semantics."""
from .faults import build_fault
from .tasks import get_task


def episode_costs(row):
    fault = build_fault(get_task(row['task']), row['cell'], row['seed'])
    anchor = sum(s['skill'] == fault.skill and s['params'].get('obj') == fault.target
                 for s in row['steps'])
    failures = sum(s['code'] != 'OK' for s in row['steps'])
    return {'anchor_attempts': anchor, 'total_failures': failures,
            'total_failure_cost': failures,
            'anchor_regret': max(0, anchor - row['oracle_attempts']),
            'legacy_regret': row['regret']}


def outcome_flags(row):
    success = row['outcome'] == 'success'
    no_human = row['human_queries'] == 0
    return {'autonomous_success': success and no_human,
            'human_assisted_success': success and not no_human,
            'raw_correct': bool(row['correct']),
            'no_human_correct': bool(row['correct']) and no_human,
            'autonomous_solvable_or_permanent_correct':
                bool(row['correct']) and (not row['solvable'] or no_human)}

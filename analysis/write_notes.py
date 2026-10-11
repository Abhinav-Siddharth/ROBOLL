"""Write paper result notes from saved v1 and optional v2 tables."""
import argparse
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def markdown_csv(path, fields=None):
    with Path(path).open() as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fields = fields or reader.fieldnames
    text = '| '+' | '.join(fields)+' |\n| '+' | '.join(['---']*len(fields))+' |\n'
    for row in rows:
        values = []
        for key in fields:
            value = row[key]
            if key not in ['method', 'hypothesis', 'comparison', 'subset_metric', 'reading']:
                try:
                    value = f'{float(value):.3f}' if key not in ['n', 'n_pairs'] else str(int(float(value)))
                except ValueError:
                    pass
            values.append(value)
        text += '| '+' | '.join(values)+' |\n'
    return text


def write_notes(v2=None):
    overall_fields = ['method', 'correct', 'regret', 'loop', 'human_queries', 'tokens', 'latency_s']
    results = '# Results: v1 archive and format-validity replication\n\n'
    results += ('The v1 archive contains 1320 episodes. The `regret` column below preserves the original '
                'global-failure-based metric for comparability. It is labeled legacy regret; '
                'literal anchor regret and total failure cost are reported separately. '
                'Table values are generated from saved CSV files.\n\n')
    results += '## V1 archived overall table\n\n'+markdown_csv(ROOT/'results/tables/overall.csv', overall_fields)
    results += '\n## V1 derived cost definitions\n\n'+markdown_csv(ROOT/'results/derived_v1/costs_overall.csv')
    results += ('\n`total_failure_cost` is the count of all non-OK execution steps. '
                '`anchor_regret` counts only original target-pick calls above the forced-initial-attempt oracle. '
                'Neither a low cost nor permanent-fault correctness implies successful task recovery.\n\n')
    results += '## V1 autonomous and assisted outcomes\n\n'+markdown_csv(ROOT/'results/derived_v1/outcomes_overall.csv')
    results += ('\n`raw_correct` counts solvable success and permanent abstain/escalate. '
                '`no_human_correct` additionally requires human_queries == 0. '
                '`autonomous_solvable_or_permanent_correct` requires autonomous success on solvable cells '
                'but retains permanent human escalation. Its name must not be shortened to purely autonomous correctness.\n\n'
                'On solvable cells B2, B4 and B5 each have 100/140 autonomous successes in v1. '
                'B4 adds 14 human-assisted successes, seven each in ST-F and PRE-F. '
                'No method has autonomous ST-F success in v1. '
                'Across all 220 episodes, no_human_correct is 100/220 for B4 and 159/220 for B5. '
                'This difference includes correct permanent termination; it is not a permanent-cell-only success rate. '
                'The alternative definition retaining permanent escalation is 136/220 versus 179/220.\n\n'
                '## V1 validity and interpretation limits\n\n'
                'All 720 executed invalid calls omit place.loc: B3 610, B4 24 and B5 86. '
                'B3 has invalid calls in 110/220 episodes and 610/1568 failure steps (38.9%). '
                'In ST-F, B3 and B5 each hold the target before their first invalid call in 18/20 episodes. '
                'These are baseline validity defects; the v1 zeros do not isolate recovery policy capability. '
                'B2 also fails ST-F/PRE-F without executed invalid calls, so schema validity alone need not solve every case.\n\n'
                'B4 vs B2 compares a context bundle: failure history, counts, remaining budget and untried values. '
                'The v1 +22.7-point raw-correct difference cannot isolate history. '
                'B4 made 857 modify decisions, 478 no-ops. Among 790 non-PARAM failures with a recovery decision, '
                '718 (90.9%) selected modify.\n\n'
                'ST regimes are observable in the state supplied to replanning. '
                'The symbolic simulator, oracle failure codes and initial plans, hand-built taxonomy, one model and one seed '
                'limit generalization. Latency sums retain original cache-entry timings and are not execution wall time. '
                'The kinematic replay has no contact physics.\n')
    hypothesis = ('# Hypothesis results\n\nH1-H4 and the three primary all-cell correctness comparisons retain their '
                  'original definitions and analysis. The B4/B2 side comparison is a context-bundle comparison. '
                  'No CI including zero proves equivalence or a tie. Secondary comparisons are descriptive, not confirmatory.\n\n'
                  '## V1 original paired-row bootstrap\n\n'+markdown_csv(ROOT/'results/tables/hypotheses.csv')+
                  '\n## V1 task-cluster sensitivity\n\n'+markdown_csv(ROOT/'results/derived_v1/hypotheses_task_cluster.csv')+
                  '\n## V1 H2 cost-definition sensitivity\n\n'+markdown_csv(ROOT/'results/derived_v1/h2_cost_definitions.csv')+
                  '\nV1 H1 and H3 are not uniformly supported; H2 favors B5 on the tested permanent-cell costs and loops. '
                  'H4 has no clear permanent-correctness difference and favors B5 on F+T3 correctness. '
                  'B3 validity defects and human assistance qualify these readings.\n')
    if v2:
        v2 = Path(v2)
        results += '\n## V2 primary replication\n\n'+markdown_csv(v2/'results/tables/overall.csv', overall_fields)
        results += '\n## V2 costs\n\n'+markdown_csv(v2/'derived/costs_overall.csv')
        results += '\n## V2 solvable success split\n\n'+markdown_csv(v2/'derived/solvable_success.csv')
        results += '\n## V2 named outcomes\n\n'+markdown_csv(v2/'derived/outcomes_overall.csv')
        results += ('\nV2 is the primary H1-H4 dataset under the prospective amendment. '
                    'The original v1 data and tables remain visible above. '
                    'The format repair gives no method new state, history or budget information. '
                    'Consult results/v2/comparison.csv and audit/phase2/GATE_REPORT.md for provenance and validity checks.\n')
        hypothesis += '\n## V2 primary paired-row bootstrap\n\n'+markdown_csv(v2/'results/tables/hypotheses.csv')
        hypothesis += '\n## V2 task-cluster sensitivity\n\n'+markdown_csv(v2/'derived/hypotheses_task_cluster.csv')
        hypothesis += '\n## V2 H2 cost-definition sensitivity\n\n'+markdown_csv(v2/'derived/h2_cost_definitions.csv')
        primary = list(csv.DictReader((v2/'results/tables/hypotheses.csv').open()))
        cluster = list(csv.DictReader((v2/'derived/hypotheses_task_cluster.csv').open()))
        h1 = next(r for r in primary if r['hypothesis']=='H1' and r['comparison']=='B5 - B3')
        h1c = next(r for r in cluster if r['hypothesis']=='H1' and r['comparison']=='B5 - B3')
        h3 = next(r for r in primary if r['hypothesis']=='H3' and r['comparison']=='B5 - B4')
        hypothesis += (f"\nV2 H1 B5-B3: paired-row CI [{h1['ci_lo']}, {h1['ci_hi']}], "
                       f"task-cluster CI [{h1c['ci_lo']}, {h1c['ci_hi']}]. "
                       "The sampling unit matters; neither comparison is an equivalence test. "
                       f"V2 H3 B5-B4 difference {h3['diff']}, CI [{h3['ci_lo']}, {h3['ci_hi']}], "
                       f"{h3['reading']}. This contrasts with the v1 F-cell reading above.\n")
        results += ('\nResidual format-valid failures include missing drawer closure and failure to visit '
                    'a required location. Goal text does not explicitly state every drawer-closure predicate, '
                    'although the original remaining plan includes close actions. The causal contribution '
                    'of goal-specification clarity is untested. V2 does not add formal goal information. '
                    'A valid empty replan is classified as incomplete, not permanent-fault abstention; '
                    'we retain this original outcome convention. Low anchor regret alone is not success.\n')
        if (v2/'ablation_comparisons.csv').exists():
            results += '\n## Matched-context ablation, faulted cells only\n\n'+markdown_csv(v2/'faulted_method_means.csv')
            hypothesis += ('\n## Secondary matched-context comparisons\n\n'+markdown_csv(v2/'ablation_comparisons.csv')+
                           '\nThese 200-pair comparisons are post-audit secondary analyses. B2C retains current '
                           'failure count, remaining budget and untried values but removes prior failure history. '
                           'Compare with B2 for the hint bundle and B4 for history conditional on those hints. '
                           'The intervals do not establish familywise control over every exploratory comparison.\n')

    (ROOT/'paper/notes/results.md').write_text(results)
    (ROOT/'paper/notes/hypothesis.md').write_text(hypothesis)
    print('Result and hypothesis notes generated from saved CSV tables')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--v2')
    args = parser.parse_args()
    write_notes(args.v2)

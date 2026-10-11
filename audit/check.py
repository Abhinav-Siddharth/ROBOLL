import json,collections,itertools,hashlib,pathlib,subprocess,copy,sys
from pfr.tasks import TASKS
from pfr.faults import CELLS,build_fault,FaultyEnv
from pfr.env import Env,Call,SKILL_ARGS,VALUES
from pfr.viz.state import reconstruct,ReplayMismatch
R=pathlib.Path('/home/abhi_pop/pfr')
rows=[json.loads(l) for l in (R/'results/raw/qwen.jsonl').read_text().splitlines() if l.strip()]
pre=[json.loads(l) for l in (R/'results/raw/qwen_pre_fix.jsonl').read_text().splitlines() if l.strip()]
by={r['episode_id']:r for r in rows}; old={r['episode_id']:r for r in pre}
expected={f'qwen2.5:7b|{m}|{t["id"]}|{c}|0' for m in ['B0','B1','B2','B3','B4','B5'] for t in TASKS for c in CELLS}
cnt=collections.Counter(r['episode_id'] for r in rows)
print('INTEGRITY rows',len(rows),'unique',len(cnt),'duplicates',sum(v-1 for v in cnt.values()),'missing',len(expected-set(cnt)),'unexpected',len(set(cnt)-expected))
print('PER CELL COUNTS: cell B0 B1 B2 B3 B4 B5')
for c in CELLS: print(c,*[sum(r['method']==m and r['cell']==c for r in rows) for m in ['B0','B1','B2','B3','B4','B5']])
print('SCHEMA required',__import__('pfr.prompts',fromlist=['REPLAN_SCHEMA']).REPLAN_SCHEMA['properties']['steps']['items']['required'])
print('INVALID: method cell episodes_with_invalid/episodes invalid_steps/all_failure_steps')
for m,c in itertools.product(['B2','B3','B4','B5'],CELLS):
 ss=[r for r in rows if r['method']==m and r['cell']==c]; fail=[s for r in ss for s in r['steps'] if s['code']!='OK']; inv=[s for s in fail if 'invalid call' in s['detail']]
 print(m,c,f'{sum(any("invalid call" in s["detail"] for s in r["steps"]) for r in ss)}/{len(ss)}',f'{len(inv)}/{len(fail)}')
print('SUCCESS SPLIT: cell B0..B5 autonomous/human-assisted (each /20 episodes)')
for c in CELLS:
 print(c,*[str(sum(r['outcome']=='success' and r['human_queries']==0 for r in rows if r['method']==m and r['cell']==c))+'/'+str(sum(r['outcome']=='success' and r['human_queries']>0 for r in rows if r['method']==m and r['cell']==c)) for m in ['B0','B1','B2','B3','B4','B5']])
print('METHOD TOTALS: method correct autonomous-success assisted-success correct-with-no-query permanent-correct')
for m in ['B0','B1','B2','B3','B4','B5']:
 ss=[r for r in rows if r['method']==m]
 print(m,sum(r['correct'] for r in ss),sum(r['outcome']=='success' and r['human_queries']==0 for r in ss),sum(r['outcome']=='success' and r['human_queries']>0 for r in ss),sum(r['correct'] and r['human_queries']==0 for r in ss),sum(r['correct'] and not r['solvable'] for r in ss))
errors=[];label=[];metrics=[];anchor_counts=[];details=[];stop_goal=[];invalids=collections.Counter();synthetic=[]
for r in rows:
 try: ep=reconstruct(r)
 except Exception as e: errors.append((r['episode_id'],str(e)));continue
 if (r['outcome']=='success') != ep.final_goal_ok: label.append((r['episode_id'],r['outcome'],ep.final_goal_ok))
 f=build_fault(ep.task,r['cell'],r['seed']); e=Env(ep.task['init_state']);fe=FaultyEnv(e,f); n=0;anchorok=False;failed_anchor=0;success_anchor=0;keys=collections.Counter(); decisions=[];hq=0
 for i,s in enumerate(r['steps'],1):
  ca=Call(s['skill'],s['params']); rr=fe.execute(ca)
  if rr.detail!=s['detail']:details.append((r['episode_id'],i,rr.detail,s['detail']))
  if s['attempt']!=i:metrics.append((r['episode_id'],'attempt_order'))
  if rr.ok and f.matches(ca):anchorok=True;success_anchor+=1
  if not rr.ok:
   n+=1;keys[ca.key()]+=1
   if f.matches(ca):failed_anchor+=1
   if s['decision']!='cutoff': decisions.append(s['decision'])
  if s['decision']=='escalate':
   hq+=1
   if f.solvable:f.clear(e)
  if 'invalid call' in rr.detail:invalids[rr.detail]+=1
 at=n+int(anchorok);reg=max(0,at-f.oracle_attempts);loop=r['outcome']=='cap_exceeded' or any(v>=3 for v in keys.values());correct=(r['outcome']=='success') if f.solvable else r['outcome'] in ('abstain','escalate')
 calc={'n_fail':n,'attempts_on_faulted_step':at,'oracle_attempts':f.oracle_attempts,'regret':reg,'loop':loop,'human_queries':hq,'correct':correct,'decisions':decisions,'solvable':f.solvable,'group':f.group}
 for k,v in calc.items():
  if r[k]!=v:metrics.append((r['episode_id'],k,r[k],v))
 real_anchor=failed_anchor+success_anchor
 if real_anchor!=r['attempts_on_faulted_step']:anchor_counts.append((r['episode_id'],r['attempts_on_faulted_step'],real_anchor,r['attempts_on_faulted_step']-real_anchor))
 if r['cell']=='ST-F' and any('invalid call' in s['detail'] for s in r['steps']):
  pos=next(i for i,s in enumerate(r['steps']) if 'invalid call' in s['detail']);fr=ep.frames[pos]
  if fr.before['holding']==f.target: synthetic.append((r['method'],r['task']))
print('REPLAY rows',len(rows),'code_mismatches',len(errors),'detail_mismatches',len(details),'metric_mismatches',len(metrics),'success_iff_goal_mismatches',len(label))
print('REPLAY_ERRORS',errors[:10]); print('LABEL_MISMATCHES',label[:10]);print('METRIC_MISMATCHES',metrics[:10])
print('ANCHOR COUNT mismatch episodes',len(anchor_counts),'excess',sum(x[3] for x in anchor_counts),'by_method',dict(collections.Counter(x[0].split('|')[1] for x in anchor_counts)))
print('ANCHOR examples',anchor_counts[:5]); print('INVALID DETAILS',invalids)
print('STF target held before first invalid:',dict(collections.Counter(m for m,t in synthetic)))
# Replay guard mutation tests do not execute a policy or model.
r=copy.deepcopy(next(r for r in rows if r['method']=='B0' and r['cell']=='NONE'));r['steps'][0]['code']='STATE_MISMATCH'
try:reconstruct(r);print('MUTATION wrong code NOT DETECTED')
except ReplayMismatch:print('MUTATION wrong code DETECTED')
r=copy.deepcopy(next(r for r in rows if r['method']=='B0' and r['cell']=='NONE'));r['outcome']='abstain';r['correct']=False;r['steps'][0]['detail']='fabricated'
try: ep=reconstruct(r);print('MUTATION wrong outcome/correct/detail NOT DETECTED final_goal',ep.final_goal_ok)
except ReplayMismatch:print('MUTATION labels DETECTED')
changed=[i for i in by if by[i]!=old.get(i)];print('ARCHIVE rows',len(pre),'full_row_changes',len(changed),'changed_cells',collections.Counter(by[i]['cell'] for i in changed),'changed_tasks',sorted({by[i]['task'] for i in changed}))
print('ARCHIVE equal to commit 06f8af8 raw',subprocess.check_output(['git','show','06f8af8:results/raw/qwen.jsonl'],cwd=R)==(R/'results/raw/qwen_pre_fix.jsonl').read_bytes())
# Independent constructive feasibility test, no recovery policy/LLM episode.
t0=[]; clean=[]; witness=[];oracle=[];initial_codes=[]
for t,c in itertools.product(TASKS,CELLS):
 f=build_fault(t,c,0);e=Env(t['init_state']);fe=FaultyEnv(e,f)
 if e.goal_satisfied(t['goal']):t0.append((t['id'],c))
 for s in t['plan'][:f.step_idx]:fe.execute(Call.from_flat(s))
 anchor=Call.from_flat(t['plan'][f.step_idx]);first=fe.execute(anchor); initial_codes.append((t['id'],c,first.code,first.detail))
 if f.solvable:
  calls=[]
  if c.startswith('TR-T'):calls=[anchor]*(f.n_clear)
  elif c=='PAR-F':calls=[Call(anchor.skill,{**anchor.args,'grasp':f.hidden_fix})]
  elif c=='ST-F':calls=[Call('goto',{'loc':f.true_loc}),anchor]
  elif c=='PRE-F':calls=[Call('goto',{'loc':f.prereq_loc}),Call('goto',{'loc':e.robot_loc}),anchor]
  for ca in calls:fe.execute(ca)
  for s in t['plan'][f.step_idx+1:]:fe.execute(Call.from_flat(s))
  if not e.goal_satisfied(t['goal']):witness.append((t['id'],c))
 if c=='NONE' and not e.goal_satisfied(t['goal']):clean.append(t['id'])
print('FEASIBILITY initial_goal_true',t0,'clean_plan_bad',clean,'solvable_witness_bad',witness,'solvable_cases',140)
print('INITIAL PAIR MISMATCHES',[(t,a,b) for t in [t['id'] for t in TASKS] for a,b in [('PAR-F','PAR-P'),('ST-F','ST-P'),('PRE-F','PRE-P')] if next(x[2:] for x in initial_codes if x[:2]==(t,a))!=next(x[2:] for x in initial_codes if x[:2]==(t,b))])
print('TIME: method seconds total episodes avg')
for m in ['B0','B1','B2','B3','B4','B5']:
 ss=[r for r in rows if r['method']==m];print(m,round(sum(r['latency_s'] for r in ss),2),len(ss),round(sum(r['latency_s'] for r in ss)/len(ss),3))
for cells in [['ST-F','PRE-F'],CELLS]:
 ss=[r for r in rows if r['method'] in ['B2','B3','B4','B5'] and r['cell'] in cells];print('RERUN',cells,'episodes',len(ss),'logged seconds',round(sum(r['latency_s'] for r in ss),2),'LLM_calls',sum(r['llm_calls'] for r in ss))
print('INVENTORY')
paths=set(subprocess.check_output(['git','ls-files'],cwd=R,text=True).splitlines());paths.update(['RUNBOOK_7DAY.md','configs/timing.yaml','docs/RUNBOOK_7DAY.md','docs/RUNBOOK_DAY8.md'])
for p in sorted(paths):
 if p.startswith(('.git','results/cache')):continue
 print('EXISTS' if (R/p).exists() else 'MISSING',p)

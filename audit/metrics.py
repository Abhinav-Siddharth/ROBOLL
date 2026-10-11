import json,pathlib,collections,importlib.util
from pfr.tasks import TASKS
from pfr.faults import build_fault
R=pathlib.Path('/home/abhi_pop/pfr');rs=[json.loads(l) for l in (R/'results/raw/qwen.jsonl').read_text().splitlines()];ts={t['id']:t for t in TASKS}
sp=importlib.util.spec_from_file_location('fig',R/'analysis/make_figures.py');mo=importlib.util.module_from_spec(sp);sp.loader.exec_module(mo)
df=mo.load([str(R/'results/raw/qwen.jsonl')])
for i,r in enumerate(rs):
 f=build_fault(ts[r['task']],r['cell'],r['seed']);n=sum(s['skill']==f.skill and s['params'].get('obj')==f.target for s in r['steps']);df.loc[i,'anchor_regret']=max(0,n-r['oracle_attempts']);df.loc[i,'anchor_attempts']=n
print('HYPOTHETICAL literal anchor metric, holding oracle baseline fixed; no source/log edits')
print(df.groupby('method')[['regret','anchor_regret','attempts_on_faulted_step','anchor_attempts']].mean().round(6).to_string())
for b in ['B0','B4','B3']:print('H2 B5 vs',b,'P anchor regret',mo.paired_boot(df,'B5',b,'anchor_regret',df.group.eq('P')))
# pilot set differs from current pilot config
pilot=[json.loads(l) for l in (R/'results/raw/pilot.jsonl').read_text().splitlines()];print('PILOT DESIGN rows',len(pilot),'models',sorted({r['model'] for r in pilot}),'methods',sorted({r['method'] for r in pilot}),'tasks',sorted({r['task'] for r in pilot}),'seeds',sorted({r['seed'] for r in pilot}));print('PILOT ID duplicates',len(pilot)-len({r['episode_id'] for r in pilot}))

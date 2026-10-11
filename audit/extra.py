import pathlib,json,collections,itertools,subprocess,copy,hashlib,csv,io
from pfr.tasks import TASKS
from pfr.faults import build_fault,FaultyEnv,CELLS
from pfr.env import Env,Call
from pfr.viz.state import reconstruct
R=pathlib.Path('/home/abhi_pop/pfr');oldraw=[json.loads(l) for l in (R/'results/raw/qwen_pre_fix.jsonl').read_text().splitlines()];newraw=[json.loads(l) for l in (R/'results/raw/qwen.jsonl').read_text().splitlines()]
oldsrc=subprocess.check_output(['git','show','06f8af8:src/pfr/faults.py'],cwd=R,text=True);ns={'__name__':'pfr._audit_old_faults','__package__':'pfr'}
import types,sys
mod=types.ModuleType(ns['__name__']);mod.__package__='pfr';sys.modules[mod.__name__]=mod;exec(oldsrc,mod.__dict__)
changed=[];degen=[];bad=[]
for t in TASKS:
 of=mod.build_fault(t,'ST-F',0);nf=build_fault(t,'ST-F',0)
 if of.true_loc!=nf.true_loc:changed.append(t['id'])
 e=Env(t['init_state']);mod.FaultyEnv(e,of)
 if e.goal_satisfied(t['goal']):degen.append(t['id'])
print('GENERATOR_CHANGED_TASKS',changed,'expected_affected_episodes',len(changed)*6,'old_initial_goal_true',degen)
for t,c in itertools.product(TASKS,CELLS):
 f=build_fault(t,c,0);e=Env(t['init_state']);fe=FaultyEnv(e,f)
 if not f.solvable:continue
 for s in t['plan'][:f.step_idx]:fe.execute(Call.from_flat(s))
 anchor=Call.from_flat(t['plan'][f.step_idx]);first=fe.execute(anchor);calls=[];origin=e.robot_loc
 if c.startswith('TR-T'):calls=[anchor]*f.n_clear
 elif c=='PAR-F':calls=[Call(anchor.skill,{**anchor.args,'grasp':f.hidden_fix})]
 elif c=='ST-F':calls=[Call('goto',{'loc':f.true_loc}),anchor,Call('goto',{'loc':origin})]
 elif c=='PRE-F':calls=[Call('goto',{'loc':f.prereq_loc}),Call('goto',{'loc':origin}),anchor]
 codes=[fe.execute(ca).code for ca in calls]
 codes += [fe.execute(Call.from_flat(s)).code for s in t['plan'][f.step_idx+1:]]
 if not e.goal_satisfied(t['goal']) or any(c!='OK' for c in codes[(f.n_clear-1 if c.startswith('TR-T') else 0):]):bad.append((t['id'],c,codes))
print('CORRECTED_WITNESSES solvable_cases',140,'bad',bad)
# sensitivity reconstruction in scratch
fields=['subset','method','n_tasks','correct_count','correct_rate','mean_regret'];out=io.StringIO();w=csv.DictWriter(out,fieldnames=fields,lineterminator='\n');w.writeheader()
for label,rs in [('pre_fix',oldraw),('post_fix',newraw)]:
 for m in ['B0','B1','B2','B3','B4','B5']:
  ss=[r for r in rs if r['cell']=='ST-F' and r['method']==m];n=len(ss);correct=sum(r['correct'] for r in ss);w.writerow(dict(subset=label,method=m,n_tasks=n,correct_count=correct,correct_rate=correct/n,mean_regret=sum(r['regret'] for r in ss)/n))
path=pathlib.Path('/tmp/pfr-audit-evidence/rederived/results/tables/st_f_sensitivity.csv');path.write_text(out.getvalue());print('SENSITIVITY identical',path.read_bytes()==(R/'results/tables/st_f_sensitivity.csv').read_bytes())
# Exact stored intervals and other fields
oldcsv=list(csv.DictReader(io.StringIO(subprocess.check_output(['git','show','06f8af8:results/tables/hypotheses.csv'],cwd=R,text=True))));newcsv=list(csv.DictReader((R/'results/tables/hypotheses.csv').open()))
print('HYPOTHESES rows',len(oldcsv),len(newcsv),'changed_rows',sum(a!=b for a,b in zip(oldcsv,newcsv)),'changed_intervals',sum((a['ci_lo'],a['ci_hi'])!=(b['ci_lo'],b['ci_hi']) for a,b in zip(oldcsv,newcsv)))
for p in sorted((R/'results/tables').glob('*.csv')):print('TABLE_BYTE_DIFF',p.name,p.read_bytes()!=(path.parent/p.name).read_bytes())
for p in sorted((R/'figures').glob('fig*.png')):print('FIGURE_BYTE_DIFF',p.name,p.read_bytes()!=(pathlib.Path('/tmp/pfr-audit-evidence/rederived/figures')/p.name).read_bytes())
# selected detailed trace
for m,c in [('B3','TR-T1'),('B3','ST-F'),('B5','PRE-F'),('B4','ST-F')]:
 r=next(r for r in newraw if r['method']==m and r['cell']==c and r['task']=='t01');print('TRACE',r['episode_id'],r['outcome'],'attempts',r['attempts_on_faulted_step'],'human',r['human_queries']);print(*[(s['attempt'],s['skill'],s['params'],s['code'],s['decision']) for s in r['steps']],sep='\n')
print('DEFAULT_REPLAN_EMPTY',__import__('pfr.prompts',fromlist=['REPLAN_SCHEMA']).REPLAN_SCHEMA['properties']['steps'].get('minItems'))
# inspect artifacts without rendering
from PIL import Image
for p in sorted((R/'figures').glob('*.png')):
 with Image.open(p) as im:im.verify()
print('PNG integrity verified',len(list((R/'figures').glob('*.png'))))
import imageio.v2 as imageio
for p in sorted((R/'results/demo').glob('*.mp4')):
 rr=imageio.get_reader(p);print('VIDEO',p.name,'frames',rr.count_frames(),'fps',rr.get_meta_data()['fps'],'size',rr.get_meta_data()['size']);rr.close()

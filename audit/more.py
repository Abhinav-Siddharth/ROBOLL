import pathlib,json,collections,sys,hashlib,subprocess,importlib.metadata
from pfr.tasks import TASKS
from pfr.env import Call,Env
from pfr.faults import build_fault,FaultyEnv
from pfr.llm import LLMClient
R=pathlib.Path('/home/abhi_pop/pfr');rs=[json.loads(l) for l in (R/'results/raw/qwen.jsonl').read_text().splitlines()]
print('REQUIRESDIST',importlib.metadata.metadata('pfr').get_all('Requires-Dist'))
for m in ['B2','B3','B4','B5']:
 ss=[r for r in rs if r['method']==m];fail=[s for r in ss for s in r['steps'] if s['code']!='OK'];inv=[s for s in fail if 'invalid call' in s['detail']];print('INVALID_TOTAL',m,sum(any('invalid call' in s['detail'] for s in r['steps']) for r in ss),len(inv),len(fail))
ss=[s for r in rs if r['method']=='B4' for s in r['steps']];mods=[s for s in ss if s['decision']=='modify'];nonpar=[s for s in ss if s['code'] not in ['OK','PARAM_MISMATCH'] and s['decision']!='cutoff'];print('B4_MODIFY',len(mods),'noop',sum(s.get('note')=='modify_noop' for s in mods),'nonparam_modify',sum(s['decision']=='modify' for s in nonpar),'nonparam_decisions',len(nonpar))
# Verify fixed ST-F solve possibility with goal-specific legal suffixes, independent of methods.
for tid in ['t01','t04','t08']:
 t=next(t for t in TASKS if t['id']==tid);f=build_fault(t,'ST-F',0);e=Env(t['init_state']);fe=FaultyEnv(e,f)
 for s in t['plan'][:f.step_idx]:fe.execute(Call.from_flat(s))
 origin=e.robot_loc;ca=Call.from_flat(t['plan'][f.step_idx]);res=fe.execute(ca)
 suffix=[Call('goto',{'loc':f.true_loc}),ca,Call('goto',{'loc':origin})]+[Call.from_flat(s) for s in t['plan'][f.step_idx+1:]]
 codes=[fe.execute(s).code for s in suffix];print('LEGAL_STF_SUFFIX',tid,'initial_failure',res.code,'suffix_codes',codes,'goal',e.goal_satisfied(t['goal']))
# Minimum anchor attempts for clairvoyant ST/PRE/PAR fixable observer versus hardcoded 2.
for c in ['ST-F','PRE-F','PAR-F']:
 t=TASKS[0];f=build_fault(t,c,0);e=Env(t['init_state']);fe=FaultyEnv(e,f)
 for s in t['plan'][:f.step_idx]:fe.execute(Call.from_flat(s))
 ca=Call.from_flat(t['plan'][f.step_idx]);origin=e.robot_loc
 if c=='ST-F':fe.execute(Call('goto',{'loc':f.true_loc}))
 if c=='PRE-F':fe.execute(Call('goto',{'loc':f.prereq_loc}));fe.execute(Call('goto',{'loc':origin}))
 if c=='PAR-F':ca.args['grasp']=f.hidden_fix
 res=fe.execute(ca);print('CLAIRVOYANT_FIRST_PICK',c,res.code,'hardcoded_oracle',f.oracle_attempts)
print('CACHE files',len(list((R/'results/cache').glob('*.json'))))
# No model invocation: check pure schema validity of missing loc.
from pfr.prompts import REPLAN_SCHEMA
print('MISSING_LOC permitted required',REPLAN_SCHEMA['properties']['steps']['items']['required'],'Call.from_flat',Call.from_flat({'skill':'place','obj':'apple','orient':'upright'}),'result',Env(TASKS[0]['init_state']).execute(Call.from_flat({'skill':'place','obj':'apple','orient':'upright'})))
# autonomous-correct metric used by updated paper retains permanent human escalation.
import importlib.util
sp=importlib.util.spec_from_file_location('makefig',R/'analysis/make_figures.py');mo=importlib.util.module_from_spec(sp);sp.loader.exec_module(mo)
df=mo.load([str(R/'results/raw/qwen.jsonl')]);df['auto']=df.apply(lambda r:float(r['correct'] and (not r['solvable'] or r['human_queries']==0)),axis=1);print('AUTO_CUSTOM_BOOT',mo.paired_boot(df,'B5','B4','auto',df.index.notna()))
for p in ['results/raw/qwen.jsonl','results/raw/qwen_pre_fix.jsonl','results/tables/hypotheses.csv']:print('SHA256',p,hashlib.sha256((R/p).read_bytes()).hexdigest())

import pathlib,json,hashlib,collections
from pfr.tasks import TASKS
from pfr.env import Env,Call,PARAM_FIELD
from pfr.faults import build_fault,FaultyEnv
from pfr.runner import _untried
from pfr import prompts
R=pathlib.Path(__file__).resolve().parents[2];import sys;rs=[json.loads(l) for file in sys.argv[1:] for l in pathlib.Path(file).read_text().splitlines() if l.strip()];tasks={t['id']:t for t in TASKS};missing=[];mismatch=[];refs=[];loc_omissions=collections.Counter()
for row in rs:
 t=tasks[row['task']];fault=build_fault(t,row['cell'],row['seed']);e=Env(t['init_state']);fe=FaultyEnv(e,fault);plan=[Call.from_flat(s) for s in t['plan']];i=0;hist=[];nf=0;nc=0;tokens=0;lat=0
 def cached(msgs,schema,kind):
  global nc,tokens,lat
  from pfr.llm import cache_key
  identity={'model_digest':row['model_digest'],'ollama_version':row['ollama_server_version'],'num_ctx':4096}
  key=cache_key(row['model'],msgs,schema,row['seed']*1000+nc,0.7,'v2-format',identity);nc+=1;p=R/'results/cache_v2'/f'{key}.json';refs.append(key)
  if not p.exists():missing.append((row['episode_id'],nc,kind,key));raise FileNotFoundError()
  out=json.loads(p.read_text());tokens+=out['tokens'];lat+=out['latency_s'];content=out['content']
  if kind=='replan':
   for call in content.get('steps',[]):
    if call.get('skill')=='place' and 'loc' not in call:loc_omissions[row['method']]+=1
  return content
 try:
  for s in row['steps']:
   ca=Call(s['skill'],s['params'])
   if i>=len(plan) or ca!=plan[i]:mismatch.append((row['episode_id'],'planned_call'));break
   res=fe.execute(ca)
   if res.ok:i+=1;continue
   nf+=1
   if s['decision']=='cutoff':continue
   pf=PARAM_FIELD.get(ca.skill);untried=_untried(ca,pf,hist)
   if row['method']=='B2':out=cached(prompts.mode_messages(t,ca,res,history=None),prompts.MODE_SCHEMA,'mode')
   elif row['method']=='B2C':out=cached(prompts.mode_messages(t,ca,res,history=None,remaining=8-nf,untried=untried if pf else None,n_fail=nf,context_only=True),prompts.MODE_SCHEMA,'mode')
   elif row['method']=='B4':out=cached(prompts.mode_messages(t,ca,res,history=hist,remaining=8-nf,untried=untried if pf else None,n_fail=nf),prompts.MODE_SCHEMA,'mode')
   else:out=None
   if row['method'] in ['B2','B4','B2C'] and out.get('mode')!=s['decision']:mismatch.append((row['episode_id'],'mode'))
   hist.append({'call':ca.to_flat(),'code':res.code,'detail':res.detail,'decision':s['decision']})
   if s['decision']=='modify' and pf and untried:
    out=cached(prompts.modify_messages(t,ca,res,pf,untried),prompts.modify_schema(pf,untried),'modify');v=out.get('new_value');plan[i]=Call(ca.skill,{**ca.args,pf:v if v in untried else untried[0]})
   elif s['decision']=='replan':
    out=cached(prompts.replan_messages(t,ca,res,[ca.to_flat() for ca in plan[i:]],fe.observe()),prompts.REPLAN_SCHEMA,'replan');plan=plan[:i]+[Call.from_flat(s) for s in out.get('steps',[])]
   elif s['decision']=='escalate' and fault.solvable:fault.clear(e)
  for k,v in [('llm_calls',nc),('tokens',tokens),('latency_s',lat)]:
   if abs(row[k]-v)>1e-8:mismatch.append((row['episode_id'],k,row[k],v))
 except FileNotFoundError:continue
print('CACHE_AUDIT model_requests',len(refs),'unique_cache_keys',len(set(refs)),'missing',len(missing),'mismatches',len(mismatch));print('CACHE missing_examples',missing[:4]);print('CACHE mismatch_examples',mismatch[:4]);print('RAW_REPLAN_PLACE_LOC_OMISSIONS',dict(loc_omissions))

if missing or mismatch:raise SystemExit(1)

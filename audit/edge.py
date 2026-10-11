import tempfile,pathlib,json,subprocess,sys,os,collections
from pfr.logging_utils import load_done_ids,log_episode
from pfr.env import Env,Call
from pfr.tasks import TASKS
from pfr.faults import build_fault,FaultyEnv
# Resume corrupted tail reproduction in scratch.
p=pathlib.Path('/tmp/pfr-audit-evidence/broken_tail.jsonl');p.write_text('{"episode_id":"broken"');print('RESUME done_before',load_done_ids(str(p)));log_episode({'episode_id':'recovered'},str(p));lines=p.read_text().splitlines();print('RESUME resulting_lines',lines)
try:[json.loads(l) for l in lines];print('RESUME parses True')
except json.JSONDecodeError:print('RESUME parses False; appended record merged with partial tail')
# Interception masks malformed call validation.
t=TASKS[0];f=build_fault(t,'TR-T1',0);e=Env(t['init_state']);fe=FaultyEnv(e,f);print('MASKED malformed_pick',fe.execute(Call('pick',{'obj':'apple','grasp':None})).code,'then_valid_pick',fe.execute(Call('pick',{'obj':'apple','grasp':'top'})).code,'fault_counter',f.attempts)
rs=[json.loads(l) for l in pathlib.Path('/home/abhi_pop/pfr/results/raw/qwen.jsonl').read_text().splitlines()]
print('EMPTY_REPLAN_EPISODES',[(r['episode_id'],r['outcome']) for r in rs if r['steps'][-1]['decision']=='replan'])
print('MULTIPLE_ANCHOR_SUCCESSES',sum(sum(s['skill']=='pick' and s['params'].get('obj')==build_fault(next(t for t in TASKS if t['id']==r['task']),r['cell'],0).target and s['code']=='OK' for s in r['steps'])>1 for r in rs))
print('PROMPT_VERSIONS',dict(collections.Counter(r['prompt_version'] for r in rs)),'PARSE_FAILURES',sum(r['parse_failures'] for r in rs),'LLM_CALLS',sum(r['llm_calls'] for r in rs))
for hs in ['0','1','42']:
 code='from pfr.tasks import TASKS; from pfr.faults import build_fault; print([build_fault(t,"ST-F",0).true_loc for t in TASKS])'
 env={**os.environ,'PYTHONPATH':'','PYTHONDONTWRITEBYTECODE':'1','PYTHONHASHSEED':hs};print('HASHSEED',hs,subprocess.check_output([sys.executable,'-c',code],env=env,text=True).strip())

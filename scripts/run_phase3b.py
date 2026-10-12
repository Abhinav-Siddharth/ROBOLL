"""Execute one frozen Phase 3b gate; retain every request and stopped batch."""
import argparse
import contextlib
import datetime
import io
import json
from pathlib import Path
import runpy
import subprocess
import sys
import time

from pfr import llm as legacy_llm
from pfr.logging_utils import log_episode
from pfr.methods import make_method
from pfr.noise import make_observer
from pfr.phase3b_runtime import (BatchHealth, BatchStopped, Phase3bLLMClient,
    assert_hashes, check_model_metadata, check_row, episode_id, episode_namespace,
    file_hash, protected_output, prove_model_independent_reuse, replay_cached_row,
    run_coordinates, safe_run_id, validate_grid)
from pfr.runner import run_episode
from pfr.tasks import get_task
from record_metadata import get_json

ROOT = Path(__file__).resolve().parents[1]
AMENDMENT_COMMIT = '07e17c38703effb6f2a630aaa167ad42f198aabd'


def manifest_inputs(root=ROOT):
    lines=(root/'results/MANIFEST.sha256').read_text().splitlines()
    return {name:digest for digest,name in (line.split('  ',1) for line in lines)}


def prepare(root, spec, design, run_id, *, smoke=False, schema_check=False):
    safe_run_id(run_id)
    model=spec['second_model'] if design=='second_model' else spec['qwen_model']
    frozen=manifest_inputs(root)
    assert_hashes(root,frozen)
    code=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
    dirty=subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],
                                  cwd=root,text=True)
    if dirty: raise BatchStopped('Tracked files are dirty; commit before inference')
    if not smoke and not schema_check:
        required={'paper/phase3b_amendment.md','configs/phase3b_hypotheses.json',
                  'analysis/phase3b.py','src/pfr/metrics.py','src/pfr/noise.py',
                  'src/pfr/phase3b_runtime.py','scripts/run_phase3b.py'}
        if not required <= frozen.keys():
            raise BatchStopped('Analysis/amendment dependency hashes are not frozen')
    audit=root/'audit/phase3b'/run_id
    if audit.exists():raise BatchStopped('Run ID already exists; evidence may not be overwritten')
    audit.mkdir(parents=True)
    model_meta=check_model_metadata(model,spec,get_json('tags'),get_json('version'),
                                   get_json('show',{'model':model}))
    model_meta['ollama_client_version_output']=subprocess.check_output(
        ['ollama','--version'],text=True).strip()
    (audit/'model.json').write_text(json.dumps(model_meta,indent=2)+'\n')
    identity=dict(model_digest=model_meta['model_digest'],
                  ollama_version=model_meta['ollama_server_version'],num_ctx=4096)
    def sink(event):
        with (audit/'requests.jsonl').open('a') as handle:
            handle.write(json.dumps(event,sort_keys=True)+'\n')
    health=BatchHealth(event_sink=sink)
    namespace=f'phase3b/{run_id}'
    return model,frozen,code,audit,model_meta,identity,health,namespace


def base_provenance(spec,code,run_id,design,model_meta,root):
    return dict(dataset_version='v3-phase3b',design=design,run_id=run_id,
                code_commit=code,amendment_commit=AMENDMENT_COMMIT,
                amendment_sha256=file_hash(root/spec['amendment']),
                hypotheses_sha256=file_hash(root/'configs/phase3b_hypotheses.json'),
                manifest_sha256=file_hash(root/'results/MANIFEST.sha256'),
                model_digest=model_meta['model_digest'],
                ollama_server_version=model_meta['ollama_server_version'],
                inference_options=model_meta['options'])


def execute(spec,design,run_id,*,smoke=False,schema_check=False,root=ROOT):
    root=Path(root)
    model,frozen,code,audit,meta,identity,health,namespace=prepare(
        root,spec,design,run_id,smoke=smoke,schema_check=schema_check)
    start=time.monotonic();rows=[];sampled=[]
    summary=dict(status='running',design=design,run_id=run_id,model=model,
                 code_commit=code,started_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 smoke=smoke,schema_check=schema_check)
    cache_dir=root/'results/cache_v3'
    try:
        if schema_check:
            clients=[]
            def factory(model,base_seed=0,temp=.7):
                c=Phase3bLLMClient(model,base_seed,temp,cache_dir=cache_dir,
                    namespace=f'{namespace}/schema-seed-{base_seed}',identity=identity,
                    health=health,cold=True)
                clients.append(c);return c
            original=legacy_llm.LLMClient;argv=sys.argv[:];output=io.StringIO()
            try:
                legacy_llm.LLMClient=factory;sys.argv=[str(root/'scripts/check_llm.py'),model]
                with contextlib.redirect_stdout(output):
                    runpy.run_path(str(root/'scripts/check_llm.py'),run_name='__main__')
            finally:
                legacy_llm.LLMClient=original;sys.argv=argv
                (audit/'check_llm.txt').write_text(output.getvalue())
            print(output.getvalue(),end='',flush=True)
            if health.json_schema_failures or sum(c.parse_failures for c in clients):
                raise BatchStopped('Second-model schema compatibility requires zero malformed responses')
            for c in clients:
                for key in c.cache_keys:
                    saved=json.loads((cache_dir/(key+'.json')).read_text())
                    if saved['request_identity']['namespace']!=c.namespace:
                        raise BatchStopped('Schema cache identity mismatch')
            summary.update(logical_calls=sum(c.n_calls for c in clients),
                           cache_hits=sum(c.cache_hits for c in clients),
                           exhausted_parse_failures=sum(c.parse_failures for c in clients))
        else:
            coords=run_coordinates(spec,design,smoke=smoke)
            relative=(f'audit/phase3b/{run_id}/episodes.jsonl' if smoke else spec['full_outputs'][design])
            allowed=[relative] if smoke else list(spec['full_outputs'].values())
            path=protected_output(root,relative,allowed)
            path.parent.mkdir(parents=True,exist_ok=True)
            provenance=base_provenance(spec,code,run_id,design,meta,root)
            for index,coordinate in enumerate(coords,1):
                task=get_task(coordinate['task'])
                client=Phase3bLLMClient(model,coordinate['seed'],cache_dir=cache_dir,
                    namespace=episode_namespace(namespace,model,coordinate),identity=identity,
                    health=health,cold=True)
                begin=time.monotonic()
                row=run_episode(task,coordinate['cell'],coordinate['seed'],
                    make_method(coordinate['method']),client,8,
                    observation_transform=make_observer(task,coordinate['cell'],
                                                       coordinate['seed'],coordinate['noise_p']))
                row['episode_id']=episode_id(model,coordinate)
                row.update(**provenance,reused=False,noise_p=coordinate['noise_p'],
                    environment_seed=coordinate['seed'],llm_base_seed=coordinate['seed'],
                    cache_namespace=client.namespace,cache_identity=identity,
                    cache_keys=client.cache_keys,cache_hits=client.cache_hits,
                    parse_retries=client.parse_retries,wall_time_s=time.monotonic()-begin,
                    recorded_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
                # Retain the executed row even if its integrity check subsequently stops the batch.
                log_episode(row,str(path));rows.append(row)
                check_row(row)
                if smoke and client.cache_hits:
                    raise BatchStopped('Cold smoke recorded a cache hit')
                try:
                    gpu=subprocess.check_output(['nvidia-smi','--query-gpu=memory.used',
                         '--format=csv,noheader,nounits'],text=True,timeout=5).strip()
                    sampled.append(int(gpu.splitlines()[0]))
                except (OSError,ValueError,subprocess.SubprocessError):pass
                if index%10==0:
                    print(f'{run_id}: {index}/{len(coords)} episodes; '
                          f'{time.monotonic()-start:.1f}s; requests={health.completed_responses}; '
                          f'JSON/schema failures={health.json_schema_failures}',flush=True)
            verdict=validate_grid(rows,model,coords)
            cached=[replay_cached_row(row,cache_dir=cache_dir) for row in rows]
            summary.update(**verdict,newly_executed=len(coords),
                           cache_verified_calls=sum(v['logical_calls'] for v in cached),
                           cache_verified_hits=sum(v['cache_hits'] for v in cached),
                           cache_verification_server_requests=0,
                           logical_calls=sum(r['llm_calls'] for r in rows),
                           cache_hits=sum(r['cache_hits'] for r in rows),
                           exhausted_parse_failures=sum(r['parse_failures'] for r in rows),
                           output=relative,seconds_per_episode=(time.monotonic()-start)/len(rows),
                           first_episode_wall_s=rows[0]['wall_time_s'],
                           mean_episode_execution_wall_s=sum(r['wall_time_s'] for r in rows)/len(rows),
                           maximum_sampled_gpu_memory_mib=max(sampled) if sampled else None)
            if design=='second_model' and not smoke:
                source=root/spec['baseline'];source_hash=file_hash(source)
                controls=[json.loads(line) for line in source.read_text().splitlines()
                          if line.strip()]
                controls=[r for r in controls if r['method'] in ('B0','B1') or r['cell']=='NONE']
                if len(controls)!=520:raise BatchStopped('Second-model reuse grid differs from 520')
                for source_row in controls:
                    row=prove_model_independent_reuse(source_row,model,source_hash,code)
                    row.update(**provenance,cache_namespace=episode_namespace(namespace,model,row),
                               cache_identity=identity,cache_keys=[],cache_hits=0,parse_retries=0,
                               environment_seed=0,llm_base_seed=0,wall_time_s=0)
                    log_episode(row,str(path));rows.append(row)
                complete=run_coordinates(spec,'seed1')
                complete=[{**r,'seed':0} for r in complete]
                summary.update(**validate_grid(rows,model,complete),reused_rows=520)
                for row in rows[-520:]:replay_cached_row(row,cache_dir=cache_dir)
        assert_hashes(root,frozen)
        summary.update(status='passed',wall_time_s=time.monotonic()-start,**health.summary())
    except BaseException as error:
        summary.update(status='stopped',completed_rows=len(rows),wall_time_s=time.monotonic()-start,
                       error_type=type(error).__name__,error=str(error),**health.summary())
        (audit/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
        print(json.dumps(summary,indent=2),flush=True)
        raise
    (audit/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2),flush=True)
    return summary


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--design',required=True,choices=['seed1','seed2','second_model',
                                                  'noise_p01','noise_p02','noise_p03'])
    p.add_argument('--run-id',required=True)
    p.add_argument('--smoke',action='store_true')
    p.add_argument('--schema-check',action='store_true')
    a=p.parse_args()
    if a.schema_check and a.design!='second_model':p.error('Schema check is for the second model')
    spec=json.loads((ROOT/'configs/phase3b_hypotheses.json').read_text())
    execute(spec,a.design,a.run_id,smoke=a.smoke,schema_check=a.schema_check)

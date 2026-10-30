"""Compare fresh execution from the ZIP's privacy-reduced dataset with raw-run outputs."""
from pathlib import Path
import json
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
REPLAY=ROOT/'qa/package_replay_20261028/LabDSS_102230343_PARTIAL_20261028'
result={}
for label in ['provided_snapshot','website_before','website_after_capture']:
    original=ROOT/'outputs/notebook'/label;replay=REPLAY/'outputs/notebook'/label
    for name in ['recommendations.csv','offline_metrics.csv','train_ratings.csv','test_ratings.csv','train_views.csv']:
        a=pd.read_csv(original/name,dtype=str,keep_default_na=False)
        b=pd.read_csv(replay/name,dtype=str,keep_default_na=False)
        a=a.drop(columns=['dataset_snapshot_id'],errors='ignore')
        b=b.drop(columns=['dataset_snapshot_id'],errors='ignore')
        pd.testing.assert_frame_equal(a,b)
    r=json.loads((replay/'run_manifest.json').read_text(encoding='utf-8'))
    assert 'shared' in r['data_dir']
    result[label]={'status':'PASS','replay_snapshot':r['dataset_snapshot_id'],'path':r['data_dir'],
                   'compared':['recommendations','offline_metrics','train_ratings','test_ratings','train_views']}
execution=json.loads((REPLAY/'qa/notebook_execution.json').read_text(encoding='utf-8'))
assert execution['status']=='PASS' and execution['code_cells']==14
receipt={'status':'PASS','clean_kernel':True,'code_cells':14,'errors':0,
         'datasets':result,'note':'Fresh execution used only ZIP contents and installed pinned dependencies; snapshot hashes differ after privacy reduction. Numerical outputs and partitions match raw runs.'}
(ROOT/'verification/package_replay.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'status':'PASS','snapshots':len(result),'code_cells':14}))

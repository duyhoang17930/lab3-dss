"""Audit the actual artifacts, tests, privacy-reduced inputs and snapshot boundaries."""
from pathlib import Path
from hashlib import sha256
import csv
import json
import math
import re
import shutil
import subprocess
import sys
import zipfile
from xml.etree import ElementTree as ET
import nbformat
import pandas as pd
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from job_recsys.data import load_dataset
from job_recsys.models import Config,RecommenderSuite
from job_recsys.evaluation import positive_holdout

def digest(path):return sha256(path.read_bytes()).hexdigest()
def main():
    out=ROOT/'verification';out.mkdir(exist_ok=True)
    result={};tests=subprocess.run([sys.executable,'-m','pytest','-q'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
    (out/'test_results.txt').write_text(tests.stdout+tests.stderr,encoding='utf-8')
    assert tests.returncode==0,tests.stdout
    result['tests']='PASS';result['test_summary']=tests.stdout.strip().splitlines()[-1]
    notebook=ROOT/'LabDSS_RECSYS_9_thuat_toan.ipynb'
    nb=nbformat.read(notebook,as_version=4);code=[c for c in nb.cells if c.cell_type=='code']
    assert all(c.execution_count is not None for c in code)
    assert not [o for c in code for o in c.outputs if o.output_type=='error']
    result['notebook']={'status':'PASS','code_cells':len(code),'sha256':digest(notebook)}
    shutil.copy2(ROOT/'qa/notebook_execution.json',out/'notebook_execution.json')
    assert json.loads((out/'notebook_execution.json').read_text())['sha256']==digest(notebook)
    cfg=Config();snapshots={};equivalence={}
    sources={'provided_snapshot':'data_MEDAJOB','website_before':'data/raw/website_before/csv','website_after_capture':'data/raw/website_after_capture/csv'}
    for label,path in sources.items():
        raw=load_dataset(ROOT/path);shared=load_dataset(ROOT/'data/shared'/label)
        snapshots[label]={'snapshot_id':raw.snapshot_id,'users':len(raw.users),'jobs':len(raw.jobs),'ratings':len(raw.ratings),
                          'views':len(raw.views),'open_jobs':int(raw.jobs.status.eq('open').sum()),'raw_sha256':raw.raw_hashes}
        # Only username masking and unused/private columns differ; all model fields must match.
        pd.testing.assert_frame_equal(raw.users[['user_id','skill_list']],shared.users[['user_id','skill_list']])
        pd.testing.assert_frame_equal(raw.jobs.drop(columns=['link']),shared.jobs.drop(columns=['link']))
        pd.testing.assert_frame_equal(raw.ratings,shared.ratings);pd.testing.assert_frame_equal(raw.views,shared.views)
        tr,te,_=positive_holdout(raw,cfg);st,se,_=positive_holdout(shared,cfg)
        pd.testing.assert_frame_equal(tr.ratings,st.ratings);pd.testing.assert_frame_equal(te,se)
        assert not set(zip(te.user_id,te.job_id)).intersection(zip(tr.views.user_id,tr.views.job_id))
        manifest=json.loads((ROOT/'outputs/notebook'/label/'run_manifest.json').read_text(encoding='utf-8'))
        assert manifest['dataset_snapshot_id']==raw.snapshot_id
        for name,h in manifest['artifact_sha256'].items():assert digest(ROOT/'outputs/notebook'/label/name)==h,name
        for name,h in manifest['source_sha256'].items():assert digest(ROOT/'job_recsys'/name)==h,name
        equivalent=RecommenderSuite(cfg).fit(shared)
        if manifest['target_user_id'] is not None:
            expected=pd.read_csv(ROOT/'outputs/notebook'/label/'recommendations.csv',dtype={'user_id':str,'job_id':str},keep_default_na=False)
            actual=equivalent.recommend(manifest['target_user_id'])
            pd.testing.assert_frame_equal(expected.drop(columns=['dataset_snapshot_id']),actual.drop(columns=['dataset_snapshot_id']),check_dtype=False,atol=1e-12,rtol=1e-12)
        equivalence[label]={'status':'PASS','shared_snapshot_id':shared.snapshot_id,'note':'All model inputs and holdout identical; target recommendations verified where target exists.'}
    original_manifest=json.loads((ROOT/'outputs/provided_snapshot/run_manifest.json').read_text(encoding='utf-8'))
    assert snapshots['provided_snapshot']['raw_sha256']==original_manifest['raw_sha256']
    result['original_data_unchanged']='PASS';result['raw_shared_equivalence']=equivalence
    result['snapshots']=snapshots
    result['live_drift']={k:snapshots['website_after_capture'][k]-snapshots['website_before'][k] for k in ['users','jobs','ratings','views','open_jobs']}
    caps=json.loads((ROOT/'data/website/verified_baseline/capture_manifest.json').read_text(encoding='utf-8'))
    assert len(caps)==11 and len({c['capture_id'] for c in caps})==11
    for c in caps:
        assert c['http_status']==200 and c['capture_status']=='success' and c['algorithm']==c['returned_algorithm']
        obj=json.loads((ROOT/'data/website/verified_baseline'/(c['capture_id']+'.json')).read_text(encoding='utf-8'))
        assert len(obj['items'])==c['n_items']
        assert all(math.isfinite(i['score']) for i in obj['items'])
        assert (ROOT/c['screenshot']).read_bytes().startswith(b'\x89PNG')
    result['captures']={'status':'PASS','count':len(caps),'visual_review':'11 recommendation images and 5 profile/employer/history/verified-search/duplicate-search images inspected','limitation':'Some baseline star-rating widgets were still loading; ranking labels/items verified.'}
    imp=json.loads((ROOT/'data/import/import_manifest.json').read_text(encoding='utf-8'))
    with (ROOT/'data/import/jobs_import_preview.csv').open(encoding='utf-8-sig',newline='') as f:rows=list(csv.reader(f))
    assert len(rows)==11 and all(len(r)==19 for r in rows)
    assert imp['selected']==10 and digest(ROOT/'data/import/jobs_import_preview.csv')==imp['csv_sha256']
    result['import']={'csv':'PASS_10_ROWS_19_COLUMNS','published_count':0,'status':'AWAITING_USER_CONFIRMATION'}
    report=ROOT/'reports/Bao_cao_LabDSS_102230343_DRAFT_NOT_VERIFIED.docx'
    with zipfile.ZipFile(report) as z:
        assert z.testzip() is None
        body=ET.fromstring(z.read('word/document.xml'))
        ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        texts=' '.join(t.text or '' for t in body.findall('.//w:t',ns))
        assert '102230343' in texts and 'Nguyễn Hoàng Hà' in texts
        assert all(name in texts for name in ['CBF','Hybrid','SGD','ALS Explicit','ALS Implicit'])
        # No example credentials inherited from the retained template.
        assert not re.search(r'sv102102102|Password\s*:',texts)
    structure=json.loads((ROOT/'qa/report_structure.json').read_text(encoding='utf-8'))
    assert structure['reference_sha256']==digest(ROOT/'LabDSS WebsiteRECSYS.docx')
    result['report']={'structure':'PASS','visual':'NOT_VERIFIED','reason':'Bundled LibreOffice soffice.exe unavailable','figures':structure['figures'],'sha256':digest(report)}
    sensitive=[]
    for p in (ROOT/'data/shared').rglob('*.csv'):
        txt=p.read_text(encoding='utf-8-sig')
        if re.search(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|eyJ[A-Za-z0-9_-]+\.eyJ',txt):sensitive.append(str(p.relative_to(ROOT)))
    assert not sensitive,f'Sensitive patterns in {sensitive}'
    result['privacy_reduced_csv_scan']='PASS_NO_EMAIL_OR_JWT_PATTERNS'
    result['overall_status']='PARTIAL_HANDOFF_NOT_ASSIGNMENT_COMPLETE'
    (out/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    shutil.copy2(ROOT/'qa/report_structure.json',out/'report_structure.json')
    print(json.dumps({'tests':result['test_summary'],'notebook':result['notebook']['status'],'captures':len(caps),'report_visual':'NOT_VERIFIED','overall':result['overall_status']},ensure_ascii=False))

if __name__=='__main__':main()

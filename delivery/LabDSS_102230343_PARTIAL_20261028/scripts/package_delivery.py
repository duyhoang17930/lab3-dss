"""Allowlist-only partial handoff. Excludes raw users, credentials and stale captures."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime
import json
import re
import shutil
import zipfile

ROOT=Path(__file__).resolve().parents[1]
LABEL='LabDSS_102230343_PARTIAL_20261028'

def main():
    validation=json.loads((ROOT/'verification/validation.json').read_text(encoding='utf-8'))
    assert validation['tests']=='PASS' and validation['notebook']['status']=='PASS'
    stage=ROOT/'delivery'/LABEL
    stage.mkdir(parents=True,exist_ok=True)
    single=['README.md','STATUS.md','METHODS.md','requirements.txt','pytest.ini','LabDSS_RECSYS_9_thuat_toan.ipynb']
    patterns=['job_recsys/*.py','tests/*.py','configs/*.json','scripts/*.py','scripts/*.mjs',
              'data/shared/**/*.csv','data/shared/*.json','data/import/*.json','data/import/*.csv','data/import/*.md',
              'data/templates/*.csv','data/website/verified_baseline/*.json','data/website/verified_baseline/*.csv',
              'evidence/website/verified_baseline/*.png','outputs/notebook/**/*.csv','outputs/notebook/**/*.json',
              'outputs/notebook/**/*.png','verification/*.json','verification/*.txt','reports/*.docx','reports/*.md']
    single += ['evidence/website/'+n+'.png' for n in ['01_profile_initial','02_employer_initial_no_jobs','03_rating_history_initial','04_search_python_verified','05_duplicate_check_J01']]
    files={ROOT/n for n in single}
    for pattern in patterns:files.update(ROOT.glob(pattern))
    manifest={}
    for p in sorted(files):
        assert p.is_file(),p
        rel=p.relative_to(ROOT);dest=stage/rel;dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(p,dest);manifest[rel.as_posix()]=sha256(dest.read_bytes()).hexdigest()
    # Source scripts may mention credential field names for redaction, but must not contain actual secrets.
    suspicious=[]
    for p in stage.rglob('*'):
        if not p.is_file() or p.suffix not in {'.py','.mjs','.json','.csv','.md','.txt','.ipynb'}:continue
        text=p.read_text(encoding='utf-8-sig')
        if re.search(r'eyJ[A-Za-z0-9_-]{10,}\.eyJ|(?:password|access_token)\s*[:=]\s*[\x22\x27][^\x22\x27]{5,}',text,re.I):suspicious.append(str(p.relative_to(stage)))
    assert not suspicious,suspicious
    status={'status':'PARTIAL_HANDOFF_NOT_ASSIGNMENT_COMPLETE','created_at':datetime.now().isoformat(),
            'files':len(manifest),'sha256':manifest,'excluded':['raw exports','original assignment with credential examples','notebook backup','venv','stale baseline captures','unverified search screenshot'],
            'open_requirements':['real profile and rating confirmation','approval and successful import of >=10 jobs','user password change','Word render visual verification'],
            'privacy':'Identifiers and interaction signals minimized; not irreversibly anonymized.'}
    (stage/'MANIFEST.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf-8')
    zip_path=ROOT/'delivery'/(LABEL+'.zip')
    # Archive exactly the allowlist, never arbitrary leftovers in staging.
    with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED,compresslevel=7) as z:
        for rel in sorted(manifest):z.write(stage/rel,LABEL+'/'+rel)
        z.write(stage/'MANIFEST.json',LABEL+'/MANIFEST.json')
    with zipfile.ZipFile(zip_path) as z:
        assert z.testzip() is None
        assert len(z.namelist())==len(manifest)+1
        for rel,h in manifest.items():assert sha256(z.read(LABEL+'/'+rel)).hexdigest()==h
    receipt={'zip':str(zip_path.relative_to(ROOT)), 'files':len(manifest)+1,'bytes':zip_path.stat().st_size,
             'sha256':sha256(zip_path.read_bytes()).hexdigest(),'crc':'PASS','allowlist_hashes':'PASS','status':status['status']}
    (ROOT/'delivery/package_verification.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    print(json.dumps(receipt,ensure_ascii=False))

if __name__=='__main__':main()

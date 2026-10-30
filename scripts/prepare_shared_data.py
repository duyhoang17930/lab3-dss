"""Minimize PII in analysis copies, preserving only fields needed by the models."""
from pathlib import Path
import hashlib
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {'provided_snapshot':'data_MEDAJOB', 'website_before':'data/raw/website_before/csv',
           'website_after_capture':'data/raw/website_after_capture/csv'}

def main():
    provenance = {}
    for label, source in SOURCES.items():
        src, dst = ROOT/source, ROOT/'data/shared'/label
        dst.mkdir(parents=True, exist_ok=True)
        tables = {}
        for name in ['users','user_profiles','job','ratings','job_views']:
            path = src/f'{name}.csv'
            if name == 'job' and not path.exists(): path = src/'jobs.csv'
            tables[name] = pd.read_csv(path,dtype=str,keep_default_na=False)
        user = tables['users'][['id','username']].copy()
        user['username'] = [n if n == 'sv102230343' else 'anonymous_'+i for i,n in zip(user.id,user.username)]
        frames = {'users':user, 'user_profiles':tables['user_profiles'][['user_id','user_skills']],
                  'job':tables['job'][[c for c in ['id','job_title','job_skills','company_name','job_location','status','deadline'] if c in tables['job']]],
                  'ratings':tables['ratings'][['user_id','job_id','rating']],
                  'job_views':tables['job_views'][['user_id','job_id','view_duration']]}
        for name, frame in frames.items(): frame.to_csv(dst/f'{name}.csv',index=False,encoding='utf-8-sig')
        provenance[label] = {'source':source,'output':str(dst.relative_to(ROOT)).replace('\\','/'),
                             'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in src.glob('*.csv')},
                             'shared_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in dst.glob('*.csv')},
                             'removed':'Emails, names other than target identity in report, phone, address, birth date, CV, profile prose, auth fields, employer IDs, HR contacts, comments and timestamps.',
                             'retained':'Pseudonymous user IDs, skill labels, job IDs/public job labels, explicit ratings and view duration; minimum model inputs. Not a claim of irreversible anonymization.'}
    (ROOT/'data/shared/provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2),encoding='utf-8')
    print({k:{n:len(pd.read_csv(ROOT/v['output']/f'{n}.csv')) for n in ['users','job','ratings']} for k,v in provenance.items()})

if __name__=='__main__': main()

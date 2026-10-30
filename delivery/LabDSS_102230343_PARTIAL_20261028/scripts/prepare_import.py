"""Prepare a quoted 19-column preview only. This script never writes to the site."""
from __future__ import annotations
import csv
from difflib import SequenceMatcher
import hashlib
import json
from pathlib import Path
import re
import unicodedata
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

def normalized(value):
    value = unicodedata.normalize('NFKD', str(value)).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', ' ', value).strip()

def source_ids(value):
    return set(re.findall(r'(?<!\d)744\d{12}(?!\d)', str(value)))

def company_group(value):
    value = normalized(value)
    return 'bosch' if 'bosch' in value else 'kms' if 'kms' in value else value

def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--catalog', default='data/raw/website_before/csv/job.csv')
    args = p.parse_args()
    catalog_path = ROOT / args.catalog
    catalog = pd.read_csv(catalog_path, dtype=str, keep_default_na=False)
    candidates = json.loads((ROOT/'data/import/candidates.json').read_text(encoding='utf-8'))
    template = ROOT/'data/templates/tkrecsys_jobtemplate_original.csv'
    with template.open(encoding='utf-8-sig', newline='') as f: fields = next(csv.reader(f))
    assert len(fields) == 19
    audit, rows = [], []
    for c in candidates:
        ids = source_ids(c['url']) | set(c['aliases'])
        matches = []
        for r in catalog.to_dict('records'):
            link = r.get('link', '')
            same_source = bool(ids & source_ids(link)) or c['url'].rstrip('/').lower() == link.rstrip('/').lower()
            same_company = company_group(c['company']) == company_group(r.get('company_name', ''))
            title_ratio = SequenceMatcher(None, normalized(c['title']), normalized(r.get('job_title', ''))).ratio()
            if same_source or (same_company and title_ratio >= .82):
                matches.append({'job_id': r['id'], 'title': r.get('job_title'), 'company': r.get('company_name'),
                                'location': r.get('job_location'), 'link': link, 'same_source': same_source,
                                'title_similarity': round(title_ratio, 4)})
        status = 'possible_duplicate_review' if matches else 'no_match_in_snapshot'
        selected = not matches and c['ref'] != 'J11'
        audit.append({'ref':c['ref'], 'title':c['title'], 'company':c['company'], 'location':c['location'],
                      'source_url':c['url'], 'dedupe_status':status,'selected':selected,'matches':matches})
        if selected:
            row = dict.fromkeys(fields, '')
            row.update(job_title=c['title'], job_description=c['description'], job_applyrequirement=c['requirements'],
                       job_skills=json.dumps(c['skills'], ensure_ascii=False), job_health_insurance=c['insurance'],
                       benefits=c['benefits'], job_location=c['location'], job_country='Vietnam', job_type=c['type'],
                       experience_level=c['experience'], company_name=c['company'], company_address=c['address'],
                       company_website='https://www.bosch.com.vn/' if 'Bosch' in c['company'] else 'https://kms-technology.com/',
                       link=c['url'])
            rows.append(row)
    out = ROOT/'data/import/jobs_import_preview.csv'
    with out.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields, quoting=csv.QUOTE_ALL)
        writer.writeheader(); writer.writerows(rows)
    with out.open(encoding='utf-8-sig', newline='') as f:
        check = list(csv.reader(f))
    assert all(len(r) == 19 for r in check)
    assert len({r['link'] for r in rows}) == len(rows)
    for r in rows: assert isinstance(json.loads(r['job_skills']), list)
    manifest = {'catalog_path':args.catalog, 'catalog_sha256':hashlib.sha256(catalog_path.read_bytes()).hexdigest(),
                'catalog_rows':len(catalog), 'candidates':len(candidates), 'selected':len(rows), 'columns':fields,
                'csv_sha256':hashlib.sha256(out.read_bytes()).hexdigest(), 'status':'AWAITING_USER_CONFIRMATION_NOT_IMPORTED',
                'unknown_fields_left_blank':['salary_min','salary_max','job_deadline','hr_contact','job_type_skills'],
                'audit':audit}
    (ROOT/'data/import/import_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    lines = ['# Danh sách dự kiến đăng trên website RECSYS', '',
             'Chưa import. Chỉ đăng sau khi người dùng xác nhận danh sách này. Không ứng tuyển hoặc gửi thông tin cho nhà tuyển dụng.', '',
             f'Đã đối chiếu {len(catalog)} tin trong snapshot; CSV có {len(rows)} dòng và đúng 19 cột.',
             'Mức lương, hạn nộp và liên hệ không được nguồn công bố được để trống, không thay bằng 0 hoặc ngày tự đặt.', '',
             '| Mã | Vị trí | Công ty | Địa điểm | Kiểm tra trùng |', '|---|---|---|---|---|']
    for a in audit:
        lines.append(f"| {a['ref']} | [{a['title']}]({a['source_url']}) | {a['company']} | {a['location']} | {a['dedupe_status']} {'(dự phòng)' if not a['selected'] else ''} |")
    lines += ['', 'Không có tin cũ thuộc tài khoản 458 tại thời điểm kiểm tra; không đóng hoặc sửa tin của tài khoản khác.',
              '', 'Đối chiếu gồm ID/URL nguồn và tên công ty + độ gần tiêu đề. Vẫn cần làm mới danh mục và kiểm tra lại nguồn ngay trước import.']
    (ROOT/'data/import/IMPORT_PREVIEW.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'selected':len(rows),'duplicates':[(a['ref'],[m['job_id'] for m in a['matches']]) for a in audit if a['matches']],
                      'csv_columns':len(fields),'status':manifest['status']},ensure_ascii=False))

if __name__ == '__main__': main()

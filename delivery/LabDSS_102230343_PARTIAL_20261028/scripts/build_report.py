"""Build a truthful Word working report from executed CSVs and real screenshots.

Run only with the bundled document Python runtime after the authoring marker.
The supplied assignment is read-only; its page geometry/styles seed the report.
"""
from pathlib import Path
from datetime import datetime
import csv
import hashlib
import json
import struct
from docx import Document
from docx.shared import Inches, Pt, RGBColor, Twips
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports'; OUT.mkdir(exist_ok=True)
REFERENCE=ROOT/'LabDSS WebsiteRECSYS.docx'
reference_hash=hashlib.sha256(REFERENCE.read_bytes()).hexdigest()
doc=Document(REFERENCE)
for child in list(doc._element.body):
    if child.tag != qn('w:sectPr'): doc._element.body.remove(child)
for section in doc.sections:
    for container in [section.header,section.footer]:
        for p0 in container.paragraphs: p0.clear()
    section.page_width=Twips(11907); section.page_height=Twips(16840)
    section.top_margin=Twips(1134);section.right_margin=Twips(1134)
    section.bottom_margin=Twips(1418);section.left_margin=Twips(1418)
for name,size in [('Normal',13),('Title',19),('Heading 1',16),('Heading 2',14),('Heading 3',13),('Caption',10)]:
    style=doc.styles[name];style.font.name='Times New Roman';style.font.size=Pt(size)
    style.font.color.rgb=RGBColor(0,0,0)
    style._element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'),'Times New Roman')
    style.paragraph_format.space_after=Pt(6)
    style.paragraph_format.line_spacing=1.12
    if name.startswith('Heading'): style.paragraph_format.keep_with_next=True
doc.core_properties.author='Nguyễn Hoàng Hà'
doc.core_properties.title='Báo cáo thực hành hệ thống RECSYS gợi ý việc làm'
doc.core_properties.subject='LabDSS MEDAJob và chín thuật toán gợi ý'
doc.core_properties.comments=''
doc.core_properties.last_modified_by=''
doc.core_properties.keywords=''
doc.core_properties.revision=1
doc.core_properties.created=datetime(2026,10,28)
doc.core_properties.modified=datetime(2026,10,28)
md=[];figure_count=0

def read_json(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))
def read_csv(path):
    with (ROOT/path).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def paragraph(text,style=None):
    p=doc.add_paragraph(text,style=style);md.extend([text,'']);return p
def heading(text,level=1):
    doc.add_heading(text,level);md.extend(['#'*(level+1)+' '+text,''])
def page(): doc.add_page_break()
def table(headers,rows,widths=None):
    t=doc.add_table(rows=1,cols=len(headers));t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
    widths=widths or [6.3/len(headers)]*len(headers)
    for col,w in zip(t.columns,widths):col.width=Inches(w)
    for c,text in zip(t.rows[0].cells,headers):c.text=str(text)
    for row in rows:
        cells=t.add_row().cells
        for c,text in zip(cells,row):c.text=str(text)
    borders=OxmlElement('w:tblBorders')
    for edge in ['top','left','bottom','right','insideH','insideV']:
        e=OxmlElement('w:'+edge);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'4');e.set(qn('w:color'),'D9D9D9');borders.append(e)
    t._tbl.tblPr.append(borders)
    for ri,row in enumerate(t.rows):
        pr=row._tr.get_or_add_trPr();keep=OxmlElement('w:cantSplit');pr.append(keep)
        if ri==0:pr.append(OxmlElement('w:tblHeader'))
        for ci,c in enumerate(row.cells):
            c.width=Inches(widths[ci]);c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            cp=c._tc.get_or_add_tcPr();margins=OxmlElement('w:tcMar')
            for side in ['top','left','bottom','right']:
                s=OxmlElement('w:'+side);s.set(qn('w:w'),'80');s.set(qn('w:type'),'dxa');margins.append(s)
            cp.append(margins)
            if ri==0:
                shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'E7EDF3');cp.append(shade)
            for p in c.paragraphs:
                p.paragraph_format.space_after=Pt(2);p.paragraph_format.line_spacing=1.0
                for r in p.runs:r.font.size=Pt(10);r.bold=ri==0;r.font.color.rgb=RGBColor(0,0,0)
    md.extend(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |'])
    md.extend('| '+' | '.join(str(v).replace('|','/') for v in row)+' |' for row in rows);md.append('')
    doc.add_paragraph().paragraph_format.space_after=Pt(1)
    return t
def figure(path,caption,max_height=6.6):
    global figure_count
    figure_count+=1
    b=(ROOT/path).read_bytes();w,h=struct.unpack('>II',b[16:24])
    width=min(6.25,max_height*w/h)
    p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after=Pt(3)
    shape=p.add_run().add_picture(str(ROOT/path),width=Inches(width))
    shape._inline.docPr.set('descr',caption)
    p.paragraph_format.keep_with_next=True
    cap=doc.add_paragraph(f'Hình {figure_count}. {caption}',style='Caption');cap.alignment=WD_ALIGN_PARAGRAPH.CENTER
    md.extend([f'![{caption}](../{path})',f'Hình {figure_count}. {caption}',''])
def fmt(value):
    if value in ['',None]:return 'N/A'
    try:return f'{float(value):.4f}'
    except (ValueError,TypeError):return str(value)
def local_time(text):
    from datetime import timezone,timedelta
    return datetime.fromisoformat(text.replace('Z','+00:00')).astimezone(timezone(timedelta(hours=7))).strftime('%H:%M:%S %d/%m/%Y')

labels=['provided_snapshot','website_before','website_after_capture']
runs={k:read_json(f'outputs/notebook/{k}/run_manifest.json') for k in labels}
quality={k:read_json(f'outputs/notebook/{k}/data_quality.json') for k in labels}
metrics={k:read_csv(f'outputs/notebook/{k}/offline_metrics.csv') for k in labels}
recs=read_csv('outputs/notebook/website_before/recommendations.csv')
comparison=read_csv('outputs/notebook/website_before/website_comparison.csv')
captures=read_json('data/website/verified_baseline/capture_manifest.json')
import_manifest=read_json('data/import/import_manifest.json')
candidates=read_json('data/import/candidates.json')
config=runs['website_before']['config']

p=paragraph('BÁO CÁO THỰC HÀNH HỆ THỐNG RECSYS GỢI Ý VIỆC LÀM','Title');p.alignment=WD_ALIGN_PARAGRAPH.CENTER
paragraph('Nguyễn Hoàng Hà\nMã số sinh viên 102230343\nBáo cáo cá nhân\nNgày thực hiện 28 tháng 10 năm 2026').alignment=WD_ALIGN_PARAGRAPH.CENTER
heading('Kết quả thực hành',1)
paragraph('Thực nghiệm đã chạy đủ chín thuật toán trên dữ liệu MEDAJob và thu 11 ảnh gợi ý thực từ website. Bản xuất website xác định đúng tài khoản user458 nhưng chưa có hồ sơ kỹ năng và rating. Vì vậy, kết quả Python cho tài khoản này chủ yếu là dự phòng Popularity, chưa có căn cứ kết luận mức độ phù hợp với sở thích cá nhân.')
paragraph('Phần cập nhật hồ sơ, tạo rating và đăng ít nhất 10 tin chưa thực hiện. Danh sách 10 tin thật và CSV đã được chuẩn bị để xác nhận; không thay yêu cầu đăng thành công bằng số dòng trong CSV. Báo cáo phản ánh trạng thái thực tế này.')
heading('Nội dung',1)
for text in ['1 Giới thiệu','2 Chức năng Hồ sơ','3 Chức năng Nhà tuyển dụng','4 Chức năng Tìm việc','5 Chức năng Gợi ý việc làm','6 MEDAJob và đối sánh chín thuật toán','7 Tham khảo']:paragraph(text)
page()

heading('1 Giới thiệu')
paragraph('Website RECSYS tại http://wandertour.ddns.net:8020 hỗ trợ quản lý hồ sơ, danh mục tuyển dụng, tìm việc và gợi ý. Bài thực hành khảo sát các chức năng này, sau đó lập trình các biến thể CBF, CF hành vi, Hybrid, User-KNN, Item-KNN, Popularity, SGD, ALS Explicit và ALS Implicit để đối sánh kết quả.')
paragraph('Đơn vị phân tích là cặp user–job. Báo cáo tách kết quả trên snapshot đầy đủ dùng đối sánh website khỏi mô hình train/test dùng đánh giá ngoại tuyến. Các bộ dữ liệu được giữ riêng và định danh bằng SHA256; không trộn dữ liệu từ các lần xuất.')
table(['Bộ dữ liệu','User','Job','Rating','View','User test'],[[k,quality[k]['users'],quality[k]['jobs'],quality[k]['ratings'],quality[k]['views_raw'],runs[k]['test_users']] for k in labels],[2.3,.65,.7,.8,.7,1.1])
for k in labels:paragraph(f'{k}: snapshot {runs[k]["dataset_snapshot_id"]}.',style='Caption')
paragraph('Dữ liệu gốc không chứa username của sinh viên. Hai bản xuất website đều chứa user458. Snapshot sau đợt thu ảnh có thêm 21 job và 42 rating so với bản trước; các thay đổi này không phải là tin/rating do phiên thực hành này ghi lên website. Chưa có ảnh và backend gắn cùng một snapshot bất biến.')

page();heading('2 Chức năng Hồ sơ')
paragraph('Đăng nhập xác nhận Nguyễn Hoàng Hà, username sv102230343, user ID458, vai trò employer. Hồ sơ ứng viên chưa tồn tại, danh sách kỹ năng rỗng và chưa có rating. Không tự điền kỹ năng, kinh nghiệm, địa điểm hoặc mức lương khi chưa có thông tin thật.')
paragraph('Chuẩn hóa dự kiến chỉ áp dụng cách trình bày kỹ năng sau khi có nội dung xác nhận, ví dụ tách từ khóa bằng dấu phẩy nhưng giữ cụm nhiều từ. Bước đổi mật khẩu cần người dùng tự xác nhận; không lưu thông tin xác thực trong tài liệu.')
figure('evidence/website/01_profile_initial.png','Hồ sơ ban đầu trống; các trường cá nhân không cần thiết đã che khi chụp',6.5)

page();heading('3 Chức năng Nhà tuyển dụng')
paragraph('Lần kiểm tra ban đầu cho thấy tài khoản chưa đăng tin nào. Không có tin riêng để rà soát đóng hết hạn, và không chỉnh sửa tin thuộc tài khoản khác.')
figure('evidence/website/02_employer_initial_no_jobs.png','Danh sách tuyển dụng của tài khoản hiển thị 0 tin',2.7)
paragraph(f'Danh sách dự kiến gồm 10 tin được đối chiếu với {import_manifest["catalog_rows"]} tin trong snapshot sau thu ảnh. Kiểm tra ID/URL nguồn và tên công ty kết hợp độ gần tiêu đề không tìm thấy ứng viên trùng. Việc rà soát này có giới hạn theo thời điểm; cần làm mới ngay trước import.')
figure('evidence/website/05_duplicate_check_J01.png','Ví dụ tìm tiêu đề J01 và công ty Bosch trả 0 mục; kiểm tra toàn bộ danh sách dùng snapshot export',1.9)
paragraph('Template có 19 cột nhưng dòng minh họa lệch cột do mảng kỹ năng chưa được CSV quoting đúng. File preview dùng quoting toàn bộ trường, đọc lại xác nhận mỗi dòng đủ 19 cột và job_skills là JSON array hợp lệ. Lương, hạn nộp và HR contact chưa được nguồn công bố được để trống, không tự đặt giá trị.')
paragraph('Chưa import nên số tin đăng thành công hiện là 0 và chưa có ID mới. Tin J03 có loại hợp đồng Intern ở nguồn; phải xác minh backend chấp nhận giá trị này, không tự đổi thành full-time. Không bấm ứng tuyển hoặc gửi hồ sơ cho nhà tuyển dụng thật.')
page();heading('Danh sách 10 tin chờ xác nhận',2)
table(['Mã','Vị trí','Nguồn','Địa điểm'],[[c['ref'],c['title'],'Bosch' if 'Bosch' in c['company'] else 'KMS',c['location']] for c in candidates[:10]],[.5,3.6,.8,1.35])
paragraph('Link kiểm chứng từng tin được ghi ở mục 7 và data/import/candidates.json. Các nguồn hết hạn như Bosch Full Stack .NET và Junior DevOps đã loại. Các tin dùng URL canonical mới sau chuyển hướng để hạn chế đăng trùng phiên bản cũ.')

page();heading('4 Chức năng Tìm việc')
search=read_json('data/website/verified_baseline/search_python.json')
paragraph(f'Thực hiện tìm kiếm từ khóa python, không lọc công ty, địa điểm hoặc loại hình. Website trả {search["total"]} việc và trang đầu có tối đa 15 mục. Ảnh được chụp sau khi trạng thái tìm kiếm kết thúc, lúc {local_time(search["captured_at"])}. Đây là thao tác kiểm tra chức năng, chưa phải danh sách phù hợp cá nhân.')
figure('evidence/website/04_search_python_verified.png','Kết quả tìm kiếm Python đã tải xong',7.0)
page();heading('Lịch sử rating',2)
paragraph('Tài khoản chưa có rating. Việc tự đánh giá thay khi chưa biết mong muốn sẽ làm sai hồ sơ hành vi, vì vậy chưa tạo rating. Sau khi có kỹ năng, nghề và địa điểm thật, cần chọn các job đang mở và trình bảng job ID–rating–lý do trước khi ghi.')
figure('evidence/website/03_rating_history_initial.png','Lịch sử đánh giá của user458 có 0 mục',2.2)

heading('5 Chức năng Gợi ý việc làm')
paragraph('Đã chọn từng thuật toán với Cosine, địa điểm ưu tiên trống. CBF được thử thêm Jaccard và Pearson. Mỗi capture lưu HTTP status, thuật toán yêu cầu/trả về, nhãn trên giao diện, thời điểm, số kết quả và ID. Bản chụp thử gặp HTTP429 và stale UI không sử dụng trong báo cáo.')
table(['Thuật toán','Độ đo','Kết quả','Ứng viên','Giờ Việt Nam'],[[c['algorithm'],c['similarity'],c['n_items'],c['candidate_count'],local_time(c['captured_at']).split(' ')[0]] for c in captures],[1.55,1.0,.8,.95,1.95])
paragraph('CBF, Hybrid và Popularity trả 10 mục; sáu phương pháp còn lại trả danh sách rỗng thành công với thông báo chưa đủ dữ liệu gợi ý. Không xem danh sách rỗng này là lỗi HTTP, và không suy ra backend sai. Một số ảnh baseline còn đang tải sao rating; chúng chứng minh danh sách xếp hạng, không chứng minh thao tác rating.')

page();heading('6 MEDAJob và đối sánh chín thuật toán')
heading('6 1 Tiền xử lý và cấu hình',2)
paragraph('Adapter nối users.id với user_profiles.user_id, giữ ID dạng chuỗi và toàn bộ catalog. Kỹ năng đọc được ở JSON array hoặc chuỗi phân cách, chuẩn hóa NFC/chữ thường, giữ nguyên cụm nhiều từ. Kiểm tra ID trùng, khóa ngoại, rating ngoài thang1–5 và thời lượng xem không hữu hạn; không tự bỏ bản ghi lỗi.')
paragraph('Rating explicit và view được tách. Rating từ4 trở lên tạo tín hiệu hành vi rating/5; view dương chỉ cho cặp chưa rating tạo trọng số0.25. Rating thấp chặn view cùng cặp. Job mở và chưa được user rating là tập ứng viên chung. Điểm bằng nhau được sắp ID tăng dần. Không clip dự đoán để tránh mất thứ hạng.')
table(['Tham số','Giá trị'],[[k,str(v)] for k,v in config.items() if k not in ['active_only','exclude_rated']],[3.65,2.6])
paragraph('Điểm model-supported được xếp trước dự phòng Popularity; mỗi dòng ghi score_type, status và fallback. Đây là chính sách Python công khai, chưa biết website có sử dụng cùng chính sách hay không. Không dùng điểm của thuật toán khác nhau để so trực tiếp độ phù hợp.')

method_text=[
 ('cbf','CBF theo kỹ năng','Dùng cosine giữa vector kỹ năng nhị phân user và job. Jaccard dùng tỷ lệ giao/hợp; Pearson dùng vector đã trừ trung bình. Không có kỹ năng user thì trả prior Popularity có nhãn.','Website vẫn trả điểm CBF khác 0 dù profile API rỗng. Chưa biết đặc trưng hoặc mặc định nội bộ backend, nên không gán chênh lệch này thành lỗi. Python chỉ dùng kỹ năng theo định nghĩa đã công bố.'),
 ('cf','CF theo hành vi','Tính cosine item–item trên tín hiệu hành vi tích cực, bỏ đường chéo; tổng có trọng số theo hành vi user được chia cho tổng tín hiệu tối thiểu1. Không có hỗ trợ đồng xuất hiện thì dùng prior.','Tài khoản chưa có hành vi huấn luyện. Website không có gợi ý, Python trả dự phòng. Đây là khác biệt chính sách cold-start, không phải bằng chứng CF được tái tạo sai.'),
 ('hybrid','Hybrid kết hợp','Trộn 0.55 lần CBF min-max và0.45 lần CF min-max theo user. Không trộn prior rating vào affinity; thiếu nhánh thì dùng nhánh còn lại với nhãn, thiếu cả hai dùng Popularity.','User458 thiếu cả hai nhánh trong Python. Website trả10 mục khác, nhưng trọng số và đặc trưng backend chưa được chứng minh giống Python.'),
 ('user_knn','User KNN','Chọn tối đa5 láng giềng cosine trên vector rating. Dự đoán là trung bình rating có trọng số, mẫu số chỉ gồm láng giềng đã rating job đang xét. User không có láng giềng dùng prior.','Không có vector rating của user458 để tìm láng giềng có ý nghĩa. Kết quả fallback không thể diễn giải là cộng đồng có sở thích giống sinh viên.'),
 ('item_knn','Item KNN','Chọn tối đa5 job gần nhất theo cosine cột rating. Weighted mean chỉ dùng rating đã quan sát của user trên các job láng giềng; không coi missing là rating0.','User458 chưa có item đã rating để lan truyền sở thích. Tỷ lệ fallback trong holdout cần đọc cùng chỉ số xếp hạng, vì một phần độ chính xác đến từ prior.'),
 ('popularity','Popularity','Điểm là trung bình Bayes: tổng rating cộng5 lần global mean, chia cho số rating cộng5. Đây là baseline theo rating, không phải đếm lượt xem.','Website trả điểm0.1 và ưu tiên các ID mới trong lần chụp; Python dùng trung bình Bayes. Không có căn cứ giả định hai nhãn Popularity có cùng định nghĩa.'),
 ('sgd','Model based CF SGD','Dự đoán gồm global mean, bias user, bias item và tích vô hướng hai vector nhân tố. Học45 epoch với12 nhân tố, learning rate0.012, regularization0.04 trên rating quan sát.','Không xếp hạng bằng vector ngẫu nhiên của user/job chưa học. User458 không có rating nên tất cả kết quả là prior có nhãn. Sai số train không phải sai số test.'),
 ('als_explicit','ALS Explicit','Trừ global mean khỏi rating rồi luân phiên giải ridge cho user và item trên các ô quan sát. Dùng12 nhân tố,12 vòng, regularization0.4; cộng lại mean khi dự đoán.','Không đưa ô thiếu vào loss explicit. User chưa có rating dùng prior. RMSE/MAE chỉ đọc trên holdout positive, không so với affinity implicit.'),
 ('als_implicit','ALS Implicit','Preference bằng1 khi B dương; confidence bằng1+16B. Luân phiên giải weighted least squares trên preference,12 nhân tố,10 vòng, regularization0.7.','Mô hình phân biệt preference với confidence theo Hu và cộng sự [2]. Rating thấp không tạo thích. Điểm là affinity nên không báo RMSE như rating; user458 chưa có tín hiệu dương dùng prior.')
]
for index,(key,title,method,note) in enumerate(method_text,2):
    page();heading(f'6 {index} {title}',2)
    paragraph(method)
    subset=[r for r in recs if r['algorithm']==key]
    cap=next(c for c in captures if c['algorithm']==key and c['similarity']=='cosine')
    paragraph(f'Python trả {len(subset)} mục cho user458 trong snapshot {runs["website_before"]["dataset_snapshot_id"]}. Bảng sau trích5 vị trí đầu; đầy đủ10 vị trí có trong recommendations.csv và notebook.')
    table(['Hạng','Job ID','Điểm','Loại kết quả'],[[r['rank'],r['job_id'],fmt(r['score']),'prior fallback' if r['status']=='fallback' else 'Bayes baseline'] for r in subset[:5]],[.65,1.0,1.1,3.5])
    m=[r for r in metrics['website_before'] if r['algorithm']==key]
    table(['K','n test','HR/Recall','NDCG','Coverage','Fallback'],[[r['k'],r['test_users'],fmt(r['hit_rate']),fmt(r['ndcg']),fmt(r['catalog_coverage']),fmt(r['fallback_fraction'])] for r in m],[.45,.7,1.25,1.1,1.25,1.5])
    r=m[-1]
    if r['rmse_positive_holdout']:paragraph(f'Rating positive-holdout: RMSE={fmt(r["rmse_positive_holdout"])}, MAE={fmt(r["mae_positive_holdout"])}; tỷ lệ dự đoán test dùng fallback={fmt(r["rating_prediction_fallback_fraction"])}.')
    paragraph(f'Website: {cap["n_items"]} mục, HTTP200, thời điểm {local_time(cap["captured_at"])}. {note}')
    if cap['n_items']:
        page();heading(f'Minh chứng website {title}',3)
        figure(cap['screenshot'],f'{title} với Cosine; ảnh thực của tài khoản sinh viên',7.3)
    else:figure(cap['screenshot'],f'{title} hiển thị chưa đủ dữ liệu gợi ý',2.1)

page();heading('6 11 Thiết kế đánh giá và tổng hợp',2)
paragraph('Không có thời gian rating đáng tin cậy, nên dùng positive leave-one-out ngẫu nhiên với seed42. User có ít nhất3 rating và có một job mở rating≥4 còn hỗ trợ train được đưa vào test. Loại toàn bộ rating và view của chính cặp test khỏi train; học lại các ma trận, độ tương tự và prior trên train.')
paragraph('HitRate là tỷ lệ user có hit trong Top-K; Recall là số relevant được tìm/số relevant test. Mỗi user có một item test nên HR=Recall. NDCG giảm trọng số theo log2 của hạng. Coverage tính trên catalog mở; fallback_fraction tính trên các dòng gợi ý trả về. RMSE/MAE chỉ tính cho dự đoán rating và chỉ đại diện holdout tích cực.')
paragraph('Dữ liệu test nhỏ và không đại diện toàn bộ466 user. Chưa có repeated split, khoảng tin cậy hoặc đánh giá online. Không dùng kết quả này để khẳng định thuật toán tốt nhất cho mọi hồ sơ.')
for label in ['provided_snapshot','website_before','website_after_capture']:
    heading('Kết quả K10 '+label.replace('_',' '),3)
    table(['Thuật toán','n','HR/Recall','NDCG','Coverage','Fallback'],[[r['algorithm'],r['test_users'],fmt(r['hit_rate']),fmt(r['ndcg']),fmt(r['catalog_coverage']),fmt(r['fallback_fraction'])] for r in metrics[label] if r['k']=='10'],[1.45,.4,1.15,1.05,1.1,1.1])
    if label!='website_after_capture':page()
page();heading('Biểu đồ đánh giá ngoại tuyến',3)
figure('outputs/notebook/website_before/figures/offline_metrics.png','Metrics K10 và tỷ lệ dự phòng trên 11 user test của snapshot website trước thu ảnh',3.5)
figure('outputs/notebook/provided_snapshot/figures/training_loss.png','MSE trên tập train của SGD và ALS Explicit; không phải độ chính xác kiểm thử',3.2)

page();heading('6 12 Đối sánh theo job ID',2)
paragraph('So sánh chỉ dùng ID, không đồng nhất title hoặc score giữa hai hệ thống. Giao nhau là số ID chung; Jaccard là giao/hợp. Overlap@10 chỉ tính khi cả hai bên đủ10. Chênh lệch hạng chỉ tính trên ID chung. HTTP lỗi/thiếu capture không được thay bằng danh sách rỗng. Với danh sách rỗng thành công, Jaccard=0 là tính chất tập hợp, không phải điểm đánh giá chất lượng backend.')
table(['Thuật toán','Web','Python','Giao','Jaccard','Overlap10'],[[r['algorithm'],r['n_web'],r['n_python'],r['intersection'],fmt(r['jaccard']),fmt(r['overlap_at_k'])] for r in comparison],[1.65,.6,.7,.6,1.2,1.5])
paragraph('Không có ID chung trong Top10 của đối sánh baseline này nên chênh lệch hạng trên giao là N/A. Các tập ứng viên không được chứng minh giống nhau: website báo1157 ứng viên trong các ảnh đầu, trong khi CSV trước thu ảnh có1146 job mở. Diagnostics chỉ chứa50 dòng mẫu, không đủ tái tạo tập ứng viên. Chênh lệch không chứng minh backend sai.')
paragraph('CBF Cosine và Jaccard cho cùng danh sách website trong lần chụp đầu; Pearson được thu sau khi khôi phục phiên và dữ liệu đã thay đổi. Python của user không có skill nên cả ba độ đo đều rơi về cùng prior. Pearson có thể âm và không phải xác suất; website hiển thị phần trăm âm không nên hiểu là xác suất phù hợp âm.')
for sim in ['jaccard','pearson']:
    page();heading('Minh chứng CBF '+sim.capitalize(),3)
    cap=next(c for c in captures if c['algorithm']=='cbf' and c['similarity']==sim)
    paragraph('Thời điểm '+local_time(cap['captured_at'])+'; giữ trường hợp hồ sơ trống, không suy ra thay đổi sở thích.')
    figure(cap['screenshot'],'CBF '+sim.capitalize()+' với tài khoản chưa có hồ sơ kỹ năng',7.0)

page();heading('6 13 Kiểm thử và phần còn thiếu',2)
paragraph('Bộ kiểm thử kiểm tra parsing kỹ năng, CSV Unicode/dấu phẩy, ID, khóa ngoại, thang rating, thời lượng xem, cold-start, hết ứng viên, đồng điểm, tái lập, mask, tách holdout/view và phân biệt capture lỗi với danh sách rỗng thành công. Notebook đã thực thi14 cell mã từ kernel mới, không có cell lỗi.')
paragraph('Đã sao lưu notebook trước chỉnh sửa và giữ nguyên dữ liệu gốc. Source dùng chung giữa tests, CLI và notebook để tránh ba bản cài đặt lệch nhau. Các file CSV/ảnh được gắn hash trong manifest để kiểm tra tính toàn vẹn.')
table(['Việc còn thiếu','Điều kiện hoàn tất'],[
 ['Hồ sơ và rating','Thông tin kỹ năng, nghề, địa điểm thật; duyệt bảng nội dung trước ghi'],
 ['Ít nhất10 tin đã đăng','Duyệt J01–J10; kiểm tra lại nguồn/trùng; import và xác minh ID thực tế'],
 ['Snapshot hậu cập nhật','Chỉ thu sau khi các thay đổi được duyệt và thành công'],
 ['Đổi mật khẩu','Người dùng tự thực hiện xác nhận cuối'],
 ['Kiểm tra bố cục Word','Render bằng môi trường hỗ trợ và kiểm tra từng trang; hiện chưa VERIFIED']],[2.0,4.25])

page();heading('7 Tham khảo')
paragraph('[1] Đề thực hành LabDSS WebsiteRECSYS do giảng viên cung cấp; website http://wandertour.ddns.net:8020, truy cập28/10/2026. File đề được giữ nguyên và không đưa vào gói chia sẻ vì chứa ví dụ thông tin đăng nhập.')
paragraph('[2] Hu, Y.; Koren, Y.; Volinsky, C. (2008). Collaborative Filtering for Implicit Feedback Datasets. https://yifanhu.net/PUB/cf.pdf. Tham khảo phân biệt preference/confidence; quy tắc chuyển rating/view của thực nghiệm được công bố riêng ở mục6.')
paragraph('[3] Koren, Y.; Bell, R.; Volinsky, C. (2009). Matrix Factorization Techniques for Recommender Systems. Computer42(8),30–37. https://doi.org/10.1109/MC.2009.263. Tham khảo họ mô hình nhân tố; không khẳng định khớp backend website.')
paragraph('Nguồn tuyển dụng được diễn giải ngắn, không sao chép toàn bộ mô tả. Ngày xác minh28/10/2026; trạng thái có thể thay đổi. Từng tin phải được mở lại ngay trước import.')
for c in candidates[:10]:paragraph(f"[{c['ref']}] {c['company']}. {c['title']}. {c['url']}")
paragraph('Căn cứ tái lập: source job_recsys, configs/experiment.json, outputs/notebook và data/website/verified_baseline trong gói bàn giao. Những file này lưu cấu hình và kết quả cụ thể đã dùng trong báo cáo.')

name='Bao_cao_LabDSS_102230343_DRAFT_NOT_VERIFIED'
doc.save(OUT/(name+'.docx'))
# The reference is an assignment, not a source of personal metadata or obsolete page counts.
from zipfile import ZipFile, ZIP_DEFLATED
from xml.etree import ElementTree as ET
output_path=OUT/(name+'.docx')
with ZipFile(output_path) as archive:parts={n:archive.read(n) for n in archive.namelist()}
app=ET.fromstring(parts['docProps/app.xml'])
for node in app:
    if node.tag.rsplit('}',1)[-1] in {'Company','Manager','HyperlinkBase'}:
        node.text=''
    if node.tag.rsplit('}',1)[-1]=='DocSecurity':node.text='0'
for node in list(app):
    if node.tag.rsplit('}',1)[-1] in {'HLinks','HeadingPairs','TitlesOfParts','TotalTime','Pages','Words','Characters','Lines','Paragraphs','CharactersWithSpaces'}:app.remove(node)
parts['docProps/app.xml']=ET.tostring(app,encoding='utf-8',xml_declaration=True)
remove={n for n in parts if n.startswith('customXml/') or n in {'docProps/custom.xml','word/media/image1.jpg','word/footnotes.xml','word/endnotes.xml','word/_rels/header1.xml.rels'}}
import posixpath
for n,b in list(parts.items()):
    if not n.endswith('.rels') or n in remove:continue
    relationships=ET.fromstring(b)
    base='' if n=='_rels/.rels' else posixpath.dirname(n).replace('/_rels','')
    for rel in list(relationships):
        target=posixpath.normpath(posixpath.join(base,rel.get('Target','')))
        if target in remove or rel.get('Type','').endswith('/hyperlink'):
            relationships.remove(rel)
    parts[n]=ET.tostring(relationships,encoding='utf-8',xml_declaration=True)
types=ET.fromstring(parts['[Content_Types].xml'])
for node in list(types):
    if node.get('PartName','').lstrip('/') in remove:types.remove(node)
parts['[Content_Types].xml']=ET.tostring(types,encoding='utf-8',xml_declaration=True)
for n in remove:parts.pop(n,None)
with ZipFile(output_path,'w',ZIP_DEFLATED) as archive:
    for n,b in parts.items():archive.writestr(n,b)
(OUT/(name+'.md')).write_text('\n'.join(md),encoding='utf-8')
assert hashlib.sha256(REFERENCE.read_bytes()).hexdigest()==reference_hash
qa=ROOT/'qa';qa.mkdir(exist_ok=True)
(qa/'report_structure.json').write_text(json.dumps({'status':'STRUCTURAL_ONLY_NOT_VISUALLY_VERIFIED',
    'reference_sha256':reference_hash,'paragraphs':len(doc.paragraphs),'tables':len(doc.tables),
    'figures':figure_count,'output':str((OUT/(name+'.docx')).relative_to(ROOT)),
    'sections':len(doc.sections),'page_count':None,'render_status':'NOT_VERIFIED_MISSING_BUNDLED_LIBREOFFICE'},indent=2),encoding='utf-8')
print(f'Created {name}.docx; {figure_count} figures; render verification required')

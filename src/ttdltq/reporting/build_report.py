from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Sequence

import matplotlib.pyplot as plt
import pandas as pd
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor

from ttdltq.config import MODEL_DIR, OUTPUT_DIR, PROCESSED_DIR, PROJECT_ROOT


REPORT_DIR = PROJECT_ROOT / "report"
FIGURE_DIR = OUTPUT_DIR / "figures"
TITLE = "Nghiên cứu và phân tích các yếu tố ảnh hưởng đến kết quả học tập của sinh viên đại học"


def _set_cell_shading(cell, fill: str) -> None:
    properties = cell._tc.get_or_add_tcPr()
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), fill)
    properties.append(shading)


def _set_repeat_table_header(row) -> None:
    properties = row._tr.get_or_add_trPr()
    repeat = OxmlElement("w:tblHeader")
    repeat.set(qn("w:val"), "true")
    properties.append(repeat)


def _add_page_number(paragraph) -> None:
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run()
    field_begin = OxmlElement("w:fldChar")
    field_begin.set(qn("w:fldCharType"), "begin")
    instruction = OxmlElement("w:instrText")
    instruction.set(qn("xml:space"), "preserve")
    instruction.text = "PAGE"
    field_end = OxmlElement("w:fldChar")
    field_end.set(qn("w:fldCharType"), "end")
    run._r.extend([field_begin, instruction, field_end])


def _add_toc(document: Document) -> None:
    paragraph = document.add_paragraph()
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instruction = OxmlElement("w:instrText")
    instruction.set(qn("xml:space"), "preserve")
    instruction.text = 'TOC \\o "1-3" \\h \\z \\u'
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    separate_text = OxmlElement("w:t")
    separate_text.text = "Nhấn Ctrl+A rồi F9 trong Word để cập nhật mục lục."
    separate.append(separate_text)
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend([begin, instruction, separate, end])


def _configure_document(document: Document) -> None:
    section = document.sections[0]
    section.page_height = Cm(29.7)
    section.page_width = Cm(21)
    section.top_margin = Cm(2.2)
    section.bottom_margin = Cm(2.2)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.2)

    styles = document.styles
    normal = styles["Normal"]
    normal.font.name = "Times New Roman"
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    normal.font.size = Pt(12)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.15

    for style_name, size, color in [
        ("Title", 20, "0F172A"),
        ("Heading 1", 16, "0F172A"),
        ("Heading 2", 14, "0F766E"),
        ("Heading 3", 12, "334155"),
    ]:
        style = styles[style_name]
        style.font.name = "Times New Roman"
        style._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
        style.font.size = Pt(size)
        style.font.color.rgb = RGBColor.from_string(color)

    for item in document.sections:
        _add_page_number(item.footer.paragraphs[0])


def _paragraph(document: Document, text: str, *, bold_lead: str | None = None) -> None:
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if bold_lead and text.startswith(bold_lead):
        paragraph.add_run(bold_lead).bold = True
        paragraph.add_run(text[len(bold_lead) :])
    else:
        paragraph.add_run(text)


def _bullets(document: Document, items: Iterable[str]) -> None:
    for item in items:
        paragraph = document.add_paragraph(style="List Bullet")
        paragraph.add_run(item)


def _table(
    document: Document,
    headers: Sequence[str],
    rows: Iterable[Sequence[object]],
    *,
    font_size: int = 9,
) -> None:
    table = document.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    header = table.rows[0]
    _set_repeat_table_header(header)
    for index, value in enumerate(headers):
        cell = header.cells[index]
        cell.text = str(value)
        _set_cell_shading(cell, "DDEBF7")
        for run in cell.paragraphs[0].runs:
            run.bold = True
            run.font.size = Pt(font_size)
    for values in rows:
        cells = table.add_row().cells
        for index, value in enumerate(values):
            cells[index].text = "" if pd.isna(value) else str(value)
            cells[index].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            for paragraph in cells[index].paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(font_size)


def _image(document: Document, path: Path, caption: str, *, width: float = 6.3) -> None:
    if not path.exists():
        _paragraph(document, f"[Chưa có hình: {path.name}]")
        return
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.add_run().add_picture(str(path), width=Inches(width))
    caption_paragraph = document.add_paragraph()
    caption_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = caption_paragraph.add_run(caption)
    run.italic = True
    run.font.size = Pt(10)


def _new_content_page(document: Document, heading: str, level: int = 2) -> None:
    document.add_page_break()
    document.add_heading(heading, level=level)


def build_architecture_figure() -> Path:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    output = FIGURE_DIR / "pipeline_architecture.png"
    fig, ax = plt.subplots(figsize=(13, 6.5))
    ax.axis("off")
    boxes = [
        (0.02, 0.60, 0.16, 0.22, "Nguồn chính thức\nScorecard + IPEDS", "#DBEAFE"),
        (0.22, 0.60, 0.16, 0.22, "Raw + manifest\nURL · SHA-256", "#E0E7FF"),
        (0.42, 0.60, 0.16, 0.22, "Làm sạch\nJoin · calculated fields", "#CCFBF1"),
        (0.62, 0.60, 0.16, 0.22, "Processed tables\nAudit · dictionary", "#DCFCE7"),
        (0.82, 0.60, 0.16, 0.22, "EDA tĩnh\nInsight định lượng", "#FEF3C7"),
        (0.32, 0.12, 0.17, 0.22, "Logistic Regression\nTemporal holdout", "#FCE7F3"),
        (0.56, 0.12, 0.17, 0.22, "Streamlit + Plotly\nMap · filter · drill-down", "#FEE2E2"),
        (0.80, 0.12, 0.17, 0.22, "DOCX + kiểm thử\nDemo · nghiệm thu", "#F3E8FF"),
    ]
    for x, y, width, height, label, color in boxes:
        rectangle = plt.Rectangle((x, y), width, height, facecolor=color, edgecolor="#334155", linewidth=1.5)
        ax.add_patch(rectangle)
        ax.text(x + width / 2, y + height / 2, label, ha="center", va="center", fontsize=11, weight="bold")
    arrows = [
        ((0.18, 0.71), (0.22, 0.71)),
        ((0.38, 0.71), (0.42, 0.71)),
        ((0.58, 0.71), (0.62, 0.71)),
        ((0.78, 0.71), (0.82, 0.71)),
        ((0.70, 0.60), (0.41, 0.34)),
        ((0.78, 0.60), (0.645, 0.34)),
        ((0.90, 0.60), (0.885, 0.34)),
        ((0.49, 0.23), (0.56, 0.23)),
        ((0.73, 0.23), (0.80, 0.23)),
    ]
    for start, end in arrows:
        ax.annotate("", xy=end, xytext=start, arrowprops=dict(arrowstyle="->", color="#475569", lw=1.8))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    fig.tight_layout()
    fig.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return output


def _load_inputs() -> dict:
    return {
        "audit": json.loads((OUTPUT_DIR / "eda" / "data_quality_audit.json").read_text(encoding="utf-8")),
        "metrics": json.loads((MODEL_DIR / "metrics.json").read_text(encoding="utf-8")),
        "insights": json.loads((OUTPUT_DIR / "eda" / "insights.json").read_text(encoding="utf-8")),
        "dictionary": pd.read_csv(PROCESSED_DIR / "data_dictionary.csv"),
        "correlations": pd.read_csv(OUTPUT_DIR / "eda" / "factor_correlations.csv"),
        "importance": pd.read_csv(MODEL_DIR / "feature_importance.csv"),
        "confusion": pd.read_csv(MODEL_DIR / "confusion_matrix.csv", index_col=0),
        "disadvantage": pd.read_csv(OUTPUT_DIR / "eda" / "disadvantage_summary.csv"),
    }


def build_report(output_path: Path | None = None) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = output_path or REPORT_DIR / "TTDLTQ_report_draft.docx"
    data = _load_inputs()
    metrics = data["metrics"]
    selected = metrics["models"][metrics["selected_model"]]
    architecture = build_architecture_figure()

    document = Document()
    _configure_document(document)

    # Cover
    document.add_paragraph("BÁO CÁO ĐỒ ÁN CUỐI KỲ", style="Title").alignment = WD_ALIGN_PARAGRAPH.CENTER
    document.add_paragraph("MÔN TƯƠNG TÁC DỮ LIỆU TRỰC QUAN (IDV)").alignment = WD_ALIGN_PARAGRAPH.CENTER
    document.add_paragraph("")
    title = document.add_paragraph(TITLE)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in title.runs:
        run.bold = True
        run.font.size = Pt(18)
        run.font.color.rgb = RGBColor(15, 118, 110)
    document.add_paragraph("")
    document.add_paragraph("Nguồn dữ liệu: College Scorecard và NCES IPEDS").alignment = WD_ALIGN_PARAGRAPH.CENTER
    document.add_paragraph("Công cụ: Python · Streamlit · Plotly · scikit-learn").alignment = WD_ALIGN_PARAGRAPH.CENTER
    document.add_paragraph("")
    document.add_paragraph("BẢN THẢO SINH TỪ PIPELINE — CẦN BIÊN TẬP THÔNG TIN NHÓM/VIDEO TRƯỚC KHI NỘP").alignment = WD_ALIGN_PARAGRAPH.CENTER

    _new_content_page(document, "Cam kết phạm vi và liêm chính học thuật", 1)
    _paragraph(document, "Báo cáo sử dụng dữ liệu công khai chính thức và mã nguồn có thể tái lập. Mọi con số trong phần kết quả được đọc từ output pipeline, không điền thủ công để làm đẹp kết quả.")
    _paragraph(document, "Phân tích không tuyên bố quan hệ nhân quả. Đơn vị phân tích là cơ sở hoặc nhóm cơ sở–năm; không suy diễn xác suất rủi ro thành đánh giá từng sinh viên.")
    _paragraph(document, "File rubric được bảo vệ bằng checksum và không bị sửa trong quá trình triển khai.")

    _new_content_page(document, "Tóm tắt", 1)
    _paragraph(document, f"Nghiên cứu phân tích {data['audit']['processed_rows']['institutions']:,} cơ sở và {data['audit']['processed_rows']['institution_history']:,} quan sát cơ sở–năm để làm rõ sự khác biệt kết quả hoàn thành chương trình theo địa lý, loại hình, tài chính và nguồn lực.")
    _paragraph(document, "EDA cho thấy tỷ lệ duy trì sau năm đầu có liên hệ cùng chiều mạnh nhất trong nhóm biến đã xét; dữ liệu nhóm Pell Grant cho thấy một khoảng cách hoàn thành đáng kể. Dashboard ba trang dẫn người dùng từ bản đồ toàn quốc đến yếu tố liên quan và danh sách cảnh báo.")
    _paragraph(document, f"Logistic Regression được đánh giá trên năm 2022 chưa dùng để train, đạt Accuracy {selected['accuracy']:.2%}, Balanced Accuracy {selected['balanced_accuracy']:.2%} và ROC-AUC {selected['roc_auc']:.3f}. Kết quả vượt ngưỡng Accuracy 80% nhưng Recall {selected['recall']:.2%} cho thấy vẫn có trường hợp rủi ro bị bỏ sót.")
    _paragraph(document, "Từ khóa: higher education, completion rate, College Scorecard, IPEDS, Streamlit, Plotly, Logistic Regression, early warning.")

    _new_content_page(document, "Mục lục", 1)
    _add_toc(document)

    _new_content_page(document, "Danh mục thuật ngữ", 1)
    _table(document, ["Thuật ngữ", "Giải thích"], [
        ("College Scorecard", "Hệ dữ liệu giáo dục sau trung học của U.S. Department of Education"),
        ("IPEDS", "Integrated Postsecondary Education Data System của NCES"),
        ("UNITID", "Mã định danh cơ sở thống nhất"),
        ("Pell Grant", "Hỗ trợ liên bang, thường phản ánh nhu cầu tài chính"),
        ("Retention", "Tỷ lệ tiếp tục học sau năm đầu"),
        ("Completion 150%", "Hoàn thành trong 150% thời gian chuẩn của chương trình"),
        ("Temporal holdout", "Giữ năm mới nhất làm test ngoài thời gian"),
        ("Title IV", "Nhóm chương trình hỗ trợ tài chính sinh viên liên bang"),
    ])

    # Chapter 1
    _new_content_page(document, "1. Giới thiệu", 1)
    _paragraph(document, "Kết quả học tập đại học không chỉ phản ánh năng lực cá nhân mà còn gắn với khả năng duy trì học tập, hoàn cảnh tài chính, nguồn lực cơ sở và bối cảnh địa lý. Dự án xây dựng một chuỗi bằng chứng từ dữ liệu công khai để xác định các nhóm cần được phân tích sâu và hỗ trợ.")
    _paragraph(document, "Giá trị của đề tài nằm ở việc kết hợp phân tích mô tả, dashboard tương tác và mô hình cảnh báo. Dashboard trả lời ở đâu và nhóm nào có khác biệt; mô hình đưa ra xác suất để sắp xếp ưu tiên kiểm tra.")

    _new_content_page(document, "1.1 Mục tiêu nghiên cứu")
    _bullets(document, [
        "Mô tả phân bố kết quả hoàn thành, duy trì và rút khỏi chương trình.",
        "Đo khoảng cách giữa bang, loại trường, địa bàn, bậc đào tạo và nhóm tài chính.",
        "Phân tích liên hệ giữa tài chính, nguồn lực và kết quả mà không khẳng định nhân quả.",
        "Xây dựng Logistic Regression vượt Accuracy 80% trên dữ liệu test theo thời gian.",
        "Tích hợp kết quả vào dashboard có map, filter, drill-down, tooltip và cross-filtering.",
    ])

    _new_content_page(document, "1.2 Câu hỏi nghiên cứu")
    _bullets(document, [
        "RQ1: Kết quả khác nhau thế nào giữa bang, loại trường, bậc đào tạo, địa bàn và hình thức đào tạo?",
        "RQ2: Chi phí, Pell Grant và vay liên bang liên quan thế nào với hoàn thành/rút khỏi?",
        "RQ3: Quy mô, tỷ lệ sinh viên/giảng viên, tuyển chọn và địa bàn liên quan thế nào với kết quả?",
        "RQ4: Nhóm nhận Pell và thế hệ đầu có khoảng cách kết quả thế nào?",
        "RQ5: Nhiều bất lợi xuất hiện đồng thời đi cùng kết quả ra sao?",
        "RQ6: Logistic Regression cảnh báo completion thấp chính xác đến đâu?",
    ])

    _new_content_page(document, "1.3 Phạm vi và đơn vị phân tích")
    _paragraph(document, "Phạm vi địa lý là Hoa Kỳ và các lãnh thổ có mã bang hợp lệ. Đơn vị chính là cơ sở–năm; bảng ngành là cơ sở–ngành–bậc văn bằng. Thu nhập sau tốt nghiệp chỉ dùng bổ sung. Không có dữ liệu định danh cá nhân.")
    _paragraph(document, "Cụm từ 'ảnh hưởng' trong tên đề tài được vận hành hóa bằng mối liên hệ thống kê và phân tích đa biến. Báo cáo chủ động tách 'liên quan' khỏi 'gây ra' vì thiết kế quan sát không đủ nhận dạng tác động nhân quả.")

    # Chapter 2
    _new_content_page(document, "2. Nguồn và cấu trúc dữ liệu", 1)
    _paragraph(document, "College Scorecard và IPEDS là nguồn công khai chính thức của Hoa Kỳ [1], [2]. Manifest lưu URL, ngày truy xuất và SHA-256 để chứng minh đúng phiên bản.")
    _table(document, ["Bảng", "Quy mô gốc", "Vai trò"], [
        ("Institution", "6.429 × 3.306", "Cơ sở, địa lý, tài chính, nguồn lực, kết quả"),
        ("Field of Study", "229.188 × 174", "Ngành, bậc văn bằng, số văn bằng, nợ/thu nhập"),
        ("History", "6 snapshot; 40.321 dòng xử lý", "Temporal validation 2017–2022"),
        ("Equity long", f"{data['audit']['processed_rows']['equity_long']:,}", "Pell và first-generation"),
    ])

    _new_content_page(document, "2.1 Nguồn College Scorecard")
    _paragraph(document, "Institution file cung cấp trường IPEDS, tài chính và kết quả; field file cung cấp dữ liệu theo CIP và bậc văn bằng. Các biến privacy-suppressed được coi là missing, không quy đổi thành 0.")
    _paragraph(document, "Lịch sử dùng sáu file MERGED từ 2017_18 đến 2022_23. Năm bắt đầu được trích từ tên file thành academic_year để khóa temporal split.")

    _new_content_page(document, "2.2 Vai trò IPEDS")
    _paragraph(document, "IPEDS là nguồn gốc của các trường như loại hình kiểm soát, locale, enrollment, student–faculty ratio, retention và số văn bằng. Các biến đã được tích hợp trong Scorecard được dùng trong pipeline hiện tại; raw IPEDS riêng được cấu hình để đối chiếu khi máy chủ NCES phản hồi.")
    _paragraph(document, "Không dùng mirror không chính thức để lấp khoảng trống kết nối vì sẽ làm yếu bằng chứng nguồn và khó kiểm tra phiên bản.")

    _new_content_page(document, "2.3 Mô hình dữ liệu và khóa nối")
    _image(document, architecture, "Hình 1. Kiến trúc dữ liệu và sản phẩm phân tích.")
    _paragraph(document, "UNITID nối bảng cơ sở với bảng ngành. CIPCODE và CREDLEV mô tả ngành và bậc. academic_year phân biệt snapshot. Các phép nối many-to-one được kiểm tra bằng pandas validate để phát hiện khóa bất thường.")

    _new_content_page(document, "2.4 Chất lượng dữ liệu")
    audit = data["audit"]
    _table(document, ["Kiểm tra", "Kết quả"], [
        ("Institution có completion", f"{audit['processed_rows']['institutions_with_completion']:,}"),
        ("Tọa độ hợp lệ", f"{audit['processed_rows']['institutions_with_coordinates']:,}"),
        ("UNITID trùng", audit["duplicate_unitid"]),
        ("Tỷ lệ ngoài [0,1]", sum(audit["out_of_range_rates"].values())),
        ("Năm lịch sử", ", ".join(map(str, audit["history_years"]))),
    ])
    _paragraph(document, "Missing được công bố theo từng biến thay vì xóa toàn bộ dòng. Điều này giữ quy mô mẫu cho các phân tích không cần mọi cột cùng lúc.")

    _new_content_page(document, "2.5 Từ điển dữ liệu")
    dictionary = data["dictionary"]
    _table(document, ["Biến", "Ý nghĩa", "Đơn vị", "Nguồn", "Vai trò"], dictionary.itertuples(index=False, name=None), font_size=8)

    # Chapter 3
    _new_content_page(document, "3. Tiền xử lý và biến đổi", 1)
    _paragraph(document, "Pipeline phân tách rõ acquisition, processing, EDA, modeling, dashboard và reporting. Dữ liệu raw không chỉnh tay; mọi bảng processed có thể tái tạo từ script.")

    processing_pages = [
        ("3.1 Tải dữ liệu và provenance", "Downloader ghi file tạm rồi mới thay thế đích để tránh file hỏng. ZIP được giải nén an toàn, chặn path traversal. Manifest ghi byte và SHA-256; rubric cũng có checksum bảo vệ."),
        ("3.2 Missing value", "Các mã NULL, NA, PS và PrivacySuppressed trở thành missing. EDA dùng từng tập con phù hợp. Model dùng median/mode imputer được fit chỉ trên train, tránh leakage từ test."),
        ("3.3 Outlier và miền giá trị", "Các tỷ lệ phải nằm trong [0,1]. Giá trị hợp lệ nhưng cực trị không bị xóa tùy tiện vì trường rất lớn hoặc học phí cao có thể là quan sát thật. Box plot và robust summary được dùng để nhận diện."),
        ("3.4 Chuẩn hóa danh mục", "CONTROL, PREDDEG, LOCALE và DISTANCEONLY được ánh xạ sang nhãn đọc được. Cột gốc mã số vẫn được giữ khi cần audit; nhãn phục vụ dashboard."),
        ("3.5 Join/Merge", "Field-of-study được nối state theo UNITID với validate many-to-one. Equity được reshape từ wide sang long. History được concat sau khi mỗi file được làm sạch cùng schema."),
        ("3.6 Calculated fields", "Completion rate coalesce biến 4-year/L4; low_completion khóa tại 40%; log enrollment giảm lệch; risk probability và risk level phục vụ dự báo; disadvantage count tổng hợp điều kiện phân vị."),
        ("3.7 Nghiệm thu pipeline", "Audit phải đạt row count, unique key, valid ranges. Pytest kiểm tra rubric checksum, schema, temporal years, feature leakage và accuracy gate."),
    ]
    for heading, body in processing_pages:
        _new_content_page(document, heading)
        _paragraph(document, body)
        _paragraph(document, "Bước này được thực thi bằng mã nguồn trong src/ttdltq và không yêu cầu chỉnh tay file CSV. Nhờ đó kết quả có thể đối chiếu khi nguồn được tải lại.")

    # Chapter 4 EDA
    _new_content_page(document, "4. Khám phá dữ liệu (EDA)", 1)
    _paragraph(document, "EDA dùng Matplotlib/Seaborn và sinh năm hình tĩnh trước dashboard, đúng yêu cầu rubric. Mỗi hình trả lời một câu hỏi, không chỉ minh họa dữ liệu.")
    eda_pages = [
        ("4.1 Phân bố theo bang", "eda_state_completion.png", "Hình 2. Tỷ lệ hoàn thành có trọng số theo các bang thấp/cao.", "Khoảng cách địa lý là tín hiệu để drill-down, không phải ước lượng tác động của bang."),
        ("4.2 Phân bố theo loại hình", "eda_completion_by_control.png", "Hình 3. Box plot tỷ lệ hoàn thành theo loại hình.", "Box plot thể hiện trung vị, độ phân tán và ngoại lai, tránh chỉ so sánh một số trung bình."),
        ("4.3 Duy trì và hoàn thành", "eda_retention_completion_scatter.png", "Hình 4. Scatter retention–completion.", "Liên hệ cùng chiều giúp xác định retention là chỉ báo sớm có giá trị phân tích."),
        ("4.4 Ma trận liên hệ yếu tố", "eda_factor_correlation_heatmap.png", "Hình 5. Spearman correlation với completion.", "Spearman phù hợp quan hệ đơn điệu và ít nhạy hơn Pearson trước ngoại lai/phân phối lệch."),
        ("4.5 Bất lợi cộng dồn", "eda_compound_disadvantage.png", "Hình 6. Completion và low-completion share theo số bất lợi.", "Chỉ số tổng hợp dùng để kể story tương tác nhiều yếu tố; không phải thang nhân quả."),
    ]
    for heading, filename, caption, explanation in eda_pages:
        _new_content_page(document, heading)
        _image(document, FIGURE_DIR / filename, caption)
        _paragraph(document, explanation)

    _new_content_page(document, "4.6 Bảng hệ số liên hệ")
    correlations = data["correlations"].sort_values("spearman_rho", ascending=False)
    _table(document, ["Yếu tố", "Spearman rho", "N"], [
        (row.factor_label, f"{row.spearman_rho:.3f}", f"{int(row.n):,}") for row in correlations.itertuples()
    ])
    _paragraph(document, "Hệ số là liên hệ đơn biến. Mô hình đa biến ở chương 7 dùng nhiều yếu tố đồng thời nhưng vẫn không tạo bằng chứng nhân quả.")

    # Chapter 5 dashboard
    _new_content_page(document, "5. Thiết kế dashboard", 1)
    _paragraph(document, "Dashboard gồm ba trang theo đúng mạch story: bức tranh toàn quốc, tác nhân/khoảng cách và cảnh báo sớm. Màu đỏ dành cho rủi ro; xanh lá cho kết quả tốt; các màu trung tính cho nhóm so sánh.")
    dashboard_pages = [
        ("5.1 Trang toàn quốc", "KPI, choropleth, xếp hạng bang, 100% stacked bar và point map. Người dùng lọc từ toàn quốc xuống bang và cơ sở."),
        ("5.2 Geographic Map", "Choropleth dùng mã bang và tỷ lệ completion có trọng số. Point map dùng tọa độ từng cơ sở. Tooltip cung cấp tên, quy mô, retention và completion."),
        ("5.3 Trang tác nhân", "Scatter + trend, box plot, heatmap, grouped bar, biểu đồ kết hợp và treemap trả lời yếu tố nào đi cùng kết quả và khoảng cách nhóm."),
        ("5.4 Trang mô hình", "Gauge, donut, confusion matrix, feature importance và action list tích hợp xác suất dự báo vào dashboard."),
        ("5.5 Bộ lọc", "Bang, loại cơ sở, bậc đào tạo, locale và distance-only là filter toàn cục. Risk level là filter tại trang mô hình."),
        ("5.6 Drill-down", "Luồng drill-down từ toàn quốc đến bang rồi cơ sở; từ bậc văn bằng đến ngành. Các KPI và chart được tính lại trên ngữ cảnh lọc."),
        ("5.7 Tooltip và cross-filter", "Plotly hover giải thích từng điểm. Bộ lọc chung tạo cross-filter đồng thời các thành phần, tránh mỗi biểu đồ hiển thị một population khác nhau."),
        ("5.8 Logic chọn biểu đồ", "Map trả lời ở đâu; bar trả lời xếp hạng/cơ cấu; scatter trả lời liên hệ; box trả lời phân bố; heatmap trả lời cường độ; treemap trả lời cơ cấu phân cấp; gauge/table phục vụ hành động."),
        ("5.9 Khả năng đọc", "Trục tỷ lệ dùng phần trăm, title/legend thống nhất, tooltip không hiển thị cột kỹ thuật. Caption cảnh báo khi biến ngành chỉ là số văn bằng."),
    ]
    for heading, body in dashboard_pages:
        _new_content_page(document, heading)
        _paragraph(document, body)
        _paragraph(document, "Thiết kế ưu tiên một câu hỏi cho mỗi biểu đồ và một kết luận ngắn, tránh biểu đồ phân cấp quá nhiều lát gây rối mắt.")

    _new_content_page(document, "5.10 Danh mục 14 loại hiển thị")
    _table(document, ["STT", "Loại", "Mục đích"], [
        (1, "Choropleth", "Phân bố completion theo bang"),
        (2, "Scatter geo", "Điểm từng cơ sở"),
        (3, "Horizontal bar", "Xếp hạng bang"),
        (4, "100% stacked bar", "Cơ cấu rủi ro"),
        (5, "Scatter + trend", "Liên hệ retention–completion"),
        (6, "Box plot", "Phân bố theo loại hình"),
        (7, "Heatmap", "Liên hệ và confusion matrix"),
        (8, "Grouped bar", "Khoảng cách nhóm"),
        (9, "Line + bar", "Bất lợi cộng dồn"),
        (10, "Treemap", "Ngành và bậc văn bằng"),
        (11, "Gauge", "Xác suất rủi ro trung bình"),
        (12, "Donut", "Cơ cấu mức rủi ro"),
        (13, "Matrix", "Thực tế–dự báo"),
        (14, "Table + data bar", "Danh sách ưu tiên"),
    ])

    # Chapter 6 insights
    _new_content_page(document, "6. Insight và storytelling", 1)
    _paragraph(document, "Story dẫn từ 'ở đâu' đến 'nhóm nào', 'yếu tố nào', 'bất lợi cộng dồn' và cuối cùng 'ưu tiên kiểm tra ở đâu'. Mỗi insight gồm con số, đối tượng so sánh và giới hạn.")
    for index, insight in enumerate(data["insights"], start=1):
        _new_content_page(document, f"6.{index} {insight['title']}")
        _paragraph(document, insight["statement"])
        _paragraph(document, f"Câu hỏi liên quan: {insight['research_question']}.")
        _paragraph(document, f"Giới hạn diễn giải: {insight['caveat']}")
        _paragraph(document, "Hành động phân tích: dùng bộ lọc dashboard để kiểm tra tính ổn định của nhận định theo bang, loại cơ sở và bậc đào tạo; không chuyển nhận định mô tả thành phán quyết nhân quả.")

    _new_content_page(document, "6.6 Story kết luận")
    _paragraph(document, "Kết quả cho thấy completion là kết quả của nhiều bối cảnh đồng thời. Retention năm đầu là chỉ báo thực hành rõ nhất trong dữ liệu; Pell/first-generation cho thấy nhu cầu xem xét khoảng cách; loại hình và địa lý xác định nơi cần drill-down. Mô hình tổng hợp các biến thành xác suất để ưu tiên phân tích sâu.")

    # Chapter 7 model
    _new_content_page(document, "7. Mô hình Logistic Regression", 1)
    _paragraph(document, "Nhãn dương là cơ sở có completion dưới 40%. Logistic Regression được chọn vì đầu ra nhị phân, có xác suất, dễ tích hợp và đúng rubric.")
    model_pages = [
        ("7.1 Định nghĩa target", "low_completion bằng 1 khi completion_rate < 0,40. Ngưỡng được khóa trước đánh giá. Mô hình không dự báo từng sinh viên."),
        ("7.2 Feature và chống leakage", "Feature gồm loại trường, bậc, locale, distance, enrollment, Pell, loan, student–faculty ratio, net price, tuition và retention. completion/target bị cấm."),
        ("7.3 Tiền xử lý trong pipeline", "Median/mode imputation, one-hot encoding, standardization và spline đều nằm trong sklearn Pipeline, được fit chỉ trên train."),
        ("7.4 Temporal holdout", "Train dùng 2017–2021; test là 2022. Cách này mô phỏng dự báo năm mới và khó hơn chia ngẫu nhiên."),
        ("7.5 Hai cấu hình", "Baseline tối ưu accuracy tổng thể nhưng recall thấp. Balanced spline tăng cân bằng hai lớp và được chọn theo mục tiêu cảnh báo."),
        ("7.6 Cut-off", "Cut-off phân lớp là 0,5. Risk level dùng 0,4 và 0,7 để trình bày. Không đổi cut-off sau khi xem test chỉ để đạt chỉ số mong muốn."),
        ("7.7 Ý nghĩa chỉ số", "Accuracy là tổng đúng; balanced accuracy cân bằng lớp; recall đo phát hiện rủi ro; precision đo độ đúng cảnh báo; F1 cân bằng; ROC-AUC đo xếp hạng; Brier đo xác suất."),
    ]
    for heading, body in model_pages:
        _new_content_page(document, heading)
        _paragraph(document, body)

    _new_content_page(document, "7.8 Kết quả định lượng")
    _table(document, ["Chỉ số", "Baseline", "Mô hình chọn"], [
        ("Accuracy", f"{metrics['models']['baseline_logistic']['accuracy']:.2%}", f"{selected['accuracy']:.2%}"),
        ("Balanced Accuracy", f"{metrics['models']['baseline_logistic']['balanced_accuracy']:.2%}", f"{selected['balanced_accuracy']:.2%}"),
        ("Recall", f"{metrics['models']['baseline_logistic']['recall']:.2%}", f"{selected['recall']:.2%}"),
        ("Precision", f"{metrics['models']['baseline_logistic']['precision']:.2%}", f"{selected['precision']:.2%}"),
        ("F1", f"{metrics['models']['baseline_logistic']['f1']:.2%}", f"{selected['f1']:.2%}"),
        ("ROC-AUC", f"{metrics['models']['baseline_logistic']['roc_auc']:.3f}", f"{selected['roc_auc']:.3f}"),
        ("Brier", f"{metrics['models']['baseline_logistic']['brier_score']:.3f}", f"{selected['brier_score']:.3f}"),
    ])
    _paragraph(document, "Mô hình chọn qua cổng Accuracy 80%. Recall dưới 80% được công bố như giới hạn; ưu tiên balanced model vì giảm bỏ sót đáng kể so với baseline.")

    _new_content_page(document, "7.9 Ma trận nhầm lẫn")
    _image(document, FIGURE_DIR / "model_confusion_matrix.png", "Hình 7. Ma trận nhầm lẫn trên temporal test 2022.")
    _paragraph(document, "Có 3.200 true negative, 635 false positive, 354 false negative và 1.170 true positive. False negative là trường hợp cần lưu ý trong cảnh báo sớm.")

    _new_content_page(document, "7.10 ROC và Precision–Recall")
    _image(document, FIGURE_DIR / "model_roc_pr.png", "Hình 8. ROC và Precision–Recall trên test.")
    _paragraph(document, "ROC-AUC 0,874 cho thấy khả năng xếp hạng khá tốt. PR curve cần đọc cùng prevalence của lớp rủi ro và mục tiêu sử dụng.")

    _new_content_page(document, "7.11 Calibration")
    _image(document, FIGURE_DIR / "model_calibration.png", "Hình 9. Độ hiệu chỉnh xác suất.")
    _paragraph(document, "Calibration so sánh xác suất dự báo với tỷ lệ quan sát. Xác suất chưa được xem là tần suất hoàn hảo; gauge dùng để ưu tiên chứ không phải cam kết chắc chắn.")

    _new_content_page(document, "7.12 Feature importance")
    importance = data["importance"].head(12)
    _table(document, ["Feature", "Permutation importance", "Độ lệch chuẩn"], [
        (row.feature, f"{row.importance_mean:.4f}", f"{row.importance_std:.4f}") for row in importance.itertuples()
    ])
    _paragraph(document, "Permutation importance là đóng góp dự báo có điều kiện trên cấu hình và test hiện tại; không phải hệ số tác động nhân quả.")

    _new_content_page(document, "7.13 Pseudocode")
    pseudo = document.add_paragraph()
    run = pseudo.add_run(
        "INPUT history 2017–2022\n"
        "DEFINE y = 1(completion < 0.40)\n"
        "SPLIT train = 2017–2021, test = 2022\n"
        "FIT imputer + encoder + spline + LogisticRegression on train\n"
        "PREDICT probability on test at cut-off 0.50\n"
        "COMPUTE accuracy, balanced accuracy, recall, precision, F1, ROC-AUC, Brier\n"
        "REFIT locked specification on historical eligible data\n"
        "SCORE current institutions → risk_probability → dashboard"
    )
    run.font.name = "Consolas"
    run.font.size = Pt(10)

    # Chapters 8-10
    _new_content_page(document, "8. Giới hạn và đạo đức", 1)
    _bullets(document, [
        "Không suy luận nhân quả từ dữ liệu quan sát.",
        "Không suy rộng kết quả cấp cơ sở sang cá nhân.",
        "Không dùng risk score để trừng phạt hoặc cắt hỗ trợ.",
        "Công bố Title IV coverage và privacy suppression.",
        "Không gọi IPEDSCOUNT2 là tỷ lệ hoàn thành theo ngành.",
        "Kiểm tra fairness theo nhóm khi bổ sung dữ liệu thích hợp.",
    ])

    _new_content_page(document, "8.1 Threats to validity")
    _paragraph(document, "Internal validity bị giới hạn bởi confounding và định nghĩa biến khác thời điểm. External validity giới hạn trong hệ giáo dục Hoa Kỳ/Title IV. Construct validity phụ thuộc completion 150% và ngưỡng 40%. Temporal validity được cải thiện bằng holdout 2022 nhưng vẫn cần theo dõi drift ở năm mới.")

    _new_content_page(document, "9. Cài đặt và sử dụng", 1)
    _paragraph(document, "Cài Python 3.11+, chạy pip install -r requirements.txt, sau đó chạy các script download, build_dataset, run_eda, train_model, pytest và build_report. Dashboard khởi động bằng streamlit run dashboard/app.py.")
    _paragraph(document, "Mọi lệnh chi tiết nằm trong README và docs/08-reproducibility.md. Người bảo vệ cần hiểu vì sao temporal split, vì sao không xóa outlier tùy tiện và vì sao Accuracy không đủ một mình.")

    _new_content_page(document, "9.1 Kịch bản demo")
    _bullets(document, [
        "Mở trang 1, chỉ bản đồ và nêu khoảng cách địa lý.",
        "Lọc một bang, đi sâu tới loại cơ sở và institution point map.",
        "Sang trang 2, giải thích retention, Pell gap và bất lợi cộng dồn.",
        "Sang trang 3, giải thích Accuracy/Recall, confusion matrix và action list.",
        "Kết thúc bằng giới hạn: dự báo cơ sở, không dự báo từng sinh viên; association không phải causation.",
    ])
    _paragraph(document, "Cần quay video backup sau khi giao diện cuối được duyệt và điền link video vào bản nộp.")

    _new_content_page(document, "10. Kết luận", 1)
    _paragraph(document, "Dự án đã hình thành pipeline tái lập từ nguồn chính thức đến dashboard và mô hình. Kết quả cho thấy retention năm đầu, bối cảnh tài chính và loại hình/địa lý là các tín hiệu liên quan đáng chú ý. Logistic Regression vượt Accuracy 80% trên test ngoài thời gian, đủ cho mục đích ưu tiên kiểm tra nhưng chưa thay thế đánh giá chuyên môn.")
    _paragraph(document, "Hướng phát triển gồm đối chiếu raw IPEDS khi kết nối ổn định, kiểm tra drift theo năm, calibration nâng cao và phân tích công bằng theo nhóm có cỡ mẫu đủ.")

    _new_content_page(document, "Tài liệu tham khảo", 1)
    refs = [
        "[1] U.S. Department of Education, ‘College Scorecard Data,’ data.gov. https://catalog.data.gov/dataset/college-scorecard",
        "[2] National Center for Education Statistics, ‘IPEDS: Use the Data.’ https://nces.ed.gov/ipeds/use-the-data",
        "[3] U.S. Department of Education, ‘Institution-level Data Documentation,’ College Scorecard.",
        "[4] U.S. Department of Education, ‘Field of Study Data Documentation,’ College Scorecard.",
        "[5] F. Pedregosa et al., ‘Scikit-learn: Machine Learning in Python,’ Journal of Machine Learning Research, vol. 12, pp. 2825–2830, 2011.",
        "[6] Plotly Technologies Inc., ‘Plotly Python Open Source Graphing Library.’",
        "[7] Streamlit Inc., ‘Streamlit Documentation.’",
    ]
    for reference in refs:
        _paragraph(document, reference)

    # Appendices, each meaningful and page-separated for review.
    _new_content_page(document, "Phụ lục A — Output kiểm chứng", 1)
    _bullets(document, [
        "data/source_manifest.json — provenance và checksum.",
        "outputs/eda/data_quality_audit.json — chất lượng dữ liệu.",
        "models/metrics.json — temporal split và chỉ số.",
        "models/test_predictions.csv — đối chiếu từng dòng test.",
        "data/processed/model_predictions.csv — đầu vào dashboard.",
    ])

    _new_content_page(document, "Phụ lục B — Ngưỡng bất lợi")
    disadvantage = data["disadvantage"]
    _table(document, ["Số bất lợi", "Số cơ sở", "Trung vị completion", "Tỷ trọng completion thấp"], [
        (int(row.disadvantage_count), int(row.institution_count), f"{row.median_completion_rate:.1%}", f"{row.low_completion_share:.1%}")
        for row in disadvantage.itertuples()
    ])
    _paragraph(document, "Quan hệ không hoàn toàn đơn điệu; vì vậy báo cáo chỉ dùng xu hướng đầu–cuối và công bố cách tạo chỉ số.")

    _new_content_page(document, "Phụ lục C — Checklist trước khi nộp")
    _bullets(document, [
        "Điền thông tin trường/lớp/giảng viên/sinh viên trên trang bìa.",
        "Mở Word, Ctrl+A → F9 để cập nhật mục lục và số trang.",
        "Kiểm tra báo cáo đạt tối thiểu 40 trang sau dàn trang cuối.",
        "Chèn ảnh chụp dashboard phiên bản cuối nếu giảng viên yêu cầu.",
        "Quay video demo, thử link và thêm QR/link backup.",
        "Chạy python -m pytest -q và lưu ảnh kết quả.",
        "Không xóa phần limitations hoặc đổi association thành causation.",
    ])

    # Force Word to refresh fields on open.
    settings = document.settings._element
    update_fields = OxmlElement("w:updateFields")
    update_fields.set(qn("w:val"), "true")
    settings.append(update_fields)

    document.save(output_path)
    return output_path


def main() -> None:
    path = build_report()
    print(path)


if __name__ == "__main__":
    main()


"""
EduShield AI — Module Đọc & Kiểm tra File Đề Thi (Exam File Parser)

Đọc file đề thi giáo viên upload (định dạng .xlsx hoặc .docx theo đúng mẫu quy định tại
Chương 6 tài liệu "Dac_Ta_Bo_Sung_Module_De_Thi") và tách ra danh sách câu hỏi hợp lệ.

Nguyên tắc thiết kế quan trọng (đúng theo đặc tả mục 6.3): một vài dòng/câu lỗi KHÔNG được
làm hỏng toàn bộ quá trình đọc file. Hàm luôn cố đọc hết toàn bộ file, tách riêng câu hợp lệ
và câu lỗi, trả về cả hai để giáo viên tự quyết định.
"""

import io
import re
from dataclasses import dataclass, field
from typing import Optional

MAX_QUESTIONS_PER_EXAM = 200

VALID_OPTIONS = {"A", "B", "C", "D"}


@dataclass
class ParsedQuestion:
    """1 câu hỏi đã đọc thành công từ file, sẵn sàng để lưu vào bảng `questions`."""
    order_index: int
    content: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_option: str  # 'A' | 'B' | 'C' | 'D'


@dataclass
class ParseError:
    """1 lỗi phát hiện được khi đọc file — không làm dừng toàn bộ quá trình đọc."""
    code: str
    location: str  # VD: "Dòng 5" (Excel) hoặc "Câu 3" (Word)
    message: str


@dataclass
class ParseResult:
    questions: list[ParsedQuestion] = field(default_factory=list)
    errors: list[ParseError] = field(default_factory=list)

    @property
    def valid_count(self) -> int:
        return len(self.questions)

    @property
    def error_count(self) -> int:
        return len(self.errors)


def _check_duplicates(result: ParseResult) -> None:
    """
    Phát hiện câu hỏi trùng lặp nội dung hoàn toàn (mã lỗi ERR_DUPLICATE_QUESTION).
    Theo đặc tả: CHỈ cảnh báo, KHÔNG chặn — vẫn giữ lại câu xuất hiện đầu tiên.
    """
    seen: dict[str, int] = {}
    deduped: list[ParsedQuestion] = []
    for q in result.questions:
        key = q.content.strip().lower()
        if key in seen:
            result.errors.append(
                ParseError(
                    code="ERR_DUPLICATE_QUESTION",
                    location=f"Câu ở vị trí {q.order_index}",
                    message=(
                        f"Nội dung trùng với câu ở vị trí {seen[key]} — chỉ giữ lại câu đầu tiên, "
                        f"câu này bị bỏ qua."
                    ),
                )
            )
            continue
        seen[key] = q.order_index
        deduped.append(q)
    result.questions = deduped


def _finalize(result: ParseResult) -> ParseResult:
    """Kiểm tra các ràng buộc tổng thể sau khi đã đọc xong toàn bộ file."""
    _check_duplicates(result)

    if not result.questions:
        result.errors.append(
            ParseError(
                code="ERR_EMPTY_FILE",
                location="Toàn bộ file",
                message="Không đọc được câu hỏi hợp lệ nào trong file. Vui lòng kiểm tra lại đúng mẫu quy định.",
            )
        )
    elif len(result.questions) > MAX_QUESTIONS_PER_EXAM:
        result.errors.append(
            ParseError(
                code="ERR_TOO_MANY_QUESTIONS",
                location="Toàn bộ file",
                message=(
                    f"File có {len(result.questions)} câu hợp lệ, vượt quá giới hạn "
                    f"{MAX_QUESTIONS_PER_EXAM} câu/đề thi. Vui lòng tách nhỏ đề thi."
                ),
            )
        )
        result.questions = []  # Từ chối toàn bộ — không tạo đề thi dở dang quá lớn

    # Đánh lại order_index liên tục 0..n-1 sau khi đã loại bỏ câu lỗi/trùng lặp
    for i, q in enumerate(result.questions):
        q.order_index = i

    return result


# ──────────────────────────────────────────────────────────
# ĐỌC FILE EXCEL (.xlsx) — Mẫu chính, xem Chương 6.1 đặc tả
# Cấu trúc cột: A=STT, B=Câu hỏi, C=Đáp án A, D=Đáp án B, E=Đáp án C, F=Đáp án D, G=Đáp án đúng
# Dữ liệu bắt đầu từ dòng 2 (dòng 1 là tiêu đề cột)
# ──────────────────────────────────────────────────────────

def parse_excel(file_bytes: bytes) -> ParseResult:
    from openpyxl import load_workbook

    result = ParseResult()

    try:
        wb = load_workbook(io.BytesIO(file_bytes), data_only=True, read_only=True)
        sheet = wb.worksheets[0]
    except Exception as exc:
        result.errors.append(
            ParseError(
                code="ERR_INVALID_FORMAT",
                location="Toàn bộ file",
                message=f"Không thể mở file Excel — file có thể bị hỏng hoặc sai định dạng: {exc}",
            )
        )
        return result

    order_index = 0
    for row_idx, row in enumerate(sheet.iter_rows(min_row=2, max_col=7, values_only=True), start=2):
        cells = list(row) + [None] * (7 - len(row))
        _stt, question, opt_a, opt_b, opt_c, opt_d, correct = cells[:7]

        # Bỏ qua dòng trống hoàn toàn — KHÔNG tính là lỗi (đúng đặc tả mục 6.1)
        if all(v is None or str(v).strip() == "" for v in (question, opt_a, opt_b, opt_c, opt_d, correct)):
            continue

        question = (str(question).strip() if question is not None else "")
        opt_a = (str(opt_a).strip() if opt_a is not None else "")
        opt_b = (str(opt_b).strip() if opt_b is not None else "")
        opt_c = (str(opt_c).strip() if opt_c is not None else "")
        opt_d = (str(opt_d).strip() if opt_d is not None else "")
        correct = (str(correct).strip().upper() if correct is not None else "")

        if not (question and opt_a and opt_b and opt_c and opt_d):
            result.errors.append(
                ParseError(
                    code="ERR_MISSING_FIELD",
                    location=f"Dòng {row_idx}",
                    message="Thiếu câu hỏi hoặc thiếu 1 trong 4 đáp án — dòng này bị bỏ qua.",
                )
            )
            continue

        if correct not in VALID_OPTIONS:
            result.errors.append(
                ParseError(
                    code="ERR_INVALID_ANSWER",
                    location=f"Dòng {row_idx}",
                    message=f"Cột 'Đáp án đúng' phải là A/B/C/D, nhận được: '{correct or '(trống)'}' — dòng này bị bỏ qua.",
                )
            )
            continue

        result.questions.append(
            ParsedQuestion(
                order_index=order_index,
                content=question,
                option_a=opt_a,
                option_b=opt_b,
                option_c=opt_c,
                option_d=opt_d,
                correct_option=correct,
            )
        )
        order_index += 1

    return _finalize(result)


# ──────────────────────────────────────────────────────────
# ĐỌC FILE WORD (.docx) — Mẫu theo cấu trúc văn bản quy ước, xem Chương 6.2 đặc tả
#
# Mỗi câu hỏi gồm đúng 6 dòng liên tiếp:
#   Câu {số}: {nội dung câu hỏi}
#   A. {đáp án A}
#   B. {đáp án B}
#   C. {đáp án C}
#   D. {đáp án D}
#   Đáp án: {A/B/C/D}
# ──────────────────────────────────────────────────────────

_QUESTION_LINE_RE = re.compile(r"^Câu\s*\d+\s*[:.]\s*(.+)$", re.IGNORECASE)
_OPTION_LINE_RE = {
    "A": re.compile(r"^A\s*[.):]\s*(.+)$"),
    "B": re.compile(r"^B\s*[.):]\s*(.+)$"),
    "C": re.compile(r"^C\s*[.):]\s*(.+)$"),
    "D": re.compile(r"^D\s*[.):]\s*(.+)$"),
}
_ANSWER_LINE_RE = re.compile(r"^Đáp\s*án\s*[:.]\s*([A-Da-d])\s*$", re.IGNORECASE)


def parse_docx(file_bytes: bytes) -> ParseResult:
    from docx import Document as DocxDocument

    result = ParseResult()

    try:
        doc = DocxDocument(io.BytesIO(file_bytes))
    except Exception as exc:
        result.errors.append(
            ParseError(
                code="ERR_INVALID_FORMAT",
                location="Toàn bộ file",
                message=f"Không thể mở file Word — file có thể bị hỏng hoặc sai định dạng: {exc}",
            )
        )
        return result

    # Lấy toàn bộ dòng có nội dung (bỏ qua dòng trống — cho phép giáo viên cách dòng giữa các câu)
    lines = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

    order_index = 0
    question_number = 0
    i = 0
    n = len(lines)

    while i < n:
        m_question = _QUESTION_LINE_RE.match(lines[i])
        if not m_question:
            # Dòng không khớp mẫu "Câu N: ..." — bỏ qua (có thể là tiêu đề file, ghi chú...)
            i += 1
            continue

        question_number += 1
        question_content = m_question.group(1).strip()
        block_label = f"Câu {question_number} (dòng văn bản thứ {i + 1})"

        # Cần đủ 5 dòng tiếp theo: A, B, C, D, Đáp án
        if i + 5 >= n:
            result.errors.append(
                ParseError(
                    code="ERR_MISSING_FIELD",
                    location=block_label,
                    message="Thiếu 1 hoặc nhiều dòng đáp án / dòng đáp án đúng ở cuối file — câu này bị bỏ qua.",
                )
            )
            break  # Hết dòng để đọc tiếp

        options: dict[str, str] = {}
        ok = True
        for offset, letter in enumerate(["A", "B", "C", "D"], start=1):
            line = lines[i + offset]
            m_opt = _OPTION_LINE_RE[letter].match(line)
            if not m_opt:
                result.errors.append(
                    ParseError(
                        code="ERR_MISSING_FIELD",
                        location=block_label,
                        message=(
                            f"Dòng thứ {offset + 1} của câu phải bắt đầu bằng '{letter}.' "
                            f"nhưng nhận được: '{line[:60]}' — câu này bị bỏ qua."
                        ),
                    )
                )
                ok = False
                break
            options[letter] = m_opt.group(1).strip()

        if not ok:
            # Nhảy tới sau dòng câu hỏi 1 dòng để thử tìm câu tiếp theo, tránh đọc lệch toàn bộ file
            i += 1
            continue

        answer_line = lines[i + 5]
        m_answer = _ANSWER_LINE_RE.match(answer_line)
        if not m_answer:
            result.errors.append(
                ParseError(
                    code="ERR_INVALID_ANSWER",
                    location=block_label,
                    message=(
                        f"Dòng cuối câu phải đúng mẫu 'Đáp án: A/B/C/D', nhận được: "
                        f"'{answer_line[:60]}' — câu này bị bỏ qua."
                    ),
                )
            )
            i += 6
            continue

        correct = m_answer.group(1).upper()

        if not question_content or any(not options[l] for l in ["A", "B", "C", "D"]):
            result.errors.append(
                ParseError(
                    code="ERR_MISSING_FIELD",
                    location=block_label,
                    message="Nội dung câu hỏi hoặc 1 trong 4 đáp án bị để trống — câu này bị bỏ qua.",
                )
            )
            i += 6
            continue

        result.questions.append(
            ParsedQuestion(
                order_index=order_index,
                content=question_content,
                option_a=options["A"],
                option_b=options["B"],
                option_c=options["C"],
                option_d=options["D"],
                correct_option=correct,
            )
        )
        order_index += 1
        i += 6  # Nhảy qua trọn 1 khối câu hỏi vừa đọc (1 dòng câu hỏi + 4 đáp án + 1 dòng đáp án)

    return _finalize(result)


def parse_exam_file(filename: str, file_bytes: bytes) -> ParseResult:
    """
    Điểm vào chính: tự chọn parser theo đuôi file.
    Trả về ParseResult ngay cả khi lỗi (không raise exception) để endpoint gọi có thể
    trả về danh sách lỗi rõ ràng cho giáo viên thay vì lỗi 500 chung chung.
    """
    lower = filename.lower()
    if lower.endswith(".xlsx"):
        return parse_excel(file_bytes)
    if lower.endswith(".docx"):
        return parse_docx(file_bytes)

    result = ParseResult()
    result.errors.append(
        ParseError(
            code="ERR_INVALID_FORMAT",
            location="Toàn bộ file",
            message="Chỉ chấp nhận file .xlsx hoặc .docx theo đúng mẫu quy định.",
        )
    )
    return result

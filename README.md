# Đường đi an toàn — Bài tập lớn CS112 (Đinh Văn Huy – 25730032)

**Demo online:** https://vanhuydotcom.github.io/cs112-duong-di-an-toan/

Demo web trực quan hóa và so sánh 4 cách giải bài đếm đường đi an toàn trên lưới n×n
(vét cạn quay lui, đệ quy có nhớ, QHĐ bottom-up, tổ hợp + bao hàm–loại trừ).

| Thư mục | Nội dung |
|---|---|
| `1_SourceCode/` | `app/` demo web (mở `app/index.html`), `solution/safe_path.py` lời giải nộp WeCode, `tools/` script quay video & chụp ảnh |
| `2_VideoDemo/` | `demo.mp4` — video demo không lời (phụ đề + rọi sáng), ~3 phút 20 giây |
| `3_Testcase/` | 103 test (`.inp`/`.out`) chia 6 nhóm, `gen_tests.py` sinh test, `run_tests.py` chạy test, `ket_qua/` kết quả |
| `4_Report/` | `report.pdf`, nguồn `report.tex` (biên dịch: `tectonic report.tex`) |

Chạy demo cục bộ: `python3 -m http.server -d 1_SourceCode/app` rồi mở http://localhost:8000
Chạy toàn bộ test: `python3 3_Testcase/run_tests.py`

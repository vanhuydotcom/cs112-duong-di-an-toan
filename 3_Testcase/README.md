# Bộ testcase — Đường đi an toàn

| Nhóm | Số test | Nội dung |
|---|---|---|
| `01_thong_thuong` | 15 | ngẫu nhiên n = 5..120, mật độ chốt 10–30% |
| `02_bien` | 27 | n = 1, chốt tại KTX/UIT (cả n = 1000), chặn hàng/cột/đường chéo, toàn bộ 16 bản đồ 2×2 |
| `03_nho` | 30 | n = 3..8, mật độ 0–60%, đối chiếu bằng vét cạn |
| `04_lon` | 10 | n = 500..1000, mật độ 0–45% |
| `05_dac_biet` | 10 | không chốt (vượt mod), hành lang 1 đường, viền, bậc thang, bàn cờ, mê cung, rất ít chốt |
| `06_khong_hop_le` | 11 | input sai định dạng; `.out` là loại lỗi demo phải báo |

- Sinh lại: `python3 3_Testcase/gen_tests.py` (seed cố định). Đáp án tính độc lập bằng QHĐ số nguyên lớn, đối chiếu thêm vét cạn (n ≤ 8) và C(2n−2, n−1) (không chốt).
- Chạy: `python3 3_Testcase/run_tests.py` → `ket_qua/ket_qua.csv`, `ket_qua/tom_tat.md`.
- Có thể mở trực tiếp từng file `.inp` trên demo (nút "📂 Mở file .inp").

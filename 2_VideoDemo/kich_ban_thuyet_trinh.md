# Kịch bản tự quay video demo & thuyết trình — "Đường đi an toàn"

> Thời lượng mục tiêu: **10–12 phút**. Cột **Thao tác** là việc làm trên màn hình, cột **Lời nói** là gợi ý — nói theo ý mình, không cần đọc thuộc.
> Đi theo đúng mạch cô yêu cầu: **bài toán → mô hình → CTDL & thuật toán → demo từng bước → testcase → đánh giá**.

---

## 0. Chuẩn bị trước khi quay (không quay)

- [ ] Mở demo: `https://vanhuydotcom.github.io/cs112-duong-di-an-toan/` (hoặc bản cục bộ) — Chrome, **zoom 110–125%**, ẩn bookmark bar, tắt thông báo.
- [ ] Chọn **Tiếng Việt**, giao diện **sáng** (quay rõ hơn).
- [ ] Mở sẵn tab 2: thư mục `3_Testcase` (Finder/VS Code) và file `ket_qua/tom_tat.md`.
- [ ] Mở sẵn tab 3: `4_Report/report.pdf` ở trang **Chương 5** (bảng dp 6×6).
- [ ] Phần mềm quay: QuickTime (`File → New Screen Recording`) hoặc OBS; bật micro; nếu được thì bật webcam góc nhỏ.
- [ ] Ghi sẵn ra giấy 3 con số: **103/103 test đạt**, **146 / 63 / 36 / 22 thao tác** (ví dụ 6×6), **~5 ms với n = 1000**.

---

## 1. Mở đầu — 0:00 → 0:40

| Thao tác | Lời nói |
|---|---|
| Màn hình demo ở đầu trang | "Em chào cô. Em là Đinh Văn Huy, MSSV 25730032, lớp CS112.2026.TX. Bài tập lớn của em là **Đường đi an toàn** — một bài quy hoạch động em đã làm và nộp đạt trên WeCode." |
| | "Em chọn bài này vì đã tự giải được nên muốn phát triển thành một demo để **nhìn thấy** thuật toán chạy, và mở rộng thành **so sánh bốn cách giải** khác nhau cho cùng một bài." |
| | "Bài trình bày gồm: phát biểu bài toán, mô hình, thuật toán, demo từng bước, so sánh, bộ testcase và đánh giá." |

## 2. Bài toán & mô hình — 0:40 → 2:00

| Thao tác | Lời nói |
|---|---|
| Chỉ chuột vào khối **1. Bài toán** | "Bản đồ n×n, KTX khu B ở góc trái trên, UIT ở góc phải dưới. Mỗi bước chỉ được **sang phải hoặc xuống dưới**, không được đi qua ô có chốt CSGT — ký hiệu dấu sao. Cần đếm số đường an toàn, lấy dư cho 10⁹+7." |
| Chỉ vào dòng Input/Output | "**Input**: số nguyên n từ 1 đến 1000, và n dòng mỗi dòng n ký tự chấm hoặc sao. **Output**: một số nguyên là số đường mod 10⁹+7." |
| | "Nhận xét quan trọng: mọi đường đều dài đúng 2n−2 bước. Nếu không có chốt thì số đường là C(2n−2, n−1) — với n = 1000 con số này khoảng 600 chữ số, nên đề mới bắt lấy dư, và cũng cho thấy **không thể liệt kê từng đường**." |
| Bấm **Ví dụ trong đề** (khối 2) | "Đây là ví dụ trong đề: lưới 4×4, ba chốt, đáp án là 3." |

## 3. Ý tưởng & thuật toán chính (QHĐ) — 2:00 → 4:00

| Thao tác | Lời nói |
|---|---|
| Kéo xuống khối **3**, đang chọn **QHĐ bottom-up**, bảng 2 chiều | "Em gọi **dp[i][j] là số đường an toàn từ KTX tới ô (i,j)**." |
| Bấm **▶\|** vài lần tới ô (2,1) hoặc (3,2) | "Bước cuối cùng để vào ô (i,j) chỉ có thể là **từ trên xuống** — ô tím — hoặc **từ trái sang** — ô xanh. Hai nhóm đường này không trùng nhau và gộp lại là đủ tất cả, nên **dp[i][j] = dp[i−1][j] + dp[i][j−1]**." |
| Chỉ vào khung giải thích + dòng mã giả tô vàng | "Bên phải là công thức với số cụ thể, và dòng mã giả đang chạy được tô vàng." |
| Bấm tới ô có chốt (2,2) | "Ô có chốt thì dp bằng 0 vì không đường nào được đi qua. Ô KTX là trường hợp cơ sở, dp = 1." |
| Bấm **▶ Chạy**, chỉnh tốc độ nhanh | "Thứ tự điền là từng hàng, từ trái sang phải — nên khi tới ô (i,j) thì ô trên và ô trái đã có giá trị." |
| Đợi xong, chỉ ô UIT | "Kết quả dp[4][4] = 3, khớp đề." |
| Chuyển tab **Mảng dp[j] (code nộp WeCode)**, bấm vài bước | "Code em nộp chỉ dùng **một mảng một chiều**. Trước khi cập nhật, dp[j] vẫn còn giá trị **ô phía trên**, còn dp[j−1] vừa cập nhật là **ô bên trái** — nên vẫn đúng công thức mà bộ nhớ chỉ còn O(n)." |
| | "Độ phức tạp: mỗi ô O(1) nên **Θ(n²) thời gian, Θ(n) bộ nhớ**; n = 1000 là một triệu phép tính." |

## 4. Các chức năng tương tác — 4:00 → 5:15

| Thao tác | Lời nói |
|---|---|
| Nhập tay trong ô input (thêm 1 dòng sai) → **Kiểm tra & nạp** | "Hệ thống kiểm tra input đầy đủ: sai số dòng, sai độ dài, ký tự lạ, n ngoài phạm vi — báo lỗi kèm vị trí." |
| Bấm **📂 Mở file .inp**, chọn `03_nho/...` | "Có thể mở trực tiếp file testcase." |
| Nạp lại bản 6×6 (`05`… hoặc nhập), bấm vào một ô trên lưới | "Bấm vào ô để thêm/bỏ chốt, đáp án tính lại ngay." |
| Khối **4. Kết quả**: **Vẽ một đường an toàn**, **Làm mờ ô** | "Đây là một đường an toàn ngẫu nhiên; ô bị làm mờ là ô không nằm trên đường an toàn nào. Ô 'Số đường thật' cho thấy giá trị trước khi lấy dư." |
| Sinh ngẫu nhiên n = 1000 | "Với n = 1000, một triệu ô, chỉ mất vài mili giây; lưới lớn hiển thị dạng bản đồ nhiệt." |

## 5. Bốn cách giải & so sánh — 5:15 → 8:15  *(phần ăn điểm sáng tạo)*

> Dùng bản đồ 6×6 trong report: `6 / ...... / .*.... / ...*.. / *..... / ..*... / ......` (đáp án 35).

| Thao tác | Lời nói |
|---|---|
| Chọn **Vét cạn quay lui**, bấm Chạy | "Cách 1 là vét cạn: DFS thử sang phải rồi xuống dưới, gặp chốt thì quay lui, tới UIT thì đếm thêm. Đúng nhưng mỗi đường phải đi riêng — số lời gọi tăng **theo hàm mũ**." |
| Chọn **Đệ quy có nhớ**, bấm từng bước | "Cách 2 là đệ quy có nhớ: gọi f(n,n) ngược về KTX. Ô tím là ngăn xếp lời gọi. Khi gặp lại một ô đã tính thì lấy từ bảng nhớ — xem bộ đếm 'dùng lại bảng nhớ'. Đây là chỗ khác vét cạn." |
| | "Với n = 1000 đệ quy sâu tới 2000 tầng, nên em cài bằng ngăn xếp tường minh để không tràn stack." |
| Chọn **Tổ hợp + bao hàm–loại trừ**, đi tới bước chốt #4 | "Cách 4 chỉ làm việc trên các chốt. Số đường không ràng buộc giữa hai ô là tổ hợp C. Với mỗi chốt, em lấy tổng số đường rồi trừ những đường mà **chốt đầu tiên gặp** là một chốt q phía trên-trái. Ví dụ chốt #4: 15 − 2·4 − 1·3 = 4. Độ phức tạp Θ(n + k²) với k là số chốt." |
| Khối **5**, bấm **So sánh trên input hiện tại** | "Trên cùng input, cả 4 cách đều ra 35. Số thao tác: vét cạn 146, đệ quy có nhớ 63, bottom-up 36, bao hàm–loại trừ 22." |
| Bấm **Benchmark theo n** (mật độ 20%) | "Benchmark thang log: vét cạn tăng theo hàm mũ và phải dừng sau khoảng n = 20; bao hàm–loại trừ tăng theo k² nên chậm khi nhiều chốt; hai cách QHĐ tăng đều theo n²." |
| | "Kết luận: **QHĐ bottom-up là lựa chọn tổng quát nhất**; bao hàm–loại trừ chỉ có lợi khi lưới rất lớn mà rất ít chốt; vét cạn chỉ để minh họa." |

## 6. Bộ testcase & kết quả — 8:15 → 9:45

| Thao tác | Lời nói |
|---|---|
| Mở thư mục `3_Testcase` | "Bộ test có **103 test, 6 nhóm**: thông thường, biên, nhỏ, lớn n = 1000, đặc biệt, và không hợp lệ." |
| Chỉ vài file: `02_bien/n2_tatca_*`, `05_dac_biet/khong_chot_n20_vuot_mod`, `ban_co_n9` | "Nhóm biên có n = 1, chốt ngay KTX hoặc UIT, chặn kín đường chéo, và **toàn bộ 16 bản đồ 2×2**. Nhóm đặc biệt có test đáp án thật vượt 10⁹+7 để kiểm tra lấy dư, hành lang chỉ 1 đường, bàn cờ ra 0, mê cung nhiều ngõ cụt." |
| | "Đáp án được tính bằng cách **độc lập**: QHĐ số nguyên lớn không lấy dư giữa chừng, đối chiếu thêm bằng vét cạn với n ≤ 8 và công thức tổ hợp khi không có chốt." |
| Terminal: `python3 3_Testcase/run_tests.py` (hoặc mở `tom_tat.md`) | "Chạy script: lời giải Python nộp WeCode và cả 4 thuật toán trên demo — **103/103 đạt**. Với n = 1000, bottom-up khoảng 5 ms." |

## 7. Quá trình làm & dùng AI — 9:45 → 11:00

| Thao tác | Lời nói |
|---|---|
| Mở report chương 6 (bảng prompt) | "Em dùng **Claude Code** để hỗ trợ. Lời giải QHĐ là em tự viết và đã Accepted trên WeCode; ba cách giải còn lại, giao diện, script test và video là AI đề xuất và viết, em kiểm tra và góp ý qua nhiều vòng." |
| | "Ví dụ vấn đề gặp phải: bao hàm–loại trừ treo trình duyệt khi có 100 nghìn chốt → giới hạn k; đệ quy n = 1000 tràn stack → dùng ngăn xếp tường minh; nhân mod trong JavaScript vượt 2⁵³ → tách 16 bit." |
| | "Em không tin kết quả AI một cách mặc nhiên: mọi kết quả đều được so với một phương pháp độc lập — vét cạn, số nguyên lớn, công thức tổ hợp, và chạy tay — ví dụ em kiểm tra tay bước chốt #4 ra 4." |

## 8. Kết luận — 11:00 → 11:40

| Thao tác | Lời nói |
|---|---|
| Quay lại đầu trang demo | "Tóm lại: demo cho phép nhập dữ liệu, theo dõi từng bước của 4 thuật toán, xem kết quả và so sánh; bộ 103 testcase đều đạt." |
| | "Hạn chế: minh họa từng bước chỉ cho lưới ≤ 16×16, bao hàm–loại trừ giới hạn 4000 chốt. Hướng phát triển: lưới m×n, cho đi chéo, hoặc cho phép bị thổi tối đa t lần với QHĐ 3 chiều." |
| | "Em cảm ơn cô đã theo dõi." |

---

## Câu hỏi cô có thể hỏi — chuẩn bị sẵn

1. **Vì sao dp[i][j] = dp[i−1][j] + dp[i][j−1] đúng?** → Phân hoạch theo bước cuối: hai nhóm rời nhau, phủ hết; bỏ bước cuối là song ánh với tập đường tới ô trên/ô trái (quy tắc cộng).
2. **Vì sao lấy dư sau mỗi phép cộng vẫn đúng?** → (a+b) mod p = ((a mod p)+(b mod p)) mod p.
3. **Mảng 1 chiều sao không sai?** → Duyệt j tăng dần: dp[j] chưa ghi đè = giá trị hàng trên; dp[j−1] đã ghi đè = ô trái hàng hiện tại.
4. **Nếu KTX có chốt?** → dp[1] khởi tạo 1 nhưng gặp '*' gán 0 ngay ⇒ đáp án 0 (có test `02_bien/chot_tai_KTX`).
5. **Độ phức tạp vét cạn?** → Ω(số đường), xấu nhất ≈ C(2n−2, n−1) ~ 4ⁿ/√n.
6. **Khi nào dùng bao hàm–loại trừ?** → Lưới rất lớn (vd 10⁵×10⁵, không lập được bảng n²) nhưng ít chốt: Θ(n + k²).
7. **Đệ quy có nhớ khác bottom-up thế nào?** → Cùng công thức; top-down chỉ tính ô cần thiết (chốt dày thì rất nhanh) nhưng tốn ngăn xếp và Θ(n²) bộ nhớ.
8. **Đếm "thao tác" thế nào?** → Vét cạn & đệ quy: số lời gọi; bottom-up: số ô; bao hàm–loại trừ: số cặp chốt — đơn vị khác nhau nên chỉ so bậc tăng trưởng.

## Mẹo quay

- Nói chậm, **dừng 1–2 giây sau mỗi thao tác** để người xem kịp nhìn; dùng chuột chỉ đúng chỗ đang nói.
- Quay **từng phần riêng** (8 đoạn) rồi ghép — sai đoạn nào quay lại đoạn đó.
- Ở phần chạy từng bước, để tốc độ chậm (mức 3–4) khi giải thích, tăng nhanh khi chỉ muốn chạy hết.
- Sau khi quay: cắt khoảng lặng, kiểm tra âm lượng, xuất MP4 1080p, đặt vào `2_VideoDemo/` (có thể giữ `demo.mp4` hiện tại làm bản phụ).

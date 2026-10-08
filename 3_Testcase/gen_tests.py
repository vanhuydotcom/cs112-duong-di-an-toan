"""Sinh bộ testcase cho bài "Đường đi an toàn".

Mỗi test gồm <tên>.inp (đúng định dạng WeCode) và <tên>.out (đáp án).
Đáp án được tính bằng phương pháp ĐỘC LẬP với lời giải nộp bài:
  - QHĐ 2 chiều bằng số nguyên lớn của Python (không lấy dư giữa chừng), chỉ lấy dư ở cuối;
  - với n <= 8 còn đối chiếu thêm bằng cách liệt kê từng đường (vét cạn);
  - với bản đồ không có chốt còn đối chiếu với công thức C(2n-2, n-1).
Nhóm 06 (input không hợp lệ) có .out là thông báo lỗi mà hệ thống phải đưa ra.

Chạy: python3 3_Testcase/gen_tests.py   (sinh lại y hệt nhờ seed cố định)
"""
import json
import random
import shutil
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
MOD = 10**9 + 7
rng = random.Random(25730032)


# ---------------- đáp án độc lập ----------------
def exact_count(grid):
  n = len(grid)
  prev = [0] * n
  for i in range(n):
    cur = [0] * n
    for j in range(n):
      if grid[i][j] == "*":
        continue
      if i == 0 and j == 0:
        cur[j] = 1
      else:
        cur[j] = (prev[j] if i else 0) + (cur[j - 1] if j else 0)
    prev = cur
  return prev[n - 1]


def enumerate_paths(grid):
  n = len(grid)
  cnt, st = 0, [(0, 0)]
  while st:
    i, j = st.pop()
    if i >= n or j >= n or grid[i][j] == "*":
      continue
    if i == n - 1 and j == n - 1:
      cnt += 1
      continue
    st += [(i + 1, j), (i, j + 1)]
  return cnt


# ---------------- các kiểu bản đồ ----------------
def rand_grid(n, d, keep=True):
  g = [["*" if rng.random() < d else "." for _ in range(n)] for _ in range(n)]
  if keep:
    g[0][0] = g[n - 1][n - 1] = "."
  return ["".join(r) for r in g]


def empty(n):
  return ["." * n for _ in range(n)]


def anti_diagonal_wall(n, gap=None):
  """Chặn cả đường chéo phụ i+j = n-1 (mọi đường đều phải đi qua) — có thể chừa 1 khe."""
  g = [list("." * n) for _ in range(n)]
  for i in range(n):
    g[i][n - 1 - i] = "*"
  if gap is not None:
    g[gap][n - 1 - gap] = "."
  return ["".join(r) for r in g]


def corridor(n):
  """Chỉ còn đúng một đường: đi hết hàng 1 rồi đi hết cột n."""
  g = [list("*" * n) for _ in range(n)]
  for j in range(n):
    g[0][j] = "."
  for i in range(n):
    g[i][n - 1] = "."
  return ["".join(r) for r in g]


def staircase(n):
  """Bậc thang: chỉ đi được trên dải rộng 2 ô quanh đường chéo chính."""
  return ["".join("." if abs(i - j) <= 1 else "*" for j in range(n)) for i in range(n)]


def checkerboard(n, keep=True):
  g = [list("*" if (i + j) % 2 else "." for j in range(n)) for i in range(n)]
  if keep:
    g[0][0] = g[n - 1][n - 1] = "."
  return ["".join(r) for r in g]


def zigzag_maze(n):
  """Mê cung răng cưa: các vách ngang chừa khe xen kẽ hai đầu — nhiều ngõ cụt."""
  g = [list("." * n) for _ in range(n)]
  for i in range(2, n - 1, 3):
    for j in range(n):
      g[i][j] = "*"
    g[i][n - 1 if (i // 3) % 2 == 0 else 0] = "."
  return ["".join(r) for r in g]


def border_only(n):
  """Chốt ở toàn bộ phần bên trong, chỉ chừa viền — đúng 2 đường."""
  return ["".join("." if i in (0, n - 1) or j in (0, n - 1) else "*" for j in range(n)) for i in range(n)]


def blocked_row(n, r):
  g = empty(n)
  g[r] = "*" * n
  return g


def blocked_col(n, c):
  return ["." * c + "*" + "." * (n - c - 1) for _ in range(n)]


def set_cell(g, i, j, ch):
  row = list(g[i]); row[j] = ch; g[i] = "".join(row); return g


# ---------------- danh sách test ----------------
def build():
  T = {"01_thong_thuong": [], "02_bien": [], "03_nho": [], "04_lon": [], "05_dac_biet": [], "06_khong_hop_le": []}

  # 01 — trường hợp thông thường: n vừa, mật độ chốt thường gặp
  for k, (n, d) in enumerate([(5, .2), (7, .15), (8, .25), (10, .1), (10, .3), (15, .2), (20, .1), (20, .25), (30, .15),
                              (40, .2), (50, .1), (60, .3), (80, .2), (100, .15), (120, .25)]):
    T["01_thong_thuong"].append((f"n{n}_d{int(d*100)}", rand_grid(n, d), f"ngẫu nhiên n={n}, mật độ {int(d*100)}%"))

  # 02 — trường hợp biên
  T["02_bien"] += [
    ("n1_trong", ["."], "n = 1, ô trống: KTX trùng UIT ⇒ 1 đường"),
    ("n1_chot", ["*"], "n = 1, có chốt ⇒ 0"),
    ("chot_tai_KTX", set_cell(empty(5), 0, 0, "*"), "chốt ngay KTX ⇒ 0"),
    ("chot_tai_UIT", set_cell(empty(5), 4, 4, "*"), "chốt ngay UIT ⇒ 0"),
    ("chan_ca_hang", blocked_row(6, 3), "một hàng bị chặn hết ⇒ 0"),
    ("chan_ca_cot", blocked_col(6, 2), "một cột bị chặn hết ⇒ 0"),
    ("vach_cheo_kin", anti_diagonal_wall(7), "chặn cả đường chéo phụ ⇒ 0"),
    ("vach_cheo_1_khe", anti_diagonal_wall(7, gap=3), "đường chéo phụ chừa 1 khe ⇒ mọi đường qua khe"),
    ("hang_dau_chan", set_cell(set_cell(empty(4), 0, 1, "*"), 1, 0, "*"), "hai ô kề KTX đều có chốt ⇒ 0"),
    ("n1000_chot_KTX", set_cell(empty(1000), 0, 0, "*"), "n lớn nhất, chốt ngay KTX"),
    ("n1000_chot_UIT", set_cell(empty(1000), 999, 999, "*"), "n lớn nhất, chốt ngay UIT"),
  ]
  for mask in range(16):  # tất cả 16 bản đồ 2×2
    g = ["".join("*" if mask >> (2 * i + j) & 1 else "." for j in range(2)) for i in range(2)]
    T["02_bien"].append((f"n2_tatca_{mask:02d}", g, "vét hết mọi bản đồ 2×2"))

  # 03 — dữ liệu nhỏ: đối chiếu được bằng vét cạn
  for k in range(30):
    n = 3 + k % 6
    d = [0, .1, .2, .3, .45, .6][k % 6]
    T["03_nho"].append((f"nho_{k:02d}_n{n}", rand_grid(n, d, keep=k % 5 != 4), f"n={n}, mật độ {int(d*100)}%" + ("" if k % 5 != 4 else ", không giữ trống 2 đầu")))

  # 04 — dữ liệu lớn: chạm giới hạn n = 1000
  for n, d in [(1000, 0.0), (1000, .01), (1000, .05), (1000, .1), (1000, .2), (1000, .3), (1000, .45), (500, .1), (750, .05), (999, .15)]:
    T["04_lon"].append((f"n{n}_d{int(d*100)}", rand_grid(n, d), f"lớn: n={n}, mật độ {d*100:g}%"))

  # 05 — trường hợp đặc biệt
  T["05_dac_biet"] += [
    ("khong_chot_n10", empty(10), "không chốt ⇒ C(18,9)"),
    ("khong_chot_n20_vuot_mod", empty(20), "C(38,19) = 35 345 263 800 > 10⁹+7 ⇒ kiểm tra lấy dư"),
    ("khong_chot_n100", empty(100), "không chốt ⇒ C(198,99) mod p"),
    ("hanh_lang_n50", corridor(50), "chỉ còn đúng 1 đường"),
    ("vien_n30", border_only(30), "chỉ đi được trên viền ⇒ đúng 2 đường"),
    ("bac_thang_n40", staircase(40), "dải hẹp quanh đường chéo"),
    ("ban_co_n9", checkerboard(9), "bàn cờ ⇒ 0 (mọi bước đều vào ô chốt)"),
    ("me_cung_rang_cua_n31", zigzag_maze(31), "mê cung nhiều ngõ cụt"),
    ("dong_chot_1_khe_n200", anti_diagonal_wall(200, gap=100), "n=200, chỉ 1 khe qua đường chéo"),
    ("it_chot_n1000", rand_grid(1000, 0.0005), "n=1000 nhưng rất ít chốt (bao hàm–loại trừ có lợi)"),
  ]

  # 06 — input không hợp lệ (dành cho bộ kiểm tra của giao diện)
  T["06_khong_hop_le"] += [
    ("rong", "", "errEmpty"),
    ("n_khong_phai_so", "abc\n...\n", "errNNotInt"),
    ("n_am", "-3\n", "errNNotInt"),
    ("n_bang_0", "0\n", "errNRange"),
    ("n_vuot_1000", "1001\n", "errNRange"),
    ("thieu_dong", "3\n...\n...\n", "errRowCount"),
    ("thua_dong", "2\n..\n..\n..\n", "errRowCount"),
    ("dong_ngan", "3\n...\n..\n...\n", "errRowLen"),
    ("dong_dai", "3\n...\n....\n...\n", "errRowLen"),
    ("ky_tu_la", "3\n...\n.x.\n...\n", "errBadChar"),
    ("so_thuc", "2.5\n..\n..\n", "errNNotInt"),
  ]
  return T


def main():
  T = build()
  manifest = []
  for group, cases in T.items():
    d = HERE / group
    if d.exists():
      shutil.rmtree(d)
    d.mkdir()
    for name, grid, note in cases:
      if group == "06_khong_hop_le":
        (d / f"{name}.inp").write_text(grid)
        (d / f"{name}.out").write_text(f"INVALID {note}\n")
        manifest.append({"group": group, "name": name, "n": None, "k": None, "expected": f"INVALID {note}", "note": note})
        continue
      n = len(grid)
      ex = exact_count(grid)
      if n <= 8:
        assert enumerate_paths(grid) == ex, name
      if all("*" not in r for r in grid):
        assert ex == comb(2 * n - 2, n - 1), name
      ans = ex % MOD
      (d / f"{name}.inp").write_text(f"{n}\n" + "\n".join(grid) + "\n")
      (d / f"{name}.out").write_text(f"{ans}\n")
      k = sum(r.count("*") for r in grid)
      manifest.append({"group": group, "name": name, "n": n, "k": k, "expected": ans,
                       "exact_digits": len(str(ex)), "note": note})
  (HERE / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1))
  by = {}
  for m in manifest:
    by[m["group"]] = by.get(m["group"], 0) + 1
  print("Đã sinh", len(manifest), "test:", by)


if __name__ == "__main__":
  main()

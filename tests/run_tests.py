"""Kiểm chứng lời giải: so sánh với vét cạn (đệ quy liệt kê mọi đường) trên bản đồ nhỏ,
và chạy cả lời giải Python lẫn lõi JS của web app trên cùng bộ test."""
import random
import subprocess
import sys
import time
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MOD = 10**9 + 7


def brute(grid):
  n = len(grid)

  @lru_cache(None)
  def go(i, j):  # số đường từ (i,j) tới (n-1,n-1), liệt kê đủ 2 hướng
    if i >= n or j >= n or grid[i][j] == "*":
      return 0
    if i == n - 1 and j == n - 1:
      return 1
    return go(i + 1, j) + go(i, j + 1)

  return go(0, 0) % MOD


def enumerate_paths(grid):  # vét cạn thật sự (không nhớ), chỉ dùng cho n <= 6
  n = len(grid)
  cnt = 0
  stack = [(0, 0)]
  while stack:
    i, j = stack.pop()
    if i >= n or j >= n or grid[i][j] == "*":
      continue
    if i == n - 1 and j == n - 1:
      cnt += 1
      continue
    stack += [(i + 1, j), (i, j + 1)]
  return cnt


def run(cmd, text):
  return subprocess.run(cmd, input=text, capture_output=True, text=True, cwd=ROOT).stdout.strip()


def to_text(grid):
  return f"{len(grid)}\n" + "\n".join(grid) + "\n"


def main():
  random.seed(112)
  cases = []
  # bản đồ trong đề (hình minh hoạ)
  cases.append(["....", ".*..", "...*", "*..."])
  cases += [["."], ["*"], ["..", ".."], ["*.", ".."], ["..", ".*"], [".*", "*."]]
  for _ in range(300):
    n = random.randint(1, 6)
    d = random.choice([0, 0.1, 0.25, 0.4, 0.7])
    cases.append(["".join("*" if random.random() < d else "." for _ in range(n)) for _ in range(n)])

  fails = 0
  for g in cases:
    exp = enumerate_paths(g) % MOD
    assert exp == brute(g)
    t = to_text(g)
    py = run([sys.executable, "solution/safe_path.py"], t)
    js = run(["node", "tests/js_count.js"], t)
    if not (str(exp) == py == js):
      fails += 1
      print("FAIL", g, exp, py, js)
  print(f"[1] Đối chiếu vét cạn: {len(cases) - fails}/{len(cases)} test đúng (Python + JS)")

  # test lớn: kiểm tra phép lấy dư và thời gian, so sánh với DP BigInt độc lập
  for n, d in [(40, 0.0), (300, 0.05), (1000, 0.0), (1000, 0.1)]:
    g = ["".join("*" if random.random() < d else "." for _ in range(n)) for _ in range(n)]
    g[0] = "." + g[0][1:]
    exp = brute(g) if n <= 300 else None
    t = to_text(g)
    t0 = time.time(); py = run([sys.executable, "solution/safe_path.py"], t); tp = time.time() - t0
    t0 = time.time(); js = run(["node", "tests/js_count.js"], t); tj = time.time() - t0
    ok = py == js and (exp is None or str(exp) == py)
    fails += not ok
    print(f"[2] n={n:4d} mật độ={d:.2f}: python={py} ({tp:.2f}s)  js={js} ({tj:.2f}s)  {'OK' if ok else 'FAIL'}")

  # n=1000 không chốt: đáp án = C(1998, 999) mod p
  from math import comb
  print("[3] C(1998,999) mod p =", comb(1998, 999) % MOD)

  # input sai phải bị bắt
  bad = ["", "abc\n", "0\n", "1001\n", "2\n..\n", "2\n..\n.x\n", "2\n...\n..\n"]
  rej = sum(run(["node", "tests/js_count.js"], b).startswith("INVALID") for b in bad)
  print(f"[4] Validate: {rej}/{len(bad)} input sai bị từ chối")
  fails += rej != len(bad)
  print("TẤT CẢ ĐẠT" if fails == 0 else f"CÓ {fails} LỖI")
  sys.exit(1 if fails else 0)


if __name__ == "__main__":
  main()

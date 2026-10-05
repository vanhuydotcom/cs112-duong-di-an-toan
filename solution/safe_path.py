import sys


def solve():
  input_line = sys.stdin.readline

  line = input_line()
  while not line.strip():
    line = input_line()
  n = int(line.strip())

  MOD = 10**9 + 7
  dp = [0] * n
  dp[0] = 1

  for _ in range(n):
    row_line = input_line()
    while not row_line.strip():
      row_line = input_line()
    row = "".join(row_line.split())

    for j in range(n):
      if row[j] == "*":
        dp[j] = 0
      elif j > 0:
        val = dp[j] + dp[j - 1]
        dp[j] = val if val < MOD else val - MOD

  print(dp[n - 1])


if __name__ == "__main__":
  solve()

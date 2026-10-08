"""Chạy toàn bộ testcase:
  (a) lời giải nộp WeCode (1_SourceCode/solution/safe_path.py), so khớp từng ký tự với .out;
  (b) 4 thuật toán của giao diện web (qua run_js.js);
  (c) nhóm 06: bộ kiểm tra input của giao diện phải báo đúng loại lỗi.
Xuất ket_qua/ket_qua.csv và ket_qua/tom_tat.md. Chạy: python3 3_Testcase/run_tests.py"""
import csv
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOL = ROOT / "1_SourceCode" / "solution" / "safe_path.py"
ALGOS = [("brute", "Vét cạn"), ("memo", "Đệ quy có nhớ"), ("dp", "QHĐ bottom-up"), ("ie", "Bao hàm–loại trừ")]
GROUPS = {"01_thong_thuong": "Thông thường", "02_bien": "Biên", "03_nho": "Dữ liệu nhỏ", "04_lon": "Dữ liệu lớn",
          "05_dac_biet": "Đặc biệt", "06_khong_hop_le": "Không hợp lệ"}


def main():
  man = json.loads((HERE / "manifest.json").read_text())
  js = {(r["group"], r["name"]): r for r in json.loads(subprocess.run(["node", str(HERE / "run_js.js")], capture_output=True, text=True, check=True).stdout)}
  rows, fails = [], []
  for m in man:
    g, name = m["group"], m["name"]
    inp = (HERE / g / f"{name}.inp").read_text()
    exp = (HERE / g / f"{name}.out").read_text().strip()
    r = js[(g, name)]
    row = {"nhom": g, "test": name, "n": m["n"] or "", "so_chot": m["k"] if m["k"] is not None else "", "dap_an": exp}
    if g == "06_khong_hop_le":
      ok = r.get("invalid") == exp.split()[1]
      row.update({"web_validate": r.get("invalid"), "ket_luan": "ĐẠT" if ok else "SAI"})
      if not ok: fails.append((g, name, "validate", r.get("invalid")))
      rows.append(row); continue
    t0 = time.perf_counter()
    py = subprocess.run([sys.executable, str(SOL)], input=inp, capture_output=True, text=True).stdout.strip()
    row["python"] = py; row["python_ms"] = round((time.perf_counter() - t0) * 1000, 1)
    ok = py == exp
    if not ok: fails.append((g, name, "python", py))
    for k, _ in ALGOS:
      a = r[k]
      if a["aborted"]:
        row[k] = "bỏ qua"
      else:
        row[k] = a["value"]
        if str(a["value"]) != exp:
          ok = False; fails.append((g, name, k, a["value"]))
      row[f"{k}_ops"] = a["ops"]; row[f"{k}_ms"] = round(a["ms"], 3)
    row["ket_luan"] = "ĐẠT" if ok else "SAI"
    rows.append(row)

  outd = HERE / "ket_qua"; outd.mkdir(exist_ok=True)
  keys = sorted({k for r in rows for k in r}, key=lambda k: list(rows[0].keys()).index(k) if k in rows[0] else 99)
  with open(outd / "ket_qua.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(rows)

  # tóm tắt theo nhóm
  lines = ["| Nhóm | Số test | n | Đạt | Vét cạn chạy được | Bao hàm–loại trừ chạy được | Python (ms, max) |", "|---|---|---|---|---|---|---|"]
  for g, label in GROUPS.items():
    rs = [r for r in rows if r["nhom"] == g]
    ns = [r["n"] for r in rs if r["n"] != ""]
    rng = f"{min(ns)}–{max(ns)}" if ns else "—"
    passed = sum(r["ket_luan"] == "ĐẠT" for r in rs)
    if g == "06_khong_hop_le":
      lines.append(f"| {label} | {len(rs)} | — | {passed}/{len(rs)} | — | — | — |"); continue
    b = sum(r["brute"] != "bỏ qua" for r in rs); ie = sum(r["ie"] != "bỏ qua" for r in rs)
    lines.append(f"| {label} | {len(rs)} | {rng} | {passed}/{len(rs)} | {b}/{len(rs)} | {ie}/{len(rs)} | {max(r['python_ms'] for r in rs):.0f} |")
  big = [r for r in rows if r["nhom"] == "04_lon"]
  lines += ["", "Dữ liệu lớn — thời gian (ms) và số thao tác:", "",
            "| Test | k (chốt) | Python | Đệ quy có nhớ | QHĐ bottom-up | Bao hàm–loại trừ |", "|---|---|---|---|---|---|"]
  for r in big:
    ie = "bỏ qua" if r["ie"] == "bỏ qua" else f"{r['ie_ms']:.1f} ({r['ie_ops']:.2e})"
    lines.append(f"| {r['test']} | {r['so_chot']} | {r['python_ms']:.0f} | {r['memo_ms']:.1f} | {r['dp_ms']:.1f} | {ie} |")
  total = len(rows); passed = sum(r["ket_luan"] == "ĐẠT" for r in rows)
  lines.insert(0, f"**Tổng: {passed}/{total} test ĐẠT.**\n")
  (outd / "tom_tat.md").write_text("\n".join(lines) + "\n")
  print("\n".join(lines))
  for f in fails: print("SAI:", f)
  sys.exit(1 if fails else 0)


if __name__ == "__main__":
  main()

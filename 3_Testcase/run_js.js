// Chạy 4 thuật toán của giao diện web (1_SourceCode/app/core.js) trên toàn bộ testcase, in kết quả dạng JSON.
const fs = require('fs'), path = require('path');
const S = require('../1_SourceCode/app/core.js');
const man = JSON.parse(fs.readFileSync(path.join(__dirname, 'manifest.json'), 'utf8'));
const algos = { brute: g => S.algoBrute(g, 5e7), memo: S.algoMemo, dp: S.algoBottomUp, ie: g => S.algoInclusion(g, 4000) };
const out = [];
for (const m of man) {
  const text = fs.readFileSync(path.join(__dirname, m.group, m.name + '.inp'), 'utf8');
  const p = S.parseInput(text);
  const row = { group: m.group, name: m.name };
  if (!p.ok) { row.invalid = p.errors[0].key; out.push(row); continue; }
  for (const [k, f] of Object.entries(algos)) {
    const t0 = process.hrtime.bigint();
    const r = f(p.grid);
    const ms = Number(process.hrtime.bigint() - t0) / 1e6;
    row[k] = { value: r.value, ops: r.ops, ms, aborted: !!r.aborted };
  }
  out.push(row);
}
console.log(JSON.stringify(out));

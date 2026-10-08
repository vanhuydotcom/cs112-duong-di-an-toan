// Sinh các bảng LaTeX cho chương "Ví dụ minh họa" từ chính lõi thuật toán của demo (đảm bảo report khớp demo).
const S = require('../1_SourceCode/app/core.js');
const fs = require('fs');
const text = '6\n......\n.*....\n...*..\n*.....\n..*...\n......';
const g = S.parseInput(text).grid, n = g.length;
let out = '';
// 1) bản đồ
out += '\\newcommand{\\ExMap}{\\begin{tabular}{c|' + 'c'.repeat(n) + '}\n & ' + [...Array(n)].map((_, j) => j + 1).join(' & ') + '\\\\\\hline\n';
for (let i = 0; i < n; i++) out += (i + 1) + ' & ' + g[i].map((b, j) => b ? '\\textbf{*}' : (i === 0 && j === 0 ? 'KTX' : i === n - 1 && j === n - 1 ? 'UIT' : '.')).join(' & ') + '\\\\\n';
out += '\\end{tabular}}\n';
// 2) bảng dp 2 chiều
const t = S.fullTable(g, true);
out += '\\newcommand{\\ExTable}{\\begin{tabular}{c|' + 'c'.repeat(n) + '}\n$dp$ & ' + [...Array(n)].map((_, j) => j + 1).join(' & ') + '\\\\\\hline\n';
for (let i = 0; i < n; i++) out += (i + 1) + ' & ' + t[i].map((v, j) => g[i][j] ? '\\cellcolor{red!12}0' : (i === n - 1 && j === n - 1 ? '\\cellcolor{yellow!35}\\textbf{' + v + '}' : String(v))).join(' & ') + '\\\\\n';
out += '\\end{tabular}}\n';
// 3) mảng 1 chiều sau mỗi hàng + các thao tác
out += '\\newcommand{\\ExRows}{\\begin{longtable}{>{\\centering\\arraybackslash}p{0.8cm} >{\\raggedright\\arraybackslash}p{9.2cm} >{\\centering\\arraybackslash}p{4.3cm}}\n\\toprule\nHàng & Các thao tác trên mảng $dp[1..6]$ & $dp$ sau hàng\\\\\\midrule\\endhead\n';
out += '-- & Khởi tạo & $[1,0,0,0,0,0]$\\\\\\midrule\n';
for (let i = 0; i < n; i++) {
  const ops = [];
  for (let j = 0; j < n; j++) {
    if (g[i][j]) ops.push(`$dp[${j + 1}]\\leftarrow 0$ (chốt)`);
    else if (j === 0) ops.push(i === 0 ? '$dp[1]=1$ (KTX)' : `$dp[1]$ giữ ${t[i][0]}`);
    else ops.push(`$dp[${j + 1}]\\leftarrow ${t[i - 1] ? t[i - 1][j] : 0}+${t[i][j - 1]}=${t[i][j]}$`);
  }
  out += `${i + 1} & ${ops.join('; ')} & $[${t[i].join(',')}]$\\\\\\midrule\n`;
}
out += '\\bottomrule\\end{longtable}}\n';
// 4) bao hàm – loại trừ
const ie = S.traceInclusion(g);
out += '\\newcommand{\\ExIE}{\\begin{longtable}{c c >{\\raggedright\\arraybackslash}p{9.6cm} c}\n\\toprule\nBước & Điểm & Công thức & $g$\\\\\\midrule\\endhead\n';
ie.events.forEach((e, k) => {
  const [a, b] = e.p;
  const terms = e.terms.map(x => { const q = ie.pts[x.q]; return `g_{${x.q + 1}}\\cdot\\binom{${a - q[0] + b - q[1]}}{${a - q[0]}}`; });
  const nums = e.terms.map(x => `${x.gq}\\cdot ${x.w}`);
  const name = e.isEnd ? `UIT (${a + 1},${b + 1})` : `\\#${k + 1}\\,(${a + 1},${b + 1})`;
  out += `${k + 1} & ${name} & $\\binom{${a + b}}{${a}}${terms.map(x => ' - ' + x).join('')} = ${e.base}${nums.map(x => ' - ' + x).join('')}$ & ${e.isEnd ? '\\textbf{' + e.g + '}' : e.g}\\\\\n`;
});
out += '\\bottomrule\\end{longtable}}\n';
// 5) thống kê 4 cách trên ví dụ
const r = { brute: S.algoBrute(g), memo: S.algoMemo(g), dp: S.algoBottomUp(g), ie: S.algoInclusion(g) };
const tm = S.traceMemo(g).events;
const hits = tm.filter(e => e.t === 'hit').length, calls = tm.filter(e => e.t !== 'ret').length;
out += `\\newcommand{\\ExOpsBrute}{${r.brute.ops}}\\newcommand{\\ExOpsMemo}{${r.memo.ops}}\\newcommand{\\ExOpsDp}{${r.dp.ops}}\\newcommand{\\ExOpsIe}{${r.ie.ops}}\\newcommand{\\ExHits}{${hits}}\\newcommand{\\ExCalls}{${calls}}\\newcommand{\\ExDepth}{${r.memo.maxDepth}}\n`;
fs.writeFileSync(__dirname + '/tables.tex', out);
console.log(r, hits, calls);

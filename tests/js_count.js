// Đọc input từ stdin, in kết quả bằng lõi JS của giao diện web.
const core = require('../app/core.js');
const text = require('fs').readFileSync(0, 'utf8');
const p = core.parseInput(text);
if (!p.ok) { console.log('INVALID ' + JSON.stringify(p.errors)); process.exit(1); }
console.log(core.countPaths(p.grid));

// Lõi thuật toán "Đường đi an toàn" — dùng chung cho trình duyệt và Node (kiểm thử).
(function (root) {
  const MOD = 1000000007;
  const MAX_N = 1000;

  // Đọc và kiểm tra input theo đúng định dạng WeCode.
  // Trả về { ok, n, grid, errors: [{key, params}] } — key là mã thông báo để giao diện dịch song ngữ.
  function parseInput(text) {
    const errors = [];
    const lines = String(text).replace(/\r/g, '').split('\n')
      .map((l, idx) => ({ raw: l, no: idx + 1 }))
      .filter(l => l.raw.trim() !== '');
    if (lines.length === 0) return { ok: false, errors: [{ key: 'errEmpty' }] };

    const first = lines[0].raw.trim();
    if (!/^\d+$/.test(first)) {
      return { ok: false, errors: [{ key: 'errNNotInt', params: { line: lines[0].no, value: first } }] };
    }
    const n = parseInt(first, 10);
    if (n < 1 || n > MAX_N) {
      return { ok: false, errors: [{ key: 'errNRange', params: { n, max: MAX_N } }] };
    }

    const rows = lines.slice(1);
    if (rows.length !== n) errors.push({ key: 'errRowCount', params: { n, got: rows.length } });

    const grid = [];
    for (let i = 0; i < Math.min(rows.length, n); i++) {
      const row = rows[i].raw.replace(/\s+/g, '');
      if (row.length !== n) {
        errors.push({ key: 'errRowLen', params: { line: rows[i].no, row: i + 1, n, got: row.length } });
      }
      const bad = row.search(/[^.*]/);
      if (bad !== -1) {
        errors.push({ key: 'errBadChar', params: { line: rows[i].no, row: i + 1, col: bad + 1, ch: row[bad] } });
      }
      grid.push(row);
      if (errors.length > 8) break; // tránh tràn danh sách lỗi
    }
    if (errors.length) return { ok: false, n, errors };
    return { ok: true, n, grid: grid.map(r => r.split('').map(c => c === '*')), errors: [] };
  }

  // Lời giải chính: quy hoạch động 1 chiều, O(n^2) thời gian, O(n) bộ nhớ.
  function countPaths(grid) {
    const n = grid.length;
    const dp = new Array(n).fill(0);
    dp[0] = 1;
    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n; j++) {
        if (grid[i][j]) dp[j] = 0;
        else if (j > 0) {
          const v = dp[j] + dp[j - 1];
          dp[j] = v >= MOD ? v - MOD : v;
        }
      }
    }
    return dp[n - 1];
  }

  // Bảng DP 2 chiều đầy đủ (dùng cho minh họa). exact=true dùng BigInt để cho thấy số thật trước khi lấy dư.
  function fullTable(grid, exact) {
    const n = grid.length;
    const zero = exact ? 0n : 0, one = exact ? 1n : 1;
    const t = Array.from({ length: n }, () => new Array(n).fill(zero));
    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n; j++) {
        if (grid[i][j]) { t[i][j] = zero; continue; }
        if (i === 0 && j === 0) { t[i][j] = one; continue; }
        const up = i > 0 ? t[i - 1][j] : zero;
        const left = j > 0 ? t[i][j - 1] : zero;
        t[i][j] = exact ? up + left : (up + left) % MOD;
      }
    }
    return t;
  }

  // Danh sách các bước để hoạt hình hóa: mỗi ô (i,j) theo thứ tự hàng → cột.
  function buildSteps(grid) {
    const n = grid.length;
    const t = fullTable(grid, true);
    const steps = [];
    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n; j++) {
        let kind;
        if (grid[i][j]) kind = 'blocked';
        else if (i === 0 && j === 0) kind = 'start';
        else kind = 'sum';
        steps.push({
          i, j, kind,
          up: i > 0 ? t[i - 1][j] : null,
          left: j > 0 ? t[i][j - 1] : null,
          value: t[i][j],
        });
      }
    }
    return { steps, table: t };
  }

  // Ô "hữu ích": vừa đến được từ (0,0) vừa đi tiếp được tới (n-1,n-1) — nằm trên ít nhất một đường an toàn.
  function usefulCells(grid) {
    const n = grid.length;
    const f = fullTable(grid, true);
    const g = Array.from({ length: n }, () => new Array(n).fill(0n));
    for (let i = n - 1; i >= 0; i--) {
      for (let j = n - 1; j >= 0; j--) {
        if (grid[i][j]) continue;
        if (i === n - 1 && j === n - 1) { g[i][j] = 1n; continue; }
        g[i][j] = (i + 1 < n ? g[i + 1][j] : 0n) + (j + 1 < n ? g[i][j + 1] : 0n);
      }
    }
    return f.map((row, i) => row.map((v, j) => v > 0n && g[i][j] > 0n));
  }

  // Lấy ngẫu nhiên một đường đi an toàn (đồng đều trong tất cả các đường) bằng cách đi ngược từ đích.
  function samplePath(grid, rng) {
    const n = grid.length;
    const t = fullTable(grid, true);
    if (t[n - 1][n - 1] === 0n) return null;
    const path = [[n - 1, n - 1]];
    let i = n - 1, j = n - 1;
    const rand = rng || Math.random;
    while (i > 0 || j > 0) {
      const up = i > 0 ? t[i - 1][j] : 0n;
      const left = j > 0 ? t[i][j - 1] : 0n;
      // chọn hướng với xác suất tỉ lệ với số đường — dùng số thực xấp xỉ là đủ cho minh họa
      const pUp = Number(up) / (Number(up) + Number(left));
      if (left === 0n || (up > 0n && rand() < pUp)) i--; else j--;
      path.push([i, j]);
    }
    return path.reverse();
  }

  // Sinh bản đồ ngẫu nhiên; seed để tái lập được.
  function mulberry32(seed) {
    let a = seed >>> 0;
    return function () {
      a = (a + 0x6D2B79F5) >>> 0;
      let t = a;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function randomGrid(n, density, seed, keepEnds) {
    const rng = mulberry32(seed);
    const g = Array.from({ length: n }, () => Array.from({ length: n }, () => rng() < density));
    if (keepEnds) { g[0][0] = false; g[n - 1][n - 1] = false; }
    return g;
  }

  function gridToText(grid) {
    return grid.length + '\n' + grid.map(r => r.map(b => (b ? '*' : '.')).join('')).join('\n');
  }

  const api = { MOD, MAX_N, parseInput, countPaths, fullTable, buildSteps, usefulCells, samplePath, randomGrid, gridToText, mulberry32 };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.SafePath = api;
})(typeof window !== 'undefined' ? window : globalThis);

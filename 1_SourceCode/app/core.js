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

  // ======================================================================
  // BỐN CÁCH GIẢI ĐỂ SO SÁNH. Mỗi hàm trả về { value, ops, ... }:
  //   value = đáp án mod 1e9+7, ops = số "thao tác cơ bản" đặc trưng của cách giải.
  // ======================================================================

  // (1) Vét cạn quay lui: liệt kê từng đường đi bằng DFS. ops = số lời gọi (số lần thăm ô).
  //     Bị chặn ở `cap` lời gọi vì số đường tăng theo hàm mũ.
  function algoBrute(grid, cap) {
    const n = grid.length;
    cap = cap || 2e7;
    if (grid[0][0]) return { value: 0, ops: 1, aborted: false };
    let ops = 0, cnt = 0;
    const si = new Int16Array(4 * n + 4), sj = new Int16Array(4 * n + 4);
    let top = 0; si[0] = 0; sj[0] = 0; top = 1;
    while (top) {
      top--; const i = si[top], j = sj[top];
      ops++;
      if (ops > cap) return { value: null, ops, aborted: true };
      if (i === n - 1 && j === n - 1) { cnt++; if (cnt >= MOD) cnt -= MOD; continue; }
      if (j + 1 < n && !grid[i][j + 1]) { si[top] = i; sj[top] = j + 1; top++; }
      if (i + 1 < n && !grid[i + 1][j]) { si[top] = i + 1; sj[top] = j; top++; }
    }
    return { value: cnt, ops, aborted: false };
  }

  // (2) Đệ quy có nhớ (top-down): f(i,j) = f(i-1,j) + f(i,j-1), lưu kết quả đã tính.
  //     Cài bằng ngăn xếp tường minh để n = 1000 không tràn stack. ops = số lời gọi f.
  function algoMemo(grid) {
    const n = grid.length;
    const memo = new Int32Array(n * n).fill(-1);
    let ops = 0, maxDepth = 0;
    // khung: [i, j, giai đoạn]; giai đoạn 0 = vừa gọi, 1 = đã gọi f(i-1,j), 2 = đã gọi f(i,j-1)
    const st = [[n - 1, n - 1, 0]];
    let ret = 0, acc = [];
    const f0 = (i, j) => (i < 0 || j < 0 || grid[i][j] ? 0 : (i === 0 && j === 0 ? 1 : -1));
    while (st.length) {
      if (st.length > maxDepth) maxDepth = st.length;
      const fr = st[st.length - 1];
      const [i, j, ph] = fr;
      if (ph === 0) {
        ops++;
        const b = f0(i, j);
        if (b >= 0) { ret = b; st.pop(); continue; }
        if (memo[i * n + j] >= 0) { ret = memo[i * n + j]; st.pop(); continue; }
        fr[2] = 1; acc[st.length - 1] = 0; st.push([i - 1, j, 0]);
      } else if (ph === 1) {
        acc[st.length - 1] = ret; fr[2] = 2; st.push([i, j - 1, 0]);
      } else {
        let v = acc[st.length - 1] + ret; if (v >= MOD) v -= MOD;
        memo[i * n + j] = v; ret = v; st.pop();
      }
    }
    return { value: ret, ops, maxDepth };
  }

  // (3) QHĐ bottom-up mảng 1 chiều — chính là countPaths. ops = số ô được xử lý = n².
  function algoBottomUp(grid) {
    const n = grid.length;
    return { value: countPaths(grid), ops: n * n };
  }

  // (4) Tổ hợp + bao hàm – loại trừ trên các chốt (kỹ thuật bài Codeforces 559C).
  //     Không có chốt: số đường từ (a,b) tới (c,d) là C((c-a)+(d-b), c-a).
  //     Sắp các chốt theo (hàng, cột); g[k] = số đường từ KTX tới chốt k mà KHÔNG đi qua chốt nào trước đó:
  //       g[k] = C(KTX→k) − Σ_{q trước k} g[q]·C(q→k).  Coi UIT là "điểm cuối", đáp án = g[UIT].
  //     Độ phức tạp O(n + k²) với k = số chốt — rất nhanh khi ít chốt, rất chậm khi nhiều chốt.
  function mulmod(a, b) { return ((a * (b >>> 16)) % MOD * 65536 + a * (b & 65535)) % MOD; }
  function powmod(a, e) { let r = 1; a %= MOD; while (e > 0) { if (e & 1) r = mulmod(r, a); a = mulmod(a, a); e = Math.floor(e / 2); } return r; }
  let FACT = [1], IFACT = [1];
  function ensureFact(m) {
    if (FACT.length > m) return;
    const f = new Array(m + 1); f[0] = 1;
    for (let i = 1; i <= m; i++) f[i] = mulmod(f[i - 1], i);
    const fi = new Array(m + 1); fi[m] = powmod(f[m], MOD - 2);
    for (let i = m; i > 0; i--) fi[i - 1] = mulmod(fi[i], i);
    FACT = f; IFACT = fi;
  }
  function binom(a, b) { return b < 0 || b > a ? 0 : mulmod(mulmod(FACT[a], IFACT[b]), IFACT[a - b]); }
  function ways(p, q) { // số đường không ràng buộc từ p tới q (chỉ phải/xuống)
    const di = q[0] - p[0], dj = q[1] - p[1];
    return di < 0 || dj < 0 ? 0 : binom(di + dj, di);
  }
  function algoInclusion(grid, kCap) {
    const n = grid.length;
    kCap = kCap || 4000;
    if (grid[0][0] || grid[n - 1][n - 1]) return { value: 0, ops: 1, k: null };
    const pts = [];
    for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) if (grid[i][j]) pts.push([i, j]);
    if (pts.length > kCap) return { value: null, ops: pts.length * pts.length / 2, k: pts.length, aborted: true };
    ensureFact(2 * n);
    pts.push([n - 1, n - 1]);
    const g = new Array(pts.length);
    let ops = 2 * n;
    for (let k = 0; k < pts.length; k++) {
      let v = ways([0, 0], pts[k]);
      for (let q = 0; q < k; q++) {
        ops++;
        if (pts[q][1] > pts[k][1]) continue; // q ở bên phải k thì không thể đi từ q tới k
        v -= mulmod(g[q], ways(pts[q], pts[k])); if (v < 0) v += MOD;
      }
      g[k] = v;
    }
    return { value: g[pts.length - 1], ops, k: pts.length - 1 };
  }

  // ---------- Dấu vết từng bước cho minh họa (chỉ dùng với lưới nhỏ) ----------

  // Đệ quy có nhớ: các sự kiện gọi / trả về, kèm ngăn xếp tại thời điểm đó.
  function traceMemo(grid, maxEvents) {
    const n = grid.length;
    maxEvents = maxEvents || 6000;
    const memo = new Map();
    const ev = [];
    const stack = [];
    const val = (i, j) => memo.get(i * n + j);
    function f(i, j, from) {
      if (ev.length > maxEvents) return 0n;
      if (i < 0 || j < 0) { ev.push({ t: 'out', i, j, from, stack: stack.slice() }); return 0n; }
      if (grid[i][j]) { ev.push({ t: 'block', i, j, stack: stack.slice() }); return 0n; }
      if (i === 0 && j === 0) { ev.push({ t: 'base', i, j, stack: stack.slice() }); return 1n; }
      if (memo.has(i * n + j)) { ev.push({ t: 'hit', i, j, v: val(i, j), stack: stack.slice() }); return val(i, j); }
      stack.push([i, j]);
      ev.push({ t: 'call', i, j, stack: stack.slice() });
      const up = f(i - 1, j, 'up');
      const left = f(i, j - 1, 'left');
      const v = up + left;
      memo.set(i * n + j, v);
      ev.push({ t: 'ret', i, j, up, left, v, stack: stack.slice() });
      stack.pop();
      return v;
    }
    f(n - 1, n - 1);
    // ảnh chụp bảng memo sau mỗi sự kiện được dựng lại khi vẽ (từ các sự kiện 'ret' trước đó)
    return { events: ev, truncated: ev.length > maxEvents };
  }

  // Vét cạn: các bước tiến/lùi của DFS, kèm đường đi hiện tại và số đường đã tìm được.
  function traceBrute(grid, maxEvents) {
    const n = grid.length;
    maxEvents = maxEvents || 4000;
    const ev = [];
    const path = [];
    let found = 0, calls = 0, stop = false;
    function go(i, j) {
      if (stop) return;
      calls++;
      if (i >= n || j >= n) return;
      if (grid[i][j]) { ev.push({ t: 'block', i, j, path: path.slice(), found, calls }); return; }
      path.push([i, j]);
      if (i === n - 1 && j === n - 1) {
        found++;
        ev.push({ t: 'found', i, j, path: path.slice(), found, calls });
      } else {
        ev.push({ t: 'move', i, j, path: path.slice(), found, calls });
        go(i, j + 1);
        go(i + 1, j);
      }
      path.pop();
      if (ev.length >= maxEvents) stop = true;
    }
    go(0, 0);
    return { events: ev, truncated: stop };
  }

  // Bao hàm – loại trừ: một bước cho mỗi chốt (theo thứ tự đã sắp) và bước cuối cho UIT.
  function traceInclusion(grid) {
    const n = grid.length;
    ensureFact(2 * n);
    const pts = [];
    for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) if (grid[i][j]) pts.push([i, j]);
    const startBlocked = grid[0][0];
    pts.push([n - 1, n - 1]);
    const g = [];
    const ev = [];
    for (let k = 0; k < pts.length; k++) {
      const base = ways([0, 0], pts[k]);
      const terms = [];
      let v = base;
      for (let q = 0; q < k; q++) {
        const w = ways(pts[q], pts[k]);
        if (w === 0) continue;
        const prod = mulmod(g[q], w);
        terms.push({ q, gq: g[q], w, prod });
        v -= prod; if (v < 0) v += MOD;
      }
      if (startBlocked) v = 0;
      g.push(v);
      ev.push({ k, p: pts[k], base, terms, g: v, isEnd: k === pts.length - 1 });
    }
    return { pts, events: ev };
  }

  const api = { MOD, MAX_N, parseInput, countPaths, fullTable, buildSteps, usefulCells, samplePath, randomGrid, gridToText, mulberry32,
    algoBrute, algoMemo, algoBottomUp, algoInclusion, traceMemo, traceBrute, traceInclusion, binom, ensureFact };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.SafePath = api;
})(typeof window !== 'undefined' ? window : globalThis);

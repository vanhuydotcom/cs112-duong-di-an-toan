"""Video demo KHÔNG lồng tiếng: người xem hiểu nhờ
  - thẻ tiêu đề chia chương,
  - vùng đang nói tới được "rọi đèn" (phần còn lại tối đi, viền vàng),
  - phụ đề ngắn, hiển thị đủ lâu theo độ dài chữ (~17 ký tự/giây; muốn xem kỹ thì tạm dừng video).
Chạy: python3 video/make_silent_video.py  →  video/demo_khong_tieng.mp4"""
import json
import subprocess
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

from make_video import HERE, PORT, TMP, W, H, serve

G6 = "6\\n......\\n.*....\\n...*..\\n*.....\\n..*...\\n......"

# Mỗi cảnh: ("card", tiêu đề, dòng phụ) hoặc (phụ đề, JS chạy trước, phần tử cuộn tới, JS trả về phần tử được rọi, giây chờ thêm)
SCENES = [
  ("card", "Đường đi an toàn", "Demo trực quan hóa Quy hoạch động · CS112 · Đinh Văn Huy – 25730032"),
  ("Bài toán: đi từ KTX 🏠 (góc trái trên) tới UIT 🏫 (góc phải dưới), mỗi bước chỉ sang phải hoặc xuống dưới, không đi qua chốt CSGT 🚓. Đếm số đường đi (mod 10⁹+7).",
   "", "top", "document.querySelector('section.problem')", 0),
  ("card", "① Nhập dữ liệu", "Định dạng giống hệt WeCode"),
  ("Nhập tay theo định dạng WeCode hoặc chọn ví dụ có sẵn. Đây là ví dụ trong đề: lưới 4×4, có 3 chốt.",
   "document.querySelector('[data-preset=statement]').click()", "top", "document.getElementById('input').closest('section')", 0),
  ("Hoặc sinh bản đồ ngẫu nhiên: chọn n và mật độ chốt.",
   "", "top", "document.getElementById('btnRandom').closest('.row')", 0),
  ("card", "② Quy hoạch động từng bước", "dp[i][j] = số đường an toàn từ KTX tới ô (i, j)"),
  ("Bảng được điền lần lượt từng hàng, từ trái sang phải. Ô xuất phát: dp = 1 (trường hợp cơ sở).",
   "demo.go(0)", "#vizCard", "document.getElementById('board')", 0),
  ("Mỗi ô = ô phía trên (tím) + ô bên trái (xanh), vì bước cuối cùng chỉ có thể đến từ hai hướng đó.",
   "demo.go(5)", "#vizCard", "document.getElementById('explain')", 0),
  ("Ô có chốt 🚓 thì dp = 0: không đường nào được phép đi qua.",
   "demo.go(4)", "#vizCard", "document.querySelector('#board .cell.cur')", 0),
  ("Mã giả tô vàng dòng đang chạy, nhật ký bên dưới ghi lại từng phép tính.",
   "", "#vizCard", "document.getElementById('code')", 0),
  ("Bấm ▶ Chạy để xem toàn bộ quá trình. Có thể lùi/tiến từng bước bằng phím ← →.",
   "document.getElementById('speed').value=6; demo.go(5); demo.play()", "#vizCard", "document.getElementById('board').closest('div').parentElement", 1.6),
  ("Kết quả: dp[4][4] = 3 → có 3 đường đi an toàn.",
   "demo.stop(); demo.go(demo.steps()-1)", "#vizCard", "document.querySelector('#board .cell[data-i=\"3\"][data-j=\"3\"]')", 0),
  ("Chế độ mảng 1 chiều = đúng code nộp WeCode: dp[j] cũ là ô phía trên, dp[j-1] vừa cập nhật là ô bên trái ⇒ bộ nhớ chỉ O(n).",
   "demo.setView('1d'); demo.go(9)", "#vizCard", "document.getElementById('arrBox')", 0),
  ("card", "③ Thử nghiệm", "Đường đi, chỉnh sửa bản đồ, kiểm tra input, n = 1000"),
  ("Bản đồ 6×6: viền xanh lá là một đường an toàn ngẫu nhiên; ô bị làm mờ không nằm trên đường an toàn nào.",
   f"demo.setView('2d'); demo.load('{G6}'); demo.go(demo.steps()-1); document.getElementById('bPath').click(); document.getElementById('bUseful').click()",
   "#vizCard", "document.getElementById('board')", 0),
  ("Bấm vào một ô để thêm/bỏ chốt: bảng và đáp án được tính lại ngay.",
   "document.querySelector('.cell[data-i=\"1\"][data-j=\"0\"]').click(); demo.go(demo.steps()-1)", "#vizCard",
   "document.querySelector('#board .cell[data-i=\"1\"][data-j=\"0\"]')", 0),
  ("Input sai (thiếu dòng, ký tự lạ, sai độ dài…) → báo lỗi rõ ràng kèm vị trí.",
   "demo.load('3\\n..x\\n....')", "top", "document.getElementById('msg')", 0),
  ("n = 1000 (một triệu ô): chỉ mất vài mili giây. Lưới lớn hiển thị bằng bản đồ nhiệt — càng đậm càng nhiều đường.",
   "document.getElementById('rn').value=1000; document.getElementById('rd').value=8; document.getElementById('btnRandom').click()",
   "#vizCard", "document.getElementById('heat')", 0),
  ("Song ngữ Việt/Anh, giao diện sáng/tối.",
   "demo.setLang('en'); document.querySelector('[data-theme=light]').click()", "top", "document.querySelector('header.top .seg').parentElement", 0),
  ("card", "Tóm tắt", "dp[i][j] = dp[i−1][j] + dp[i][j−1]   ·   Thời gian Θ(n²)   ·   Bộ nhớ Θ(n)"),
  ("Phần cuối trang giải thích công thức, tính đúng đắn và độ phức tạp.",
   "demo.setLang('vi'); document.querySelector('[data-theme=dark]').click(); demo.load('4\\n....\\n.*..\\n...*\\n*...'); demo.go(15)",
   "h2:has([data-i18n=h5])", "document.querySelector('[data-i18n=h5]').closest('section')", 0),
  ("card", "Cảm ơn cô đã theo dõi!", "Demo online: vanhuydotcom.github.io/cs112-duong-di-an-toan"),
]

OVERLAY_CSS = """
#caption{bottom:108px!important;font-size:22px!important;background:rgba(8,12,20,.92)!important;border:1px solid rgba(255,255,255,.15)}
#spot{position:fixed;z-index:40;pointer-events:none;border:3px solid #fbbf24;border-radius:14px;
  box-shadow:0 0 0 4000px rgba(0,0,0,.55),0 0 24px 4px rgba(251,191,36,.6);transition:all .45s ease;opacity:0}
#card{position:fixed;inset:0;z-index:60;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:18px;
  background:radial-gradient(circle at 50% 40%,#1d2a47,#0b0f17 70%);color:#fff;font-family:'Be Vietnam Pro',sans-serif;
  opacity:0;transition:opacity .5s;pointer-events:none;padding-bottom:86px;text-align:center}
#ptr{position:fixed;z-index:45;width:46px;height:46px;pointer-events:none;opacity:0;
  transition:left .7s cubic-bezier(.4,0,.2,1),top .7s cubic-bezier(.4,0,.2,1),opacity .3s;filter:drop-shadow(0 3px 6px rgba(0,0,0,.6))}
#ptr svg{animation:bob 1.1s ease-in-out infinite}
@keyframes bob{0%,100%{transform:translate(0,0)}50%{transform:translate(-5px,-5px)}}
.ripple{position:fixed;z-index:44;width:16px;height:16px;margin:-8px 0 0 -8px;border-radius:50%;border:3px solid #fbbf24;pointer-events:none;
  animation:rip .7s ease-out forwards}
@keyframes rip{from{transform:scale(.4);opacity:1}to{transform:scale(3.6);opacity:0}}
#card h1{font-size:54px;margin:0;letter-spacing:-.01em}
#card p{font-size:24px;margin:0;color:#b9c6e4;max-width:1000px}
"""

OVERLAY_JS = """
(() => {
  const spot = document.createElement('div'); spot.id = 'spot'; document.body.appendChild(spot);
  const card = document.createElement('div'); card.id = 'card'; card.innerHTML = '<h1></h1><p></p>'; document.body.appendChild(card);
  const ptr = document.createElement('div'); ptr.id = 'ptr';
  ptr.innerHTML = '<svg viewBox="0 0 24 24" width="46" height="46"><path d="M4 2l15 11.2-6.6 1.1 3.9 7.2-2.9 1.5-3.9-7.3L4 20z" fill="#fff" stroke="#111" stroke-width="1.4" stroke-linejoin="round"/></svg>';
  document.body.appendChild(ptr);
  let target = null, tapT = null;
  const VIS_H = innerHeight - 86;  // vùng thực sự được quay
  function aim(r) {  // mũi chuột chỉ vào gần tâm vùng (giới hạn trong khung hình)
    const x = Math.min(innerWidth - 60, Math.max(20, r.left + Math.min(r.width * 0.5, r.width - 20)));
    const y = Math.min(VIS_H - 150, Math.max(20, r.top + Math.min(r.height * 0.5, r.height - 20)));
    return [x, y];
  }
  (function loop() {
    if (target && document.contains(target)) {
      const r = target.getBoundingClientRect(), pad = 8;
      Object.assign(spot.style, {left: r.left - pad + 'px', top: r.top - pad + 'px', width: r.width + 2 * pad + 'px', height: r.height + 2 * pad + 'px', opacity: 1});
      const [x, y] = aim(r);
      ptr.style.left = x + 'px'; ptr.style.top = y + 'px'; ptr.style.opacity = 1;
    } else { spot.style.opacity = 0; ptr.style.opacity = 0; }
    requestAnimationFrame(loop);
  })();
  window.spotOn = el => {
    target = el; clearTimeout(tapT);
    if (el) tapT = setTimeout(() => {  // tới nơi thì "chạm" một cái
      const [x, y] = aim(el.getBoundingClientRect());
      const d = document.createElement('div'); d.className = 'ripple'; d.style.left = x + 2 + 'px'; d.style.top = y + 2 + 'px';
      document.body.appendChild(d); setTimeout(() => d.remove(), 800);
    }, 750);
  };
  window.showCard = (t, s) => { card.querySelector('h1').textContent = t; card.querySelector('p').textContent = s; card.style.opacity = t ? 1 : 0; };
})();
"""


def read_time(text):
  return max(2.6, len(text) / 17 + 0.9)


def main():
  httpd = serve()
  with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome")
    ctx = browser.new_context(viewport={"width": W, "height": H}, record_video_dir=str(TMP), record_video_size={"width": W, "height": H},
                              color_scheme="dark")
    t0 = time.time()
    page = ctx.new_page()
    page.goto(f"http://127.0.0.1:{PORT}/")
    page.evaluate("try{localStorage.clear()}catch(e){}")
    page.reload()
    page.add_style_tag(content=OVERLAY_CSS)
    page.evaluate(OVERLAY_JS)
    real_h = (H - 86) // 2 * 2  # Chrome headless chỉ vẽ ~H-86px khi quay (xem make_video.py)
    for sc in SCENES:
      if sc[0] == "card":
        page.evaluate("spotOn(null); demo.caption('')")
        page.evaluate(f"showCard({json.dumps(sc[1])}, {json.dumps(sc[2])})")
        page.wait_for_timeout(int(max(1.9, len(sc[2]) / 24 + 1.1) * 1000))
        page.evaluate("showCard('', '')")
        page.wait_for_timeout(350)
        continue
      text, js, scroll, spot, extra = sc
      page.evaluate("spotOn(null); demo.caption('')")
      if js:
        page.evaluate(js)
      if scroll == "top":
        page.evaluate("scrollTo({top:0,behavior:'smooth'})")
      else:
        page.evaluate(f"document.querySelector({json.dumps(scroll)}).scrollIntoView({{behavior:'smooth',block:'start'}})")
      page.wait_for_timeout(450)
      page.evaluate(f"spotOn({spot})")
      page.evaluate(f"demo.caption({json.dumps(text)})")
      page.wait_for_timeout(int((read_time(text) + extra) * 1000))
    page.wait_for_timeout(800)
    vid = Path(page.video.path())
    total = time.time() - t0
    ctx.close()
    browser.close()
  httpd.shutdown()
  out = HERE / "demo_khong_tieng.mp4"
  subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(vid), "-vf", f"crop={W}:{real_h}:0:0",
                  "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "22", "-an", str(out)], check=True)
  print(f"OK → {out}  ({total:.0f}s)")


if __name__ == "__main__":
  main()

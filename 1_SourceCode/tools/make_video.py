"""Tự động quay video demo: Playwright điều khiển Chrome theo kịch bản, edge-tts (giọng neural tiếng Việt)
đọc thuyết minh, ffmpeg ghép hình + tiếng. Chạy: python3 video/make_video.py  →  video/demo.mp4"""
import functools
import http.server
import json
import subprocess
import sys
import threading
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
APP = HERE.parent / "app"
TMP = HERE / "_build"
TMP.mkdir(exist_ok=True)
PORT = 8799
W, H = 1366, 860
# giọng đọc: vi-VN-HoaiMyNeural (nữ) hoặc vi-VN-NamMinhNeural (nam); đổi bằng: python3 video/make_video.py NamMinh
VOICE = f"vi-VN-{sys.argv[1] if len(sys.argv) > 1 else 'HoaiMy'}Neural"

# (lời thuyết minh, hành động JS trước khi đọc, cách cuộn tới phần tử)
SCENES = [
  ("Xin chào, em là Đinh Văn Huy, mã số sinh viên 25730032. Đây là demo bài tập lớn môn Phân tích và thiết kế thuật toán: bài Đường đi an toàn, giải bằng quy hoạch động.",
   "", "top"),
  ("Đề bài: bản đồ n nhân n, đi từ ký túc xá khu B ở góc trái trên tới trường U I T ở góc phải dưới, mỗi bước chỉ sang phải hoặc xuống dưới, không được đi qua chốt cảnh sát giao thông. Cần đếm số đường đi, lấy dư cho mười mũ chín cộng bảy.",
   "", "top"),
  ("Dữ liệu nhập theo đúng định dạng trên WeCode. Em nạp ví dụ trong đề: lưới bốn nhân bốn, có ba chốt.",
   "document.querySelector('[data-preset=statement]').click()", "top"),
  ("Bảng quy hoạch động được điền lần lượt từng hàng, từ trái sang phải. Ô xuất phát có đúng một cách đi, đó là trường hợp cơ sở.",
   "demo.go(0)", "#vizCard"),
  ("Với mỗi ô, bước cuối cùng chỉ có thể đến từ ô phía trên, tô màu tím, hoặc từ ô bên trái, tô màu xanh. Vì vậy số đường tới ô này bằng tổng hai ô đó.",
   "demo.go(5)", "#vizCard"),
  ("Ô có chốt cảnh sát thì không đường nào được đi qua, nên giá trị bằng không. Bên phải là mã giả, dòng đang chạy được tô vàng, kèm nhật ký từng phép tính.",
   "demo.go(4)", "#vizCard"),
  ("Bấm nút chạy để xem toàn bộ quá trình. Có thể chỉnh tốc độ, lùi hoặc tiến từng bước bằng phím mũi tên.",
   "document.getElementById('speed').value=7; demo.go(5); demo.play()", "#vizCard"),
  ("Kết quả: có ba đường đi an toàn từ ký túc xá tới trường.",
   "demo.stop(); demo.go(demo.steps()-1)", "#vizCard"),
  ("Chế độ thứ hai minh họa đúng đoạn code em nộp trên WeCode: chỉ dùng một mảng một chiều. Trước khi cập nhật, d p j vẫn là giá trị ô phía trên, còn d p j trừ một vừa cập nhật là ô bên trái. Nhờ vậy bộ nhớ chỉ còn O của n.",
   "demo.setView('1d'); demo.go(9)", "#vizCard"),
  ("Em có thể bấm trực tiếp vào lưới để thêm hoặc bỏ chốt. Thử với một bản đồ sáu nhân sáu.",
   "demo.setView('2d'); demo.load('6\\n......\\n.*....\\n...*..\\n*.....\\n..*...\\n......'); demo.go(-1)", "#vizCard"),
  ("Chạy hết bảng, rồi vẽ ngẫu nhiên một đường an toàn bằng viền xanh lá, và làm mờ những ô không nằm trên bất kỳ đường an toàn nào.",
   "demo.go(demo.steps()-1); document.getElementById('bPath').click(); document.getElementById('bUseful').click()", "#vizCard"),
  ("Thêm một chốt ở ô hàng hai cột một: đáp án được tính lại ngay.",
   "document.querySelector('.cell[data-i=\"1\"][data-j=\"0\"]').click(); demo.go(demo.steps()-1)", "#vizCard"),
  ("Chương trình kiểm tra input rất kỹ: sai số dòng, sai độ dài hàng hay có ký tự lạ đều báo lỗi rõ ràng kèm vị trí.",
   "demo.load('3\\n..x\\n....')", "top"),
  ("Với n bằng một nghìn, tức một triệu ô, thuật toán chạy chỉ vài mili giây. Lưới lớn được hiển thị dưới dạng bản đồ nhiệt: ô càng đậm thì càng có nhiều đường đi tới.",
   "document.getElementById('rn').value=1000; document.getElementById('rd').value=8; document.getElementById('btnRandom').click()", "#vizCard"),
  ("Giao diện hỗ trợ song ngữ Việt và Anh, cùng chế độ sáng và tối.",
   "demo.setLang('en'); document.querySelector('[data-theme=light]').click()", "top"),
  ("Cuối trang là phần phân tích: công thức truy hồi, tính đúng đắn, và độ phức tạp theta n bình phương về thời gian, theta n về bộ nhớ. Em xin cảm ơn cô đã theo dõi.",
   "demo.setLang('vi'); document.querySelector('[data-theme=dark]').click(); demo.load('4\\n....\\n.*..\\n...*\\n*...'); demo.go(15)", "h2:has([data-i18n=h5])"),
]


def serve():
  handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(APP))
  httpd = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), handler)
  threading.Thread(target=httpd.serve_forever, daemon=True).start()
  return httpd


def tts(i, text):
  """Thuyết minh bằng giọng neural tiếng Việt của Microsoft (edge-tts); thử lại khi mạng chập chờn."""
  mp3 = TMP / f"s{i:02d}.mp3"
  for attempt in range(4):
    r = subprocess.run([sys.executable, "-m", "edge_tts", "-v", VOICE, "--rate", "+4%", "-t", text, "--write-media", str(mp3)],
                       capture_output=True, text=True)
    if r.returncode == 0 and mp3.exists() and mp3.stat().st_size > 1000:
      break
    time.sleep(2 + attempt * 2)
  else:
    raise RuntimeError(f"edge-tts lỗi ở cảnh {i}: {r.stderr[-300:]}")
  dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp3)],
                             capture_output=True, text=True, check=True).stdout)
  return mp3, dur


def main():
  audio = [tts(i, s[0]) for i, s in enumerate(SCENES)]
  httpd = serve()
  marks = []
  with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome")
    ctx = browser.new_context(viewport={"width": W, "height": H}, record_video_dir=str(TMP), record_video_size={"width": W, "height": H},
                              color_scheme="dark", device_scale_factor=1)
    t0 = time.time()
    page = ctx.new_page()
    page.goto(f"http://127.0.0.1:{PORT}/")
    page.evaluate("try{localStorage.clear()}catch(e){}")
    page.reload()
    page.wait_for_timeout(1500)
    # Chrome headless chỉ vẽ ~H-86px của viewport khi quay; đẩy phụ đề lên và cắt phần xám bên dưới
    real_h = (H - 86) // 2 * 2
    page.add_style_tag(content="#caption{bottom:108px!important}")
    for i, (text, js, target) in enumerate(SCENES):
      if js:
        page.evaluate(js)
      if target == "top":
        page.evaluate("scrollTo({top:0,behavior:'smooth'})")
      else:
        page.evaluate(f"document.querySelector({json.dumps(target)}).scrollIntoView({{behavior:'smooth',block:'start'}})")
      page.evaluate(f"demo.caption({json.dumps(text)})")
      page.wait_for_timeout(400)
      marks.append(time.time() - t0)
      page.wait_for_timeout(int(audio[i][1] * 1000) + 700)
    page.evaluate("demo.caption('')")
    page.wait_for_timeout(1200)
    total = time.time() - t0
    vid = Path(page.video.path())
    ctx.close()
    browser.close()
  httpd.shutdown()

  # ghép: mỗi đoạn tiếng được đặt đúng thời điểm của cảnh
  inputs, filters = ["-i", str(vid)], []
  for k, ((aiff, _), at) in enumerate(zip(audio, marks)):
    inputs += ["-i", str(aiff)]
    ms = int(at * 1000)
    filters.append(f"[{k + 1}:a]adelay={ms}|{ms},apad[a{k}]")
  mix = "".join(f"[a{k}]" for k in range(len(audio)))
  filters.append(f"[0:v]crop={W}:{real_h}:0:0[vout]")
  filters.append(f"{mix}amix=inputs={len(audio)}:normalize=0,atrim=0:{total:.2f}[aout]")
  out = HERE.parent.parent / "2_VideoDemo" / f"demo_{VOICE.split('-')[2].replace('Neural', '')}.mp4"
  subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(filters),
                  "-map", "[vout]", "-map", "[aout]", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "22",
                  "-c:a", "aac", "-b:a", "128k", "-shortest", str(out)], check=True)
  print(f"OK → {out}  ({total:.0f}s, {W}x{real_h})")


if __name__ == "__main__":
  main()

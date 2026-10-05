"""Chụp ảnh giao diện cho report (Playwright + Chrome)."""
import functools, http.server, threading
from pathlib import Path
from playwright.sync_api import sync_playwright
APP = Path(__file__).resolve().parent.parent / "app"; OUT = Path(__file__).resolve().parent / "img"
h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(APP))
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8798), h); threading.Thread(target=srv.serve_forever, daemon=True).start()
G6 = '6\\n......\\n.*....\\n...*..\\n*.....\\n..*...\\n......'
with sync_playwright() as p:
  b = p.chromium.launch(channel="chrome")
  pg = b.new_page(viewport={"width": 1366, "height": 900}, device_scale_factor=2, color_scheme="light")
  pg.goto("http://127.0.0.1:8798/"); pg.wait_for_timeout(800)
  pg.screenshot(path=OUT / "overview.png", full_page=True)
  card = pg.locator("#vizCard")
  pg.evaluate("demo.go(5)"); card.screenshot(path=OUT / "step_sum.png")
  pg.evaluate("demo.go(4)"); card.screenshot(path=OUT / "step_block.png")
  pg.evaluate("demo.setView('1d'); demo.go(9)"); card.screenshot(path=OUT / "step_1d.png")
  pg.evaluate(f"demo.setView('2d'); demo.load('{G6}'); demo.go(demo.steps()-1); document.getElementById('bPath').click(); document.getElementById('bUseful').click()")
  card.screenshot(path=OUT / "path.png")
  pg.evaluate("demo.load('3\\n..x\\n....')"); pg.locator("section.card").nth(1).screenshot(path=OUT / "validate.png")
  pg.evaluate("document.getElementById('rn').value=1000; document.getElementById('rd').value=8; document.getElementById('btnRandom').click()")
  card.screenshot(path=OUT / "big.png")
  pg.emulate_media(color_scheme="dark"); pg.evaluate("demo.setLang('en'); demo.load('4\\n....\\n.*..\\n...*\\n*...'); demo.go(15)")
  card.screenshot(path=OUT / "english_dark.png")
  pg.set_viewport_size({"width": 390, "height": 844}); pg.evaluate("demo.setLang('vi'); demo.go(9)"); pg.wait_for_timeout(300)
  card.screenshot(path=OUT / "mobile.png")
  b.close()
srv.shutdown(); print("ok")

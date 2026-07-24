"""Headless-browser-fallback (Playwright/Chromium) voor sites die
simpele requests blokkeren of hun inhoud met JavaScript renderen.
Een browser-instantie voor de hele run."""
_pl = None
_browser = None

def fetch_html(url, wacht_ms=2500, timeout_ms=25000):
    global _pl, _browser
    page = None
    try:
        if _browser is None:
            from playwright.sync_api import sync_playwright
            _pl = sync_playwright().start()
            _browser = _pl.chromium.launch(headless=True, args=["--no-sandbox"])
        page = _browser.new_page(locale="nl-NL",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
        page.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined})")
        resp = page.goto(url, timeout=timeout_ms, wait_until="domcontentloaded")
        if resp is not None and resp.status >= 400:
            page.close()
            return None
        page.wait_for_timeout(wacht_ms)
        html = page.content()
        if "Just a moment" in html or "cf-chl" in html:
            page.wait_for_timeout(6500)
            html = page.content()
        page.close()
        return html
    except Exception:
        try:
            if page:
                page.close()
        except Exception:
            pass
        return None

def sluit():
    global _pl, _browser
    try:
        if _browser:
            _browser.close()
        if _pl:
            _pl.stop()
    except Exception:
        pass
    _browser = None
    _pl = None

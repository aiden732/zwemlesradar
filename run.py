#!/usr/bin/env python3
"""
ZwemlesRadar-scraper v2. Drie sporen, dagelijks via GitHub Actions:
1. publicisten (vaste pagina's met duur)  2. Sportfondsen-module
3. Optisport via DEWI Online (club-enumeratie).
Flow per bron: requests -> parse; leeg? -> headless browser -> parse;
nog leeg? -> indicator (wachtlijst/direct) over alle opgehaalde pagina's.
Fouten degraderen naar de vorige waarde met stale=True.
"""
import json, sys, datetime, pathlib, time, re
sys.path.insert(0, str(pathlib.Path(__file__).parent / "scrapers"))
import requests
from bronnen import BRONNEN
from multibronnen import SPORTFONDSEN, SF_PADEN, OPTISPORT
from parsers import (parse_dataduiker_lesdagen, parse_vrije_tekst,
                     parse_sportfondsen_wachtlijst, detecteer_indicator)
from dewi import scan_dewi
import browser

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
      "Accept-Language": "nl-NL,nl;q=0.9"}
UIT = pathlib.Path(__file__).parent / "data" / "wachttijden.json"
PARSERS = {"dataduiker": parse_dataduiker_lesdagen,
           "sportfondsen": parse_sportfondsen_wachtlijst}

def laad_vorige():
    if UIT.exists():
        return {b["id"]: b for b in json.loads(UIT.read_text())["bronnen"]}
    return {}

def haal(url):
    try:
        r = requests.get(url, headers=UA, timeout=20)
        r.raise_for_status()
        if len(r.text) > 400:
            return r.text
    except Exception:
        pass
    return None

def probeer(urls, parse_fn, browser_max=2):
    """Probeer urls met requests, dan browser. Geeft (metingen, url, htmls)."""
    htmls = []
    for url in urls:
        h = haal(url)
        if not h:
            continue
        htmls.append(h)
        m = parse_fn(h)
        if m:
            return m, url, htmls
    for url in urls[:browser_max]:
        h = browser.fetch_html(url)
        if not h:
            continue
        htmls.append(h)
        m = parse_fn(h)
        if m:
            return m, url, htmls
    return [], None, htmls

def indicator_uit(htmls):
    beste = None
    for h in htmls:
        ind = detecteer_indicator(h)
        if ind == "wachtlijst":
            return "wachtlijst"
        if ind and not beste:
            beste = ind
    return beste

def crawl_links(basis_url, html):
    from urllib.parse import urljoin, urlparse
    dom = urlparse(basis_url).netloc
    uit = []
    for l in re.findall(r'href="([^"#]+)"', html):
        vol = urljoin(basis_url, l)
        if urlparse(vol).netloc == dom and re.search(r"zwemles|wachtlijst|wachttijd|veelgestelde|faq", vol, re.I):
            if vol not in uit:
                uit.append(vol)
    return uit[:4]

def maak_record(basis, vorige, vandaag, metingen, gebruikt, indicator, foutlabel):
    rec = dict(basis)
    if metingen:
        los = [x["lo"] for x in metingen] + [x["hi"] for x in metingen if x["hi"] is not None]
        rec.update(status="ok", peildatum=vandaag, metingen=metingen, bron_url=gebruikt,
                   min_mnd=min(los), max_mnd=max(los), stale=False, indicator="duur")
    elif indicator:
        rec.update(status="ok (indicator)", peildatum=vandaag, metingen=[],
                   min_mnd=None, max_mnd=None, stale=False, indicator=indicator)
    else:
        oud = vorige.get(basis["id"], {})
        rec.update(status=foutlabel, peildatum=oud.get("peildatum"),
                   metingen=oud.get("metingen", []), min_mnd=oud.get("min_mnd"),
                   max_mnd=oud.get("max_mnd"), stale=True, indicator=oud.get("indicator"))
    n = len(rec.get("metingen") or [])
    print(f"[{'OK ' if not rec['stale'] else '---'}] {rec['id']:24} {n:2}x  ind={rec.get('indicator')}")
    return rec

def main():
    vandaag = datetime.date.today().isoformat()
    vorige = laad_vorige()
    resultaat = []

    # ---- 1. publicisten ----
    for bron in BRONNEN:
        fn = PARSERS.get(bron["parser"], parse_vrije_tekst)
        metingen, gebruikt, htmls = probeer(bron["urls"], fn)
        if not metingen and htmls:
            for url in crawl_links(bron["urls"][0], htmls[0]):
                h = haal(url)
                if h:
                    htmls.append(h)
                    metingen = fn(h)
                    if metingen:
                        gebruikt = url
                        break
        indicator = None if metingen else indicator_uit(htmls)
        basis = {k: bron[k] for k in ("id", "naam", "plaats", "prov")}
        basis["groep"] = "publicist"
        resultaat.append(maak_record(basis, vorige, vandaag, metingen, gebruikt, indicator,
                                     "geen duur en geen indicator gevonden"))
        time.sleep(0.2)

    # ---- 2. Sportfondsen-module ----
    for mid, naam, plaats, prov, sub in SPORTFONDSEN:
        urls = [f"https://{sub}.sportfondsen.nl{p}" for p in SF_PADEN] + [f"https://{sub}.sportfondsen.nl/"]
        metingen, gebruikt, htmls = probeer(urls, parse_sportfondsen_wachtlijst, browser_max=1)
        indicator = None if metingen else indicator_uit(htmls)
        basis = dict(id=mid, naam=naam, plaats=plaats, prov=prov, groep="sportfondsen")
        resultaat.append(maak_record(basis, vorige, vandaag, metingen, gebruikt, indicator,
                                     "subdomein/pagina niet bruikbaar"))
        time.sleep(0.2)

    # ---- 3. Optisport via DEWI ----
    dewi_recs = scan_dewi(lambda u: (time.sleep(0.25), haal(u))[1], OPTISPORT, max_id=140)
    dewi_ids = set()
    for dr in dewi_recs:
        dewi_ids.add(dr["id"])
        rec = dict(dr)
        if rec["indicator"]:
            rec.update(status="ok (dewi-indicator)", peildatum=vandaag, metingen=[],
                       min_mnd=None, max_mnd=None, stale=False)
        else:
            rec.update(status="dewi-check ok; geen wachtlijst-tekst bij kinderzwemles",
                       peildatum=vandaag, metingen=[], min_mnd=None, max_mnd=None, stale=False)
        print(f"[OK ] {rec['id']:24} dewi-club {rec['dewi_club']:3}  ind={rec['indicator']}")
        resultaat.append(rec)
    for mid, naam, plaats, prov, basis_url in OPTISPORT:
        if mid in dewi_ids:
            continue
        oud = vorige.get(mid, {})
        resultaat.append(dict(id=mid, naam=naam, plaats=plaats, prov=prov, groep="optisport",
                              status="geen dewi-club gematcht", peildatum=oud.get("peildatum"),
                              metingen=oud.get("metingen", []), min_mnd=oud.get("min_mnd"),
                              max_mnd=oud.get("max_mnd"), stale=True, indicator=oud.get("indicator")))

    browser.sluit()
    UIT.parent.mkdir(exist_ok=True)
    UIT.write_text(json.dumps({"gegenereerd": vandaag, "bronnen": resultaat},
                              ensure_ascii=False, indent=1))
    ok = sum(1 for r in resultaat if not r["stale"])
    print(f"\n{ok}/{len(resultaat)} bronnen vers -> {UIT}")

if __name__ == "__main__":
    main()

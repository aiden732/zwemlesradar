#!/usr/bin/env python3
"""
ZwemlesRadar-scraper: haalt alle bronnen op, parseert wachttijden,
schrijft data/wachttijden.json. Faalt een bron, dan blijft de vorige
waarde staan met stale=True — eerlijk zichtbaar op de site.
Draait lokaal (python3 run.py) en dagelijks via GitHub Actions.
"""
import json, sys, datetime, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent / "scrapers"))
import requests
from bronnen import BRONNEN
from parsers import (parse_dataduiker_lesdagen, parse_vrije_tekst,
                     parse_sportfondsen_wachtlijst, detecteer_indicator)
from multibronnen import SPORTFONDSEN, SF_PADEN, OPTISPORT, OPTI_PADEN
import time

UA = {"User-Agent": "ZwemlesRadar/1.0 (+wachttijd-overzicht voor ouders; contact via site)"}
UIT = pathlib.Path(__file__).parent / "data" / "wachttijden.json"

def laad_vorige():
    if UIT.exists():
        return {b["id"]: b for b in json.loads(UIT.read_text())["bronnen"]}
    return {}

def main():
    vandaag = datetime.date.today().isoformat()
    vorige = laad_vorige()
    resultaat = []
    for bron in BRONNEN:
        rec = dict(bron)
        try:
            fn = {"dataduiker": parse_dataduiker_lesdagen,
                  "sportfondsen": parse_sportfondsen_wachtlijst}.get(bron["parser"], parse_vrije_tekst)
            metingen, eerste_html, gebruikte_url = [], None, None
            kandidaten = list(bron["urls"])
            geprobeerd = set()
            while kandidaten and not metingen:
                url = kandidaten.pop(0)
                if url in geprobeerd: continue
                geprobeerd.add(url)
                try:
                    resp = requests.get(url, headers=UA, timeout=25)
                    resp.raise_for_status()
                except Exception:
                    continue
                if eerste_html is None: eerste_html = (url, resp.text)
                metingen = fn(resp.text)
                if metingen: gebruikte_url = url
            if not metingen and eerste_html:
                # crawl 1 niveau: links met zwemles/wachtlijst/faq op zelfde domein
                import re as _re
                from urllib.parse import urljoin, urlparse
                basis_url, basis_html = eerste_html
                dom = urlparse(basis_url).netloc
                links = _re.findall(r'href="([^"#]+)"', basis_html)
                extra = []
                for l in links:
                    vol = urljoin(basis_url, l)
                    if urlparse(vol).netloc == dom and _re.search(r"zwemles|wachtlijst|wachttijd|veelgestelde|faq", vol, _re.I):
                        if vol not in geprobeerd and vol not in extra:
                            extra.append(vol)
                for url in extra[:4]:
                    try:
                        resp = requests.get(url, headers=UA, timeout=25)
                        resp.raise_for_status()
                    except Exception:
                        continue
                    metingen = fn(resp.text)
                    if metingen:
                        gebruikte_url = url
                        break
            if not metingen:
                raise ValueError("geen wachttijd-waarden gevonden op kandidaat-pagina's")
            rec["bron_url"] = gebruikte_url
            los = [m["lo"] for m in metingen] + [m["hi"] for m in metingen if m["hi"]]
            rec.update(status="ok", peildatum=vandaag, metingen=metingen,
                       min_mnd=min(los), max_mnd=max(los), stale=False)
        except Exception as e:
            oud = vorige.get(bron["id"], {})
            rec.update(status=f"fout: {type(e).__name__}: {e}"[:160],
                       peildatum=oud.get("peildatum"),
                       metingen=oud.get("metingen", []),
                       min_mnd=oud.get("min_mnd"), max_mnd=oud.get("max_mnd"),
                       stale=True)
        n = len(rec["metingen"])
        print(f"[{'OK ' if not rec['stale'] else 'OUD'}] {bron['id']:24} {n:2} meting(en)"
              + (f"  {rec['min_mnd']}-{rec['max_mnd']} mnd" if rec.get("min_mnd") is not None else "")
              + ("" if not rec["stale"] else f"  ({rec['status']})"))
        resultaat.append(rec)
    # ---------- multibronnen: Sportfondsen-module ----------
    def haal(url):
        try:
            resp = requests.get(url, headers=UA, timeout=20)
            resp.raise_for_status()
            return resp.text
        except Exception:
            return None

    for mid, naam, plaats, prov, sub in SPORTFONDSEN:
        time.sleep(0.3)
        rec = dict(id=mid, naam=naam, plaats=plaats, prov=prov, groep="sportfondsen")
        metingen, indicator, gebruikt = [], None, None
        beste_html = None
        for pad in SF_PADEN:
            url = f"https://{sub}.sportfondsen.nl{pad}"
            html = haal(url)
            if html is None: continue
            if beste_html is None: beste_html = html
            m = parse_sportfondsen_wachtlijst(html)
            if m:
                metingen, gebruikt = m, url
                break
        if not metingen and beste_html:
            indicator = detecteer_indicator(beste_html)
        if metingen:
            los = [x["lo"] for x in metingen] + [x["hi"] for x in metingen if x["hi"] is not None]
            rec.update(status="ok", peildatum=vandaag, metingen=metingen, bron_url=gebruikt,
                       min_mnd=min(los), max_mnd=max(los), stale=False, indicator="duur")
        elif indicator:
            rec.update(status="ok (indicator)", peildatum=vandaag, metingen=[],
                       min_mnd=None, max_mnd=None, stale=False, indicator=indicator)
        else:
            oud = vorige.get(mid, {})
            rec.update(status="geen data", peildatum=oud.get("peildatum"),
                       metingen=oud.get("metingen", []), min_mnd=oud.get("min_mnd"),
                       max_mnd=oud.get("max_mnd"), stale=True,
                       indicator=oud.get("indicator"))
        print(f"[{'OK ' if not rec['stale'] else '---'}] {mid:22} {len(rec['metingen']):2}x  ind={rec.get('indicator')}")
        resultaat.append(rec)

    # ---------- multibronnen: Optisport-locaties ----------
    for mid, naam, plaats, prov, basis in OPTISPORT:
        time.sleep(0.3)
        rec = dict(id=mid, naam=naam, plaats=plaats, prov=prov, groep="optisport")
        metingen, indicator, gebruikt = [], None, None
        beste_html = None
        for pad in OPTI_PADEN:
            html = haal(basis + pad)
            if html is None: continue
            if beste_html is None: beste_html = html
            m = parse_dataduiker_lesdagen(html) or parse_vrije_tekst(html)
            if m:
                metingen, gebruikt = m, basis + pad
                break
        if not metingen and beste_html:
            indicator = detecteer_indicator(beste_html)
        if metingen:
            los = [x["lo"] for x in metingen] + [x["hi"] for x in metingen if x["hi"] is not None]
            rec.update(status="ok", peildatum=vandaag, metingen=metingen, bron_url=gebruikt,
                       min_mnd=min(los), max_mnd=max(los), stale=False, indicator="duur")
        elif indicator:
            rec.update(status="ok (indicator)", peildatum=vandaag, metingen=[],
                       min_mnd=None, max_mnd=None, stale=False, indicator=indicator)
        else:
            oud = vorige.get(mid, {})
            rec.update(status="geen data", peildatum=oud.get("peildatum"),
                       metingen=oud.get("metingen", []), min_mnd=oud.get("min_mnd"),
                       max_mnd=oud.get("max_mnd"), stale=True,
                       indicator=oud.get("indicator"))
        print(f"[{'OK ' if not rec['stale'] else '---'}] {mid:22} {len(rec['metingen']):2}x  ind={rec.get('indicator')}")
        resultaat.append(rec)

    UIT.parent.mkdir(exist_ok=True)
    UIT.write_text(json.dumps({"gegenereerd": vandaag, "bronnen": resultaat},
                              ensure_ascii=False, indent=1))
    ok = sum(1 for r in resultaat if not r["stale"])
    print(f"\n{ok}/{len(resultaat)} bronnen vers -> {UIT}")

if __name__ == "__main__":
    main()

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
from parsers import parse_dataduiker_lesdagen, parse_vrije_tekst

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
            r = requests.get(bron["url"], headers=UA, timeout=25)
            r.raise_for_status()
            fn = parse_dataduiker_lesdagen if bron["parser"] == "dataduiker" else parse_vrije_tekst
            metingen = fn(r.text)
            if not metingen:
                raise ValueError("pagina geladen, geen wachttijd-waarden gevonden")
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
    UIT.parent.mkdir(exist_ok=True)
    UIT.write_text(json.dumps({"gegenereerd": vandaag, "bronnen": resultaat},
                              ensure_ascii=False, indent=1))
    ok = sum(1 for r in resultaat if not r["stale"])
    print(f"\n{ok}/{len(resultaat)} bronnen vers -> {UIT}")

if __name__ == "__main__":
    main()

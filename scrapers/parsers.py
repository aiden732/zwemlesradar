"""
ZwemlesRadar — parsers voor publiek gepubliceerde wachttijden.
Parser 1 (publicisten, vrije tekst) + parser 2 (Dataduiker-lesdagenmodule).
Elke parser krijgt HTML en geeft metingen terug:
  {"label": "...", "raw": "...", "lo": maanden, "hi": maanden}
"""
import re
from bs4 import BeautifulSoup

MND = r"(?:maanden|maand|mnd)"
JR  = r"(?:jaar|jr)"

def _f(x): return float(x.replace(",", "."))

def parse_range(tekst):
    """'13-16 maanden' / '6 - 8 maanden' / '1,5 jaar' / '9 maanden tot een jaar'
    / 'anderhalf jaar' / 'zes maanden' -> (lo, hi) in maanden, of None."""
    t = " ".join(tekst.lower().split()).replace("anderhalf jaar", "1,5 jaar")
    woord = {"twee":2,"drie":3,"vier":4,"vijf":5,"zes":6,"zeven":7,"acht":8,
             "negen":9,"tien":10,"elf":11,"twaalf":12}
    for w, v in woord.items():
        t = re.sub(rf"\b{w}\b(?=\s*{MND})", str(v), t)
    t = re.sub(rf"\b(een|1)\s+{JR}\b", "12 maanden", t)
    m = re.search(rf"(\d+[.,]?\d*)\s*{MND}\s*tot\s*(\d+[.,]?\d*)\s*{MND}", t)
    if m: return _f(m.group(1)), _f(m.group(2))
    m = re.search(rf"(\d+[.,]?\d*)\s*[-\u2013]\s*(\d+[.,]?\d*)\s*{MND}", t)
    if m: return _f(m.group(1)), _f(m.group(2))
    m = re.search(rf"(\d+[.,]?\d*)\s*(?:tot|[-\u2013])\s*(\d+[.,]?\d*)\s*{JR}", t)
    if m: return _f(m.group(1)) * 12, _f(m.group(2)) * 12
    m = re.search(rf"(\d+[.,]?\d*)\s*tot\s*(\d+[.,]?\d*)\s*{MND}", t)
    if m: return _f(m.group(1)), _f(m.group(2))
    m = re.search(rf"(\d+[.,]?\d*)\s*{JR}", t)
    if m:
        v = _f(m.group(1)) * 12
        return (v, None) if "minimaal" in t else (v, v)
    m = re.search(rf"(\d+[.,]?\d*)\s*{MND}", t)
    if m:
        v = _f(m.group(1))
        return v, v
    return None

def parse_dataduiker_lesdagen(html):
    """Dataduiker 'Zwemles dagen en tijden'-module (o.a. De Vallei):
    kop (h2) = dag(en), daaronder een tabel met kolommen TIJD | WACHTTIJD."""
    soup = BeautifulSoup(html, "html.parser")
    out = []
    for table in soup.find_all("table"):
        eerste_rij = table.find("tr")
        headers = [c.get_text(strip=True).upper()
                   for c in (eerste_rij.find_all(["th", "td"]) if eerste_rij else [])]
        if not any("WACHTTIJD" in h for h in headers):
            continue
        dag = ""
        for prev in table.find_all_previous(["h2", "h3"]):
            txt = prev.get_text(strip=True)
            if txt and "LESSEN" not in txt.upper():
                dag = txt
                break
        for tr in table.find_all("tr"):
            cellen = [td.get_text(" ", strip=True) for td in tr.find_all("td")]
            if len(cellen) < 2:
                continue
            tijd, wt = cellen[0], cellen[1]
            rng = parse_range(wt)
            if rng:
                out.append({"label": f"{dag} {tijd}".strip(), "raw": wt,
                            "lo": rng[0], "hi": rng[1]})
    return out

def parse_vrije_tekst(html, contextwoorden=(r"wachttijd", r"wachtlijst")):
    """Generieke publicisten-parser: maand-/jaarwaarden in zinnen over wachten
    (Helsdingen, Tropiqua, Alkmaar, Koploper, ...)."""
    soup = BeautifulSoup(html, "html.parser")
    tekst = soup.get_text(" ", strip=True)
    out = []
    for zin in re.split(r"(?<=[.!?])\s+|\n", tekst):
        z = zin.lower()
        if not any(re.search(c, z) for c in contextwoorden):
            continue
        if "review" in z or "doorstroom" in z:
            continue
        for stuk in re.split(r",|;| en bij | bij ", zin):
            rng = parse_range(stuk)
            if rng:
                out.append({"label": "site", "raw": stuk.strip()[:160],
                            "lo": rng[0], "hi": rng[1]})
    uniek, gezien = [], set()
    for m in out:
        k = (m["lo"], m["hi"])
        if k not in gezien:
            gezien.add(k); uniek.append(m)
    return uniek


def parse_sportfondsen_wachtlijst(html):
    """Sportfondsen-module /ik-ben-nieuw/wachtlijst/: regels als
    '08.15 uur - 6 tot 9 maanden' + B/C-zinnen."""
    soup = BeautifulSoup(html, "html.parser")
    tekst = soup.get_text(" ", strip=True)
    out = []
    for m in re.finditer(r"(\d{1,2}[.:]\d{2})\s*uur\s*[-\u2013]\s*([^.;]{0,40}?maanden)", tekst):
        rng = parse_range(m.group(2))
        if rng:
            out.append({"label": m.group(1) + " uur", "raw": m.group(2).strip(),
                        "lo": rng[0], "hi": rng[1]})
    m = re.search(r"B[- ]?\s*en\s*C[- ]?diploma[^.]{0,60}?(\d+)\s*[-\u2013tot ]+\s*(\d+)\s*maanden", tekst)
    if m:
        out.append({"label": "B/C-diploma", "raw": m.group(0)[-40:],
                    "lo": float(m.group(1)), "hi": float(m.group(2))})
    if not out:
        out = parse_vrije_tekst(html)
    return out

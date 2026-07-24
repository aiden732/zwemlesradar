"""DEWI Online-scan voor Optisport: loopt club-ID's af op
optisport.dewi-online.nl (het boekingssysteem achter de inschrijfknoppen,
publiek en zonder firewall). Per club: clubnaam uit de titel en de
wachtlijst-verklikker per zwemlesproduct ('Zodra er een plekje vrijkomt')."""
import re

DEWI_URL = "https://optisport.dewi-online.nl/iframe/club/{cid}/sign-up/subscription-group/0/subscriptions"
KIND_RE = re.compile(r"(Startpakket\s+Zed\s*&\s*Sop[^A-Za-z]*zwemles|Zed\s*&\s*Sop\s*zwemles|Startpakket\s+zwemles(?!\s*(9\+|volwassen)))", re.I)
PLEK_RE = re.compile(r"Zodra er een plekje\s*vrij", re.I)
TITEL_RE = re.compile(r"<title>\s*Inschrijven als lid\s*-\s*(.*?)\s*</title>", re.I | re.S)

def _norm(s):
    s = (s or "").lower()
    s = re.sub(r"zwembad|optisport|bronbad|het |de |'t ", "", s)
    return re.sub(r"[^a-z0-9]", "", s)

def scan_dewi(haal_fn, opti_lijst, max_id=140):
    """haal_fn(url)->html|None; opti_lijst = OPTISPORT-registry voor naam->plaats.
    Geeft records terug (zonder peildatum/stale-velden)."""
    out = []
    gezien_namen = set()
    for cid in range(1, max_id + 1):
        html = haal_fn(DEWI_URL.format(cid=cid))
        if not html:
            continue
        m = TITEL_RE.search(html)
        if not m:
            continue
        clubnaam = re.sub(r"\s+", " ", m.group(1)).strip()
        import html as _h
        vlak = re.sub(r"\s+", " ", _h.unescape(re.sub(r"<[^>]+>", " ", html)))
        if not clubnaam or clubnaam.lower() in gezien_namen:
            continue
        gezien_namen.add(clubnaam.lower())
        # koppel aan bekende Optisport-locatie voor id/plaats/prov
        cn = _norm(clubnaam)
        koppel = None
        for oid, naam, plaats, prov, _u in opti_lijst:
            on = _norm(naam)
            if on and cn and (on in cn or cn in on):
                koppel = (oid, naam, plaats, prov)
                break
        # alle zwemlesproducten checken op de wachtlijst-verklikker
        indicator = None
        kind_gezien = False
        extra = []
        ZWEMLES_RE = re.compile(r"(Startpakket[^<\n]{0,60}zwemles[^<\n]{0,20}|Zed\s*&\s*Sop\s*zwemles|zwemles\s*9\+|Volwassen(en)?\s*zwemles)", re.I)
        for zm in ZWEMLES_RE.finditer(vlak):
            naam_p = re.sub(r"\s+", " ", zm.group(0)).strip()
            venster = vlak[zm.start(): zm.start() + 900]
            heeft_wacht = bool(PLEK_RE.search(venster))
            is_kind = not re.search(r"9\+|volwassen", naam_p, re.I)
            if is_kind:
                kind_gezien = True
                if heeft_wacht:
                    indicator = "wachtlijst"
            elif heeft_wacht:
                extra.append(naam_p)
        detail = "DEWI-boekingssysteem gecheckt (club %d)" % cid
        if kind_gezien and indicator is None:
            detail += "; kinderzwemles-inschrijving open zonder wachtlijst-vermelding"
        if extra:
            detail += "; wachtlijst gemeld bij: " + ", ".join(sorted(set(extra))[:3])
        rec = {
            "id": koppel[0] if koppel else "dewi-%d" % cid,
            "naam": koppel[1] if koppel else ("Optisport " + clubnaam.replace("Optisport", "").strip()),
            "plaats": koppel[2] if koppel else "",
            "prov": koppel[3] if koppel else "",
            "groep": "optisport",
            "indicator": indicator,
            "dewi_club": cid,
            "dewi_detail": detail,
        }
        out.append(rec)
    return out

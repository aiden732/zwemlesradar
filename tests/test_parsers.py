import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "scrapers"))
from parsers import parse_dataduiker_lesdagen, parse_vrije_tekst, parse_range

# --- parser 2: Dataduiker-module op de Vallei-fixture ---
html = (pathlib.Path(__file__).parent / "fixture_vallei.html").read_text()
m = parse_dataduiker_lesdagen(html)
print(f"Dataduiker-parser: {len(m)} lesmomenten met wachttijd")
for x in m:
    print(f"  {x['label']:38} {x['raw']:15} -> {x['lo']:.0f}-{x['hi']:.0f} mnd")
assert len(m) == 22, f"verwacht 22, kreeg {len(m)}"
los = [x['lo'] for x in m] + [x['hi'] for x in m]
print(f"  => spreiding: {min(los):.0f}-{max(los):.0f} mnd | kortste: di/do & ma 14:45 | langste: za 09:00")
assert min(los) == 6 and max(los) == 17

# --- parser 1: vrije-tekst op echte publicisten-zinnen ---
zinnen = """
<p>Is er een wachtlijst? Jazeker. De wachttijd is op het moment van inschrijven minimaal 1,5 jaar.</p>
<p>Houd rekening met een wachtlijst van 9 maanden tot een jaar.</p>
<p>Op dit moment hebben we een wachtlijst van zes maanden voor zwemdiploma A.</p>
<p>De wachttijd voor zwemlessen bedraagt momenteel 9 maanden.</p>
<p>We hebben op dit moment een wachtlijst van anderhalf jaar.</p>
<p>De wachtlijst varieert, gemiddeld is deze 3 maanden.</p>
<p>Volwassenen: op dit moment hebben we een wachtlijst van een jaar.</p>
"""
t = parse_vrije_tekst(zinnen)
print(f"\nVrije-tekst-parser: {len(t)} waarden uit 7 echte publicisten-zinnen")
for x in t:
    hi = f"-{x['hi']:.0f}" if x['hi'] and x['hi'] != x['lo'] else ""
    print(f"  {x['lo']:.1f}{hi} mnd  <- \"{x['raw'][:70]}\"")
assert len(t) == 7
assert parse_range("minimaal 1,5 jaar") == (18.0, None)
assert parse_range("9 maanden tot een jaar") == (9.0, 12.0)
print("\nALLE TESTS GESLAAGD")

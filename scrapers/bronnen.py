"""
Bronregistry. Elke bron heeft een lijst kandidaat-URL's; run.py probeert ze
op volgorde en crawlt daarna 1 niveau diep (links met zwemles/wachtlijst/faq).
parser: "dataduiker" | "tekst" | "sportfondsen".
"""
BRONNEN = [
 dict(id="vallei-veenendaal", naam="Zwembad De Vallei", plaats="Veenendaal", prov="Utrecht", parser="dataduiker",
      urls=["https://www.sportserviceveenendaal.nl/zwemles-dagen-en-tijden"]),
 dict(id="helsdingen-vianen", naam="Helsdingen", plaats="Vianen", prov="Utrecht", parser="tekst",
      urls=["https://www.helsdingen.nl/zwemmen/zwemles/veel-gestelde-vragen/"]),
 dict(id="koploper-lelystad", naam="De Koploper", plaats="Lelystad", prov="Flevoland", parser="tekst",
      urls=["https://www.sportbedrijf.nl/veelgestelde-vragen", "https://www.sportbedrijf.nl/zwemles", "https://www.sportbedrijf.nl/"]),
 dict(id="tropiqua-veendam", naam="Tropiqua", plaats="Veendam", prov="Groningen", parser="tekst",
      urls=["https://www.tropiqua.nl/zwemles/"]),
 dict(id="sport050-groningen", naam="Sport050", plaats="Groningen", prov="Groningen", parser="tekst",
      urls=["https://sport050.nl/sporten/zwemmen/zwemles-volwassenen/", "https://sport050.nl/sporten/zwemmen/zwemles-kinderen/", "https://sport050.nl/"]),
 dict(id="dehout-alkmaar", naam="Zwembad De Hout", plaats="Alkmaar", prov="Noord-Holland", parser="tekst",
      urls=["https://www.zwembaddehout.nl/zwemles/", "https://www.zwembaddehout.nl/", "https://www.alkmaarsport.nl/zwemles"]),
 dict(id="hoornsevaart-alkmaar", naam="Hoornse Vaart", plaats="Alkmaar", prov="Noord-Holland", parser="tekst",
      urls=["https://www.hoornsevaart.nl/zwemles/", "https://www.hoornsevaart.nl/"]),
 dict(id="drijver-hoofddorp", naam="Zwemschool de Drijver", plaats="Hoofddorp e.o.", prov="Noord-Holland", parser="tekst",
      urls=["https://www.zwemschooldedrijver.nl/zwemles/", "https://www.zwemschooldedrijver.nl/"]),
 dict(id="unikco-drachten", naam="Zwemschool Unikco", plaats="Drachten", prov="Friesland", parser="tekst",
      urls=["https://www.zwemschoolunikco.nl/zwemles/", "https://www.zwemschoolunikco.nl/"]),
 dict(id="watervrienden-venlo", naam="Watervrienden Venlo", plaats="Venlo", prov="Limburg", parser="tekst",
      urls=["https://www.watervriendenvenlo.nl/zwemles/", "https://www.watervriendenvenlo.nl/"]),
 dict(id="bvsport-leeuwarden", naam="bv SPORT", plaats="Leeuwarden", prov="Friesland", parser="tekst",
      urls=["https://www.bvsport.nl/zwemlessen/", "https://www.bvsport.nl/"]),
 dict(id="sportiom-denbosch", naam="Sportiom", plaats="Den Bosch", prov="Noord-Brabant", parser="tekst",
      urls=["https://www.sportiom.nl/zwemmen/zwemles/", "https://www.sportiom.nl/"]),
 dict(id="arnhem-perbad", naam="Sportbedrijf Arnhem (beide baden)", plaats="Arnhem", prov="Gelderland", parser="tekst",
      urls=["https://www.sportbedrijfarnhem.nl/klantenservice/veelgestelde-vragen/"]),
 dict(id="rotterdam-oostelijk", naam="Sportfondsen Oostelijk Zwembad", plaats="Rotterdam", prov="Zuid-Holland", parser="sportfondsen",
      urls=["https://oostelijkzwembad.sportfondsen.nl/ik-ben-nieuw/wachtlijst/"]),
 dict(id="rotterdam-oostervant", naam="Recreatiecentrum Oostervant", plaats="Rotterdam", prov="Zuid-Holland", parser="sportfondsen",
      urls=["https://oostervant.sportfondsen.nl/ik-ben-nieuw/wachtlijst/"]),
 dict(id="rotterdam-sportbedrijf", naam="Sportbedrijf Rotterdam (zwemles)", plaats="Rotterdam", prov="Zuid-Holland", parser="tekst",
      urls=["https://www.sportbedrijfrotterdam.nl/zwemles-test-wachttijden"]),
]

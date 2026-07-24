"""
Bronregistry voor parser 1 + 2.
DAG-1-TAAK: URL's met # TODO eenmalig in de browser verifieren;
run.py rapporteert per bron netjes of hij faalt.
parser: "dataduiker" (lesdagen-tabellen) of "tekst" (vrije-tekst-zinnen).
"""
BRONNEN = [
 dict(id="vallei-veenendaal", naam="Zwembad De Vallei", plaats="Veenendaal", prov="Utrecht",
      url="https://www.sportserviceveenendaal.nl/zwemles-dagen-en-tijden", parser="dataduiker"),
 dict(id="helsdingen-vianen", naam="Helsdingen Sport en Cultuur", plaats="Vianen", prov="Utrecht",
      url="https://www.helsdingen.nl/zwemmen/zwemles/veel-gestelde-vragen/", parser="tekst"),
 dict(id="koploper-lelystad", naam="De Koploper", plaats="Lelystad", prov="Flevoland",
      url="https://www.sportbedrijf.nl/zwemmen/zwemles", parser="tekst"),  # TODO exacte FAQ-URL
 dict(id="tropiqua-veendam", naam="Tropiqua", plaats="Veendam", prov="Groningen",
      url="https://www.tropiqua.nl/zwemles/", parser="tekst"),
 dict(id="sport050-groningen", naam="Sport050 (Kardinge e.a.)", plaats="Groningen", prov="Groningen",
      url="https://sport050.nl/zwemmen/zwemles/", parser="tekst"),  # TODO
 dict(id="dehout-alkmaar", naam="Zwembad De Hout", plaats="Alkmaar", prov="Noord-Holland",
      url="https://www.zwembaddehout.nl/zwemles/", parser="tekst"),  # TODO
 dict(id="hoornsevaart-alkmaar", naam="Hoornse Vaart", plaats="Alkmaar", prov="Noord-Holland",
      url="https://www.hoornsevaart.nl/zwemles/", parser="tekst"),  # TODO
 dict(id="drijver-hoofddorp", naam="Zwemschool de Drijver", plaats="Hoofddorp e.o.", prov="Noord-Holland",
      url="https://www.zwemschooldedrijver.nl/veelgestelde-vragen/", parser="tekst"),  # TODO
 dict(id="unikco-drachten", naam="Zwemschool Unikco", plaats="Drachten", prov="Friesland",
      url="https://www.zwemschoolunikco.nl/", parser="tekst"),
 dict(id="watervrienden-venlo", naam="Watervrienden Venlo", plaats="Venlo", prov="Limburg",
      url="https://www.watervriendenvenlo.nl/", parser="tekst"),
 dict(id="bvsport-leeuwarden", naam="bv SPORT", plaats="Leeuwarden", prov="Friesland",
      url="https://www.bvsport.nl/zwemles/", parser="tekst"),  # TODO
 dict(id="sportiom-denbosch", naam="Sportiom", plaats="Den Bosch", prov="Noord-Brabant",
      url="https://www.sportiom.nl/zwemles/", parser="tekst"),  # TODO
 dict(id="arnhem-perbad", naam="Sportbedrijf Arnhem (per bad)", plaats="Arnhem", prov="Gelderland",
      url="https://www.sportinarnhem.nl/zwemles/", parser="tekst"),  # TODO
 dict(id="rotterdam-wachttijden", naam="Zwembaden Rotterdam (wachttijd-tab)", plaats="Rotterdam", prov="Zuid-Holland",
      url="https://www.zwembadenrotterdam.nl/zwemles/", parser="tekst"),  # TODO
]

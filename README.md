# ZwemlesRadar-scraper

Haalt dagelijks publiek gepubliceerde zwemles-wachttijden op en schrijft ze
naar `data/wachttijden.json` (met peildatum per bron). Kost niets, draait
op GitHub Actions, geen server nodig.

## Zelf draaien
    pip install requests beautifulsoup4
    python run.py

## Automatisch (eenmalige setup, ±10 min)
1. Maak een gratis GitHub-account en een nieuwe repository (public).
2. Upload deze map (of push met git).
3. Tab **Actions** -> workflow "Dagelijkse wachttijd-scrape" -> **Enable**
   -> knop **Run workflow** voor de eerste run.
4. Vanaf nu draait hij elke ochtend en commit hij verse data.

## Dag-1-taak
In `scrapers/bronnen.py` staan URL's met `# TODO`: die eenmalig in de
browser controleren (juiste zwemles-/FAQ-pagina) en aanpassen. `run.py`
laat per bron zien of hij werkt.

## Site koppelen (stap 2)
De kaart (index.html) leest straks `data/wachttijden.json` — via Netlify
uit dezelfde repo, of rechtstreeks van
`https://raw.githubusercontent.com/<user>/<repo>/main/data/wachttijden.json`.

## Uitbreiden
- Parser 2: meer Dataduiker-klanten met de "Zwemles dagen en tijden"-module.
- Parser 3: Optisport/DEWI Online (club-ID per locatie).
- Parser 4: portaal-bezetting (Zwemscore, Recreatex, SportCom, Sportfondsen).

## Site + data samen live (aangeraden opzet)
`index.html` (de kaart) staat in deze zelfde repo en leest `data/wachttijden.json`.
1. Push deze map naar GitHub (zie hierboven).
2. Netlify -> **Add new site** -> **Import an existing project** -> kies deze
   GitHub-repo. Build command: *(leeg)*, publish directory: `/` (root).
3. Klaar: elke ochtend commit de bot verse data en deployt Netlify de site
   automatisch opnieuw. De kaart toont per bron de eigen peildatum
   ("LIVE: ... vandaag ververst").
Zonder `wachttijden.json` (of als een bron faalt) draait de kaart gewoon op
de ingebakken dataset — er kan niets stuk.

"""Sangam Europa website (v2) — static site generator.

Run:  python3 build.py
Pages are written to public/, the only folder that is published. Every page is regenerated from the content in this file and from data/india-europe-datapack.csv.
Facts were checked on 17 October 2026 against the sources listed in SOURCES; see ../research/.
"""
import csv, html, os, re

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'public')   # the published site: everything in here goes online, nothing outside it
AS_OF = '17 October 2026'
CONTACT_EMAIL = 'tony@sangam-europa.com'

FONTS = ('<link rel="preload" href="assets/fonts/source-serif-4-latin.woff2" as="font" type="font/woff2" crossorigin>'
         '<link rel="preload" href="assets/fonts/montserrat-latin.woff2" as="font" type="font/woff2" crossorigin>'
         '<link rel="stylesheet" href="assets/fonts/fonts.css">')

def esc(s): return html.escape(s, quote=True)

# ---------------------------------------------------------------- sources
SOURCES = {
 'ec_india': ('European Commission, DG Trade: EU trade relations with India', 'https://policy.trade.ec.europa.eu/eu-trade-relationships-country-and-region/countries-and-regions/india_en'),
 'ec_memo': ('European Commission: EU–India FTA, chapter-by-chapter summary', 'https://policy.trade.ec.europa.eu/eu-trade-relationships-country-and-region/countries-and-regions/india/eu-india-agreements/memo-eu-india-free-trade-agreement-chapter-chapter-summary_en'),
 'ec_topic': ('European Commission: The EU–India trade agreement', 'https://commission.europa.eu/topics/trade/eu-india-trade-agreement_en'),
 'eeas_fta': ('EEAS / European Commission: EU and India conclude landmark free trade agreement, 27 Jan 2026', 'https://www.eeas.europa.eu/delegations/malawi/eu-and-india-conclude-landmark-free-trade-agreement_en'),
 'ep_train': ('European Parliament, Legislative Train: EU–India FTA, investment and GI agreements', 'https://www.europarl.europa.eu/legislative-train/theme-a-global-europe-leveraging-our-power-and-partnerships/file-eu-india-fta-bit-and-gi-agreement'),
 'hindu_dec16': ('The Hindu (summary by Vision IAS), 24 Sep 2026: signature reported for 16 Dec 2026', 'https://visionias.in/current-affairs/upsc-daily-news-summary/article/2026-09-24/the-hindu/international-relations/india-eu-fta-to-be-signed-on-december-16'),
 'reuters_cbam': ('Reuters (via bilaterals.org), 27 Jan 2026: CBAM in the EU–India deal', 'https://www.bilaterals.org/eu-india-trade-deal-leaves-bloc-s'),
 'reuters_steel': ('Reuters (via Euronext), 14 Sep 2026: steel quotas', 'https://live.euronext.com/en/financial-news/india-gains-wider-eu-steel-access-carbon-levy-remains'),
 'ie_data': ('Indian Express (summary by SuperKalam), 2 Mar 2026: data flows deferred to review', 'https://superkalam.com/current-affairs/02-03-2026/data-flows-india-eu-kick-can-down-the-road-to-review-later-pg12-37a6c764-6d72-43fc-a6eb-d57acfd79e50'),
 'council_5727': ('Council of the EU: Joint Statement, 16th EU–India Summit, 27 Jan 2026 (ST 5727/26)', 'https://data.consilium.europa.eu/doc/document/ST-5727-2026-INIT/en/pdf'),
 'eeas_sdp': ('EEAS: EU and India sign Security and Defence Partnership, 27 Jan 2026', 'https://eeas.europa.eu/eeas/security-and-defence-eu-and-india-sign-security-defence-partnership_en'),
 'eeas_sdd': ('EEAS: 1st EU–India Security and Defence Dialogue, New Delhi, 6 Mar 2026', 'https://www.eeas.europa.eu/eeas/eu-india-1st-security-and-defence-dialogue-held-new-delhi_en'),
 'join2025': ('EEAS/Commission: A New Strategic EU–India Agenda, JOIN(2025) 50, 17 Sep 2025', 'https://www.eeas.europa.eu/sites/default/files/2025/documents/JOIN_2025_50_1_EN_ACT_part1_v9.pdf'),
 'aa_75': ('Auswärtiges Amt: 75 years of Germany–India relations', 'https://www.auswaertiges-amt.de/en/aussenpolitik/laenderinformationen/indien-node/75-years-india-germany-2759238'),
 'pib_js': ('India–Germany Joint Statement, 12 Jan 2026 (PIB)', 'https://www.pib.gov.in/PressReleasePage.aspx?PRID=2213744'),
 'mea_eu': ('Ministry of External Affairs of India: India–EU relations brief, July 2026', 'https://www.mea.gov.in/Portal/ForeignRelation/India-European_Union_July_2026.pdf'),
 'mea_de': ('MEA briefing on the 7th India–Germany IGC, 25 Oct 2024 (via GlobalSecurity)', 'https://www.globalsecurity.org/wmd/library/news/india/2024/india-241025-india-meab01.htm'),
 'ani_imec': ('ANI, 6 Oct 2026: IMEC ministerial hoped for by year-end', 'https://www.aninews.in/news/world/asia/egypt-lebanon-oman-greece-cyprus-keen-to-join-imec-ministerial-meet-likely-later-this-year-france16020261006192339/'),
 'ians_wieck': ('IANS, 13 Aug 2026: new German Ambassador Jasper Wieck', 'https://ianslive.in/want-to-serve-as-catalyst-to-take-indo-german-friendship-to-new-level-new-german-envoy--20260813191016'),
 'embassy_brief': ('Embassy of India, Berlin: bilateral brief, 15 Jun 2026', 'https://indianembassyberlin.gov.in/pdf/menu/Bilateral_Brief_as_on_15_June_2026.pdf'),
 'ttc3': ('European Commission: Joint statement, 3rd EU–India Trade and Technology Council, 15 Jul 2026', 'https://digital-strategy.ec.europa.eu/en/library/joint-statement-third-meeting-eu-india-trade-and-technology-council'),
 'bruegel': ('Bruegel Policy Brief 18/2026 (Sep 2026): Europe’s share of AI compute', 'https://www.bruegel.org/sites/default/files/2026-09/PB%2018%202026.pdf'),
 'scibus': ('Science|Business, 16 Jul 2026: India starts formal Horizon Europe talks', 'https://sciencebusiness.net/news/horizon-europe/india-starts-formal-talks-horizon-europe-association'),
 'amgreen': ('Energética India, 30 Sep 2026: AM Green wins H2Global Asian lot', 'https://www.energetica-india.net/news/am-green-wins-h2global-asian-lot-for-eur-585-million-green-ammonia-deal'),
 'aerzte': ('Deutsches Ärzteblatt, 21 Oct 2025: IW Köln study for Pro Generika', 'https://www.aerzteblatt.de/news/abhangigkeit-von-china-wachsendes-risiko-fur-arzneimittelversorgung-a771ebe9-f1a0-4a2d-b04e-ad73482016ef'),
 'bk': ('Federal Chancellor: Chancellor’s trip to India, 12 Jan 2026', 'https://www.bundeskanzler.de/bk-en/news/chancellor-trip-india-2402282'),
 'gtai': ('Germany Trade & Invest, 5 Jun 2026: German–Indian trade (Destatis, preliminary)', 'https://www.gtai.de/de/trade/indien/wirtschaftsumfeld/aussenhandel-mit-deutschland-804584'),
 'eurostat_valid': ('Eurostat migr_resvalid: valid residence permits, Indian citizens, EU-27', 'https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/migr_resvalid?citizen=IN&geo=EU27_2020&reason=TOTAL&duration=TOTAL&unit=PER&sinceTimePeriod=2022'),
 'eurostat_first': ('Eurostat migr_resfirst: first residence permits, Indian citizens, EU-27', 'https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/migr_resfirst?citizen=IN&geo=EU27_2020&reason=TOTAL&duration=TOTAL&unit=PER&sinceTimePeriod=2022'),
 'destatis': ('Destatis: foreign population by citizenship (Central Register of Foreigners)', 'https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/Bevoelkerung/Migration-Integration/Tabellen/auslaendische-bevoelkerung-staatsangehoerigkeit-jahre.html'),
 'ww': ('DAAD/DZHW: Wissenschaft weltoffen kompakt 2026', 'https://www.pedocs.de/volltexte/2026/35348/pdf/Knuettgen_et_al_2026_Wissenschaft_weltoffen_kompakt.pdf'),
 'iw': ('IW Köln, Kurzbericht 1/2026: Indian employees in Germany', 'https://www.iwkoeln.de/studien/axel-pluennecke-indische-beschaeftigte-verdienen-weiterhin-am-meisten.html'),
 'eeas_lgo': ('EEAS Delegation to India: launch of the European Legal Gateway Office pilot', 'https://www.eeas.europa.eu/delegations/india/launch-european-legal-gateway-office-pilot_en'),
 'mea_mob': ('Ministry of External Affairs of India: labour mobility agreements', 'https://www.mea.gov.in/labour-mobility-agreements'),
 'bmi_mmpa': ('Federal Ministry of the Interior, 5 Dec 2022: India–Germany migration and mobility agreement', 'https://www.bmi.bund.de/SharedDocs/pressemitteilungen/EN/2022/12/migration_agreement.html'),
 'schengen': ('Travel Trade Journal, 2026: Schengen visa statistics 2025 (European Commission data)', 'https://traveltradejournal.com/schengen-visa-applications-near-12-million-in-2025-india-ranks-third-globally/'),
 'austriaca': ('Austrian Academy of Sciences Press: E. Franco, The Spitzer Manuscript (2004)', 'https://austriaca.at/3301-4'),
 'bbaw_dta': ('BBAW: Digital Turfan Archive', 'https://turfan.bbaw.de/dta-i-en.html'),
 'sbb': ('Staatsbibliothek zu Berlin: South Asian manuscripts', 'https://staatsbibliothek-berlin.de/en/about-the-library/departments/orient/translate-to-english-sammlungen/translate-to-english-handschriften/translate-to-english-suedasiatische-handschriften'),
 'herring': ('H. Herring (ed. and tr.), Hegel on the Episode of the Mahābhārata known by the name Bhagavad-Gītā by Wilhelm von Humboldt (ICPR)', 'https://icpr.in/wp-content/uploads/2024/01/Pdf-10.pdf'),
 'rosenkranz': ('K. Rosenkranz, Life of Hegel: the late critical essays', 'https://en.hegel.net/rosenkranz-life-of-hegel21-Late_Critical_Essays.htm'),
 'dta_schlegel': ('BBAW Deutsches Textarchiv: F. Schlegel, Über die Sprache und Weisheit der Indier (1808)', 'https://clarin.bbaw.de/en/objects/dta:1049/'),
 'kollwitz': ('Käthe-Kollwitz-Museum Berlin: Tagore in Berlin, 1930', 'https://www.kaethe-kollwitz.berlin/en/news/the-world-artist/'),
 'goethe': ('Goethe-Institut India: locations', 'https://goethe.de/ins/in/en/sta.html'),
 'iccr': ('ICCR: Tagore Centre Berlin', 'https://iccr.gov.in/indianculturalcenter/tagore-centre-berlin-germany'),
 'cama': ('Encyclopaedia Britannica: Bhikaiji Cama', 'https://www.britannica.com/biography/Bhikaiji-Cama'),
 'app': ('Urs App, Schopenhauer-Forschungsstelle Mainz (PDF)', 'https://download.uni-mainz.de/fb05-philosophie-schopenhauer/files/2020/03/2012_App.pdf'),
 'hartmann': ('J.-U. Hartmann, LMU Munich: Śakuntalā in Germany (PDF)', 'https://epub.ub.uni-muenchen.de/21357/1/21357.pdf'),
 'bopp': ('Encyclopaedia Britannica: Franz Bopp', 'https://www.britannica.com/biography/Franz-Bopp'),
 'wwi_schlegel': ('Who Was Who in Indology: August Wilhelm von Schlegel', 'https://whowaswho-indology.info/5708/schlegel-august-wilhelm-von'),
 'gifford': ('Gifford Lectures archive: Friedrich Max Müller', 'https://giffordarchives.org/node/335'),
 'vivek': ('vivekananda.net: chronology, September 1896', 'https://vivekananda.net/dates-1896-sep'),
 'hesse': ('Goethe-Institut: Hermann Hesse and India', 'https://www.goethe.de/ins/lk/en/kul/art/exo/22770175.html'),
 'grass': ('Outlook India: Günter Grass’s Show Your Tongue', 'https://outlookindia.com/culture-society/kali-as-metaphor-revisiting-gunter-grass-s-show-your-tongue--news-209318'),
 'humboldt_letter': ('Wilhelm von Humboldt to A. W. Schlegel, 18 Sep 1826 (Digital edition of A. W. Schlegel’s correspondence)', 'https://august-wilhelm-schlegel.de/briefedigital/letters/view_pdf/3147.pdf'),
 'local_bluecard': ('The Local, 4 Feb 2026: EU Blue Cards by nationality (Eurostat data)', 'https://www.thelocal.de/20260204/which-nationalities-get-the-most-eu-blue-cards-and-where-do-they-go'),
 'pew2026': ('Pew Research Center, 13 Aug 2026: Public opinion of India across 36 countries', 'https://www.pewresearch.org/short-reads/2026/08/13/public-opinion-of-india-is-mixed-across-36-countries/'),
 'asml': ('Malay Mail/AFP, 17 May 2026: ASML signs MoU with Tata Electronics', 'https://www.malaymail.com/news/money/2026/05/17/dutch-chip-giant-asml-signs-deal-with-tata-to-power-india-semiconductor-plant/220229'),
 'orf_sdp': ('ORF: The strategic logic of the India–EU Security and Defence Partnership (SIPRI data)', 'https://www.orfonline.org/expert-speak/the-strategic-logic-of-the-india-eu-security-and-defence-partnership'),
 'ey_cbam': ('EY, 2025: EU adopts CBAM Omnibus regulation', 'https://taxnews.ey.com/news/2025-2136-eu-adopts-cbam-omnibus-regulation'),
 'euiss': ('EUISS Brief 2/2026: The EU–India partnership', 'https://www.iss.europa.eu/sites/default/files/2026-01/Brief_2026-02_EU-India%20partnership.pdf'),
 'cidob': ('CIDOB: The EU–India relationship, key to Europe’s diversification strategy', 'https://www.cidob.org/en/publications/eu-india-relationship-key-europes-diversification-strategy'),
 'csis_re': ('CSIS: Rare earth export restrictions one year later', 'https://www.csis.org/analysis/rare-earth-export-restrictions-one-year-later'),
 'gmj_media': ('Global Media Journal, 2024: Stereotypes in German and US press coverage of India and China', 'https://doaj.org/article/275bb5a3d1a049d3bbcd58edf1670f41'),
 'wb_ppp': ('World Bank, World Development Indicators: GDP at purchasing-power parity, 2025', 'https://data.worldbank.org/indicator/NY.GDP.MKTP.PP.CD'),
 'ai_summit': ('European Commission, 20 Feb 2026: EU endorses the New Delhi AI Summit declaration', 'https://digital-strategy.ec.europa.eu/en/news/european-union-endorses-leaders-declaration-ai-summit-india'),
}

# ---------------------------------------------------------------- data pack
ROWS = list(csv.DictReader(open(os.path.join(OUT, 'data', 'india-europe-datapack.csv'), encoding='utf-8')))

def row(ind, ent, year=None, src=None):
    for r in ROWS:
        if r['indicator'] == ind and r['entity'] == ent and (year is None or r['year'].startswith(year)) and (src is None or r['source'].startswith(src)):
            return r
    raise KeyError((ind, ent, year, src))

def v(*a, **k): return float(row(*a, **k)['value'])

def r1(x): return f'{float(x)+1e-9:.1f}'

def num(x, d=0):
    s = f'{x:,.{d}f}'
    return s

# ---------------------------------------------------------------- shell
NAV = [('geopolitics', 'Geopolitics'), ('business-tech', 'Business & Tech'), ('culture', 'Philosophy, Art & Culture'), ('people', 'People-to-People'), ('briefing', 'Briefing')]

SHORT = {'herring': 'Herring, ICPR', 'rosenkranz': 'Rosenkranz, Life of Hegel', 'humboldt_letter': 'Humboldt to Schlegel, 1826',
 'eurostat_valid': 'Eurostat', 'eurostat_first': 'Eurostat', 'ww': 'DAAD/DZHW', 'iw': 'IW Köln', 'aerzte': 'IW Köln for Pro Generika, via Ärzteblatt',
 'hindu_dec16': 'The Hindu', 'ec_india': 'European Commission', 'ec_memo': 'European Commission', 'ec_topic': 'European Commission',
 'eeas_fta': 'European Commission', 'council_5727': 'Council of the EU', 'aa_75': 'Auswärtiges Amt', 'pib_js': 'Joint statement (PIB)',
 'mea_eu': 'Indian Ministry of External Affairs', 'mea_mob': 'Indian Ministry of External Affairs', 'mea_de': 'Indian Ministry of External Affairs',
 'ani_imec': 'ANI', 'ians_wieck': 'IANS', 'embassy_brief': 'Embassy of India, Berlin', 'ttc3': 'European Commission', 'bruegel': 'Bruegel',
 'scibus': 'Science|Business', 'amgreen': 'Energética India', 'destatis': 'Destatis', 'eeas_lgo': 'EEAS', 'eeas_sdp': 'EEAS', 'eeas_sdd': 'EEAS',
 'schengen': 'European Commission data', 'austriaca': 'Austrian Academy of Sciences', 'bbaw_dta': 'BBAW', 'sbb': 'Staatsbibliothek zu Berlin',
 'kollwitz': 'Käthe-Kollwitz-Museum', 'goethe': 'Goethe-Institut', 'iccr': 'ICCR', 'wb_ppp': 'World Bank', 'ep_train': 'European Parliament',
 'reuters_cbam': 'Reuters', 'reuters_steel': 'Reuters', 'ie_data': 'Indian Express', 'bmi_mmpa': 'Federal Ministry of the Interior',
 'join2025': 'European Commission', 'cama': 'Britannica', 'app': 'Urs App', 'hartmann': 'J.-U. Hartmann, LMU', 'bopp': 'Britannica',
 'wwi_schlegel': 'Who Was Who in Indology', 'gifford': 'Gifford Lectures archive', 'vivek': 'vivekananda.net', 'hesse': 'Goethe-Institut',
 'grass': 'Outlook India', 'local_bluecard': 'Eurostat, via The Local', 'pew2026': 'Pew Research Center', 'asml': 'AFP', 'orf_sdp': 'SIPRI data, via ORF', 'ey_cbam': 'EY', 'euiss': 'EUISS', 'cidob': 'CIDOB', 'csis_re': 'CSIS', 'gmj_media': 'Global Media Journal', 'dta_schlegel': 'Deutsches Textarchiv', 'gtai': 'GTAI', 'bk': 'Federal Chancellor', 'ai_summit': 'European Commission'}

def cite(keys):
    parts, seen = [], set()
    for k in keys:
        label, url = SOURCES[k]
        name = SHORT.get(k, label)
        if name in seen: continue
        seen.add(name)
        parts.append(f'<a href="{esc(url)}" rel="noopener" title="{esc(label)}">{esc(name)}</a>')
    return '<p class="src">' + ', '.join(parts) + '</p>'

class Page:
    def __init__(self): self.used = []
    def src(self, *keys):
        for k in keys:
            if k not in self.used: self.used.append(k)
        return cite(keys)
    def sources_block(self):
        if not self.used: return ''
        items = ''.join(f'<li><a href="{esc(SOURCES[k][1])}" rel="noopener">{esc(SOURCES[k][0])}</a></li>' for k in self.used)
        return f'<section class="sources" aria-labelledby="src-h"><h2 id="src-h">Sources</h2><ol>{items}</ol><p class="src asof">Facts and figures checked {AS_OF}.</p></section>'

def head(title, current=None, desc='Sangam Europa, a quarterly magazine on India and Europe.'):
    CUR = ' aria-current="page"'
    nav = ''.join(f'<a href="{k}.html"{CUR if current==k else ""}>{esc(n)}</a>' for k, n in NAV)
    nav_m = nav + f'<a href="about.html"{CUR if current=="about" else ""}>About</a>'
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} | Sangam Europa</title>
<meta name="color-scheme" content="light dark">
<meta name="description" content="{esc(desc)}">
<link rel="icon" href="assets/favicon.png">
{FONTS}
<link rel="stylesheet" href="assets/tokens.css">
<link rel="stylesheet" href="assets/site.css">
<link rel="stylesheet" href="assets/briefing.css">
<noscript><style>.menu-btn {{ display: none; }} @media (max-width: 899px) {{ .masthead {{ position: static; }} .nav-mobile {{ display: grid; }} }}</style></noscript>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="masthead" onkeydown="var n=document.getElementById('nav-mobile');if(event.key==='Escape'&amp;&amp;n.classList.contains('open')){{n.classList.remove('open');var b=this.querySelector('.menu-btn');b.setAttribute('aria-expanded','false');b.focus()}}">
 <div class="wrap">
  <div class="masthead-row">
   <a class="brand" href="index.html" aria-label="Sangam Europa home"><picture><source srcset="assets/logo-white.svg" media="(prefers-color-scheme: dark)"><img src="assets/logo.svg" alt="Sangam Europa"></picture></a>
   <nav class="nav" aria-label="Sections">{nav}</nav>
   <div class="masthead-action">
    <a class="btn btn-quiet btn-sm" href="about.html"{CUR if current=="about" else ""}><span>About</span></a>
    <button class="menu-btn" type="button" aria-expanded="false" aria-controls="nav-mobile" onclick="var n=document.getElementById('nav-mobile');var o=n.classList.toggle('open');this.setAttribute('aria-expanded',o)">Menu</button>
   </div>
  </div>
  <nav class="nav-mobile" id="nav-mobile" aria-label="Sections">{nav_m}</nav>
 </div>
 <div class="rule" aria-hidden="true"></div>
</header>
<main id="main">
'''

def contact_html():
    if CONTACT_EMAIL:
        return f'<a href="mailto:{esc(CONTACT_EMAIL)}">Write to the editorial board</a>'
    return '<span>Contact address to follow.</span>'

def band():
    btn = (f'<a class="btn btn-accent" href="mailto:{esc(CONTACT_EMAIL)}"><span>Write to the editors</span></a>' if CONTACT_EMAIL
           else '<a class="btn btn-accent" href="about.html#contact"><span>Contact the editors</span></a>')
    return f'''<section class="band" aria-labelledby="band-h">
 <div class="wrap">
  <div><h2 id="band-h">The first issue appears in November 2026.</h2><p>Embassies, ministries and research institutions that would like to receive the first issue or contribute to it can contact the editorial board.</p></div>
  <div>{btn}</div>
 </div>
</section>'''

def footer():
    secs = ''.join(f'<li><a href="{k}.html">{esc(n)}</a></li>' for k, n in NAV[:4])
    return f'''</main>
{band()}
<footer class="footer">
 <div class="wrap">
  <div><picture><source srcset="assets/logo-white.svg" media="(prefers-color-scheme: dark)"><img src="assets/logo.svg" alt="Sangam Europa"></picture><p>A quarterly magazine on India and Europe. Sangam (<span class="sanskrit" lang="sa">संगम</span>) means confluence.</p></div>
  <div><h2>Sections</h2><ul>{secs}</ul></div>
  <div><h2>Briefing</h2><ul><li><a href="fta.html">The trade agreement</a></li><li><a href="timeline.html">Timeline</a></li><li><a href="figures.html">In figures</a></li></ul></div>
  <div><h2>Magazine</h2><ul><li><a href="about.html">About</a></li><li><a href="about.html#board">Editorial board</a></li><li><a href="about.html#contact">Contact</a></li></ul></div>
 </div>
 <div class="footer-bottom"><div class="wrap"><span>© 2026 Sangam Europa, Berlin</span><span>Facts checked {AS_OF}</span></div></div>
</footer>
<script>addEventListener('beforeprint', function () {{ document.querySelectorAll('details').forEach(function (d) {{ d.open = true; }}); }});</script>
</body>
</html>
'''

def write(name, s):
    with open(os.path.join(OUT, name), 'w', encoding='utf-8') as f: f.write(s)

def fact(p, when, text, keys):
    return f'<li class="entry"><p class="when">{esc(when)}</p><div><p>{text}</p>{p.src(*keys)}</div></li>'

def planned(items):
    lis = ''.join(f'<li><h3>{esc(t)}</h3><p class="note">{esc(fmt)}</p></li>' for fmt, t, n in items)
    return f'<ul class="planned">{lis}</ul>'

# ---------------------------------------------------------------- sections
SECTIONS = {
 'geopolitics': dict(
   name='Geopolitics', tone='',
   standfirst='Foreign policy, security and the agreements between India, the European Union and its member states.',
   facts=[
    ('27 January 2026', 'The 16th EU–India Summit in New Delhi adopted <em>Towards 2030: A Joint India–European Union Comprehensive Strategic Agenda</em>. It replaces the Roadmap to 2025.', ['council_5727']),
    ('27 January 2026', 'The EU and India signed their first Security and Defence Partnership, covering 17 areas, including maritime and cyber security. The first Security and Defence Dialogue met in New Delhi on 6 March 2026.', ['eeas_sdp', 'eeas_sdd']),
    ('7 March 1951', 'Bonn and New Delhi agreed to exchange diplomatic missions. 2026 is the 75th year of relations; the Strategic Partnership dates from May 2000.', ['aa_75']),
    ('12–13 January 2026', 'Chancellor Merz visited Ahmedabad and Bengaluru, his first trip to Asia in office. The joint statement lists a defence-industrial roadmap and agreements on semiconductors and critical minerals. The 8th intergovernmental consultations are planned in Germany toward the end of 2026.', ['pib_js', 'aa_75']),
    ('September 2023 – October 2026', 'The India–Middle East–Europe Economic Corridor was agreed at the G20 in New Delhi by India, the US, Saudi Arabia, the UAE, France, Germany, Italy and the EU. Three years on, no ministerial meeting has been held; France’s envoy hopes for one by the end of 2026.', ['mea_eu', 'ani_imec']),
    ('2020–2024', 'France supplied 33% of India’s arms imports, up from 18% in 2016–2020; Russia’s share fell from 49% to 36%.', ['orf_sdp']),
    ('August 2026', 'Jasper Wieck took up his post as German Ambassador to India. He served as Deputy Head of Mission in New Delhi from 2017 to 2020.', ['ians_wieck']),
   ],
   planned=[
    ('Essay', 'What to expect from the 8th India–Germany government consultations', ''),
    ('Analysis', 'The EU–India strategic agenda to 2030', ''),
   ]),
 'business-tech': dict(
   name='Business & Tech', tone='saffron',
   standfirst='Trade, investment, technology and energy between India and Europe.',
   facts=[
    ('27 January 2026', 'Negotiations on the EU–India free trade agreement concluded on 27 January 2026. The Commission sent its proposals for signature to the Council on 11 September; signature is reported for 16 December 2026 and entry into force is expected in early 2027. <a href="fta.html">More on the trade agreement</a>.', ['ec_india', 'hindu_dec16']),
    ('2025', 'EU goods trade with India reached €118 billion. India is the EU’s ninth-largest trading partner in goods, with 2.3% of EU goods trade; for India, the EU accounts for 11.1% of its goods trade.', ['ec_india']),
    ('October 2025', 'India supplies about 37% of the active pharmaceutical ingredients used in the EU, more than any other country; China supplies about 24%.', ['aerzte']),
    ('15 July 2026', 'The third EU–India Trade and Technology Council in Brussels agreed to explore a joint AI roadmap and to link the EU’s chip pilot lines with India’s design facilities. Formal talks on India joining Horizon Europe began the same month.', ['ttc3', 'scibus']),
    ('2025–2026', 'The EU produces about 14% of world GDP at purchasing-power parity. Europe hosts about 5% of the world’s operational AI computing capacity, by Bruegel’s 2026 estimate.', ['wb_ppp', 'bruegel']),
    ('16 May 2026', 'ASML signed a memorandum of understanding with Tata Electronics to supply lithography equipment for the planned US$11 billion chip plant at Dholera, Gujarat.', ['asml']),
    ('From February 2027', 'EU importers of Indian steel and aluminium buy the first certificates under the EU’s carbon border adjustment mechanism (CBAM), for goods imported in 2026. The trade agreement gives India no exemption.', ['ey_cbam', 'reuters_cbam']),
    ('30 September 2026', 'India’s AM Green won the Asian lot of Germany’s H2Global tender: at least €585 million over ten years for green ammonia shipped from Kakinada, with first deliveries expected in 2029.', ['amgreen']),
   ],
   planned=[
    ('Analysis', 'India and Germany as partners in artificial intelligence', ''),
    ('Analysis', 'Where the Indian and European economies complement each other', ''),
    ('Report', 'India and Europe as aviation markets', ''),
    ('Report', 'German automotive suppliers in India', ''),
    ('Data', 'India and the EU in figures', ''),
   ]),
 'culture': dict(
   name='Philosophy, Art & Culture', tone='',
   standfirst='Philosophy, literature, art and music, and the long history of scholarly exchange between India and Germany.',
   facts=[
    ('Today', 'The Spitzer manuscript, palm-leaf fragments found on the Silk Road, is the oldest known philosophical manuscript in Sanskrit. It contains the oldest surviving list of the books of the Mahābhārata. Berlin’s Turfan collection of Silk Road manuscripts, about 40,000 fragments, is digitised and online.', ['austriaca', 'bbaw_dta']),
    ('Since 1823', 'The Staatsbibliothek zu Berlin holds about 10,000 South Asian manuscripts, more than 1,500 of them on palm leaf. Its first acquisitions were two Tamil palm-leaf manuscripts bought by Alexander von Humboldt in Paris in 1823.', ['sbb']),
    ('1825–1827', 'Wilhelm von Humboldt read two papers on the Bhagavad Gītā to the Prussian Academy of Sciences, on 30 June 1825 and 15 June 1826. Hegel answered in a long two-part review, published in 1827.', ['herring', 'rosenkranz']),
    ('11–17 July 1930', 'Rabindranath Tagore exhibited his paintings in Berlin and visited Albert Einstein at Caputh on 14 July.', ['kollwitz']),
    ('Today', 'There are six Goethe-Institutes (Max Mueller Bhavan) in India. The Tagore Centre in Berlin, run by the Indian Council for Cultural Relations, opened in 1994.', ['goethe', 'iccr']),
   ],
   quote=('“The Gītā seems to me, as much as a Platonic dialogue or a book of Aristotle, a metaphysical essay – if one could call a poem that.”', 'Wilhelm von Humboldt', 'letter to A. W. Schlegel, Tegel, 18 September 1826', 'German original: „die Gítá scheint mir ebenso wohl, wie ein Platonisches Gespräch oder ein Buch des Aristoteles, ein metaphysischer Aufsatz, wenn man ein Gedicht so nennen könnte“. Translation: Sangam Europa.', 'humboldt_letter'),
   planned=[
    ('Feature', 'The Spitzer manuscript in Berlin', ''),
    ('Essay', 'German philosophy and Indian thought', ''),
   ]),
 'people': dict(
   name='People-to-People', tone='saffron',
   standfirst='Students, professionals and families who live between India and Europe, and the institutions that support them.',
   facts=[
    ('31 December 2025', 'Indian citizens held 1,033,926 valid residence permits in the EU, up from 755,288 at the end of 2022. In 2025 the EU issued them 227,577 first permits, the most for work.', ['eurostat_valid', 'eurostat_first']),
    ('31 December 2025', '311,130 Indian citizens lived in Germany, two and a half times as many as in 2018 (124,095).', ['destatis']),
    ('Winter semester 2024/25', 'India was the largest country of origin for international students in Germany: 58,833 students, 14.6% of the total, ahead of China.', ['ww']),
    ('End of 2024', 'Full-time employees with Indian citizenship had the highest median monthly pay of any nationality in Germany: €5,393 gross.', ['iw']),
    ('2024', 'Indian citizens received 16,300 of about 78,100 EU Blue Cards, more than any other nationality. Germany issued 13,300 of them.', ['local_bluecard']),
    ('Spring 2026', '63% of Germans held a favourable view of India, up from 47% in 2023.', ['pew2026']),
    ('27 January 2026', 'The EU and India signed a memorandum on a comprehensive framework for mobility; member states take part by choice. The first European Legal Gateway Office opened in New Delhi on 18 February 2026, starting with IT professionals.', ['mea_mob', 'eeas_lgo']),
    ('2025', 'Indians filed about 1.15 million Schengen visa applications, the third-largest number of any nationality.', ['schengen']),
   ],
   planned=[
    ('Report', 'Indian–German families', ''),
    ('Profiles', 'Indian students and professionals in Germany', ''),
   ]),
}

def section_page(key):
    s = SECTIONS[key]; p = Page()
    facts = ''.join(fact(p, *f) for f in s['facts'])
    quote = ''
    if s.get('quote'):
        q, who, ctx, orig, k = s['quote']
        orig_html = re.sub('„(.*?)“', r'<span lang="de">„\1“</span>', esc(orig))
        quote = f'<figure class="quote"><div class="rule short" aria-hidden="true"></div><blockquote>{esc(q)}</blockquote><figcaption>{esc(who)}, <span>{esc(ctx)}</span></figcaption><p class="caption orig">{orig_html}</p>{p.src(k)}</figure>'
    body = head(s['name'], key, s['standfirst']) + f'''
<div class="wrap">
 <section class="section-hero"><h1 class="display-1">{esc(s["name"])}</h1><p class="standfirst">{esc(s["standfirst"])}</p></section>
 <section class="section" aria-labelledby="ctx-h">
  <div class="section-head"><h2 id="ctx-h">Background</h2></div>
  <ol class="ledger">{facts}</ol>
  {quote}
 </section>
 <section class="section" aria-labelledby="pl-h">
  <div class="section-head"><h2 id="pl-h">In preparation for issue one</h2></div>
  {planned(s["planned"])}
 </section>
 {p.sources_block()}
</div>
''' + footer()
    write(f'{key}.html', body)

# ---------------------------------------------------------------- FTA page
def fta_page():
    p = Page()
    steps = [
     ('done', 'Done', 'Negotiations concluded', '27 January 2026, at the 16th EU–India Summit in New Delhi.'),
     ('done', 'Done', 'Proposal to the Council', '11 September 2026: the Commission proposes signature and conclusion.'),
     ('next', 'Reported', 'Signature', 'Reported for 16 December 2026; not yet confirmed by the Council.'),
     ('', 'Expected', 'European Parliament consent', 'Expected one to two months after signature.'),
     ('', 'Expected', 'Entry into force', 'Expected in early 2027, after India’s approval.'),
    ]
    st = ''.join(f'<li class="{c}"><span class="state">{esc(s1)}</span><b>{esc(t)}</b><p>{esc(d)}</p></li>' for c, s1, t, d in steps)
    terms = [
     ('Tariff lines liberalised', 'More than 90% of lines (91% of trade value)', '86% of lines (93% of trade value)'),
     ('Cars', '–', 'From 110% to as low as 10%, within a quota of 250,000 vehicles a year'),
     ('Wine', '–', 'From 150% to 75% at entry into force, then down to 20–30%'),
     ('Spirits and beer', '–', 'Spirits to 40%, beer to 50%'),
     ('Machinery, chemicals, pharmaceuticals', '–', 'Tariffs of up to 44%, 22% and 11% largely removed'),
     ('Excluded by the EU', 'Beef, poultry, rice, sugar, milk powders, honey, among others', '–'),
     ('Small firms', 'A dedicated SME chapter with contact points on both sides', 'Same chapter'),
    ]
    tr = ''.join(f'<tr><th scope="row">{esc(a)}</th><td>{esc(b)}</td><td>{esc(c)}</td></tr>' for a, b, c in terms)
    s_terms = p.src('ec_memo', 'eeas_fta')
    outside = [
     ('Investment protection', 'Negotiated separately since June 2022; not concluded.', 'ep_train'),
     ('Geographical indications', 'A separate agreement, also still under negotiation.', 'ep_train'),
     ('Carbon border adjustment (CBAM)', 'No exemption. India receives an assurance that any flexibility the EU grants another country will also apply to India.', 'reuters_cbam'),
     ('Steel', 'Duty-free quotas, with volumes reported differently by the two sides; above quota, the EU’s 50% tariff applies.', 'reuters_steel'),
     ('Cross-border data flows', 'Deferred to a review within five years.', 'ie_data'),
     ('Movement of people', 'Short-term mobility of professionals is covered in the services chapter. Wider labour mobility runs through a separate EU–India memorandum signed the same day.', 'ec_memo'),
    ]
    out = ''.join(fact(p, a, esc(b), [k]) for a, b, k in outside)
    body = head('The EU–India trade agreement', 'briefing', 'Status, terms and open questions of the EU–India free trade agreement.') + f'''
<div class="wrap">
 <section class="section-hero"><h1 class="display-1">The EU–India trade agreement</h1><p class="standfirst">Talks began in 2007, stalled in 2013 and resumed in June 2022. The text was concluded in January 2026; it has not yet been signed.</p></section>
 <section class="section" aria-labelledby="st-h">
  <div class="section-head"><h2 id="st-h">Where it stands</h2></div>
  <ol class="steps">{st}</ol>
  {p.src('ec_india', 'hindu_dec16', 'ep_train')}
 </section>
 <section class="section" aria-labelledby="tm-h">
  <div class="section-head"><h2 id="tm-h">Main terms</h2></div>
  <div class="table-wrap" role="region" aria-labelledby="tm-h" tabindex="0"><table class="data"><thead><tr><th scope="col">Area</th><th scope="col">EU commitments</th><th scope="col">India’s commitments</th></tr></thead><tbody>{tr}</tbody></table></div>
  {s_terms}
  <ol class="ledger" style="margin-top:var(--space-8)">
   {fact(p, '€4 bn a year', 'Duties EU exporters are expected to save, according to the European Commission.', ['eeas_fta'])}
   {fact(p, '€118 bn', 'EU–India goods trade in 2025, before the agreement takes effect.', ['ec_india'])}
   {fact(p, '~6,000', 'European companies present in India.', ['ec_topic'])}
  </ol>
 </section>
 <section class="section" aria-labelledby="out-h">
  <div class="section-head"><h2 id="out-h">Outside the agreement</h2></div>
  <ol class="ledger">{out}</ol>
 </section>
 {p.sources_block()}
</div>
''' + footer()
    write('fta.html', body)

# ---------------------------------------------------------------- timeline
TL = [
 ('1791', 'ideas', 'Georg Forster’s German <em>Śakuntalā</em>, translated from William Jones’s English version. Goethe’s verses on the play appear the same year.', 'hartmann'),
 ('1808', 'ideas', 'Friedrich Schlegel publishes <em lang="de">Über die Sprache und Weisheit der Indier</em> in Heidelberg.', 'dta_schlegel'),
 ('1816', 'ideas', 'Franz Bopp’s study of the Sanskrit verb system founds comparative Indo-European linguistics.', 'bopp'),
 ('1818', 'ideas', 'August Wilhelm Schlegel is appointed at the new University of Bonn, which becomes Germany’s first centre of Indology.', 'wwi_schlegel'),
 ('1823', 'ideas', 'A. W. Schlegel prints the Bhagavad Gītā with a Latin translation. Alexander von Humboldt buys two Tamil palm-leaf manuscripts in Paris, the first in Berlin’s collection.', ['wwi_schlegel', 'sbb']),
 ('1825', 'ideas', 'Wilhelm von Humboldt reads the first of two papers on the Bhagavad Gītā to the Prussian Academy of Sciences (30 June 1825; the second follows on 15 June 1826).', 'herring'),
 ('1827', 'ideas', 'Hegel replies to Humboldt in a two-part review in the <em lang="de">Jahrbücher für wissenschaftliche Kritik</em>.', 'herring'),
 ('1849', 'ideas', 'Max Müller’s edition of the Rig Veda begins to appear; six volumes follow by 1874, much of the printing paid for by the East India Company.', 'gifford'),
 ('1851', 'ideas', 'Schopenhauer calls the Upanishads, which he read in a Latin translation of a Persian one, “the solace of my life”.', 'app'),
 ('1896', 'ideas', 'Swami Vivekananda visits the philosopher Paul Deussen in Kiel and travels on with him to London.', 'vivek'),
 ('1907', 'states', 'Bhikaiji Cama raises an early Indian flag at the International Socialist Congress in Stuttgart.', 'cama'),
 ('1922', 'ideas', 'Hermann Hesse publishes <em>Siddhartha</em>; he never travelled to India itself.', 'hesse'),
 ('1930', 'ideas', 'Rabindranath Tagore shows his paintings in Berlin and visits Einstein at Caputh.', 'kollwitz'),
 ('1951', 'states', 'The Federal Republic and India agree to exchange diplomatic missions (7 March).', 'aa_75'),
 ('1962', 'states', 'India establishes relations with the European Economic Community.', 'mea_eu'),
 ('1972', 'states', 'India and the German Democratic Republic establish relations (8 October).', 'aa_75'),
 ('1988', 'ideas', 'Günter Grass publishes <em lang="de">Zunge zeigen</em>, written after a year in Calcutta.', 'grass'),
 ('1994', 'ideas', 'The Tagore Centre opens in Berlin.', 'iccr'),
 ('2000', 'states', 'India and Germany sign the agenda for their Strategic Partnership (May). The first EU–India Summit meets in Lisbon (June).', ['embassy_brief', 'mea_eu']),
 ('2004', 'states', 'The EU and India become strategic partners.', 'mea_eu'),
 ('2007', 'states', 'Negotiations on a broad trade and investment agreement begin.', 'ep_train'),
 ('2013', 'states', 'The trade talks stall after fifteen rounds.', ['ep_train', 'ec_topic']),
 ('2022', 'states', 'The trade talks are relaunched (17 June). India and Germany sign a migration and mobility agreement (5 December).', ['ep_train', 'bmi_mmpa']),
 ('2023', 'states', 'The first EU–India Trade and Technology Council meets (May). IMEC is agreed at the G20 in New Delhi (September).', 'mea_eu'),
 ('2024', 'states', 'Germany publishes its “Focus on India” strategy; the 7th intergovernmental consultations meet in New Delhi (October).', 'mea_de'),
 ('2025', 'states', 'The College of Commissioners visits India for the first time (February). The Commission and the High Representative propose “A New Strategic EU–India Agenda” (September).', 'join2025'),
 ('2026', 'states', 'Chancellor Merz in India (January). The EU–India Summit concludes the trade negotiations, adopts “Towards 2030” and signs a security and defence partnership (27 January).', 'council_5727'),
 ('2026', 'states', 'The third Trade and Technology Council meets in Brussels; formal talks on Horizon Europe begin (July). The Commission proposes signature of the trade agreement (September).', ['ttc3', 'scibus', 'ec_india']),
]

def timeline_page():
    p = Page()
    lis = []
    for yr, lane, text, k in TL:
        lab = 'Culture and scholarship' if lane == 'ideas' else 'Politics and trade'
        ks = k if isinstance(k, list) else [k]
        lis.append(f'<li><span class="yr">{yr}</span><div class="ev {lane}"><span class="lane">{lab}</span><p>{text}</p>{p.src(*ks)}</div></li>')
    body = head('Timeline', 'briefing', 'Two centuries of India and Germany, and India and Europe: ideas and institutions.') + f'''
<div class="wrap">
 <section class="section-hero"><h1 class="display-1">Timeline, 1791–2026</h1><p class="standfirst">Key dates in relations between India and Germany, and between India and Europe. Each entry is marked as culture and scholarship, or as politics and trade.</p></section>
 <div class="tl-key" aria-hidden="true"><span class="ideas">Culture and scholarship</span><span class="states">Politics and trade</span></div>
 <ol class="tl">{''.join(lis)}</ol>
 {p.sources_block()}
</div>
''' + footer()
    write('timeline.html', body)

# ---------------------------------------------------------------- figures
def bars(rows, unit='', d=0, maxv=None):
    """rows: list of (label, [(value, colourclass, text)])"""
    m = maxv or max(val for _, items in rows for val, _, _ in items)
    out = []
    for lab, items in rows:
        b = ''.join(f'<span class="bar"><i class="{c}" style="width:{max(val/m*100*0.82, 0.4):.2f}%"></i>{esc(t)}</span>' for val, c, t in items)
        out.append(f'<div class="bar-row"><span class="lab">{esc(lab)}</span><div class="bar-group">{b}</div></div>')
    return f'<div class="bars">{"".join(out)}</div>'

def datatable(label, head_cells, rows):
    th = ''.join(f'<th scope="col">{esc(h)}</th>' for h in head_cells)
    tr = ''.join('<tr>' + ''.join(f'<td class="n">{esc(str(c))}</td>' if i else f'<th scope="row">{esc(str(c))}</th>' for i, c in enumerate(r)) + '</tr>' for r in rows)
    return f'<details class="datatable"><summary>Show the numbers</summary><div class="table-wrap" role="region" aria-label="{esc(label)}, data table" tabindex="0"><table class="data"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div></details>'

DATA_SHORT = [('European Commission', 'European Commission'), ('World Bank', 'World Bank'), ('UN World Population', 'United Nations'),
 ('Eurostat', 'Eurostat'), ('Destatis', 'Destatis'), ('Global Carbon', 'Global Carbon Project'), ('Ember', 'Ember'), ('IMF', 'IMF')]

def src_rows(*rs):
    seen = []; parts = []; parts_names = []
    for r in rs:
        key = (r['source'], r['url'])
        if key in seen: continue
        seen.append(key)
        name = next((v for k, v in DATA_SHORT if r['source'].startswith(k)), r['source'])
        if name in [n for n, _ in parts_names]: continue
        parts_names.append((name, 1))
        parts.append(f'<a href="{esc(r["url"])}" rel="noopener" title="{esc(r["source"])}">{esc(name)}</a>')
    return '<p class="src">' + '; '.join(parts) + '</p>'

def legend(*items):
    return '<div class="legend">' + ''.join(f'<span><i class="{c}"></i>{esc(t)}</span>' for c, t in items) + '</div>'

def figures_page():
    p = Page()
    charts = []

    # 1 — how much each side matters to the other
    fdi_eu = row('EU FDI stock (outward position) in India', 'EU-27'); fdi_in = row('Indian FDI stock (inward position) in EU', 'India')
    a, b = float(fdi_eu['value'])/1000, float(fdi_in['value'])/1000
    charts.append(f'''<article class="chart" id="weight">
 <h2>How much each side matters to the other</h2>
 <p class="what">For the EU, India is the ninth-largest partner in goods. For India, the EU is among the three largest. Investment runs mostly one way: the stock of EU direct investment in India is almost ten times the reverse.</p>
 {legend(('c-blue','EU to India'),('c-saffron','India to the EU'))}
 {bars([('Share of the partner’s goods trade, 2025', [(11.1,'c-blue','EU in India’s trade: 11.1%'),(2.3,'c-saffron','India in the EU’s trade: 2.3%')])])}
 {bars([('Direct investment stock, 2024', [(a,'c-blue',f'EU in India: €{a:,.1f} bn'),(b,'c-saffron',f'India in the EU: €{b:,.1f} bn')])])}
 {datatable('How much each side matters to the other', ['Measure','EU in India','India in the EU'], [('Share of the partner’s goods trade, 2025, %','11.1','2.3'), ('Direct investment stock, 2024, € bn',f'{a:,.1f}',f'{b:,.1f}')])}
 {p.src('ec_india')}{src_rows(fdi_eu)}
</article>''')

    # 2 — what each sends the other (two-way)
    secs = ['Machinery and appliances','Chemical products','Textiles','Base metals','Transport equipment','Mineral products (incl. fuels)','Optical/medical instruments','Plastics and rubber','Pearls, precious metals','Vegetable products']
    data = []
    for s in secs:
        ex = row(f'EU exports to India by HS section: {s}', 'EU-27'); im = row(f'EU imports from India by HS section: {s}', 'EU-27')
        data.append((s, float(ex['value'])/1000, float(im['value'])/1000))
    m = max(max(x, y) for _, x, y in data)
    fr = ''.join(f'<div class="flow-row"><span class="lab">{esc(s.replace(" (incl. fuels)",""))}</span><span class="l"><span class="v">€{x:.1f} bn</span><i class="c-blue" style="width:{x/m*80:.1f}%"></i></span><span class="r"><i class="c-saffron" style="width:{y/m*80:.1f}%"></i><span class="v">€{y:.1f} bn</span></span></div>' for s, x, y in data)
    tot_ex = row('EU goods exports to India','EU-27','2025','European'); tot_im = row('EU goods imports from India','EU-27','2025','European')
    charts.append(f'''<article class="chart" id="flows">
 <h2>What each sends the other</h2>
 <p class="what">Goods trade by product group in 2025. Machinery travels in both directions in almost equal value; chemicals, textiles and metals flow mainly from India to Europe, transport equipment and instruments mainly from Europe to India. Totals: €{float(tot_ex["value"])/1000:.1f} bn from the EU to India, €{float(tot_im["value"])/1000:.1f} bn from India to the EU.</p>
 <div class="flow"><div class="flow-head"><span class="l">EU to India</span><span class="mid"></span><span class="r">India to the EU</span></div>{fr}</div>
 {datatable('What each sends the other', ['Product group','EU to India, € bn','India to the EU, € bn'], [(s, f'{x:.1f}', f'{y:.1f}') for s, x, y in data])}
 {src_rows(row('EU exports to India by HS section: Chemical products','EU-27'))}
</article>''')

    # 3 — goods trade over time
    yrs = ['2021','2022','2023','2024','2025']
    tt = [(y, float(row('EU goods exports to India','EU-27',y,'European')['value'])/1000, float(row('EU goods imports from India','EU-27',y,'European')['value'])/1000) for y in yrs]
    charts.append(f'''<article class="chart" id="trade-years">
 <h2>Goods trade, 2021–2025</h2>
 <p class="what">In each of the last five years the EU bought more from India than it sold there; since 2022 the gap has been €17–23 bn a year.</p>
 {legend(('c-blue','EU exports to India'),('c-saffron','EU imports from India'))}
 {bars([(y, [(x,'c-blue',f'Exports: €{x:.1f} bn'),(z,'c-saffron',f'Imports: €{z:.1f} bn')]) for y, x, z in tt])}
 {datatable('Goods trade, 2021–2025', ['Year','EU exports to India, € bn','EU imports from India, € bn'], [(y, f'{x:.1f}', f'{z:.1f}') for y, x, z in tt])}
 {src_rows(row('EU goods exports to India','EU-27','2025','European'))}
</article>''')

    # 4 — two age structures
    ma = [('India', row('Median age','India','2025','UN')), ('EU-27', row('Median age','EU-27','2025','Eurostat')), ('Germany', row('Median age','Germany','2025','UN'))]
    u25 = [('India', row('Share of population under 25','India')), ('EU-27', row('Share of population under 25','EU-27')), ('Germany', row('Share of population under 25','Germany'))]
    o65 = [('India', row('Share of population aged 65+','India','2025','World')), ('EU-27', row('Share of population aged 65+','EU-27','2025','World')), ('Germany', row('Share of population aged 65+','Germany','2025','World'))]
    col = {'India':'c-saffron','EU-27':'c-blue','Germany':'c-ink'}
    charts.append(f'''<article class="chart" id="age">
 <h2>Two age structures</h2>
 <p class="what">India’s median age is 29, the EU’s 45. Four in ten people in India are under 25, against one in four in the EU.</p>
 {legend(('c-saffron','India'),('c-blue','EU-27'),('c-ink','Germany'))}
 {bars([('Median age, years', [(float(r['value']), col[n], f'{n}: {float(r["value"]):.1f}') for n, r in ma])])}
 {bars([('Under 25, % of population', [(float(r['value']), col[n], f'{n}: {float(r["value"]):.1f}%') for n, r in u25]), ('65 and over, % of population', [(float(r['value']), col[n], f'{n}: {float(r["value"]):.1f}%') for n, r in o65])])}
 {datatable('Two age structures', ['Measure','India','EU-27','Germany'], [(lab, *[f'{float(r["value"]):.1f}' for _, r in rs]) for lab, rs in [('Median age, years', ma), ('Under 25, % of population', u25), ('65 and over, % of population', o65)]])}
 {src_rows(ma[0][1], ma[1][1], o65[0][1])}
</article>''')

    # 5 — size measured two ways
    def sh(ind, e): return row(ind, e, '2025', 'World')
    ents = ['India','EU-27','Germany']
    nom = {e: sh('Share of world GDP, nominal', e) for e in ents}; ppp = {e: sh('Share of world GDP, PPP', e) for e in ents}
    charts.append(f'''<article class="chart" id="size">
 <h2>The same economies, measured two ways</h2>
 <p class="what">At market exchange rates India produces 3.3% of world output; adjusted for what money buys at home, 8.1%. The EU’s share moves the other way.</p>
 {legend(('c-ink','At market exchange rates'),('c-blue','At purchasing-power parity'))}
 {bars([(e, [(float(nom[e]['value']),'c-ink',f'Market rates: {r1(nom[e]["value"])}%'),(float(ppp[e]['value']),'c-blue',f'PPP: {r1(ppp[e]["value"])}%')]) for e in ents])}
 {datatable('The same economies, measured two ways', ['Economy','Share of world GDP at market exchange rates, %','Share of world GDP at purchasing-power parity, %'], [(e, r1(nom[e]['value']), r1(ppp[e]['value'])) for e in ents])}
 <p class="caption">Share of world GDP, 2025.</p>{src_rows(nom['India'], ppp['India'])}
</article>''')

    # 6 — Indians in Germany
    ys = ['2018','2019','2020','2021','2022','2023','2024','2025']
    ig = [(y, row('Indian nationals resident in Germany','Germany',y)) for y in ys]
    charts.append(f'''<article class="chart" id="germany">
 <h2>Indian citizens living in Germany</h2>
 <p class="what">From 124,095 at the end of 2018 to 311,130 at the end of 2025.</p>
 {bars([(y, [(float(r['value']),'c-saffron',num(float(r['value'])))]) for y, r in ig])}
 {datatable('Indian citizens living in Germany', ['End of year','Indian citizens in Germany'], [(y, num(float(r['value']))) for y, r in ig])}
 {src_rows(ig[-1][1])}
</article>''')

    # 7 — emissions and electricity
    co2 = {e: row('CO2 emissions per capita', e, '2024', 'Global') for e in ents}
    clean = {e: row('Clean (low-carbon) share of electricity', e) for e in ents}
    charts.append(f'''<article class="chart" id="climate">
 <h2>Emissions per person, and clean power</h2>
 <p class="what">India emits more carbon dioxide in total than the EU, but less than half as much per person. Low-carbon sources produced 27% of India’s electricity in 2025 and 71% of the EU’s.</p>
 {legend(('c-saffron','India'),('c-blue','EU-27'),('c-ink','Germany'))}
 {bars([('CO₂ per person, tonnes, 2024', [(float(co2[e]['value']), col[e], f'{e}: {float(co2[e]["value"]):.1f} t') for e in ents])])}
 {bars([('Low-carbon electricity, 2025', [(float(clean[e]['value']), col[e], f'{e}: {float(clean[e]["value"]):.0f}%') for e in ents])], maxv=100)}
 {datatable('Emissions per person, and clean power', ['Measure','India','EU-27','Germany'], [('CO₂ per person, tonnes, 2024', *[f'{float(co2[e]["value"]):.1f}' for e in ents]), ('Low-carbon share of electricity, 2025, %', *[f'{float(clean[e]["value"]):.0f}' for e in ents])])}
 {src_rows(co2['India'], row('CO2 emissions, fossil (territorial)','India','2024','Global'), clean['India'], clean['EU-27'], clean['Germany'])}
</article>''')

    body = head('In figures', 'briefing', 'India and Europe compared, in sourced charts.') + f'''
<div class="wrap">
 <section class="section-hero"><h1 class="display-1">India and Europe in figures</h1><p class="standfirst">Selected figures on trade, investment, population and energy. Each chart gives its source, and the full data can be <a href="data/india-europe-datapack.csv" download>downloaded as a spreadsheet</a>.</p></section>
 {''.join(charts)}
 {p.sources_block()}
</div>
''' + footer()
    write('figures.html', body)

# ---------------------------------------------------------------- briefing hub
def briefing_page():
    body = head('Briefing', 'briefing', 'Sourced background on India and Europe: the trade agreement, a timeline and figures.') + f'''
<div class="wrap">
 <section class="section-hero"><h1 class="display-1">Briefing</h1><p class="standfirst">Background pages on the EU–India trade agreement, the history of relations and key figures. Each fact is dated and sourced.</p></section>
 <section class="section"><div class="brief-links">
  <a href="fta.html"><h2 class="title">The EU–India trade agreement</h2><p>Status, main terms and open issues.</p></a>
  <a href="timeline.html"><h2 class="title">Timeline, 1791–2026</h2><p>Key dates in culture, scholarship, politics and trade.</p></a>
  <a href="figures.html"><h2 class="title">India and Europe in figures</h2><p>Trade, investment, population and energy in charts.</p></a>
 </div></section>
 <p class="caption" style="padding-block:var(--space-8) var(--space-12)">Facts and figures checked {AS_OF}.</p>
</div>
''' + footer()
    write('briefing.html', body)

# ---------------------------------------------------------------- home
def _hermite(pts):
    """pts: [(x, y, slope)] -> function y(x), piecewise cubic Hermite."""
    def f(x):
        for (x0, y0, m0), (x1, y1, m1) in zip(pts, pts[1:]):
            if x0 <= x <= x1:
                h = x1 - x0; t = (x - x0) / h
                h00 = 2*t**3 - 3*t**2 + 1; h10 = t**3 - 2*t**2 + t; h01 = -2*t**3 + 3*t**2; h11 = t**3 - t**2
                return h00*y0 + h10*h*m0 + h01*y1 + h11*h*m1
        return pts[-1][1]
    return f

def _ease(t):
    t = max(0.0, min(1.0, t)); return t*t*(3 - 2*t)

def river():
    """Hero: EU–India goods trade 2025 drawn like the Sangam mark. Vertical band widths are to scale."""
    ex = row('EU goods exports to India','EU-27','2025','European'); im = row('EU goods imports from India','EU-27','2025','European')
    e, i = float(ex['value'])/1000, float(im['value'])/1000
    T = 150.0                                  # full width of the merged river, in viewBox units
    ws, wb = T*i/(i+e), T*e/(i+e)              # saffron = India to the EU, blue = the EU to India
    yc = 225.0                                 # centre of the merged tail
    x0, xfull, xm, xt, xe = 40, 330, 960, 1230, 1440
    tail_s = yc - T/2 + wb + ws/2              # saffron runs below blue in the tail
    tail_b = yc - T/2 + wb/2
    ys = _hermite([(x0, 205, -0.55), (360, 92, 0), (540, 232, 0.95), (700, 312, 0), (xm, tail_s, 0), (xe, tail_s, 0)])
    yb = _hermite([(x0, 238, 0.65), (250, 335, 0), (540, 222, -0.85), (700, 118, 0), (xm, tail_b, 0), (xe, tail_b, 0)])
    def outline(yfun, w, is_blue):
        xs = list(range(x0, xe + 1, 6)); top, bot = [], []
        for x in xs:
            g = _ease((x - x0) / (xfull - x0))          # pointed start, as in the mark
            k = 1.0 if x < xt else max(0.0, 1 - _ease((x - xt) / (xe - xt)))   # pointed tail
            if x < xt:
                yy, ww = yfun(x), w * g
            else:                                        # in the tail both bands narrow together
                total = T * k
                yy = (yc - total/2 + wb*k/2) if is_blue else (yc - total/2 + wb*k + ws*k/2)
                ww = w * k
            top.append((x, yy - ww/2)); bot.append((x, yy + ww/2))
        pts = top + bot[::-1]
        return 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts) + ' Z'
    pb, ps = outline(yb, wb, True), outline(ys, ws, False)
    svg = f'''<svg class="river-svg" viewBox="0 0 1440 440" preserveAspectRatio="none" aria-hidden="true" focusable="false">
  <defs>
   <linearGradient id="tailgrad" gradientUnits="userSpaceOnUse" x1="{xm-60}" y1="0" x2="{xe}" y2="0"><stop offset="0" class="stop-blue"/><stop offset="1" class="stop-saffron"/></linearGradient>
   <clipPath id="crossing"><rect x="470" y="0" width="150" height="440"/></clipPath>
   <clipPath id="reveal"><rect class="reveal" x="0" y="0" width="1440" height="440"/></clipPath>
  </defs>
  <g clip-path="url(#reveal)">
   <path class="cur-blue" d="{pb}" fill="url(#tailgrad)"/>
   <path class="cur-gap" d="{ps}" clip-path="url(#crossing)"/>
   <path class="cur-saffron" d="{ps}"/>
  </g>
</svg>'''
    legend = f'''<div class="river-key">
  <p><i class="sw c-saffron"></i><span>India to the EU</span><b>€{i:.1f} bn</b></p>
  <p><i class="sw c-blue"></i><span>EU to India</span><b>€{e:.1f} bn</b></p>
  <p class="sum"><span>Total, 2025</span><b>€{i+e:.1f} bn</b></p>
</div>'''
    return svg, legend, ex

def index_page():
    p = Page()
    ledger = [
     ('7 March 1951', 'Germany and India agreed to exchange diplomatic missions. 2026 marks 75 years of relations.', ['aa_75']),
     ('Winter 2024/25', 'India was the largest country of origin for international students in Germany: 58,833.', ['ww']),
     ('2025', 'About 37% of the active pharmaceutical ingredients used in the EU came from India, more than from any other country.', ['aerzte']),
     ('End of 2025', 'Indian citizens held 1,033,926 valid residence permits in the EU, up from 755,288 at the end of 2022.', ['eurostat_valid']),
     ('27 January 2026', 'The EU and India concluded their free trade negotiations, after talks that began in 2007. Signature is reported for 16 December 2026.', ['ec_india', 'hindu_dec16']),
    ]
    led = ''.join(fact(p, *x) for x in ledger)
    contents = ''
    for k in ['geopolitics','business-tech','culture','people']:
        sct = SECTIONS[k]
        items = ''.join(f'<li><span class="t">{esc(t)}</span><span class="f">{esc(fmt)}</span></li>' for fmt, t, n in sct['planned'])
        contents += f'<div class="toc-row"><h3><a href="{k}.html">{esc(sct["name"])}</a></h3><ul>{items}</ul></div>'
    svg, legend, ex = river()
    body = head('A quarterly magazine on India and Europe', None) + f'''
<section class="opening" aria-labelledby="hero-h">
 <div class="wrap opening-grid">
  <h1 class="headline-xl" id="hero-h">India and Europe, read in both directions.</h1>
  <div class="opening-side">
   <p class="standfirst">Sangam Europa is a quarterly magazine on relations between India and Europe, edited in Berlin. The first issue appears in November 2026.</p>
   <p><a class="btn btn-primary" href="about.html"><span>About the magazine</span></a></p>
  </div>
 </div>
 <figure class="river">
  {svg}
  <figcaption class="wrap">{legend}<p class="caption">Goods traded between India and the EU in 2025. Band widths are to scale.</p>{src_rows(ex)}</figcaption>
 </figure>
</section>
<div class="wrap">
 <section class="section why" aria-labelledby="why-h">
  <div class="section-head"><h2 id="why-h">Why now</h2><a class="more" href="about.html">Read more</a></div>
  <div class="why-grid">
   <p>US tariffs, Chinese export controls and closed shipping routes pushed the EU and India together in 2026. On 27 January they concluded a trade agreement and signed a defence partnership. Most of it is still to be implemented.</p>
   <p>Ties between people have grown faster than the institutions: more than a million residence permits, the largest share of EU Blue Cards, and rising goodwill in Germany. The magazine follows both.</p>
  </div>
  {p.src('ec_india', 'cidob', 'eurostat_valid', 'local_bluecard', 'pew2026')}
 </section>
 <section class="section" aria-labelledby="toc-h">
  <div class="section-head"><h2 id="toc-h">In preparation for issue one</h2></div>
  <div class="toc">{contents}</div>
 </section>
 <section class="section" aria-labelledby="now-h">
  <div class="section-head"><h2 id="now-h">Key facts</h2><a class="more" href="figures.html">More figures</a></div>
  <ol class="ledger">{led}</ol>
 </section>
 <section class="section" aria-labelledby="br-h">
  <div class="section-head"><h2 id="br-h">Briefing</h2></div>
  <div class="brief-links">
   <a href="fta.html"><h3 class="title-sm">The EU–India trade agreement</h3><p>Status and main terms.</p></a>
   <a href="timeline.html"><h3 class="title-sm">Timeline, 1791–2026</h3><p>Key dates since 1791.</p></a>
   <a href="figures.html"><h3 class="title-sm">India and Europe in figures</h3><p>Trade, investment, population and energy.</p></a>
  </div>
 </section>
 {p.sources_block()}
</div>
''' + footer()
    write('index.html', body)

# ---------------------------------------------------------------- about
BOARD = [
 ('Dr Vishnu Ramdeo', 'Editorial Board'),
 ('Luisa von Richthofen', 'Editorial Board'),
 ('Tushar Shetty', 'Editorial Board'),
 ('Shalu Yadav', 'Editorial Board'),
 ('Dr Renu Mann', 'Editorial Board'),
 ('Tony Siewert', 'Editorial Board'),
]

def about_page():
    p = Page()
    people = ''.join(f'<div><b>{esc(n)}</b><span>{esc(r)}</span></div>' for n, r in BOARD)
    why1 = p.src('ec_india', 'eeas_sdp', 'cidob', 'csis_re')
    why2 = p.src('eurostat_valid', 'local_bluecard', 'pew2026', 'gmj_media')
    body = head('About', 'about', 'About Sangam Europa, a quarterly magazine on India and Europe.') + f'''
<div class="wrap">
 <section class="section-hero"><h1 class="display-1">About Sangam Europa</h1><p class="standfirst">Sangam Europa is a platform dedicated to exploring and strengthening one of the most consequential partnerships of the 21st century: that between India and the European Union.</p></section>
 <div class="prose">
  <p>At a time of growing geopolitical uncertainty, shifting economic realities, technological disruption and intensifying climate challenges, we believe the India–EU relationship offers a compelling prospect for a more stable, democratic and prosperous global future. Bringing together diverse voices and perspectives, Sangam Europa examines how India and Europe can collaborate not only to navigate today’s challenges but also to shape tomorrow’s world.</p>
  <p>Co-initiated by journalists, young leaders and founding members of the Indo-German Young Leaders Forum, Sangam Europa serves as a forum for ideas, analysis and dialogue across the full spectrum of India–EU engagement.</p>
  <p>The magazine covers geopolitics, defence and security, trade and investment, technology and innovation, climate and sustainability, education, culture and people-to-people connections. Through original reporting, expert commentary, interviews and thought leadership, we seek to illuminate the opportunities, challenges and human stories that define this partnership.</p>
  <p>Sangam Europa wants to be more than a magazine. We want to be a bridge between two dynamic regions, to foster greater understanding and help shape a shared vision that gives hope in an increasingly multipolar world.</p>
  <h2>Why India and Europe, and why now</h2>
  <p>In January 2026 the EU and India concluded a free trade agreement and signed their first security and defence partnership. Both sides were reacting to the same pressures: US tariffs, Chinese export controls on critical materials, and disrupted shipping routes in the Gulf and the Red Sea. Most of what was agreed still has to be put into practice, and much of it depends on individual member states such as France and Germany.</p>
  {why1}
  <p>Ties between people have grown faster than the institutions. Indian citizens now hold more than a million residence permits in the EU and receive more EU Blue Cards than any other nationality, and the share of Germans with a favourable view of India rose from 47% in 2023 to 63% in 2026. Press coverage has not kept pace: a 2024 study of German and US newspapers found that reporting on India still leans on stereotypes. Sangam Europa sets out to report on the relationship in depth, from both sides.</p>
  {why2}
  <h2>How we work</h2>
  <p>Sangam Europa appears quarterly and is edited in Berlin. We begin with relations between India and Germany and will extend our coverage to the rest of Europe.</p>
  <p>We label each piece as reporting, interview, analysis or opinion. Every figure is given with its source and year. We give priority to subjects that will still matter in a few years.</p>
  <p>We try to understand each country on its own terms rather than measure one against the other.</p>
  <h2>The name</h2>
  <p>Sangam (<span class="sanskrit" lang="sa">संगम</span>) is the Sanskrit word for the confluence of two rivers. The best-known is at Prayagraj, where the Ganga and the Yamuna meet. Our logo shows two streams, saffron and blue, joining into one.</p>
  <h2>Working with us</h2>
  <p>We welcome contributions and interview proposals from diplomats, officials, researchers and practitioners in India and Europe. Institutions that would like to receive the magazine can write to the editorial board.</p>
  <h2 id="board">Editorial board</h2>
  <div class="people">{people}</div>
  <h2 id="contact">Contact</h2>
  <p>Sangam Europa, Berlin. {contact_html()}</p>
 </div>
 {p.sources_block()}
</div>
''' + footer()
    write('about.html', body)

# ---------------------------------------------------------------- build
# ledgers read oldest to newest
_ORDER = {
 'geopolitics': ['7 March 1951', '2020–2024', 'September 2023 – October 2026', '12–13 January 2026', '27 January 2026', 'August 2026'],
 'business-tech': ['October 2025', '2025', '2025–2026', '27 January 2026', '16 May 2026', '15 July 2026', '30 September 2026', 'From February 2027'],
 'culture': ['Since 1823', '1825–1827', '11–17 July 1930', 'Today'],
 'people': ['2024', 'End of 2024', 'Winter semester 2024/25', '2025', '31 December 2025', '27 January 2026', 'Spring 2026'],
}
for _k, _keys in _ORDER.items():
    SECTIONS[_k]['facts'] = sorted(SECTIONS[_k]['facts'], key=lambda f: _keys.index(f[0]))
for k in SECTIONS: section_page(k)
fta_page(); timeline_page(); figures_page(); briefing_page(); index_page(); about_page()
print('built', len(SECTIONS) + 6, 'pages')

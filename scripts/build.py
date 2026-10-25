"""Generate the static site from scripts/content.py."""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).parent))
import content as C

PHONE = C.PHONE_DISPLAY
TEL = C.PHONE_TEL
HOST = C.HOST
NAME = C.NAME
OG = f"{HOST}/images/vinyl-privacy.jpg"


def paras(items):
    return "\n".join(f"<p>{p}</p>" for p in items)


def steps(items):
    lis = []
    for i, (title, text) in enumerate(items, 1):
        lis.append(f"<li><span>{i}</span><h3>{title}</h3><p>{text}</p></li>")
    return '<ol class="steps">\n' + "\n".join(lis) + "\n</ol>"


def factors(items):
    cards = [f"<article class=\"factor\"><h3>{t}</h3><p>{p}</p></article>" for t, p in items]
    return '<div class="factor-grid">\n' + "\n".join(cards) + "\n</div>"


def faq_block(items):
    blocks = []
    for q, a in items:
        blocks.append(f"<details><summary>{q}</summary><p>{a}</p></details>")
    return '<div class="faq">\n' + "\n".join(blocks) + "\n</div>"


def chips(links):
    lis = [f'<li><a href="{href}">{label}</a></li>' for label, href in links]
    return '<ul class="related">\n' + "\n".join(lis) + "\n</ul>"


def service_cards():
    cards = []
    for s in C.SERVICES:
        cards.append(
            f"""<article class="service-card">
  <img src="{s["image"]}" alt="{s["alt"]}" width="{s["w"]}" height="{s["h"]}" loading="lazy" decoding="async">
  <div class="card-body">
    <h3><a href="{s["href"]}">{s["nav"]}</a></h3>
    <p>{s["card"]}</p>
    <p class="card-link"><a class="details" href="{s["href"]}">Details</a></p>
  </div>
</article>"""
        )
    return '<div class="service-list">\n' + "\n".join(cards) + "\n</div>"


def place_links(include_home=True):
    links = []
    for p in C.PLACES:
        if p["href"] == "/" and not include_home:
            continue
        links.append((p["name"], p["href"]))
    return links


def other_services(current):
    return [(s["nav"], s["href"]) for s in C.SERVICES if s["href"] != current]


FORM = """<iframe data-tally-src="https://tally.so/embed/xX6B0y?alignLeft=1&amp;hideTitle=1&amp;transparentBackground=1&amp;dynamicHeight=1&amp;source=Roanoke+VA+Fence+Company" width="100%" height="552" frameborder="0" marginheight="0" marginwidth="0" title="Get a free quote"></iframe>
<script>var d=document,w="https://tally.so/widgets/embed.js",v=function(){d.querySelectorAll("iframe[data-tally-src]:not([src])").forEach(function(e){e.src=e.dataset.tallySrc});if("undefined"!=typeof Tally)Tally.loadEmbeds()};if("undefined"!=typeof Tally)v();else if(d.querySelector('script[src="'+w+'"]')==null){var s=d.createElement("script");s.src=w,s.onload=v,s.onerror=v,d.body.appendChild(s);}else v();</script>"""


def cta(heading, text):
    return f"""<section class="band">
  <div class="wrap band-inner">
    <div class="band-copy">
      <h2>{heading}</h2>
      <p>{text}</p>
    </div>
    <div class="band-panel">
      <a class="band-phone" href="tel:{TEL}">{PHONE}</a>
      <div class="cta-actions">
        <a class="btn btn-solid" href="/contact.html#quote">Request an estimate</a>
        <a class="btn btn-ghost" href="tel:{TEL}">Call now</a>
      </div>
    </div>
  </div>
</section>"""


def crumbs(items):
    lis = []
    for label, href in items:
        if href:
            lis.append(f'<li><a href="{href}">{label}</a></li>')
        else:
            lis.append(f"<li>{label}</li>")
    return '<ol class="crumbs">' + "".join(lis) + "</ol>"


def hero_buttons(estimate):
    return f"""<div class="hero-actions">
  <a class="btn btn-solid" href="{estimate}">Request an estimate</a>
  <a class="btn btn-ghost" href="tel:{TEL}">Call {PHONE}</a>
</div>"""


def nav(current, estimate):
    service_items = ['<li><a href="/services.html">All services</a></li>']
    for s in C.SERVICES:
        current_attr = ' aria-current="page"' if s["href"] == current else ""
        service_items.append(f'<li><a href="{s["href"]}"{current_attr}>{s["nav"]}</a></li>')
    place_items = ['<li><a href="/service-areas.html">All service areas</a></li>']
    for p in C.PLACES:
        current_attr = ' aria-current="page"' if p["href"] == current else ""
        place_items.append(f'<li><a href="{p["href"]}"{current_attr}>{p["name"]}</a></li>')

    def top(href, label):
        attr = ' aria-current="page"' if href == current else ""
        return f'<li><a href="{href}"{attr}>{label}</a></li>'

    return f"""<nav class="site-nav" id="site-nav" aria-label="Primary">
  <ul>
    {top("/", "Home")}
    <li class="has-sub">
      <a href="/services.html">Services</a>
      <ul class="sub">
        {"".join(service_items)}
      </ul>
    </li>
    <li class="has-sub">
      <a href="/service-areas.html">Service area</a>
      <ul class="sub">
        {"".join(place_items)}
      </ul>
    </li>
    {top("/about.html", "About")}
    {top("/contact.html", "Contact")}
  </ul>
</nav>
<div class="header-actions">
  <a class="btn btn-ghost btn-call" href="tel:{TEL}" aria-label="Call {PHONE}">{PHONE_ICON}<strong><span class="call-long">Call {PHONE}</span><span class="call-short">Call</span></strong></a>
  <a class="btn btn-solid" href="{estimate}">Free estimate</a>
</div>"""


OFFICE_HOURS = "Monday–Sunday: 7:00 AM – 7:00 PM"
PHONE_ICON = '<svg class="phone-icon" width="18" height="18" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path fill="currentColor" d="M6.6 10.8c1.4 2.8 3.8 5.1 6.6 6.6l2.2-2.2c.3-.3.7-.4 1.1-.3 1.2.4 2.5.6 3.8.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1C10.6 21 3 13.4 3 4c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.6.6 3.8.1.4 0 .8-.3 1.1L6.6 10.8z"/></svg>'
MAP_SRC = "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d101622.894!2d-80.0442!3d37.27097!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x884d0e17c5f574c9%3A0x3c9ef7ee322576de!2sRoanoke%2C%20VA!5e0!3m2!1sen!2sus"


def phone_link(extra_class=""):
    cls = "phone-link" + (f" {extra_class}" if extra_class else "")
    return f'<a class="{cls}" href="tel:{TEL}">{PHONE_ICON}<strong>{PHONE}</strong></a>'


def map_embed(title="Roanoke VA Fence Company service area"):
    return f"""<div class="map-frame">
  <iframe src="{MAP_SRC}" width="600" height="450" style="border:0;" allowfullscreen loading="lazy" referrerpolicy="strict-origin-when-cross-origin" title="{title}"></iframe>
</div>"""


def footer(estimate):
    services = "\n".join(f'<li><a href="{s["href"]}">{s["nav"]}</a></li>' for s in C.SERVICES)
    return f"""<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <h2>Company</h2>
        <ul>
          <li><a href="/about.html">About</a></li>
          <li><a href="/contact.html">Contact</a></li>
          <li><a href="/faq.html">FAQ</a></li>
          <li>{phone_link()}</li>
        </ul>
      </div>
      <div>
        <h2>Services</h2>
        <ul>
          <li><a href="/services.html">All services</a></li>
          {services}
        </ul>
      </div>
      <div>
        <h2>Quick Links</h2>
        <ul>
          <li><a href="/">Home</a></li>
          <li><a href="/service-areas.html">Service areas</a></li>
          <li><a href="/faq.html">Fence questions</a></li>
          <li><a href="/blog.html">Blog</a></li>
          <li><a href="{estimate}">Request an estimate</a></li>
        </ul>
      </div>
      <div>
        <h2>Office Hours</h2>
        <p>{OFFICE_HOURS}</p>
        <p>{phone_link()}</p>
      </div>
    </div>
    <p class="legal">{NAME}. Roanoke, Virginia. {phone_link()}</p>
  </div>
</footer>
<div class="mobile-bar">
  <a class="btn btn-ghost" href="tel:{TEL}">{PHONE_ICON} Call</a>
  <a class="btn btn-solid" href="{estimate}">Estimate</a>
</div>"""


def graph(page):
    crumbs_ld = []
    for i, (label, href) in enumerate(page["crumbs"], 1):
        item = {"@type": "ListItem", "position": i, "name": label}
        if href:
            item["item"] = HOST + href
        else:
            item["item"] = page["canonical"]
        crumbs_ld.append(item)
    nodes = [
        {
            "@type": "HomeAndConstructionBusiness",
            "@id": HOST + "/#business",
            "name": NAME,
            "url": HOST + "/",
            "telephone": "+1-540-234-2867",
            "image": OG,
            "address": {
                "@type": "PostalAddress",
                "addressLocality": "Roanoke",
                "addressRegion": "VA",
                "addressCountry": "US",
            },
            "areaServed": [
                {"@type": "City", "name": "Roanoke"},
                {"@type": "City", "name": "Salem"},
                {"@type": "City", "name": "Vinton"},
                {"@type": "AdministrativeArea", "name": "Cave Spring"},
                {"@type": "AdministrativeArea", "name": "Hollins"},
                {"@type": "AdministrativeArea", "name": "Roanoke County"},
            ],
        },
        {
            "@type": "WebSite",
            "@id": HOST + "/#website",
            "url": HOST + "/",
            "name": NAME,
            "publisher": {"@id": HOST + "/#business"},
        },
        {
            "@type": "WebPage",
            "@id": page["canonical"] + "#webpage",
            "url": page["canonical"],
            "name": page["title"],
            "description": page["description"],
            "isPartOf": {"@id": HOST + "/#website"},
            "about": {"@id": HOST + "/#business"},
        },
        {"@type": "BreadcrumbList", "itemListElement": crumbs_ld},
    ]
    if page.get("faqs"):
        nodes.append(
            {
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": a},
                    }
                    for q, a in page["faqs"]
                ],
            }
        )
    if page.get("service_name"):
        nodes.append(
            {
                "@type": "Service",
                "name": page["service_name"],
                "serviceType": page["service_name"],
                "url": page["canonical"],
                "areaServed": "Roanoke, VA",
                "provider": {"@id": HOST + "/#business"},
            }
        )
    return json.dumps({"@context": "https://schema.org", "@graph": nodes}, ensure_ascii=False)


def shell(page):
    estimate = "/contact.html#quote" if page["path"] != "/" else "/#quote"
    if page["path"] == "/contact.html":
        estimate = "#quote"
    ld = graph(page)
    return f"""<!DOCTYPE html>
<html class="no-js" lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{page["title"]}</title>
<meta name="description" content="{page["description"]}">
<meta name="robots" content="{page.get("robots", "index, follow")}">
<link rel="canonical" href="{page["canonical"]}">
<meta property="og:site_name" content="{NAME}">
<meta property="og:title" content="{page["title"]}">
<meta property="og:description" content="{page["description"]}">
<meta property="og:url" content="{page["canonical"]}">
<meta property="og:type" content="website">
<meta property="og:image" content="{OG}">
<meta name="theme-color" content="#1b232c">
<link rel="icon" href="/images/mark.svg" type="image/svg+xml">
<link rel="stylesheet" href="/css/site.css">
<script>document.documentElement.classList.remove("no-js");</script>
<script type="application/ld+json">{ld}</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="utility">
  <div class="wrap utility-inner">
    <span>Roanoke, Virginia · {OFFICE_HOURS}</span>
    {phone_link()}
  </div>
</div>
<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="/">
      <img src="/images/mark.svg" alt="Roanoke VA Fence Company logo" width="64" height="64">
      <span>Roanoke VA<small>Fence Company</small></span>
    </a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav">Menu</button>
    {nav(page["path"], estimate)}
  </div>
</header>
<main id="main">
{page["body"]}
</main>
{footer(estimate)}
<script src="/js/site.js" defer></script>
</body>
</html>
"""


def write_page(page):
    path = page["path"]
    if path == "/":
        dest = ROOT / "index.html"
    elif path.endswith(".html"):
        dest = ROOT / path.lstrip("/")
    else:
        dest = ROOT / path.strip("/") / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    html = shell(page)
    dest.write_text(html, encoding="utf-8")
    page["_file"] = dest
    page["_html"] = html
    return dest


def page_hero(crumb_html, h1, intro, estimate):
    return f"""<section class="page-hero">
  <div class="wrap">
    {crumb_html}
    <h1>{h1}</h1>
    <p>{intro}</p>
    {hero_buttons(estimate)}
  </div>
</section>"""


def related_block(current_href):
    return f"""<section class="section">
  <div class="wrap">
    <h2>Other fence services</h2>
    {chips(other_services(current_href))}
    <h2>Areas we cover</h2>
    {chips(place_links())}
  </div>
</section>"""


def build_service(s):
    estimate = "/contact.html#quote"
    seo = s.get("seo_sections") or [
        ("Where this fence fits local lots", s.get("fit") or s["intro"]),
        ("Materials and styles", "The estimate names the height, style, gate count, and anything on the line that changes the dig: slope, rock, trees, and tear-out. We do not publish a flat price per foot."),
        ("Repair versus a new run", "Sound posts can take a repair. Posts that have failed at the ground usually mean a new line is the clearer job. We will say which one it is after we see the fence."),
        ("What an estimate covers", "Length, height, style, gates, post method, access, and removal of any existing fence that has to come out. Call " + PHONE + " or use the form with the town and a rough foot count."),
    ]
    seo_html = "".join(f"<h2>{title}</h2>{paras([body] if isinstance(body, str) else body)}" for title, body in seo)
    body = f"""<section class="hero slim-hero service-hero">
  <div class="wrap hero-grid">
    <div>
      {crumbs([("Home", "/"), ("Services", "/services.html"), (s["nav"], None)])}
      <p class="eyebrow">{s["nav"]}</p>
      <h1>{s["h1"]}</h1>
      <p class="lede">{s["intro"]}</p>
      {hero_buttons(estimate)}
    </div>
    <div class="quote-card" id="quote">
      <p class="kicker">Free estimate</p>
      <h2>Get a fence quote</h2>
      {FORM}
    </div>
  </div>
</section>
<section class="section">
  <div class="wrap story story-balanced">
    <img src="{s["image"]}" alt="{s["alt"]}" width="{s["w"]}" height="{s["h"]}" loading="lazy" decoding="async">
    <div>
      <h2>{s["when_h"]}</h2>
      {paras(s["when"])}
      <p>{phone_link("phone-link-lg")}</p>
    </div>
  </div>
</section>
<section class="section section-alt">
  <div class="wrap prose service-copy">
    {seo_html}
    <h2>{s["process_h"]}</h2>
    <p>{s["process_lead"]}</p>
    {steps(s["steps"])}
    <h2>{s["cost_h"]}</h2>
    <p>{s["cost_lead"]}</p>
    {factors(s["costs"])}
    <h2>{s["faq_h"]}</h2>
    {faq_block(s["faqs"])}
  </div>
</section>
{related_block(s["href"])}"""
    return {
        "path": s["href"],
        "title": s["title"],
        "description": s["description"],
        "canonical": HOST + s["href"],
        "crumbs": [("Home", "/"), ("Services", "/services.html"), (s["nav"], None)],
        "faqs": s["faqs"],
        "service_name": s["nav"] + " installation",
        "body": body,
    }


def build_place(p):
    if "h1" not in p:
        return None
    estimate = "/contact.html#quote"
    body = f"""<section class="hero slim-hero location-hero">
  <div class="wrap hero-grid">
    <div>
      {crumbs([("Home", "/"), ("Service areas", "/service-areas.html"), (p["name"], None)])}
      <p class="eyebrow">Service area</p>
      <h1>{p["h1"]}</h1>
      <p class="lede">{p["intro"]}</p>
      {hero_buttons(estimate)}
    </div>
    <div class="quote-card" id="quote">
      <p class="kicker">Free estimate</p>
      <h2>Get a fence quote</h2>
      {FORM}
    </div>
  </div>
</section>
<section class="section">
  <div class="wrap location-split">
    <div class="prose">
      <h2>{p["when_h"]}</h2>
      {paras(p["when"])}
      <h2>{p["more_h"]}</h2>
      {paras(p["more"])}
      <h2>Fence services</h2>
      {chips([(s["nav"], s["href"]) for s in C.SERVICES])}
      <h2>Other places</h2>
      {chips([(o["name"], o["href"]) for o in C.PLACES if o["href"] != p["href"]])}
      <h2>Questions about fencing in {p["name"].replace(", VA", "")}</h2>
      {faq_block(p["faqs"])}
      <p>{phone_link("phone-link-lg")}</p>
    </div>
    {map_embed("Fence service area map for " + p["name"])}
  </div>
</section>"""
    return {
        "path": p["href"],
        "title": p["title"],
        "description": p["description"],
        "canonical": HOST + p["href"],
        "crumbs": [("Home", "/"), ("Service areas", "/service-areas.html"), (p["name"], None)],
        "faqs": p["faqs"],
        "body": body,
    }


def build_home():
    links = ", ".join(f'<a href="{s["href"]}">{s["nav"].lower()}</a>' for s in C.SERVICES)
    # fix grammar: last "and"
    parts = [f'<a href="{s["href"]}">{s["nav"].lower()}</a>' for s in C.SERVICES]
    inline = ", ".join(parts[:-1]) + ", and " + parts[-1]
    body = f"""<section class="hero">
  <div class="wrap hero-grid">
    <div>
      <p class="eyebrow">Roanoke, Virginia</p>
      <h1>Fence Company in Roanoke, VA</h1>
      <p class="lede">Roanoke VA Fence Company installs and repairs fences for houses, businesses, and farms in Roanoke and the towns around it. The price follows the length of the line, the material, the gates, and what the ground does between the posts.</p>
      {hero_buttons("/#quote")}
      <p class="hero-links">Services: {inline}.</p>
    </div>
    <div class="quote-card" id="quote">
      <p class="kicker">Free estimate</p>
      <h2>Get a fence quote</h2>
      {FORM}
    </div>
  </div>
</section>
<section class="section">
  <div class="wrap">
    <div class="section-head">
      <p class="kicker">Our services</p>
      <h2>Fence services</h2>
      <p>Each card goes to its own page. The short description is the job, not a slogan.</p>
    </div>
    {service_cards()}
  </div>
</section>
<section class="section section-alt">
  <div class="wrap">
    <div class="section-head">
      <h2>Houses, businesses, and farms</h2>
    </div>
    <div class="split">
      <article>
        <h3>Homes</h3>
        <p>Most house jobs are a backyard privacy fence in <a href="/landscape-lighting-installation.html">wood</a> or <a href="/vinyl-fence.html">vinyl</a>, a picket or <a href="/aluminum-fence.html">aluminum</a> front line, or <a href="/chain-link-fence.html">chain link</a> for a dog or a side yard.</p>
        <p>A repair is the right job when the posts are still sound. When the posts have failed at the ground, replacing the run is usually clearer than patching boards onto a lean.</p>
      </article>
      <article>
        <h3>Businesses and farms</h3>
        <p><a href="/commercial-fencing.html">Commercial lines</a> are chain link, ornamental metal, and gates for parking lots, storage yards, and job sites. The pipe and the openings are specified for that traffic.</p>
        <p><a href="/farm-fencing.html">Farm lines</a> are longer: split rail, horse fence, and cattle fence, with a gate wide enough for a truck. Those are different products from a privacy panel.</p>
      </article>
    </div>
  </div>
</section>
<section class="section">
  <div class="wrap">
    <div class="section-head">
      <h2>What we ask before we price a fence</h2>
      <p>These are the facts that decide the estimate. We would rather ask them up front than invent a rate per foot.</p>
    </div>
    {factors([
        ("How many feet", "The length is the first number. A rough measurement is enough to start, as long as it includes the corners."),
        ("The layout", "Level, slope, trees, roots, rock, and whether the truck can reach the line. Two of those can matter more than the style."),
        ("Style and gates", "Privacy, picket, chain link, aluminum, or farm fence, plus every gate. The style is the third piece of the price."),
        ("Repair or replace", "Sound posts can take a repair. A line that leans, or posts that are soft at the soil, is usually a new run."),
    ])}
  </div>
</section>
<section class="section section-alt">
  <div class="wrap">
    <div class="section-head">
      <h2>Service area</h2>
      <p>We work in Roanoke and the surrounding towns. Lot size and the fence job change from one place to the next. The <a href="/service-areas.html">service area page</a> has the detail, without a list of every neighborhood.</p>
    </div>
    {chips(place_links())}
  </div>
</section>
<section class="section">
  <div class="wrap">
    <div class="section-head">
      <h2>Fence questions</h2>
      <p>Short answers. Material-specific questions live on each service page, and the full set is on the <a href="/faq.html">FAQ</a>.</p>
    </div>
    {faq_block(C.HOME_FAQS)}
  </div>
</section>
<section class="section locations-band">
  <div class="wrap">
    <div class="section-head">
      <p class="kicker">Service area</p>
      <h2>Towns we fence</h2>
      <p>Wood, vinyl, chain-link, aluminum, farm, and commercial fencing in these Roanoke-area towns.</p>
    </div>
    {chips(place_links())}
    <p><a class="details" href="/service-areas.html">All service areas</a> · {phone_link()}</p>
    <p class="hours-note">{OFFICE_HOURS}</p>
  </div>
</section>"""
    return {
        "path": "/",
        "title": "Fence Company in Roanoke, VA | Installation and Repair",
        "description": "Wood, vinyl, chain-link, aluminum, and farm fence installation and repair in Roanoke, VA. Call (540) 234-2867 for a free estimate.",
        "canonical": HOST + "/",
        "crumbs": [("Home", None)],
        "faqs": C.HOME_FAQS,
        "body": body,
    }


def build_services():
    articles = []
    for s in C.SERVICES:
        articles.append(f'<article class="factor"><h3><a href="{s["href"]}">{s["nav"]}</a></h3><p>{s["fit"]}</p></article>')
    body = f"""{page_hero(crumbs([("Home", "/"), ("Services", None)]), "Fence Services in Roanoke, VA", "Six kinds of fence work, each with its own page. Start with what the fence has to do. Privacy, a dog, a pool, livestock, and a commercial lot are not one product.", "/contact.html#quote")}
<section class="section">
  <div class="wrap">
    {service_cards()}
  </div>
</section>
<section class="section section-alt">
  <div class="wrap">
    <div class="section-head">
      <h2>Match the fence to the job</h2>
      <p>Use this to pick a page. The price still depends on the line at the property.</p>
    </div>
    <div class="factor-grid">
      {"".join(articles)}
    </div>
  </div>
</section>
<section class="section">
  <div class="wrap">
    <h2>Where we install</h2>
    {chips(place_links())}
  </div>
</section>
{cta("Not sure which fence you need?", "Describe the yard, the animals, or the lot and we will tell you which of these pages fits. Call " + PHONE + " or send the estimate form.")}"""
    return {
        "path": "/services.html",
        "title": "Fence Services in Roanoke, VA",
        "description": "Compare vinyl, wood, chain-link, aluminum, farm, and commercial fencing in Roanoke, VA. See what each fence is for, then request an estimate.",
        "canonical": HOST + "/services.html",
        "crumbs": [("Home", "/"), ("Services", None)],
        "body": body,
    }


def build_about():
    body = f"""{page_hero(crumbs([("Home", "/"), ("About", None)]), "About Roanoke VA Fence Company", "We install and repair residential, commercial, and farm fences in Roanoke and the nearby towns. The work happens at the property. This site does not list a showroom address.", "/contact.html#quote")}
<section class="section">
  <div class="wrap story">
    <img src="/images/vinyl-privacy.jpg" alt="White vinyl privacy fence with scalloped tops along a lawn" width="1100" height="619" loading="lazy" decoding="async">
    <div>
      <h2>What we install</h2>
      <p>Vinyl, wood, chain link, aluminum, farm fence, and commercial fencing and gates. If you need a horse fence, a pool fence, or a wood privacy fence replaced, start with the matching service page or call {PHONE}.</p>
      <p>An estimate starts with the line: approximate length, material, gates, slope, and access. We do not publish a price per foot, because a flat backyard and a rocky hillside are not the same job.</p>
    </div>
  </div>
</section>
<section class="section section-alt">
  <div class="wrap prose">
    <h2>How an estimate works</h2>
    <p>Call or use the form. Estimates are free. Say whether a fence is already there and whether you want it repaired or taken out. If the posts are the problem, we will say so instead of selling boards onto a bad line.</p>
    <p>We cover <a href="/service-areas.html">Roanoke, Salem, Vinton, Cave Spring, Hollins, and Roanoke County</a>. If the property is farther out, say so on the form and we will tell you whether we can take the trip.</p>
    <p>This page does not list a year the company opened, a license number, or a warranty term. Those details are not published here. What we will do is price the fence in front of us and build that fence.</p>
  </div>
</section>
<section class="section">
  <div class="wrap">
    <h2>Services</h2>
    {chips([(s["nav"], s["href"]) for s in C.SERVICES])}
  </div>
</section>
{cta("Request an estimate", "Call " + PHONE + " or send the form with the town, the material, and a rough length.")}"""
    return {
        "path": "/about.html",
        "title": "About Roanoke VA Fence Company",
        "description": "Roanoke VA Fence Company installs and repairs residential, commercial, and farm fences in Roanoke and nearby towns. Call (540) 234-2867.",
        "canonical": HOST + "/about.html",
        "crumbs": [("Home", "/"), ("About", None)],
        "body": body,
    }


def build_contact():
    body = f"""{page_hero(crumbs([("Home", "/"), ("Contact", None)]), "Contact Roanoke VA Fence Company", "Call " + PHONE + " or send the form. Estimates are free. There is no published street address. The conversation is about the fence at your property.", "#quote")}
<section class="section">
  <div class="wrap contact-grid">
    <div class="note">
      <h2>What to include</h2>
      <p>The town, the fence material, about how many feet, and how many gates. If a fence is already there, say whether you want it repaired or removed.</p>
      <p>Roanoke city, Salem, Vinton, and Roanoke County do not share one fence rule. Name the place so the height and the placement can be planned for that parcel.</p>
      <p><a href="tel:{TEL}">{PHONE}</a></p>
      <p><a href="/service-areas.html">Service areas</a> and <a href="/faq.html">common questions</a>.</p>
    </div>
    <div class="quote-card" id="quote">
      <p class="kicker">Free estimate</p>
      <h2>Get a fence quote</h2>
      {FORM}
    </div>
  </div>
</section>"""
    return {
        "path": "/contact.html",
        "title": "Contact Roanoke VA Fence Company",
        "description": "Request a free fence estimate in Roanoke, VA, or call (540) 234-2867. Share the material, the approximate length, and the gates.",
        "canonical": HOST + "/contact.html",
        "crumbs": [("Home", "/"), ("Contact", None)],
        "body": body,
    }


def build_faq():
    body = f"""{page_hero(crumbs([("Home", "/"), ("FAQ", None)]), "Fence Questions", "Five questions we hear before a fence estimate in Roanoke. For a specific material, use the questions at the bottom of that service page.", "/contact.html#quote")}
<section class="section">
  <div class="wrap">
    {faq_block(C.HOME_FAQS)}
    <h2>Go to a service</h2>
    {chips([(s["nav"], s["href"]) for s in C.SERVICES])}
  </div>
</section>
{cta("Still pricing a real yard?", "The form and the phone are how you get a number for your line. Call " + PHONE + ".")}"""
    return {
        "path": "/faq.html",
        "title": "Fence Questions | Roanoke VA Fence Company",
        "description": "Answers on fence cost, repairs, materials, permits, and sloped lots in Roanoke, VA. Call (540) 234-2867 or request a free estimate.",
        "canonical": HOST + "/faq.html",
        "crumbs": [("Home", "/"), ("FAQ", None)],
        "faqs": C.HOME_FAQS,
        "body": body,
    }


def build_areas():
    cards = []
    for p in C.PLACES:
        cards.append(
            f"""<article class="place-card">
  <h2><a href="{p["href"]}">{p["name"]}</a></h2>
  <p>{p["card"]}</p>
  <p class="card-link"><a class="details" href="{p["href"]}">Fence details</a></p>
</article>"""
        )
    body = f"""{page_hero(crumbs([("Home", "/"), ("Service areas", None)]), "Fence Service Areas", "We install fences in Roanoke and the towns around it. The pages below are about the fence work in each place, not a town history.", "/contact.html#quote")}
<section class="section">
  <div class="wrap">
    <div class="place-grid">
      {"".join(cards)}
    </div>
  </div>
</section>
<section class="section section-alt">
  <div class="wrap prose">
    <h2>Neighborhoods are not separate fence types</h2>
    <p>A steep street in southwest Roanoke and a steep street in Salem ask for the same thing on install day: posts that follow the grade, and a gate that still swings. Naming every neighborhood would not change the material or the price method.</p>
    <p>What does change is the lot and the locality. City yards are tighter. Cave Spring backyards run longer. Hollins and other county parcels pick up farm fence. Salem and Vinton are not the City of Roanoke for permit questions. Start with the place page, then the <a href="/services.html">service</a> that matches the job.</p>
  </div>
</section>
{cta("Tell us the town", "Put the place in the estimate form, along with the material and a rough length. Call " + PHONE + " if that is easier.")}"""
    return {
        "path": "/service-areas.html",
        "title": "Fence Service Areas around Roanoke, VA",
        "description": "Fence installation in Roanoke, Salem, Vinton, Cave Spring, Hollins, and Roanoke County. See how the work differs, then call (540) 234-2867.",
        "canonical": HOST + "/service-areas.html",
        "crumbs": [("Home", "/"), ("Service areas", None)],
        "body": body,
    }


def build_blog():
    body = f"""{page_hero(crumbs([("Home", "/"), ("Blog", None)]), "Fence Notes", "One practical note on hiring someone to install a fence in Roanoke. It is the same topic as the older post, rewritten so it is useful.", "/contact.html#quote")}
<section class="section">
  <div class="wrap">
    <article class="post-card">
      <p class="kicker">May 25, 2023</p>
      <h2><a href="/blog/the-benefits-of-hiring-professional-fence-contractors">The benefits of hiring a fence contractor</a></h2>
      <p>What the crew is actually there to do, what to measure before the visit, and when a repair is a better job than a new line.</p>
      <p class="card-link"><a class="details" href="/blog/the-benefits-of-hiring-professional-fence-contractors">Read the note</a></p>
    </article>
  </div>
</section>"""
    return {
        "path": "/blog.html",
        "title": "Fence Notes | Roanoke VA Fence Company",
        "description": "Notes on hiring a fence contractor in Roanoke, VA: what to measure, what changes the price, and when to repair instead of replace.",
        "canonical": HOST + "/blog.html",
        "crumbs": [("Home", "/"), ("Blog", None)],
        "body": body,
    }


def build_post():
    path = "/blog/the-benefits-of-hiring-professional-fence-contractors"
    body = f"""<section class="page-hero">
  <div class="wrap">
    {crumbs([("Home", "/"), ("Blog", "/blog.html"), ("Hiring a contractor", None)])}
    <h1>The Benefits of Hiring a Fence Contractor</h1>
    <p>Hiring someone to install a fence is about who lays out the line, sets the posts, and hangs the gates. This note is for a Roanoke homeowner comparing a crew with a weekend project.</p>
    <p>Published May 25, 2023. Updated October 16, 2026.</p>
  </div>
</section>
<section class="section">
  <div class="wrap prose">
    <h2>What you are paying the crew to handle</h2>
    <p>The hard parts are the layout and the posts. A fence that looks straight in a photo still has to follow a yard that drops, miss a root, and meet a gate that has to swing. The crew brings the posts, the panels or rails, and the tools to set them.</p>
    <p>You should not have to rent an auger to discover the corner is rock, then rebuild the corner on Sunday. That discovery is part of the job you are hiring.</p>
    <h2>What to know before the visit</h2>
    <p>Measure the run as best you can, even if the number is rough. Count the gates, including a wider one for a mower or a driveway. Decide whether the fence is for privacy, a dog, a pool, livestock, or simply a line you want marked.</p>
    <p>Confirm the property line yourself. We set the fence where you tell us. We do not survey. On a tight lot in Roanoke or Vinton, that confirmation matters more than the catalog photo.</p>
    <h2>Repair versus a new line</h2>
    <p>A few broken boards or a sagging gate can be a repair, if the posts are still solid in the ground. Posts that are soft at the soil, or a line that leans for most of its length, usually mean a new run. New boards on rotten posts follow the lean.</p>
    <p>A contractor should say which one it is after looking. A full replacement is not the automatic answer, and a patch is not a favor if it fails next season.</p>
    <h2>Materials are not interchangeable</h2>
    <p><a href="/vinyl-fence.html">Vinyl</a> skips the stain cycle, and many privacy panels look finished on both sides. <a href="/landscape-lighting-installation.html">Wood</a> can be stained, and it weathers if you ignore it. <a href="/chain-link-fence.html">Chain link</a> encloses a yard or a lot and does not give privacy unless you add slats or a screen. <a href="/aluminum-fence.html">Aluminum</a> keeps the view and is the usual pool fence. <a href="/farm-fencing.html">Farm fence</a> is for animals and long lines. <a href="/commercial-fencing.html">Commercial work</a> specifies the pipe and the gates for traffic, not for a backyard.</p>
    <h2>A usable price is a layout</h2>
    <p>Anyone can quote a low number per foot and then add the slope, the gates, and the tear-out. Ask what is included: old fence removal, haul-away, every gate, and whether the posts are set so the line will stay put. We do not list a dollar amount on this site, because the visit is what makes the number real.</p>
    <p>If you want that visit, call <a href="tel:{TEL}">{PHONE}</a> or <a href="/contact.html#quote">request an estimate</a>. More direct answers are on the <a href="/faq.html">FAQ</a>.</p>
  </div>
</section>"""
    return {
        "path": path,
        "title": "Hiring a Fence Contractor in Roanoke, VA",
        "description": "What a fence contractor handles on a Roanoke job, from the property line and the slope to posts, gates, and repair versus replacement.",
        "canonical": HOST + path,
        "crumbs": [("Home", "/"), ("Blog", "/blog.html"), ("Hiring a contractor", None)],
        "body": body,
    }


def sentence_count(text):
    return len(re.findall(r"[.!?]", text))


def audit(pages):
    problems = []
    banned = [
        "south carolina",
        "landscape drainage",
        "decades of",
        "unmatched",
        "biggest purchaser",
        "homeadvisor",
        "fenceinstallationspringhill",
        "weebly",
        "naked squirrel",
        "look no further",
    ]
    hrefs = set()
    files = {}
    for page in pages:
        html = page["_html"]
        hrefs.update(re.findall(r'href="([^"]+)"', html))
        files[page["path"]] = page
        h1s = re.findall(r"<h1[^>]*>", html)
        if len(h1s) != 1:
            problems.append(f"{page['path']} has {len(h1s)} h1 tags")
        if 'rel="canonical"' not in html:
            problems.append(f"{page['path']} missing canonical")
        if len(page["title"]) > 65:
            problems.append(f"title {len(page['title'])}: {page['title']}")
        if not 70 <= len(page["description"]) <= 170:
            problems.append(f"desc {len(page['description'])}: {page['description']}")
        low = html.lower()
        for phrase in banned:
            if phrase in low:
                problems.append(f"{page['path']} contains {phrase}")
        if "tel:+15402342867" not in html:
            problems.append(f"{page['path']} missing phone link")
        for q, a in page.get("faqs") or []:
            n = sentence_count(a)
            if n < 2 or n > 5:
                problems.append(f"FAQ sentence count {n}: {q}")
    internal = set()
    for href in hrefs:
        if href.startswith("/") and not href.startswith("//"):
            path = href.split("#")[0] or "/"
            internal.add(path)
    for path in sorted(internal):
        if path.startswith("/css/") or path.startswith("/images/") or path.startswith("/js/"):
            continue
        if path not in files:
            problems.append(f"missing target {path}")
    if "/" not in files:
        problems.append("missing home")
    return problems


def main():
    pages = [build_home(), build_services(), build_about(), build_contact(), build_faq(), build_areas(), build_blog(), build_post()]
    for s in C.SERVICES:
        pages.append(build_service(s))
    for p in C.PLACES:
        built = build_place(p)
        if built:
            pages.append(built)
    for page in pages:
        write_page(page)
    locs = []
    for page in pages:
        loc = page["canonical"]
        locs.append(f"  <url><loc>{loc}</loc><lastmod>2026-10-16</lastmod></url>")
    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(locs)
        + "\n</urlset>\n"
    )
    (ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    (ROOT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\nSitemap: https://www.roanokevafence.net/sitemap.xml\n",
        encoding="utf-8",
    )
    (ROOT / "_redirects").write_text(
        "\n".join(
            [
                "/index.html / 301",
                "/favicon.ico /images/mark.svg 200",
                "/wood-fence.html /landscape-lighting-installation.html 301",
                "/privacy-fence.html /vinyl-fence.html 301",
                "/blog /blog.html 301",
                "/blog/ /blog.html 301",
                "/blog/the-benefits-of-hiring-professional-fence-contractors/ /blog/the-benefits-of-hiring-professional-fence-contractors 301",
                "/blog/the-benefits-of-hiring-professional-fence-contractors /blog/the-benefits-of-hiring-professional-fence-contractors/index.html 200",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (ROOT / "blog" / "index.html").write_text(
        """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Fence Notes | Roanoke VA Fence Company</title>
<meta name="robots" content="noindex">
<link rel="canonical" href="https://www.roanokevafence.net/blog.html">
<meta http-equiv="refresh" content="0; url=/blog.html">
</head>
<body>
<p><a href="/blog.html">Fence notes</a></p>
<script>location.replace("/blog.html");</script>
</body>
</html>
""",
        encoding="utf-8",
    )
    missing = {
        "path": "/404.html",
        "title": "Page not found | Roanoke VA Fence Company",
        "description": "That address is not a page on Roanoke VA Fence Company. Call (540) 234-2867 or go back to the fence services.",
        "canonical": HOST + "/404.html",
        "robots": "noindex, follow",
        "crumbs": [("Home", "/"), ("Page not found", None)],
        "body": """<section class="page-hero">
  <div class="wrap">
    <ol class="crumbs"><li><a href="/">Home</a></li><li>Page not found</li></ol>
    <h1>That page is not on this site</h1>
    <p>The address does not match a fence page. The services list and the contact form are the way back.</p>
    <div class="hero-actions">
      <a class="btn btn-solid" href="/services.html">View services</a>
      <a class="btn btn-ghost" href="tel:+15402342867">Call (540) 234-2867</a>
    </div>
  </div>
</section>""",
    }
    write_page(missing)
    problems = audit(pages)
    print(f"Wrote {len(pages)} pages")
    if problems:
        print("AUDIT")
        for item in problems:
            print(" -", item)
        sys.exit(1)
    print("Audit clean")


if __name__ == "__main__":
    main()

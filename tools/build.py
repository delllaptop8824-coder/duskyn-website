#!/usr/bin/env python3
"""
DUSKYN static site generator.

Generates the HTML pages, sitemap.xml and robots.txt in the project root from
the content defined in this file, so the header, footer, SEO tags and WhatsApp
links stay identical on every page. The output is plain static HTML that GitHub
Pages serves as-is; Python is only needed when you want to regenerate it.

Usage:
    python3 tools/build.py                          # build (uses domain in CNAME, if any)
    python3 tools/build.py --domain duskyn.co      # set custom domain, write CNAME, build
    python3 tools/build.py --domain example.com --force   # replace a different existing CNAME
"""

import argparse
import html
import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent

# --------------------------------------------------------------------------
# Business details (as supplied by the business)
# --------------------------------------------------------------------------
BRAND = "DUSKYN"
COMPANY = "DUSKYN APPARELS LLP"
SINCE = "2017"
PHONE_DISPLAY = "+91 8000190745"
PHONE_TEL = "+918000190745"
WA_NUMBER = "918000190745"
ADDRESS_LINES = [
    "Plot N 40, Block C, Sector 88,",
    "Noida, Gautam Buddha Nagar,",
    "Uttar Pradesh – 201301, India.",
]
ADDRESS_ONE_LINE = "Plot N 40, Block C, Sector 88, Noida, Gautam Buddha Nagar, Uttar Pradesh – 201301, India."
MAPS_URL = "https://www.google.com/maps/search/?api=1&query=" + quote(
    "Plot N 40, Block C, Sector 88, Noida, Gautam Buddha Nagar, Uttar Pradesh 201301, India", safe=""
)
DEFAULT_MSG = "Hello DUSKYN APPARELS LLP, I am interested in your services. Please share more information."


def wa(message=DEFAULT_MSG):
    return f"https://wa.me/{WA_NUMBER}?text={quote(message, safe='')}"


def esc(s):
    return html.escape(s, quote=True)


# --------------------------------------------------------------------------
# Icons (inline SVG, 24x24, stroke based)
# --------------------------------------------------------------------------
ICONS = {
    "whatsapp": '<path d="M3.6 20.4l1.3-4.3A8.6 8.6 0 1 1 8 19.3z"/>'
                '<path fill="currentColor" stroke="none" d="M9.3 8.3c.2-.4.5-.5.8-.5h.4c.2 0 .4.1.5.4l.7 1.6c.1.2 0 .5-.1.6l-.5.6c-.1.2-.1.4 0 .5.6 1 1.4 1.8 2.4 2.4.2.1.4.1.5 0l.6-.5c.2-.2.4-.2.6-.1l1.6.7c.3.1.4.3.4.5v.4c0 .3-.1.7-.6.9-.6.3-1.3.4-2 .2-2.5-.7-4.4-2.6-5.1-5.1-.2-.7-.1-1.4.2-2z"/>',
    "arrow-right": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "check-circle": '<circle cx="12" cy="12" r="9"/><path d="m8.2 12.4 2.5 2.5 5.1-5.3"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "close": '<path d="M6 6l12 12M18 6 6 18"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>',
    "factory": '<path d="M3 20V9.5l5 3.2V9.5l5 3.2V4h4.5v16"/><path d="M2.5 20h19"/><path d="M17.5 20V8H21v12"/><path d="M6.5 16.5h1.5M10.5 16.5H12"/>',
    "package": '<path d="m21 8-9-5-9 5 9 5 9-5z"/><path d="M3 8v8l9 5 9-5V8"/><path d="M12 13v8"/><path d="m7.5 5.5 9 5"/>',
    "sliders": '<path d="M4 6h9M17 6h3M4 12h3M11 12h9M4 18h11M19 18h1"/><circle cx="15" cy="6" r="2"/><circle cx="9" cy="12" r="2"/><circle cx="17" cy="18" r="2"/>',
    "user-search": '<circle cx="10" cy="8" r="3.5"/><path d="M3.5 19.5a6.5 6.5 0 0 1 9.4-5.8"/><circle cx="17" cy="16" r="3"/><path d="m19.2 18.2 1.8 1.8"/>',
    "ship": '<path d="M2.5 15h19l-2 4.4c-.2.4-.6.6-1 .6H5.5c-.4 0-.8-.2-1-.6z"/><path d="M5 15v-4.5h14V15"/><path d="M8 10.5V7h4v3.5M12 8h4v2.5"/><path d="M10 4v3"/>',
    "research": '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.9-3.9"/><path d="M8 13.5v-2M11 13.5V8.5M14 13.5v-3.5"/>',
    "briefcase": '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M9 7V5.5A1.5 1.5 0 0 1 10.5 4h3A1.5 1.5 0 0 1 15 5.5V7"/><path d="M3 13h18"/>',
    "phone": '<path d="M20.5 16.4v2.7a1.8 1.8 0 0 1-2 1.8 17.8 17.8 0 0 1-7.8-2.8 17.5 17.5 0 0 1-5.4-5.4A17.8 17.8 0 0 1 2.5 4.9a1.8 1.8 0 0 1 1.8-2h2.7A1.8 1.8 0 0 1 8.8 4.5c.1.9.3 1.7.6 2.5a1.8 1.8 0 0 1-.4 1.9L7.9 10a14.4 14.4 0 0 0 5.4 5.4l1.1-1.1a1.8 1.8 0 0 1 1.9-.4c.8.3 1.6.5 2.5.6a1.8 1.8 0 0 1 1.7 1.9z"/>',
    "map-pin": '<path d="M12 21s-7-6.1-7-11.5a7 7 0 0 1 14 0C19 14.9 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',
    "building": '<rect x="4" y="3" width="16" height="18" rx="1.5"/><path d="M9.5 21v-4h5v4M8 7h2M14 7h2M8 11h2M14 11h2"/>',
    "tag": '<path d="M3 4v7.6l9.4 9.4 8.6-8.6L11.6 3H4a1 1 0 0 0-1 1z"/><circle cx="7.5" cy="7.5" r="1.5"/>',
    "calendar": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>',
    "chat": '<path d="M21 12a8 8 0 0 1-11.6 7.1L4 20.5l1.4-4.9A8 8 0 1 1 21 12z"/><path d="M8.5 12h.01M12 12h.01M15.5 12h.01"/>',
    "layers": '<path d="m12 3 9 5-9 5-9-5 9-5z"/><path d="m3 12.5 9 5 9-5"/><path d="m3 17 9 5 9-5" opacity=".45"/>',
    "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
    "compass": '<circle cx="12" cy="12" r="9"/><path d="m15.5 8.5-2 5-5 2 2-5z"/>',
    "clipboard": '<rect x="5" y="4.5" width="14" height="16.5" rx="2"/><rect x="9" y="3" width="6" height="3" rx="1"/><path d="M9 11h6M9 14.5h6M9 18h3"/>',
    "handshake": '<path d="m11 17 2 2a1.5 1.5 0 0 0 2-2"/><path d="m14 14 2.5 2.5a1.5 1.5 0 0 0 2-2l-3.9-3.9a2.1 2.1 0 0 0-3 0l-.9.9a1.5 1.5 0 0 1-2-2l2.8-2.8a3.7 3.7 0 0 1 4.4-.6l.4.2a3 3 0 0 0 2 .3L21 6"/><path d="m21 15-1.5-1.5"/><path d="M3 6l.8.8a2.8 2.8 0 0 0 2.2.8L9 7"/><path d="m3 15 6 6"/><path d="m3 15 1.5-1.5"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/>',
    "external": '<path d="M14 4h6v6M20 4l-9 9"/><path d="M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/>',
    "users": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><path d="M16 4.6a3.5 3.5 0 0 1 0 6.8M18.5 14.5a6.5 6.5 0 0 1 3 5.5"/>',
    "store": '<path d="M4 10v10h16V10"/><path d="M3 10 4.5 4h15L21 10a3 3 0 0 1-6 0 3 3 0 0 1-6 0 3 3 0 0 1-6 0z"/><path d="M10 20v-5h4v5"/>',
    "warehouse": '<path d="M3 21V9l9-5 9 5v12"/><path d="M7 21v-8h10v8M7 17h10"/>',
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4.5 21a7.5 7.5 0 0 1 15 0"/>',
    "home": '<path d="m3 11 9-7 9 7"/><path d="M5 10v10h14V10"/>',
}


def icon(name, cls="icon"):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{ICONS[name]}</svg>')


def wa_attrs(message=DEFAULT_MSG):
    return f'href="{esc(wa(message))}" target="_blank" rel="noopener noreferrer"'


# --------------------------------------------------------------------------
# Content
# --------------------------------------------------------------------------
SERVICES = [
    {
        "id": "china-product-sourcing",
        "icon": "globe",
        "title": "China Product Sourcing",
        "short": "Explore product sourcing opportunities from China. Tell us what you are looking for and discuss possible options with our team.",
        "points": ["Products you would like to source from China",
                   "Quantities, specifications and target budget",
                   "Possible sourcing options to explore"],
        "msg": "Hello DUSKYN APPARELS LLP, I have a China product sourcing enquiry. Please share more information.",
        "enquiry": "China sourcing enquiry",
    },
    {
        "id": "indian-manufacturer-sourcing",
        "icon": "factory",
        "title": "Indian Manufacturer Sourcing",
        "short": "Identify manufacturers in India that may suit your product, quantity and business requirements.",
        "points": ["The product or type of manufacturing you need",
                   "Production quantities and specifications",
                   "Indian manufacturers that may suit your requirement"],
        "msg": "Hello DUSKYN APPARELS LLP, I have an Indian manufacturer sourcing enquiry. Please share more information.",
        "enquiry": "Indian manufacturer enquiry",
    },
    {
        "id": "wholesale-product-sourcing",
        "icon": "package",
        "title": "Wholesale Product Sourcing",
        "short": "Assistance in finding wholesale suppliers for products you plan to buy in bulk or resell.",
        "points": ["Product categories for bulk purchase or resale",
                   "Indicative order volumes",
                   "Wholesale supplier options to consider"],
        "msg": "Hello DUSKYN APPARELS LLP, I have a wholesale product sourcing enquiry. Please share more information.",
        "enquiry": "Wholesale product enquiry",
    },
    {
        "id": "custom-manufacturing-assistance",
        "icon": "sliders",
        "title": "Custom Manufacturing Assistance",
        "short": "Explore manufacturers for products made to your own designs, specifications or requirements.",
        "points": ["Your designs, samples or specifications",
                   "Material, size, packaging or branding needs",
                   "Manufacturers to explore for your product"],
        "msg": "Hello DUSKYN APPARELS LLP, I have a custom manufacturing enquiry. Please share more information.",
        "enquiry": "Custom manufacturing enquiry",
    },
    {
        "id": "supplier-discovery",
        "icon": "user-search",
        "title": "Supplier Discovery",
        "short": "Identify potential suppliers in India or China based on the requirements you share with us.",
        "points": ["What you need and where you prefer to source it",
                   "Your key requirements for a supplier",
                   "Potential suppliers to shortlist and discuss"],
        "msg": "Hello DUSKYN APPARELS LLP, I need help with supplier discovery. Please share more information.",
        "enquiry": "Supplier discovery enquiry",
    },
    {
        "id": "import-sourcing-assistance",
        "icon": "ship",
        "title": "Import Sourcing Assistance",
        "short": "Sourcing-related assistance for customers who are exploring importing products from China.",
        "points": ["Products you are considering importing",
                   "Sourcing questions related to China",
                   "Next steps to discuss with our team"],
        "msg": "Hello DUSKYN APPARELS LLP, I have an import sourcing enquiry for products from China. Please share more information.",
        "enquiry": "Import sourcing enquiry",
    },
    {
        "id": "product-research",
        "icon": "research",
        "title": "Product Research",
        "short": "Explore products, suppliers and sourcing options before you make your sourcing decisions.",
        "points": ["Product ideas or categories you are evaluating",
                   "Available product variants and options",
                   "Suppliers and sourcing routes to consider"],
        "msg": "Hello DUSKYN APPARELS LLP, I have a product research enquiry. Please share more information.",
        "enquiry": "Product research enquiry",
    },
    {
        "id": "business-sourcing-solutions",
        "icon": "briefcase",
        "title": "Business Sourcing Solutions",
        "short": "Sourcing assistance for businesses, shaped around the requirements you discuss with us.",
        "points": ["Ongoing or one-time sourcing requirements",
                   "Products across different categories",
                   "A sourcing approach suited to your business"],
        "msg": "Hello DUSKYN APPARELS LLP, I am looking for business sourcing solutions. Please share more information.",
        "enquiry": "Business sourcing enquiry",
    },
]

STEPS = [
    ("Share Your Requirement", "Tell us what product or manufacturer you need."),
    ("Discuss Your Needs", "Contact our team through WhatsApp to explain your requirements."),
    ("Explore Sourcing Options", "Discuss potential suppliers and sourcing possibilities with our team."),
    ("Move Forward", "Discuss the next steps, commercial terms, and arrangements directly with DUSKYN."),
]

WHY = [
    ("globe", "India &amp; China Sourcing",
     "Explore sourcing opportunities across two major manufacturing destinations: India and China."),
    ("layers", "Different Product Categories",
     "Assistance with sourcing requirements across a range of product categories."),
    ("chat", "Direct WhatsApp Communication",
     "Talk to our team directly on WhatsApp. Share details, photos and questions in one conversation."),
    ("briefcase", "Business-Focused Approach",
     "We work with individuals, retailers, wholesalers and companies, with a focus on practical business needs."),
    ("factory", "Manufacturer &amp; Supplier Support",
     "Support in exploring manufacturers and suppliers that may suit what you are looking for."),
    ("target", "Based on Your Requirements",
     "Sourcing assistance shaped around the product, quantity and specifications you share with us."),
]

ABOUT_PARAS = [
    f"{BRAND}, operated by {COMPANY}, provides online sourcing assistance for businesses and individuals "
    "seeking products and manufacturing opportunities in India and China.",
    "Whether you need help finding a suitable manufacturer in India, sourcing products from China, or identifying "
    f"suppliers for your business requirements, {BRAND} aims to make the sourcing process more accessible and convenient.",
    "Our focus is on understanding your requirements and helping you explore suitable sourcing solutions.",
]

NAV = [
    ("home", "Home", "index.html"),
    ("about", "About Us", "about.html"),
    ("services", "Our Services", "services.html"),
    ("how", "How It Works", "index.html#how-it-works"),
    ("contact", "Contact Us", "contact.html"),
]


# --------------------------------------------------------------------------
# Layout
# --------------------------------------------------------------------------
def head(page, domain, prefix):
    title = esc(page["title"])
    desc = esc(page["description"])
    tags = [
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{title}</title>",
        f'<meta name="description" content="{desc}">',
        '<meta name="theme-color" content="#0b1b33">',
        '<meta name="format-detection" content="telephone=no">',
    ]
    if page.get("noindex"):
        tags.append('<meta name="robots" content="noindex">')
    if domain and not page.get("noindex"):
        tags.append(f'<link rel="canonical" href="{page_url(domain, page["file"])}">')
    tags += [
        '<meta property="og:type" content="website">',
        f'<meta property="og:site_name" content="{BRAND}">',
        f'<meta property="og:title" content="{title}">',
        f'<meta property="og:description" content="{desc}">',
        '<meta property="og:locale" content="en_IN">',
    ]
    if domain:
        tags += [
            f'<meta property="og:url" content="{page_url(domain, page["file"])}">',
            f'<meta property="og:image" content="https://{domain}/assets/images/og-image.png">',
            '<meta property="og:image:width" content="1200">',
            '<meta property="og:image:height" content="630">',
            f'<meta property="og:image:alt" content="{BRAND} — Global product sourcing from India and China">',
            f'<meta name="twitter:image" content="https://{domain}/assets/images/og-image.png">',
        ]
    if domain and page.get("jsonld"):
        tags.append(f'<script type="application/ld+json">{organization_jsonld(domain)}</script>')
    tags += [
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{title}">',
        f'<meta name="twitter:description" content="{desc}">',
        f'<link rel="icon" href="{prefix}assets/images/favicon.svg" type="image/svg+xml">',
        f'<link rel="icon" href="{prefix}assets/images/favicon-32.png" sizes="32x32" type="image/png">',
        f'<link rel="apple-touch-icon" href="{prefix}assets/images/apple-touch-icon.png">',
        f'<link rel="manifest" href="{prefix}site.webmanifest">',
        f'<link rel="stylesheet" href="{prefix}assets/css/style.css">',
        f'<script src="{prefix}assets/js/main.js" defer></script>',
    ]
    return "\n  ".join(tags)


def organization_jsonld(domain):
    data = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": COMPANY,
        "alternateName": BRAND,
        "url": f"https://{domain}/",
        "logo": f"https://{domain}/assets/images/icon-512.png",
        "telephone": PHONE_TEL,
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "Plot N 40, Block C, Sector 88",
            "addressLocality": "Noida",
            "addressRegion": "Uttar Pradesh",
            "postalCode": "201301",
            "addressCountry": "IN",
        },
    }
    return json.dumps(data, ensure_ascii=False).replace("</", "<\\/")


def page_url(domain, file):
    path = "" if file == "index.html" else file
    return f"https://{domain}/{path}"


def brand_html(prefix):
    return (f'<a class="brand" href="{prefix}index.html" aria-label="{BRAND} home">'
            f'<span class="brand-mark">DUSK<span>YN</span></span>'
            f'<span class="brand-sub">Global Sourcing</span></a>')


def header(active, prefix):
    items = []
    for key, label, href in NAV:
        current = ' aria-current="page"' if key == active else ""
        items.append(f'<li><a href="{prefix}{href}"{current}>{label}</a></li>')
    return f"""<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
  <div class="container header-inner">
    {brand_html(prefix)}
    <nav class="site-nav" id="site-nav" aria-label="Main navigation">
      <ul class="nav-list">
        {"".join(items)}
      </ul>
      <div class="mobile-cta">
        <a class="btn btn-primary" {wa_attrs()}>{icon("whatsapp")}Contact Us on WhatsApp</a>
      </div>
    </nav>
    <div class="header-actions">
      <a class="btn btn-primary btn-sm" {wa_attrs()}>{icon("whatsapp")}Contact Us</a>
      <button class="nav-toggle" type="button" aria-controls="site-nav" aria-expanded="false" aria-label="Open menu">
        {icon("menu", "icon icon-open")}{icon("close", "icon icon-close")}
      </button>
    </div>
  </div>
</header>"""


def footer(prefix):
    year = date.today().year
    quick = "".join(f'<li><a href="{prefix}{href}">{label}</a></li>' for _, label, href in NAV)
    services = "".join(
        f'<li><a href="{prefix}services.html#{s["id"]}">{s["title"]}</a></li>' for s in SERVICES[:6])
    return f"""<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div class="footer-about">
        {brand_html(prefix)}
        <p>Online sourcing services for individuals, businesses, retailers, wholesalers and companies looking to source products from India and China.</p>
        <a class="btn btn-primary btn-sm" {wa_attrs()}>{icon("whatsapp")}Contact Us on WhatsApp</a>
      </div>
      <nav aria-label="Footer navigation">
        <h2 class="footer-title">Quick Links</h2>
        <ul class="footer-links">{quick}</ul>
      </nav>
      <nav aria-label="Services">
        <h2 class="footer-title">Services</h2>
        <ul class="footer-links">{services}</ul>
      </nav>
      <div>
        <h2 class="footer-title">Contact</h2>
        <ul class="footer-links footer-contact">
          <li>{icon("phone")}<a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></li>
          <li>{icon("whatsapp")}<a {wa_attrs()}>WhatsApp: {PHONE_DISPLAY}</a></li>
          <li>{icon("map-pin")}<address>{"<br>".join(ADDRESS_LINES)}</address></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <p>&copy; <span data-year>{year}</span> {COMPANY}. All rights reserved.</p>
      <p>{BRAND} is a brand operated by {COMPANY}.</p>
    </div>
  </div>
</footer>
<a class="wa-float" {wa_attrs()} aria-label="Contact DUSKYN on WhatsApp">{icon("whatsapp")}<span class="wa-float-label">WhatsApp Us</span></a>"""


def layout(page, body, domain):
    prefix = page.get("prefix", "")
    return f"""<!doctype html>
<html lang="en">
<head>
  {head(page, domain, prefix)}
</head>
<body>
{header(page.get("active"), prefix)}
<main id="main">
{body}
</main>
{footer(prefix)}
</body>
</html>
"""


# --------------------------------------------------------------------------
# Reusable sections
# --------------------------------------------------------------------------
def section_head(eyebrow, title, text="", center=False, h="h2", title_id=None):
    cls = "section-head center" if center else "section-head"
    tid = f' id="{title_id}"' if title_id else ""
    p = f"<p>{text}</p>" if text else ""
    return f'<div class="{cls} reveal"><span class="eyebrow">{eyebrow}</span><{h}{tid}>{title}</{h}>{p}</div>'


def about_block(full=False):
    paras = "".join(f"<p>{p}</p>" for p in ABOUT_PARAS)
    heading = "" if full else '<span class="eyebrow">Who We Are</span><h2 id="about-title">About DUSKYN</h2>'
    more = "" if full else f'<p><a class="text-link" href="about.html">Learn more about DUSKYN {icon("arrow-right")}</a></p>'
    return f"""<div class="split">
      <div class="split-media reveal">
        <img src="assets/images/about-manufacturing.svg" width="640" height="520" loading="lazy" decoding="async"
             alt="Illustration of a manufacturing facility with shipping containers and packed goods, representing sourcing from manufacturers">
      </div>
      <div class="split-content reveal">
        {heading}
        {paras}
        <div class="history-card">
          <span class="icon-box">{icon("calendar")}</span>
          <div><strong>Online sourcing services since {SINCE}</strong>
          <span>{BRAND} has been providing online sourcing services since {SINCE}.</span></div>
        </div>
        <p class="company-line">{BRAND} is operated by <strong>{COMPANY}</strong>, based in Noida, Uttar Pradesh, India.</p>
        {more}
      </div>
    </div>"""


def service_cards():
    cards = []
    for i, s in enumerate(SERVICES, 1):
        cards.append(f"""<article class="card reveal" id="svc-{s["id"]}">
          <span class="card-num" aria-hidden="true">{i:02d}</span>
          <span class="icon-box">{icon(s["icon"])}</span>
          <h3>{s["title"]}</h3>
          <p>{s["short"]}</p>
          <a class="text-link" {wa_attrs(s["msg"])} aria-label="Contact us on WhatsApp about {s["title"]}">Contact Us {icon("arrow-right")}</a>
        </article>""")
    return f'<div class="card-grid">{"".join(cards)}</div>'


def service_cards_detailed():
    cards = []
    for i, s in enumerate(SERVICES, 1):
        points = "".join(f"<li>{icon('check')}{p}</li>" for p in s["points"])
        cards.append(f"""<article class="card reveal" id="{s["id"]}">
          <span class="card-num" aria-hidden="true">{i:02d}</span>
          <span class="icon-box">{icon(s["icon"])}</span>
          <h2 class="h3">{s["title"]}</h2>
          <p>{s["short"]}</p>
          <p class="detail-label">What you can discuss with us</p>
          <ul class="card-list">{points}</ul>
          <a class="text-link" {wa_attrs(s["msg"])} aria-label="Contact us on WhatsApp about {s["title"]}">Contact Us on WhatsApp {icon("arrow-right")}</a>
        </article>""")
    return f'<div class="card-grid cols-2">{"".join(cards)}</div>'


def services_note():
    return f"""<div class="note reveal">{icon("info")}<p>The scope of assistance, commercial terms and any charges are discussed and agreed directly with {BRAND} for each requirement. Supplier availability, pricing, quality and delivery depend on the individual supplier and the arrangements made.</p></div>"""


def steps_block(section_alt=True):
    items = []
    for i, (t, d) in enumerate(STEPS, 1):
        items.append(f"""<li class="step reveal">
          <span class="step-num">{i:02d}</span>
          <span class="step-label">Step {i}</span>
          <h3>{t}</h3>
          <p>{d}</p>
        </li>""")
    return f"""<ol class="steps">{"".join(items)}</ol>
      <div class="steps-cta reveal">
        <a class="btn btn-primary" {wa_attrs()}>{icon("whatsapp")}Contact Us on WhatsApp</a>
        <small>Opens a WhatsApp chat with {BRAND} at {PHONE_DISPLAY}</small>
      </div>"""


def why_section():
    items = "".join(f"""<div class="feature reveal">
          <span class="icon-box">{icon(ic)}</span>
          <h3>{t}</h3>
          <p>{d}</p>
        </div>""" for ic, t, d in WHY)
    return f"""<section class="section section-dark" id="why-duskyn" aria-labelledby="why-title">
    <div class="container">
      {section_head("Why Choose Us", "Why Choose DUSKYN?", "A practical, requirement-led approach to sourcing from India and China, with direct communication throughout.", title_id="why-title")}
      <div class="feature-grid">{items}</div>
    </div>
  </section>"""


def contact_panel(heading_level="h2"):
    return f"""<div class="contact-panel reveal">
        <div class="contact-intro">
          <span class="eyebrow">Contact Us</span>
          <{heading_level} id="contact-title">Let’s Discuss Your Sourcing Requirements</{heading_level}>
          <p class="lead">Looking for a manufacturer in India or sourcing products from China? Contact {BRAND} and tell us what you need.</p>
          <div class="btn-row">
            <a class="btn btn-primary" {wa_attrs()}>{icon("whatsapp")}Contact Us on WhatsApp</a>
            <a class="btn btn-outline" href="tel:{PHONE_TEL}">{icon("phone")}Call Now</a>
          </div>
        </div>
        <div class="contact-details">
          <ul class="detail-list">
            <li><span class="icon-box">{icon("building")}</span>
              <div><span class="detail-label">Company</span><span class="detail-value">{COMPANY}</span></div></li>
            <li><span class="icon-box">{icon("tag")}</span>
              <div><span class="detail-label">Brand</span><span class="detail-value">{BRAND}</span></div></li>
            <li><span class="icon-box">{icon("phone")}</span>
              <div><span class="detail-label">Phone / WhatsApp</span><span class="detail-value"><a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></span></div></li>
            <li><span class="icon-box">{icon("map-pin")}</span>
              <div><span class="detail-label">Address</span>
              <address class="detail-value">{" ".join(ADDRESS_LINES)}</address>
              <a class="text-link detail-extra" href="{esc(MAPS_URL)}" target="_blank" rel="noopener noreferrer">View on Google Maps {icon("external")}</a></div></li>
          </ul>
        </div>
      </div>"""


def cta_band(title="Have a product or manufacturer in mind?",
             text=f"Send us your requirement on WhatsApp and our team will discuss it with you."):
    return f"""<div class="cta-band reveal">
        <div><h2>{title}</h2><p>{text}</p></div>
        <div class="btn-row">
          <a class="btn btn-light" {wa_attrs()}>{icon("whatsapp")}Contact Us on WhatsApp</a>
          <a class="btn btn-ghost-light" href="tel:{PHONE_TEL}">{icon("phone")}Call Now</a>
        </div>
      </div>"""


def page_hero(crumb, eyebrow, title, lead, prefix=""):
    return f"""<section class="page-hero">
    <div class="container">
      <ol class="breadcrumb" aria-label="Breadcrumb"><li><a href="{prefix}index.html">Home</a></li><li aria-current="page">{crumb}</li></ol>
      <span class="eyebrow">{eyebrow}</span>
      <h1>{title}</h1>
      <p class="lead">{lead}</p>
    </div>
  </section>"""


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------
def page_index():
    body = f"""  <section class="hero" aria-labelledby="hero-title">
    <div class="container hero-grid">
      <div class="hero-content">
        <p class="hero-badge"><span class="dot">{icon("calendar")}</span>Online Sourcing Services Since {SINCE}</p>
        <h1 id="hero-title">Your Trusted Partner for <em>Global Product Sourcing</em></h1>
        <p class="lead">From finding the right manufacturers in India to sourcing products from China, {BRAND} helps businesses connect with suitable suppliers and sourcing solutions.</p>
        <div class="btn-row">
          <a class="btn btn-primary" {wa_attrs()}>{icon("whatsapp")}Contact Us on WhatsApp</a>
          <a class="btn btn-outline" href="#services">Explore Our Services {icon("arrow-right")}</a>
        </div>
        <ul class="hero-points">
          <li>{icon("check-circle")}India &amp; China sourcing</li>
          <li>{icon("check-circle")}Direct WhatsApp communication</li>
          <li>{icon("check-circle")}For individuals &amp; businesses</li>
        </ul>
      </div>
      <div class="hero-visual">
        <img src="assets/images/hero-global-sourcing.svg" width="640" height="560" fetchpriority="high" decoding="async"
             alt="Illustration of a globe with a trade route connecting India and China, a container ship and manufacturer and product sourcing labels">
      </div>
    </div>
  </section>

  <section class="section" id="about" aria-labelledby="about-title">
    <div class="container">
      {about_block()}
    </div>
  </section>

  <section class="section section-alt" id="services" aria-labelledby="services-title">
    <div class="container">
      {section_head("Our Services", "Sourcing Services for India &amp; China", "Whether you are an individual, retailer, wholesaler or company, explore the ways DUSKYN can assist with your sourcing requirements.", center=True, title_id="services-title")}
      {service_cards()}
      {services_note()}
    </div>
  </section>

  <section class="section" id="how-it-works" aria-labelledby="how-title">
    <div class="container">
      {section_head("How It Works", "A Simple Four-Step Process", "Getting started is straightforward. Share what you need and our team will take the conversation forward with you on WhatsApp.", center=True, title_id="how-title")}
      {steps_block()}
    </div>
  </section>

  {why_section()}

  <section class="section section-alt" id="contact" aria-labelledby="contact-title">
    <div class="container">
      {contact_panel()}
    </div>
  </section>"""
    return {
        "file": "index.html",
        "active": "home",
        "title": "DUSKYN APPARELS LLP | Product Sourcing Solutions",
        "description": "DUSKYN, operated by DUSKYN APPARELS LLP, provides online sourcing services for products and manufacturers in India and China. Contact us on WhatsApp.",
        "jsonld": True,
        "body": body,
    }


def page_about():
    audiences = [("user", "Individuals"), ("briefcase", "Businesses"), ("store", "Retailers"),
                 ("warehouse", "Wholesalers"), ("building", "Companies")]
    aud = "".join(f'<li class="enquiry-link reveal">{icon(ic)}{t}</li>'
                  for ic, t in audiences)
    body = f"""  {page_hero("About Us", "About DUSKYN", "About DUSKYN", f"Online sourcing assistance for businesses and individuals seeking products and manufacturing opportunities in India and China, since {SINCE}.")}

  <section class="section" aria-label="Company overview">
    <div class="container">
      {about_block(full=True)}
    </div>
  </section>

  <section class="section section-alt" aria-labelledby="what-title">
    <div class="container">
      {section_head("What We Do", "Sourcing Assistance Across Two Markets", "Our services focus on two major manufacturing destinations. Tell us your requirement and we will discuss which sourcing options may suit you.", title_id="what-title")}
      <div class="card-grid cols-2">
        <article class="card reveal">
          <span class="icon-box">{icon("factory")}</span>
          <h3>Sourcing in India</h3>
          <p>Help with finding suitable manufacturers in India, whether you need a standard product, wholesale supply, or manufacturing to your own specifications.</p>
          <a class="text-link" {wa_attrs(SERVICES[1]["msg"])}>Ask about Indian manufacturers {icon("arrow-right")}</a>
        </article>
        <article class="card reveal">
          <span class="icon-box">{icon("globe")}</span>
          <h3>Sourcing from China</h3>
          <p>Help with exploring product sourcing opportunities from China, including sourcing-related assistance for customers considering importing products.</p>
          <a class="text-link" {wa_attrs(SERVICES[0]["msg"])}>Ask about China sourcing {icon("arrow-right")}</a>
        </article>
      </div>
    </div>
  </section>

  <section class="section" aria-labelledby="who-title">
    <div class="container">
      {section_head("Who We Work With", "Sourcing Support for Different Kinds of Buyers", "DUSKYN provides online sourcing services to individuals, businesses, retailers, wholesalers and companies looking to source products from India and China.", title_id="who-title")}
      <ul class="audience-grid">{aud}</ul>
    </div>
  </section>

  {why_section()}

  <section class="section">
    <div class="container">
      {cta_band()}
    </div>
  </section>"""
    return {
        "file": "about.html",
        "active": "about",
        "title": "About DUSKYN | Online Sourcing Services Since 2017",
        "description": "Learn about DUSKYN, operated by DUSKYN APPARELS LLP in Noida, providing online sourcing assistance for products and manufacturers in India and China since 2017.",
        "body": body,
    }


def page_services():
    body = f"""  {page_hero("Our Services", "Our Services", "Sourcing Services for India &amp; China", "Explore how DUSKYN can assist with finding manufacturers in India, sourcing products from China and identifying suppliers for your business requirements.")}

  <section class="section" aria-label="Service list">
    <div class="container">
      {service_cards_detailed()}
      {services_note()}
    </div>
  </section>

  <section class="section section-alt" id="how-it-works" aria-labelledby="how-title">
    <div class="container">
      {section_head("How It Works", "From Requirement to Next Steps", "Every enquiry starts with a conversation. Here is how working with DUSKYN typically begins.", center=True, title_id="how-title")}
      {steps_block()}
    </div>
  </section>

  <section class="section">
    <div class="container">
      {cta_band("Not sure which service fits?", "Describe your product or requirement on WhatsApp and we will discuss the options with you.")}
    </div>
  </section>"""
    return {
        "file": "services.html",
        "active": "services",
        "title": "Our Services | China & India Product Sourcing | DUSKYN",
        "description": "China product sourcing, Indian manufacturer sourcing, wholesale sourcing, custom manufacturing assistance, supplier discovery and more from DUSKYN. Enquire on WhatsApp.",
        "body": body,
    }


def page_contact():
    links = "".join(
        f'<a class="enquiry-link reveal" {wa_attrs(s["msg"])}>{s["enquiry"]}{icon("whatsapp")}</a>' for s in SERVICES)
    checklist_items = [
        "Product name or a short description",
        "Photos, samples or reference links, if available",
        "Approximate quantity you need",
        "Specifications such as size, material or colour",
        "Preferred sourcing country: India, China or either",
        "Your location and expected timeline",
    ]
    checklist = "".join(f"<li>{icon('check-circle')}<span>{c}</span></li>" for c in checklist_items)
    body = f"""  {page_hero("Contact Us", "Contact Us", "Contact DUSKYN", "The quickest way to reach us is WhatsApp. You can also call us or find our address below.")}

  <section class="section" aria-labelledby="contact-title">
    <div class="container">
      {contact_panel()}
    </div>
  </section>

  <section class="section section-alt" aria-labelledby="enquiry-title">
    <div class="container">
      {section_head("Quick Enquiry", "Start a WhatsApp Enquiry by Service", "Choose the service you are interested in. WhatsApp will open with a message that mentions it, so our team knows what you need.", title_id="enquiry-title")}
      <div class="enquiry-grid">{links}</div>
    </div>
  </section>

  <section class="section" aria-labelledby="include-title">
    <div class="container split align-start">
      <div class="reveal">
        <span class="eyebrow">Helpful Tips</span>
        <h2 id="include-title">What to Include in Your Message</h2>
        <p class="lead">Sharing a few details at the start helps our team understand your requirement and respond more usefully.</p>
      </div>
      <ul class="checklist reveal">{checklist}</ul>
    </div>
  </section>"""
    return {
        "file": "contact.html",
        "active": "contact",
        "title": "Contact DUSKYN | WhatsApp +91 8000190745",
        "description": "Contact DUSKYN (DUSKYN APPARELS LLP) on WhatsApp or call +91 8000190745. Plot N 40, Block C, Sector 88, Noida, Gautam Buddha Nagar, Uttar Pradesh 201301.",
        "body": body,
    }


def page_404(domain):
    prefix = f"https://{domain}/" if domain else ""
    body = f"""  <section class="not-found">
    <div class="container">
      <p class="code">ERROR 404</p>
      <h1>Page not found</h1>
      <p class="lead">The page you are looking for does not exist or may have moved.</p>
      <div class="btn-row">
        <a class="btn btn-dark" href="{prefix}index.html">Back to Home</a>
        <a class="btn btn-primary" {wa_attrs()}>{icon("whatsapp")}Contact Us on WhatsApp</a>
      </div>
    </div>
  </section>"""
    return {
        "file": "404.html",
        "active": None,
        "prefix": prefix,
        "noindex": True,
        "title": "Page Not Found | DUSKYN",
        "description": "The page you are looking for could not be found.",
        "body": body,
    }


# --------------------------------------------------------------------------
# Build
# --------------------------------------------------------------------------
DOMAIN_RE = re.compile(r"^(?=.{1,253}$)(?!-)[a-z0-9-]{1,63}(?<!-)(\.(?!-)[a-z0-9-]{1,63}(?<!-))+$")


def resolve_domain(arg, force):
    cname = ROOT / "CNAME"
    existing = cname.read_text().strip().lower() if cname.exists() else None
    if not arg:
        return existing
    domain = arg.strip().lower().removeprefix("https://").removeprefix("http://").rstrip("/")
    if not DOMAIN_RE.match(domain):
        sys.exit(f"error: '{arg}' does not look like a valid domain name")
    if existing and existing != domain and not force:
        sys.exit(f"error: CNAME already contains '{existing}'. Re-run with --force to replace it.")
    if existing != domain:
        cname.write_text(domain + "\n")
        print(f"wrote CNAME -> {domain}")
    return domain


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--domain", help="custom domain, e.g. www.example.com")
    ap.add_argument("--force", action="store_true", help="replace an existing, different CNAME")
    args = ap.parse_args()
    domain = resolve_domain(args.domain, args.force)

    pages = [page_index(), page_about(), page_services(), page_contact(), page_404(domain)]
    for p in pages:
        (ROOT / p["file"]).write_text(layout(p, p["body"], domain), encoding="utf-8")
        print(f"built {p['file']}")

    robots = "User-agent: *\nAllow: /\n"
    if domain:
        robots += f"\nSitemap: https://{domain}/sitemap.xml\n"
        today = date.today().isoformat()
        urls = "".join(
            f"  <url>\n    <loc>{page_url(domain, p['file'])}</loc>\n    <lastmod>{today}</lastmod>\n  </url>\n"
            for p in pages if not p.get("noindex"))
        (ROOT / "sitemap.xml").write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n")
        print("built sitemap.xml")
    else:
        print("note: no domain set; skipped canonical URLs, og:url/og:image and sitemap.xml "
              "(run with --domain your-domain.com)")
    (ROOT / "robots.txt").write_text(robots)
    print("built robots.txt")


if __name__ == "__main__":
    main()

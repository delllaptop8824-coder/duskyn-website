# DUSKYN APPARELS LLP — website

Static website for **DUSKYN APPARELS LLP**, to be served at **https://duskyn.co**.
Plain HTML, CSS and vanilla JavaScript. No framework, backend, database or paid service. Built for GitHub Pages.

The design, layout and page structure are reused from the BB247 website
(`delllaptop8824-coder/bb247-website`, owned by the same account), with all branding,
contact details and company-specific claims replaced for DUSKYN APPARELS LLP. This
project is separate from BB247: it has its own repository, its own GitHub Pages site and
its own domain.

## Company details used on the site

| Field            | Value |
|------------------|-------|
| Legal name       | DUSKYN APPARELS LLP |
| Registered address | Plot N 40, Block C, Sector 88, Noida, Gautam Buddha Nagar, Uttar Pradesh – 201301, India. |
| Phone / WhatsApp | +91 8000190745 (`tel:+918000190745`, `https://wa.me/918000190745`) |
| GSTIN            | **Not yet added.** Set `GSTIN` in `tools/build.py` from the GST certificate, then rebuild. |
| Domain           | https://duskyn.co |

## Structure

```
index.html          Home: hero, about, services, how it works, why choose, contact
about.html          About, what we do, who we work with
services.html       All 8 services in detail, with service-specific WhatsApp enquiries
contact.html        Contact details, per-service WhatsApp enquiries, what to include
404.html            Not-found page (served automatically by GitHub Pages)
assets/css/style.css
assets/js/main.js   Mobile menu, header state, footer year, subtle reveal animation
assets/images/      SVG illustrations, favicons, Open Graph image (og-image.png)
site.webmanifest
robots.txt
sitemap.xml         Generated once the custom domain is set
CNAME               Generated once the custom domain is set
.nojekyll           Tells GitHub Pages to serve files as-is
tools/build.py      Generator for the HTML pages, sitemap and robots.txt
```

## Editing content

The pages are generated from `tools/build.py` so that the header, footer, SEO tags and
WhatsApp links stay the same on every page. To change text, services or contact details:

1. Edit `tools/build.py` (business details are at the top, services in `SERVICES`).
2. Run `python3 tools/build.py`.
3. Commit the regenerated files.

Styling lives in `assets/css/style.css`. If you edit an `.html` file directly, the next
build will overwrite your change, so make the change in `tools/build.py` as well.

## WhatsApp and phone

- Every "Contact Us" button opens `https://wa.me/918000190745` with the URL-encoded message
  "Hello DUSKYN APPARELS LLP, I am interested in your services. Please share more information."
- Each service has its own prefilled message (for example a China sourcing enquiry).
- "Call Now" uses `tel:+918000190745`.

## Deploy to GitHub Pages

1. Create an empty repository named `duskyn-website` on GitHub (no README, licence or .gitignore).
2. Push this project:

   ```bash
   git remote add origin https://github.com/<your-username>/duskyn-website.git
   git remote -v        # check it says duskyn-website, not bb247-website
   git push -u origin main
   ```

3. On GitHub: **Settings → Pages → Build and deployment → Source: Deploy from a branch**,
   **Branch: `main`**, folder **`/ (root)`**, **Save**.
4. Check the site at `https://<your-username>.github.io/duskyn-website/`.

## Custom domain (duskyn.co)

Do this only after the default GitHub Pages URL works.

1. Add the DNS records below at the registrar for duskyn.co.
2. Build with the domain. This writes `CNAME`, canonical URLs, `og:url`/`og:image`,
   Organization structured data, `sitemap.xml` and the sitemap line in `robots.txt`:

   ```bash
   python3 tools/build.py --domain duskyn.co
   git add -A && git commit -m "Set custom domain duskyn.co" && git push
   ```

3. **Settings → Pages → Custom domain**: enter `duskyn.co`, **Save**, wait for the DNS check.
4. When GitHub says the certificate is ready, tick **Enforce HTTPS**.
5. Recommended: verify the domain under your GitHub **profile Settings → Pages → Add a domain**.

### DNS records for duskyn.co

`duskyn.co` (the apex) is the main address. `www.duskyn.co` is redirected to it by GitHub Pages.

| Type  | Host / Name | Value |
|-------|-------------|-------|
| A     | `@`   | `185.199.108.153` |
| A     | `@`   | `185.199.109.153` |
| A     | `@`   | `185.199.110.153` |
| A     | `@`   | `185.199.111.153` |
| AAAA  | `@`   | `2606:50c0:8000::153` |
| AAAA  | `@`   | `2606:50c0:8001::153` |
| AAAA  | `@`   | `2606:50c0:8002::153` |
| AAAA  | `@`   | `2606:50c0:8003::153` |
| CNAME | `www` | `<your-username>.github.io` |

Notes:
- A CNAME record cannot be used on the apex `@`; use the A/AAAA records above.
- Before adding these, look at the records that already exist for `@` and `www` on duskyn.co.
  Parking or old hosting A/AAAA/CNAME records for those names conflict and need removing, but
  leave MX, TXT (email, verification) and other unrelated records alone.
- Do not use wildcard records (`*`).
- These changes apply only to duskyn.co. They do not touch bb247.vip.
- Check with `dig duskyn.co +short` and `dig www.duskyn.co +short`.

## Images

The illustrations are original SVGs reused from the BB247 site. The DUSKYN favicon,
app icons and Open Graph image were generated for this site. You can replace
`assets/images/hero-global-sourcing.svg` or `assets/images/about-manufacturing.svg` with
licensed photographs; keep the `width`/`height` and `alt` attributes in `tools/build.py`
accurate when you do.

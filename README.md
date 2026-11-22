![logo](Logo/Webcrack.png)

# SK WEB v1.0
> Ultimate Deep Web Crawler & Recon Engine

![logo](Logo/Logo.jpeg)

---

## Developer
**SK 

---

## Features

```
✔ Multi-thread Crawling     — 2-15 threads, fast & deep
✔ JS Secret Scanner         — API key, AWS, Stripe, JWT, Firebase, MongoDB
✔ WAF Detection             — Cloudflare, Akamai, Sucuri, Imperva, AWS WAF
✔ Tech Fingerprinting       — WordPress, Laravel, React, Django, 20+ tech
✔ Security Header Audit     — CSP, HSTS, X-Frame, 10+ headers
✔ SSL Certificate Info      — issuer, expiry, cipher
✔ Email & Phone Extractor   — from HTML and JS files
✔ API Endpoint Discovery    — extracts /api/v1/... paths from JS
✔ Hidden Path Probe         — /.env, /.git, /admin, /phpmyadmin, 40+ paths
✔ Robots.txt + Sitemap      — disallowed paths + auto-queue sitemap URLs
✔ Broken Link Checker       — parallel HEAD requests
✔ HTML Report               — browser-ready dark theme report
✔ Full Asset Download       — HTML, CSS, JS, Images, SVG, Fonts
```

---

## Install & Run (Termux)

```bash
apt update -y
apt upgrade -y
apt install python -y
apt install git -y
termux-setup-storage
git clone https://github.com/rdxsakib65/SK_WEB.git
cd SK-WEB
python sk_web.py
```

> No extra libraries needed. Pure Python stdlib.

---

## Save Output to Storage

After scan is done, open a new terminal:

```bash
ls
cd SK-WEB
ls
cp -r SK_WEB_targetname_timestamp ~/storage/shared
```

Then check your file manager — output folder will be there.

---

## Output Structure

```
SK_WEB_target_timestamp/
├── report.html        ← Open in browser (full HTML report)
├── manifest.json      ← Full JSON data
├── pages/             ← All HTML pages
├── css/               ← All CSS files
├── js/                ← All JS files (scanned for secrets)
├── images/            ← Images
├── svg/               ← SVG files
├── fonts/             ← Fonts
├── docs/              ← Documents
├── media/             ← Media files
└── recon/             ← robots.txt and recon notes
```

---

## Menu Options

```
[1] Full scan — assets + hidden path probe + full recon
[2] Source + recon — no asset download
[3] Full + broken link check
[4] Recon only — 1 page, full analysis
```

---

## Legal Notice

> This tool is for educational and authorized security testing only.
> Do not use on websites without permission.
> Developer not responsible for misuse.

---

**SK WEB v1.0** — Developed by SK

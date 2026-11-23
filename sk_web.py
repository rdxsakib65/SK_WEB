#!/usr/bin/env python3
# ╔══════════════════════════════════════════════════════════════════════╗
# ║          SK WEB v1.0 — Ultimate Deep Crawler & Recon Engine         ║
# ║          Author : SK SAKIB 👿  [ SK WEB ]                            ║
# ║          Mode   : Multi-thread · Full Recon · HTML Report            ║
# ╚══════════════════════════════════════════════════════════════════════╝

import sys, os, re, json, time, gzip, hashlib, socket, ssl, threading
import urllib.request, urllib.parse, urllib.error
from html.parser import HTMLParser
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# ════════════════════════════════════════════════════════════════════
#  ANSI COLORS
# ════════════════════════════════════════════════════════════════════
G1="\033[38;5;46m"; G2="\033[38;5;40m"; G3="\033[38;5;34m"
W="\033[1;37m"; DW="\033[0;37m"; DIM="\033[2m"
RED="\033[1;31m"; YEL="\033[1;33m"; CYN="\033[1;36m"
MAG="\033[1;35m"; BLU="\033[1;34m"; RS="\033[0m"; BLD="\033[1m"

# ════════════════════════════════════════════════════════════════════
#  BANNER
# ════════════════════════════════════════════════════════════════════
def banner():
    os.system("clear")
    print(f"""
{G1}  ███████╗██╗  ██╗    ██╗    ██╗███████╗██████╗ {RS}
{G1}  ██╔════╝██║ ██╔╝    ██║    ██║██╔════╝██╔══██╗{RS}
{G2}  ███████╗█████╔╝     ██║ █╗ ██║█████╗  ██████╔╝{RS}
{G2}  ╚════██║██╔═██╗     ██║███╗██║██╔══╝  ██╔══██╗{RS}
{G3}  ███████║██║  ██╗    ╚███╔███╔╝███████╗██████╔╝{RS}
{G3}  ╚══════╝╚═╝  ╚═╝     ╚══╝╚══╝ ╚══════╝╚═════╝ {RS}

{G2}  ╔══════════════════════════════════════════════════════════╗{RS}
{G2}  ║  {W}Tool    : {G1}SK WEB v1.0 — Ultimate Recon Engine     {G2}║{RS}
{G2}  ║  {W}Author  : {G1}SK SAKIB 👿                             {G2}║{RS}
{G2}  ║  {W}Modules : {G1}Crawl·Recon·JS·WAF·SSL·Report·Threads  {G2}║{RS}
{G2}  ╚══════════════════════════════════════════════════════════╝{RS}
""")

# ════════════════════════════════════════════════════════════════════
#  STATUS
# ════════════════════════════════════════════════════════════════════
_print_lock = threading.Lock()
def _p(*a, **kw):
    with _print_lock: print(*a, **kw)

def ok(m):   _p(f"  {G1}[+]{RS} {W}{m}{RS}")
def info(m): _p(f"  {G2}[*]{RS} {DW}{m}{RS}")
def warn(m): _p(f"  {YEL}[!]{RS} {DW}{m}{RS}")
def err(m):  _p(f"  {RED}[✗]{RS} {DW}{m}{RS}")
def step(m): _p(f"  {G3}[→]{RS} {DW}{m}{RS}")
def hit(m):  _p(f"  {CYN}[★]{RS} {CYN}{m}{RS}")
def vuln(m): _p(f"  {RED}[⚠]{RS} {RED}{BLD}{m}{RS}")
def saved(m):_p(f"  {G1}[✔]{RS} {G2}{m}{RS}")

def section(t):
    pad=max(0,52-len(t))
    _p(f"\n{G2}  ╔══ {G1}{t}{G2} {'═'*pad}╗{RS}")
def section_end():
    _p(f"{G2}  ╚{'═'*58}╝{RS}\n")

def progress_bar(d,t,w=28):
    pct=d/max(t,1); fill=int(w*pct)
    bar="█"*fill+"░"*(w-fill)
    return f"{G1}[{bar}]{RS} {W}{d}/{t}{RS} {DIM}{pct*100:.0f}%{RS}"

# ════════════════════════════════════════════════════════════════════
#  SPINNER
# ════════════════════════════════════════════════════════════════════
_spin_active=False; _spin_thread=None
def _spin_worker(msg):
    frames=["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]; i=0
    while _spin_active:
        with _print_lock:
            print(f"\r{G1}  {frames[i%len(frames)]}  {W}{msg}{RS}",end="",flush=True)
        time.sleep(0.08); i+=1
    with _print_lock:
        print("\r"+" "*(len(msg)+10)+"\r",end="",flush=True)

def spin_start(msg):
    global _spin_active,_spin_thread
    _spin_active=True
    _spin_thread=threading.Thread(target=_spin_worker,args=(msg,),daemon=True)
    _spin_thread.start()

def spin_stop():
    global _spin_active
    _spin_active=False
    if _spin_thread: _spin_thread.join()

# ════════════════════════════════════════════════════════════════════
#  HEADERS
# ════════════════════════════════════════════════════════════════════
UA = ("Mozilla/5.0 (Linux; Android 14; Pixel 8) "
      "AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0.6367.82 Mobile Safari/537.36")

HEADERS = {
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "no-cache", "DNT": "1",
}
ASSET_HEADERS = dict(HEADERS)
ASSET_HEADERS["Accept"] = "image/avif,image/webp,image/*,*/*;q=0.8"

# ════════════════════════════════════════════════════════════════════
#  ASSET TYPES
# ════════════════════════════════════════════════════════════════════
IMAGE_EXTS={".png",".jpg",".jpeg",".gif",".webp",".avif",".ico",".bmp",".tiff"}
SVG_EXTS={".svg",".svgz"}
FONT_EXTS={".woff",".woff2",".ttf",".otf",".eot"}
DOC_EXTS={".pdf",".doc",".docx",".xls",".xlsx",".ppt",".pptx"}
MEDIA_EXTS={".mp4",".webm",".mp3",".ogg",".wav"}
SKIP_EXTS={".exe",".dmg",".apk",".zip",".tar",".gz",".rar"}
HTML_EXTS={"",".html",".htm",".php",".asp",".aspx",".jsp",".cfm",".cgi"}

def asset_category(url):
    ext=os.path.splitext(urllib.parse.urlparse(url).path)[1].lower()
    if ext in IMAGE_EXTS: return "images"
    if ext in SVG_EXTS:   return "svg"
    if ext in FONT_EXTS:  return "fonts"
    if ext in DOC_EXTS:   return "docs"
    if ext in MEDIA_EXTS: return "media"
    if ext in SKIP_EXTS:  return None
    if ext==".css": return "css"
    if ext==".js":  return "js"
    return None

def is_html_url(url):
    ext=os.path.splitext(urllib.parse.urlparse(url).path)[1].lower()
    return ext in HTML_EXTS

# ════════════════════════════════════════════════════════════════════
#  FETCH
# ════════════════════════════════════════════════════════════════════
def raw_fetch(url, timeout=20, extra_headers=None):
    h=dict(HEADERS)
    if extra_headers: h.update(extra_headers)
    req=urllib.request.Request(url, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            enc=resp.headers.get("Content-Encoding","")
            ct=resp.headers.get("Content-Type","")
            srv=resp.headers.get("Server","Unknown")
            raw=resp.read()
            if enc=="gzip":
                try: raw=gzip.decompress(raw)
                except: pass
            charset="utf-8"
            if "charset=" in ct:
                charset=ct.split("charset=")[-1].split(";")[0].strip()
            try: text=raw.decode(charset,errors="replace")
            except: text=raw.decode("utf-8",errors="replace")
            resp_headers=dict(resp.headers)
            return {"ok":True,"text":text,"raw":raw,"status":resp.status,
                    "url":resp.geturl(),"ct":ct,"server":srv,
                    "headers":resp_headers}
    except urllib.error.HTTPError as e:
        return {"ok":False,"status":e.code,"error":str(e),"headers":{}}
    except urllib.error.URLError as e:
        return {"ok":False,"status":0,"error":str(e.reason),"headers":{}}
    except socket.timeout:
        return {"ok":False,"status":0,"error":"Timeout","headers":{}}
    except Exception as e:
        return {"ok":False,"status":-1,"error":str(e),"headers":{}}

def head_fetch(url, timeout=10):
    try:
        req=urllib.request.Request(url, headers=HEADERS, method="HEAD")
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status
    except urllib.error.HTTPError as e: return e.code
    except: return 0

def binary_fetch(url, timeout=30):
    req=urllib.request.Request(url, headers=ASSET_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw=resp.read()
            return {"ok":True,"raw":raw,"size":len(raw),
                    "status":resp.status,"ct":resp.headers.get("Content-Type","")}
    except Exception as e:
        return {"ok":False,"error":str(e)}

# ════════════════════════════════════════════════════════════════════
#  SSL INFO
# ════════════════════════════════════════════════════════════════════
def get_ssl_info(host, port=443):
    try:
        ctx=ssl.create_default_context()
        with ctx.wrap_socket(socket.create_connection((host,port),timeout=8),
                             server_hostname=host) as s:
            cert=s.getpeercert()
            cipher=s.cipher()
            nb=cert.get("notBefore","?")
            na=cert.get("notAfter","?")
            issuer=dict(x[0] for x in cert.get("issuer",())) if cert.get("issuer") else {}
            subject=dict(x[0] for x in cert.get("subject",())) if cert.get("subject") else {}
            return {
                "valid":True,
                "cn": subject.get("commonName","?"),
                "issuer": issuer.get("organizationName","?"),
                "not_before": nb,
                "not_after": na,
                "cipher": cipher[0] if cipher else "?",
                "protocol": cipher[1] if cipher else "?",
            }
    except ssl.SSLCertVerificationError as e:
        return {"valid":False,"error":f"CERT ERROR: {e}"}
    except Exception as e:
        return {"valid":None,"error":str(e)}

# ════════════════════════════════════════════════════════════════════
#  WAF DETECTION
# ════════════════════════════════════════════════════════════════════
WAF_SIGNATURES = {
    "Cloudflare":     ["cf-ray","cloudflare","__cfduid","cf-cache-status"],
    "Akamai":         ["akamai","x-check-cacheable","x-akamai-transformed"],
    "Sucuri":         ["sucuri","x-sucuri-id","x-sucuri-cache"],
    "Imperva/Incapsula":["x-iinfo","incap_ses","visid_incap","x-cdn=imperva"],
    "AWS WAF":        ["awselb","x-amzn-requestid","x-amz-cf-id"],
    "ModSecurity":    ["mod_security","modsecurity","x-mod-pagespeed"],
    "F5 BIG-IP":      ["bigip","ts","f5-"],
    "Barracuda":      ["barra_counter_session","barracuda_"],
    "DDoS-Guard":     ["ddos-guard","__ddg"],
    "Qrator":         ["qrator"],
    "Wordfence":      ["wordfence"],
}

def detect_waf(response_headers, html=""):
    detected=[]
    hdr_str=" ".join(f"{k.lower()}:{v.lower()}"
                     for k,v in response_headers.items())
    for waf,sigs in WAF_SIGNATURES.items():
        if any(s in hdr_str or s in html.lower() for s in sigs):
            detected.append(waf)
    return detected

# ════════════════════════════════════════════════════════════════════
#  SECURITY HEADER AUDIT
# ════════════════════════════════════════════════════════════════════
SEC_HEADERS = {
    "Strict-Transport-Security": "HSTS",
    "Content-Security-Policy":   "CSP",
    "X-Frame-Options":           "Clickjack Protection",
    "X-Content-Type-Options":    "MIME Sniff Protection",
    "Referrer-Policy":           "Referrer Policy",
    "Permissions-Policy":        "Permissions Policy",
    "X-XSS-Protection":          "XSS Protection",
    "Expect-CT":                 "Certificate Transparency",
    "Cross-Origin-Opener-Policy":"COOP",
    "Cross-Origin-Embedder-Policy":"COEP",
}

def audit_security_headers(headers):
    present=[]; missing=[]
    hl={k.lower():v for k,v in headers.items()}
    for hdr,label in SEC_HEADERS.items():
        if hdr.lower() in hl:
            present.append({"header":hdr,"label":label,"value":hl[hdr.lower()]})
        else:
            missing.append({"header":hdr,"label":label})
    return {"present":present,"missing":missing}

# ════════════════════════════════════════════════════════════════════
#  TECH FINGERPRINT
# ════════════════════════════════════════════════════════════════════
TECH_SIGS = {
    "WordPress":      [r'wp-content',r'wp-includes',r'wordpress'],
    "Joomla":         [r'/components/com_',r'joomla'],
    "Drupal":         [r'sites/all',r'drupal\.js',r'Drupal\.settings'],
    "Laravel":        [r'laravel_session',r'csrf-token.*laravel'],
    "Django":         [r'csrfmiddlewaretoken',r'django'],
    "React":          [r'react\.production\.min\.js',r'__REACT',r'data-reactroot'],
    "Vue.js":         [r'vue\.runtime',r'__vue__',r'data-v-'],
    "Angular":        [r'ng-version',r'angular\.min\.js',r'ng-app'],
    "Next.js":        [r'__NEXT_DATA__',r'/_next/'],
    "Bootstrap":      [r'bootstrap\.min\.css',r'bootstrap\.bundle'],
    "jQuery":         [r'jquery\.min\.js',r'jquery-\d'],
    "Shopify":        [r'cdn\.shopify\.com',r'Shopify\.'],
    "WooCommerce":    [r'woocommerce',r'wc-blocks'],
    "PHP":            [r'\.php',r'X-Powered-By.*PHP'],
    "ASP.NET":        [r'__VIEWSTATE',r'aspnetForm',r'ASP\.NET'],
    "Ruby on Rails":  [r'rails',r'authenticity_token'],
    "Nginx":          [r'nginx'],
    "Apache":         [r'apache'],
    "Cloudflare CDN": [r'cf-ray',r'cloudflare'],
    "Google Analytics":[r'google-analytics\.com',r'gtag\(',r'_ga'],
    "Google Tag Mgr": [r'googletagmanager\.com',r'GTM-'],
    "Facebook Pixel": [r'connect\.facebook\.net',r'fbq\('],
    "reCAPTCHA":      [r'recaptcha',r'grecaptcha'],
}

def fingerprint_tech(html, headers, url):
    found={}
    hdr_str=" ".join(f"{k}:{v}" for k,v in headers.items())
    combo=html[:50000]+hdr_str
    for tech,sigs in TECH_SIGS.items():
        for sig in sigs:
            if re.search(sig,combo,re.IGNORECASE):
                found[tech]=True; break
    srv=headers.get("Server",headers.get("server",""))
    if srv: found[f"Server: {srv}"]=True
    xpb=headers.get("X-Powered-By",headers.get("x-powered-by",""))
    if xpb: found[f"Powered-By: {xpb}"]=True
    return list(found.keys())

# ════════════════════════════════════════════════════════════════════
#  JS RECON -- secrets, endpoints, emails
# ════════════════════════════════════════════════════════════════════
SECRET_PATTERNS = {
    "API Key (generic)":    r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\']([A-Za-z0-9_\-]{16,})["\']',
    "AWS Access Key":       r'AKIA[0-9A-Z]{16}',
    "AWS Secret":           r'(?i)aws.{0,20}secret.{0,20}["\']([A-Za-z0-9/+=]{40})["\']',
    "Google API Key":       r'AIza[0-9A-Za-z\-_]{35}',
    "Firebase URL":         r'https://[a-z0-9-]+\.firebaseio\.com',
    "Firebase API Key":     r'(?i)firebase.{0,20}["\']([A-Za-z0-9_\-]{35,40})["\']',
    "Stripe Key":           r'(?:pk|sk)_(test|live)_[A-Za-z0-9]{24,}',
    "GitHub Token":         r'(?i)github.{0,20}["\']([0-9a-zA-Z]{35,40})["\']',
    "JWT Token":            r'eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}',
    "Bearer Token":         r'(?i)bearer\s+([A-Za-z0-9_\-\.]{20,})',
    "Password in JS":       r'(?i)(password|passwd|pwd)\s*[=:]\s*["\']([^"\']{4,})["\']',
    "Private Key":          r'-----BEGIN (RSA|EC|OPENSSH|DSA) PRIVATE KEY-----',
    "Slack Webhook":        r'https://hooks\.slack\.com/services/T[A-Z0-9]+/B[A-Z0-9]+/[A-Za-z0-9]+',
    "Telegram Bot Token":   r'\d{8,10}:[A-Za-z0-9_\-]{35}',
    "MongoDB URI":          r'mongodb(\+srv)?://[^"\'<>\s]+',
    "MySQL URI":            r'mysql://[^"\'<>\s]+',
    "Redis URI":            r'redis://[^"\'<>\s]+',
}

ENDPOINT_PATTERN = re.compile(
    r'["\`](\/(api|v[0-9]|rest|graphql|endpoint|auth|login|user|admin|'
    r'account|token|refresh|data|query|upload|webhook)'
    r'[a-zA-Z0-9/_\-\.]*)["\`]'
)
EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}')
PHONE_PATTERN = re.compile(r'(?<!\d)(\+?[0-9]{1,3}[\s\-]?)?(\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4})(?!\d)')
IP_PATTERN    = re.compile(r'\b(?!10\.|192\.168\.|172\.)(\d{1,3}\.){3}\d{1,3}\b')

def scan_js(js_text, source_url=""):
    findings={"secrets":[],"endpoints":set(),"emails":set(),
              "phones":set(),"ips":set()}
    for label,pat in SECRET_PATTERNS.items():
        for m in re.finditer(pat,js_text):
            val=m.group(0)[:120]
            findings["secrets"].append({"type":label,"value":val,"source":source_url})
    for m in ENDPOINT_PATTERN.finditer(js_text):
        findings["endpoints"].add(m.group(1))
    for m in EMAIL_PATTERN.finditer(js_text):
        e=m.group(0)
        if not any(x in e for x in [".png",".jpg",".gif",".css",".js"]):
            findings["emails"].add(e)
    for m in PHONE_PATTERN.finditer(js_text):
        findings["phones"].add(m.group(0).strip())
    for m in IP_PATTERN.finditer(js_text):
        findings["ips"].add(m.group(0))
    findings["endpoints"]=list(findings["endpoints"])
    findings["emails"]=list(findings["emails"])
    findings["phones"]=list(findings["phones"])
    findings["ips"]=list(findings["ips"])
    return findings

def scan_html_for_emails_phones(html):
    emails=set(); phones=set()
    for m in EMAIL_PATTERN.finditer(html):
        e=m.group(0)
        if not any(x in e for x in [".png",".jpg",".gif",".css",".js",".php@"]):
            emails.add(e)
    for m in PHONE_PATTERN.finditer(html):
        phones.add(m.group(0).strip())
    return list(emails),list(phones)

# ════════════════════════════════════════════════════════════════════
#  ROBOTS.TXT + SITEMAP
# ════════════════════════════════════════════════════════════════════
def fetch_robots(base_url):
    r=raw_fetch(urllib.parse.urljoin(base_url,"/robots.txt"),timeout=10)
    if not r["ok"]: return {"raw":"","disallowed":[],"sitemaps":[]}
    disallowed=[]; sitemaps=[]
    for line in r["text"].splitlines():
        line=line.strip()
        if line.lower().startswith("disallow:"):
            p=line.split(":",1)[1].strip()
            if p: disallowed.append(p)
        elif line.lower().startswith("sitemap:"):
            s=line.split(":",1)[1].strip()
            if s: sitemaps.append(s)
    return {"raw":r["text"],"disallowed":disallowed,"sitemaps":sitemaps}

def fetch_sitemap_urls(sitemap_url, limit=200):
    r=raw_fetch(sitemap_url,timeout=15)
    if not r["ok"]: return []
    urls=re.findall(r'<loc>(.*?)</loc>',r["text"],re.IGNORECASE)
    return urls[:limit]

# ════════════════════════════════════════════════════════════════════
#  COMMON PATHS PROBE
# ════════════════════════════════════════════════════════════════════
COMMON_PATHS=[
    "/admin","/wp-admin","/administrator","/login","/wp-login.php",
    "/phpmyadmin","/pma","/cpanel","/webmail","/mail",
    "/.env","/.git/config","/.htaccess","/web.config","/config.php",
    "/backup","/backup.zip","/db.sql","/database.sql","/dump.sql",
    "/api","/api/v1","/api/v2","/graphql","/swagger","/swagger-ui.html",
    "/sitemap.xml","/sitemap_index.xml","/robots.txt",
    "/readme.txt","/README.md","/CHANGELOG.md",
    "/server-status","/server-info",
    "/debug","/test","/tmp","/temp","/logs","/log",
    "/uploads","/files","/media","/assets","/static",
    "/.DS_Store","/.well-known/security.txt",
    "/wp-json/wp/v2/users","/wp-config.php.bak",
    "/composer.json","/package.json","/yarn.lock",
    "/Dockerfile","/.dockerignore",
]

def probe_paths(base_url, paths, threads=8):
    base=base_url.rstrip("/")
    found=[]
    def check(p):
        url=base+p
        code=head_fetch(url,timeout=8)
        if code in (200,301,302,403):
            return {"path":p,"url":url,"status":code}
        return None
    with ThreadPoolExecutor(max_workers=threads) as ex:
        futures={ex.submit(check,p):p for p in paths}
        for f in as_completed(futures):
            r=f.result()
            if r: found.append(r)
    return sorted(found,key=lambda x:x["status"])

# ════════════════════════════════════════════════════════════════════
#  HTML LINK PARSER
# ════════════════════════════════════════════════════════════════════
class LinkParser(HTMLParser):
    def __init__(self,base_url):
        super().__init__()
        self.base=base_url
        self.links=set(); self.css_links=set(); self.js_links=set()
        self.img_links=set(); self.svg_links=set()
        self.bg_links=set(); self.srcset_links=set()
        self.forms=[]; self._cur_form=None

    def _abs(self,href):
        if not href: return None
        href=href.strip().split("#")[0]
        if href.startswith(("javascript:","mailto:","tel:","data:","blob:")): return None
        return urllib.parse.urljoin(self.base,href)

    def _srcset(self,ss):
        for part in ss.split(","):
            u=self._abs(part.strip().split()[0])
            if u: yield u

    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if tag=="a":
            u=self._abs(d.get("href",""))
            if u: self.links.add(u)
        elif tag in("img","image"):
            u=self._abs(d.get("src",""))
            if u:
                ext=os.path.splitext(urllib.parse.urlparse(u).path)[1].lower()
                (self.svg_links if ext in SVG_EXTS else self.img_links).add(u)
            for su in self._srcset(d.get("srcset","")): self.srcset_links.add(su)
        elif tag=="source":
            for su in self._srcset(d.get("srcset","")): self.srcset_links.add(su)
            u=self._abs(d.get("src",""))
            if u: self.srcset_links.add(u)
        elif tag=="link":
            rel=d.get("rel",""); u=self._abs(d.get("href",""))
            if not u: return
            if "stylesheet" in rel: self.css_links.add(u)
            elif "icon" in rel or "apple-touch-icon" in rel: self.img_links.add(u)
            elif d.get("href","").endswith(tuple(SVG_EXTS)): self.svg_links.add(u)
        elif tag=="script":
            u=self._abs(d.get("src",""))
            if u: self.js_links.add(u)
        elif tag in("use","object","embed"):
            u=self._abs(d.get("href","") or d.get("xlink:href","") or d.get("data","") or d.get("src",""))
            if u: self.img_links.add(u)
        elif tag=="form":
            self._cur_form={"action":d.get("action",""),"method":d.get("method","GET").upper(),"inputs":[]}
        elif tag=="input" and self._cur_form is not None:
            self._cur_form["inputs"].append({"name":d.get("name",""),"type":d.get("type","text"),"id":d.get("id","")})
        style=d.get("style","")
        if style and "url(" in style:
            for m in re.finditer(r'url\(["\']?([^"\')\s]+)["\']?\)',style):
                u=self._abs(m.group(1))
                if u: self.bg_links.add(u)

    def handle_endtag(self,tag):
        if tag=="form" and self._cur_form:
            self.forms.append(self._cur_form); self._cur_form=None

# ════════════════════════════════════════════════════════════════════
#  CSS URL EXTRACT
# ════════════════════════════════════════════════════════════════════
def extract_css_urls(css,base):
    urls=set()
    for m in re.finditer(r'url\(["\']?([^"\')\s]+)["\']?\)',css):
        raw=m.group(1).strip()
        if raw.startswith("data:"): continue
        urls.add(urllib.parse.urljoin(base,raw))
    return urls

def extract_inline(html):
    css=re.findall(r'<style[^>]*>(.*?)</style>',html,re.DOTALL|re.IGNORECASE)
    js=re.findall(r'<script(?![^>]*src)[^>]*>(.*?)</script>',html,re.DOTALL|re.IGNORECASE)
    return css,js

# ════════════════════════════════════════════════════════════════════
#  HELPERS
# ════════════════════════════════════════════════════════════════════
PAGE_TAGS={
    "LOGIN":["login","signin","sign-in","log-in","auth"],
    "SIGNUP":["signup","register","sign-up","create-account","join"],
    "CONTACT":["contact","support","help"],
    "ABOUT":["about","team","company"],
    "CHECKOUT":["checkout","cart","basket","order"],
    "ADMIN":["admin","panel","cpanel","wp-admin"],
    "BLOG":["blog","news","post","article"],
    "PRODUCT":["product","shop","store","item"],
    "GALLERY":["gallery","photo","portfolio","media"],
    "API":["api","graphql","rest","json","endpoint"],
    "PRIVACY":["privacy","terms","policy","legal"],
}
def page_type(url):
    low=url.lower()
    for label,keys in PAGE_TAGS.items():
        if any(k in low for k in keys): return label
    return "PAGE"

def url_to_filename(url,n=1):
    parsed=urllib.parse.urlparse(url)
    path=parsed.path.strip("/")
    if not path: return "index.html"
    name=re.sub(r'[^a-zA-Z0-9._\-]','_',path.replace("/","_"))
    if not any(name.endswith(e) for e in(".html",".htm",".php",".asp")): name+=".html"
    return name[:80]

def asset_safe_name(url):
    parsed=urllib.parse.urlparse(url)
    name=os.path.basename(parsed.path)
    if not name:
        h=hashlib.md5(url.encode()).hexdigest()[:8]
        ext=os.path.splitext(parsed.path)[1] or ".bin"
        name=f"asset_{h}{ext}"
    name=re.sub(r'[^a-zA-Z0-9._\-]','_',name)
    return name[:80] or "unknown"

def resolve_ip(url):
    try: return socket.gethostbyname(urllib.parse.urlparse(url).hostname)
    except: return "N/A"

def make_output_dir(base_url):
    parsed=urllib.parse.urlparse(base_url)
    domain=re.sub(r'[^a-zA-Z0-9_\-]','_',parsed.netloc.replace("www.",""))
    ts=time.strftime("%Y%m%d_%H%M%S")
    root=f"SK_WEB_{domain}_{ts}"
    for sub in("pages","css","js","images","svg","fonts","docs","media","assets","recon"):
        os.makedirs(os.path.join(root,sub),exist_ok=True)
    return root

def write_text(folder,sub,name,content):
    p=os.path.join(folder,sub,name)
    with open(p,"w",encoding="utf-8",errors="replace") as f: f.write(content)
    return p

def write_binary(folder,sub,name,data):
    p=os.path.join(folder,sub,name)
    with open(p,"wb") as f: f.write(data)
    return p

# ════════════════════════════════════════════════════════════════════
#  PARALLEL ASSET DOWNLOADER
# ════════════════════════════════════════════════════════════════════
def download_assets(folder, asset_urls, manifest, workers=8):
    total=len(asset_urls); done=0; success=0; failed=0
    section(f"ASSET DOWNLOAD  ({total} files)  [{workers} threads]")
    lock=threading.Lock()

    def dl_one(item):
        url,cat=item
        name=asset_safe_name(url)
        dest=os.path.join(folder,cat,name)
        if os.path.exists(dest): return True,cat,name,0
        res=binary_fetch(url,timeout=20)
        if res["ok"]:
            write_binary(folder,cat,name,res["raw"])
            return True,cat,name,res["size"]
        return False,cat,name,0

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures={ex.submit(dl_one,item):item for item in asset_urls}
        for f in as_completed(futures):
            with lock: done+=1
            ok_v,cat,name,sz=f.result()
            if ok_v:
                success+=1
                sz_s=f"{sz/1024:.1f}KB" if sz<1048576 else f"{sz/1048576:.2f}MB"
                manifest.setdefault(cat,[]).append({"file":name,"size":sz_s})
            else: failed+=1
            with _print_lock:
                print(f"\r  {progress_bar(done,total)}  {DW}{name[:28]:<28}{RS}",
                      end="",flush=True)

    print()
    section_end()
    ok(f"Assets: {success} saved · {failed} failed")
    return success,failed

# ════════════════════════════════════════════════════════════════════
#  BROKEN LINK CHECKER  (parallel HEAD requests)
# ════════════════════════════════════════════════════════════════════
def check_broken_links(links, workers=10):
    broken=[]; checked=0
    total=min(len(links),150)
    sample=list(links)[:total]
    section(f"BROKEN LINK CHECK  ({total} links)")

    def chk(url):
        code=head_fetch(url,timeout=8)
        return url,code

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures={ex.submit(chk,u):u for u in sample}
        for f in as_completed(futures):
            checked+=1
            url,code=f.result()
            if code in(404,410,0):
                broken.append({"url":url,"status":code})
            with _print_lock:
                print(f"\r  {progress_bar(checked,total)}",end="",flush=True)
    print()
    section_end()
    if broken:
        warn(f"{len(broken)} broken links found")
        for b in broken[:10]:
            err(f"  [{b['status']}] {b['url'][:70]}")
    else: ok("No broken links found")
    return broken

# ════════════════════════════════════════════════════════════════════
#  HTML REPORT GENERATOR
# ════════════════════════════════════════════════════════════════════
def generate_html_report(folder, manifest):
    pages=manifest.get("pages",[])
    secrets=manifest.get("all_secrets",[])
    endpoints=manifest.get("all_endpoints",[])
    emails=manifest.get("all_emails",[])
    phones=manifest.get("all_phones",[])
    waf=manifest.get("waf",[])
    tech=manifest.get("technologies",[])
    sec_hdrs=manifest.get("security_headers",{})
    ssl_info=manifest.get("ssl",{})
    hidden=manifest.get("hidden_paths",[])
    broken=manifest.get("broken_links",[])
    robots=manifest.get("robots",{})
    disallowed=robots.get("disallowed",[])

    def badge(text,color="#27ae60"):
        return f'<span style="background:{color};color:#fff;padding:2px 8px;border-radius:4px;font-size:12px;margin:2px;display:inline-block">{text}</span>'

    def status_color(code):
        if code==200: return "#27ae60"
        if code in(301,302): return "#2980b9"
        if code==403: return "#e67e22"
        if code==404: return "#c0392b"
        return "#7f8c8d"

    secs_html=""
    for s in secrets:
        secs_html+=f'''<tr><td><span style="color:#e74c3c;font-weight:bold">{s["type"]}</span></td>
        <td><code style="color:#e74c3c;word-break:break-all">{s["value"][:100]}</code></td>
        <td style="font-size:11px;color:#888">{s.get("source","")[:50]}</td></tr>'''

    pages_html=""
    for p in pages:
        fc=len(p.get("forms",[]))
        pages_html+=f'''<tr>
        <td><span style="background:{status_color(p["status"])};color:#fff;padding:2px 6px;border-radius:3px">{p["status"]}</span></td>
        <td><span style="background:#1a252f;color:#27ae60;padding:2px 6px;border-radius:3px;font-size:11px">{p["type"]}</span></td>
        <td style="font-size:12px;word-break:break-all"><a href="{p["url"]}" target="_blank" style="color:#3498db">{p["url"][:80]}</a></td>
        <td style="font-size:11px">{p["file"]}</td>
        <td style="text-align:center">{fc if fc else ""}</td>
        <td style="font-size:11px;color:#888">{p["size_kb"]} KB</td>
        </tr>'''

    hidden_html=""
    for h in hidden:
        sc=h["status"]
        hidden_html+=f'''<tr>
        <td><span style="background:{status_color(sc)};color:#fff;padding:2px 6px;border-radius:3px">{sc}</span></td>
        <td><a href="{h["url"]}" target="_blank" style="color:#e74c3c">{h["path"]}</a></td>
        </tr>'''

    tech_badges="".join(badge(t,"#2c3e50") for t in tech)
    waf_badges="".join(badge(w,"#e74c3c") for w in waf) if waf else badge("None detected","#27ae60")

    sec_present="".join(badge(h["label"],"#27ae60") for h in sec_hdrs.get("present",[]))
    sec_missing="".join(badge(h["label"],"#c0392b") for h in sec_hdrs.get("missing",[]))

    ssl_color="#27ae60" if ssl_info.get("valid") else "#e74c3c"
    ssl_block=f'''
    <div style="background:#1a252f;padding:12px;border-radius:6px;margin:8px 0">
        <div style="color:{ssl_color};font-weight:bold">{"✓ Valid" if ssl_info.get("valid") else "✗ Invalid / N/A"}</div>
        <div style="color:#bdc3c7;font-size:12px">CN: {ssl_info.get("cn","?")}</div>
        <div style="color:#bdc3c7;font-size:12px">Issuer: {ssl_info.get("issuer","?")}</div>
        <div style="color:#bdc3c7;font-size:12px">Expires: {ssl_info.get("not_after","?")}</div>
        <div style="color:#bdc3c7;font-size:12px">Cipher: {ssl_info.get("cipher","?")}</div>
    </div>''' if ssl_info else "<div style='color:#888'>SSL check skipped (HTTP)</div>"

    emails_html="".join(f'<div style="color:#3498db;font-size:13px">📧 {e}</div>' for e in emails)
    phones_html="".join(f'<div style="color:#27ae60;font-size:13px">📞 {p}</div>' for p in phones)
    endpts_html="".join(f'<code style="display:block;color:#f39c12;font-size:12px">▸ {e}</code>' for e in endpoints[:50])
    disallow_html="".join(f'<code style="display:block;color:#e74c3c;font-size:12px">✗ {d}</code>' for d in disallowed)
    broken_html="".join(f'<div style="color:#e74c3c;font-size:12px">[{b["status"]}] {b["url"][:80]}</div>' for b in broken)

    score=100
    if not waf: score-=10
    if secrets: score-=min(len(secrets)*5,30)
    if hidden: score-=min(len([h for h in hidden if h["status"]==200])*5,20)
    score=max(score,0)
    score_color="#27ae60" if score>=70 else "#e67e22" if score>=40 else "#e74c3c"

    img_count=len(manifest.get("images",[]))
    css_count=len(manifest.get("css",[]))
    js_count=len(manifest.get("js",[]))
    total_pages=len(pages)

    html=f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SK WEB v4.0 — {manifest.get("target","")}</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#0d1117;color:#c9d1d9;font-family:"Segoe UI",Arial,sans-serif;font-size:14px}}
.container{{max-width:1200px;margin:0 auto;padding:20px}}
h1{{color:#27ae60;font-size:22px;margin-bottom:4px}}
h2{{color:#27ae60;font-size:16px;margin:16px 0 8px;border-left:3px solid #27ae60;padding-left:8px}}
h3{{color:#3498db;font-size:13px;margin:8px 0 4px}}
.header{{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:16px;margin-bottom:16px}}
.meta{{color:#8b949e;font-size:12px;margin-top:4px}}
.card{{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:16px;margin-bottom:16px}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
.grid3{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px}}
.stat{{text-align:center;padding:12px;background:#0d1117;border-radius:6px}}
.stat-num{{font-size:28px;font-weight:bold;color:#27ae60}}
.stat-label{{font-size:11px;color:#8b949e;text-transform:uppercase;margin-top:2px}}
.score-box{{text-align:center;padding:16px}}
.score-num{{font-size:48px;font-weight:bold;color:{score_color}}}
table{{width:100%;border-collapse:collapse;font-size:12px}}
th{{background:#21262d;color:#8b949e;padding:8px 10px;text-align:left;font-weight:600;text-transform:uppercase;font-size:11px}}
td{{padding:7px 10px;border-bottom:1px solid #21262d;vertical-align:middle}}
tr:hover{{background:#1c2128}}
.secret-box{{background:#1a0a0a;border:1px solid #5c1f1f;border-radius:6px;padding:12px}}
code{{font-family:"Courier New",monospace;background:#0d1117;padding:1px 4px;border-radius:3px}}
.tag{{background:#21262d;color:#8b949e;padding:1px 6px;border-radius:3px;font-size:11px;margin-right:4px}}
.footer{{text-align:center;color:#8b949e;font-size:11px;margin-top:24px;padding-top:16px;border-top:1px solid #21262d}}
@media(max-width:768px){{.grid2,.grid3{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<div class="container">

<div class="header">
  <h1>🕷️ SK WEB v1.0 — Recon Report</h1>
  <div class="meta">Target: <strong style="color:#27ae60">{manifest.get("target","")}</strong></div>
  <div class="meta">IP: {manifest.get("ip","?")} &nbsp;|&nbsp; Crawled: {manifest.get("started","?")} &nbsp;|&nbsp; Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
</div>

<div class="grid3">
  <div class="card"><div class="score-box"><div class="score-num">{score}</div><div style="color:{score_color};font-weight:bold">Security Score</div><div style="color:#8b949e;font-size:11px">/100</div></div></div>
  <div class="card">
    <div class="grid2" style="gap:8px">
      <div class="stat"><div class="stat-num">{total_pages}</div><div class="stat-label">Pages</div></div>
      <div class="stat"><div class="stat-num">{css_count}</div><div class="stat-label">CSS</div></div>
      <div class="stat"><div class="stat-num">{js_count}</div><div class="stat-label">JS</div></div>
      <div class="stat"><div class="stat-num">{img_count}</div><div class="stat-label">Images</div></div>
    </div>
  </div>
  <div class="card">
    <div class="grid2" style="gap:8px">
      <div class="stat"><div class="stat-num" style="color:#e74c3c">{len(secrets)}</div><div class="stat-label">Secrets</div></div>
      <div class="stat"><div class="stat-num" style="color:#f39c12">{len(endpoints)}</div><div class="stat-label">Endpoints</div></div>
      <div class="stat"><div class="stat-num" style="color:#3498db">{len(emails)}</div><div class="stat-label">Emails</div></div>
      <div class="stat"><div class="stat-num" style="color:#9b59b6">{len(hidden)}</div><div class="stat-label">Hidden</div></div>
    </div>
  </div>
</div>

<div class="grid2">
<div>
<div class="card">
  <h2>🛡️ WAF / CDN</h2>
  {waf_badges}
</div>
<div class="card">
  <h2>⚙️ Technologies</h2>
  {tech_badges if tech_badges else "<span style='color:#888'>None detected</span>"}
</div>
<div class="card">
  <h2>🔒 SSL Certificate</h2>
  {ssl_block}
</div>
</div>
<div>
<div class="card">
  <h2>🛡️ Security Headers</h2>
  <h3 style="color:#27ae60">Present</h3>{sec_present if sec_present else "<span style='color:#888'>None</span>"}
  <h3 style="color:#e74c3c;margin-top:10px">Missing</h3>{sec_missing if sec_missing else "<span style='color:#888'>All present ✓</span>"}
</div>
<div class="card">
  <h2>📋 Robots.txt Disallowed</h2>
  {disallow_html if disallow_html else "<div style='color:#888'>None / not found</div>"}
</div>
</div>
</div>

{f"""<div class="card secret-box">
  <h2 style="color:#e74c3c">🔑 Secrets Found ({len(secrets)})</h2>
  <table><thead><tr><th>Type</th><th>Value</th><th>Source</th></tr></thead>
  <tbody>{secs_html}</tbody></table>
</div>""" if secrets else ""}

<div class="card">
  <h2>🔗 API Endpoints ({len(endpoints)})</h2>
  {endpts_html if endpts_html else "<div style='color:#888'>None found</div>"}
</div>

<div class="grid2">
<div class="card">
  <h2>📧 Emails & Phones</h2>
  {emails_html}
  {phones_html}
  {"<div style='color:#888'>None found</div>" if not emails and not phones else ""}
</div>
<div class="card">
  <h2>🚪 Hidden Paths Found ({len(hidden)})</h2>
  {f"<table><thead><tr><th>Status</th><th>Path</th></tr></thead><tbody>{hidden_html}</tbody></table>" if hidden else "<div style='color:#888'>None found</div>"}
</div>
</div>

<div class="card">
  <h2>📄 Pages Crawled ({total_pages})</h2>
  <table>
    <thead><tr><th>Status</th><th>Type</th><th>URL</th><th>File</th><th>Forms</th><th>Size</th></tr></thead>
    <tbody>{pages_html}</tbody>
  </table>
</div>

{f"""<div class="card">
  <h2 style="color:#e74c3c">💔 Broken Links ({len(broken)})</h2>
  {broken_html}
</div>""" if broken else ""}

<div class="footer">SK WEB v1.0 · Report generated {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} · SK SAKIB 👿 · SK WEB</div>
</div>
</body>
</html>'''

    rp=os.path.join(folder,"report.html")
    with open(rp,"w",encoding="utf-8") as f: f.write(html)
    return rp

# ════════════════════════════════════════════════════════════════════
#  SAVE MANIFEST
# ════════════════════════════════════════════════════════════════════
def save_manifest(folder,manifest):
    manifest["finished"]=time.strftime("%Y-%m-%d %H:%M:%S")
    p=os.path.join(folder,"manifest.json")
    # convert sets to lists for JSON
    def fix(obj):
        if isinstance(obj,set): return list(obj)
        if isinstance(obj,dict): return {k:fix(v) for k,v in obj.items()}
        if isinstance(obj,list): return [fix(i) for i in obj]
        return obj
    with open(p,"w",encoding="utf-8") as f:
        json.dump(fix(manifest),f,indent=2,ensure_ascii=False)

# ════════════════════════════════════════════════════════════════════
#  PRINT SUMMARY
# ════════════════════════════════════════════════════════════════════
def print_summary(folder,manifest,report_path):
    pages=manifest["pages"]; total=len(pages)
    section("SK WEB — EXTRACTION COMPLETE")
    print(f"""
{G2}  ╔══════════════════════════════════════════════════════╗{RS}
{G2}  ║  {W}Target     {G1}: {manifest['target'][:46]:<46}{G2}║{RS}
{G2}  ║  {W}IP         {G1}: {manifest['ip']:<46}{G2}║{RS}
{G2}  ║  {W}Output     {G1}: {folder:<46}{G2}║{RS}
{G2}  ║  {W}HTML Report{G1}: {os.path.basename(report_path):<46}{G2}║{RS}
{G2}  ╠══════════════════════════════════════════════════════╣{RS}
{G2}  ║  {W}Pages      {G1}: {str(total):<44}{G2}║{RS}
{G2}  ║  {W}CSS        {G1}: {str(len(manifest.get('css',[]))):<44}{G2}║{RS}
{G2}  ║  {W}JS         {G1}: {str(len(manifest.get('js',[]))):<44}{G2}║{RS}
{G2}  ║  {W}Images     {G1}: {str(len(manifest.get('images',[]))):<44}{G2}║{RS}
{G2}  ║  {W}Secrets    {G1}: {str(len(manifest.get('all_secrets',[]))):<44}{G2}║{RS}
{G2}  ║  {W}Endpoints  {G1}: {str(len(manifest.get('all_endpoints',[]))):<44}{G2}║{RS}
{G2}  ║  {W}Emails     {G1}: {str(len(manifest.get('all_emails',[]))):<44}{G2}║{RS}
{G2}  ║  {W}Hidden     {G1}: {str(len(manifest.get('hidden_paths',[]))):<44}{G2}║{RS}
{G2}  ║  {W}WAF        {G1}: {str(manifest.get('waf','?'))[:44]:<44}{G2}║{RS}
{G2}  ╚══════════════════════════════════════════════════════╝{RS}
""")
    secs=manifest.get("all_secrets",[])
    if secs:
        vuln(f"SECRETS FOUND: {len(secs)}")
        for s in secs[:5]:
            vuln(f"  [{s['type']}] {s['value'][:60]}")
    hidden=[h for h in manifest.get("hidden_paths",[]) if h["status"]==200]
    if hidden:
        warn(f"EXPOSED PATHS: {len(hidden)}")
        for h in hidden[:5]: warn(f"  [{h['status']}] {h['path']}")
    emails=manifest.get("all_emails",[])
    if emails:
        hit(f"EMAILS: {', '.join(emails[:5])}")
    tech=manifest.get("technologies",[])
    if tech:
        hit(f"TECH: {' · '.join(tech[:6])}")
    waf=manifest.get("waf",[])
    if waf: warn(f"WAF: {', '.join(waf)}")
    else:   ok("No WAF detected")
    ok(f"Report: open {report_path} in browser")

# ════════════════════════════════════════════════════════════════════
#  MAIN CRAWL ENGINE
# ════════════════════════════════════════════════════════════════════
def crawl(start_url, max_pages=50, threads=6,
          do_assets=True, do_fonts=True, do_docs=False,
          do_probe=True, do_broken=False):

    base_host=urllib.parse.urlparse(start_url).netloc
    folder=make_output_dir(start_url)
    visited=set(); queue=deque([start_url])

    manifest={
        "target":start_url,"ip":resolve_ip(start_url),
        "started":time.strftime("%Y-%m-%d %H:%M:%S"),
        "pages":[],"css":[],"js":[],"images":[],"svg":[],
        "fonts":[],"docs":[],"media":[],"assets":[],
        "all_secrets":[],"all_endpoints":[],"all_emails":[],
        "all_phones":[],"all_links":set(),
        "waf":[],"technologies":[],"security_headers":{},
        "ssl":{},"robots":{},"hidden_paths":[],"broken_links":[],
    }

    all_assets=set(); css_done=set(); js_done=set()
    page_n=0; first_page=True

    # ── Stats counters ──────────────────────────────────────────
    start_time=time.time()

    section("SK WEB v1.0 RECON STARTED")
    info(f"Target  : {start_url}")
    info(f"IP      : {manifest['ip']}")
    info(f"Folder  : {folder}/")
    info(f"Threads : {threads}  Pages: {max_pages}")
    section_end()

    # ── SSL ─────────────────────────────────────────────────────
    if start_url.startswith("https://"):
        spin_start("Checking SSL certificate...")
        ssl_info=get_ssl_info(base_host)
        spin_stop()
        manifest["ssl"]=ssl_info
        if ssl_info.get("valid"):
            ok(f"SSL valid · {ssl_info.get('cn')} · expires {ssl_info.get('not_after')}")
        else:
            warn(f"SSL issue: {ssl_info.get('error','?')}")

    # ── robots.txt ──────────────────────────────────────────────
    spin_start("Fetching robots.txt & sitemap...")
    robots=fetch_robots(start_url)
    manifest["robots"]=robots
    spin_stop()
    if robots["disallowed"]:
        info(f"robots.txt: {len(robots['disallowed'])} disallowed paths")
        for sm in robots["sitemaps"]:
            sm_urls=fetch_sitemap_urls(sm)
            for su in sm_urls:
                if urllib.parse.urlparse(su).netloc==base_host:
                    queue.append(su)
            info(f"Sitemap {sm}: {len(sm_urls)} URLs added")
    write_text(folder,"recon","robots.txt",robots["raw"] or "# Not found")

    # ── hidden path probe ───────────────────────────────────────
    if do_probe:
        spin_start("Probing hidden paths...")
        hidden=probe_paths(start_url, COMMON_PATHS, threads=threads)
        spin_stop()
        manifest["hidden_paths"]=hidden
        exposed=[h for h in hidden if h["status"]==200]
        if exposed:
            vuln(f"EXPOSED: {len(exposed)} paths accessible")
            for h in exposed[:8]: warn(f"  [200] {h['path']}")
        else: ok(f"Path probe done · {len(hidden)} responded")

    # ── CRAWL LOOP ──────────────────────────────────────────────
    section("CRAWLING PAGES")
    while queue and page_n < max_pages:
        url=queue.popleft()
        if url in visited: continue
        p=urllib.parse.urlparse(url)
        if p.netloc != base_host: continue
        if not is_html_url(url) and page_n>0:
            cat=asset_category(url)
            if cat and do_assets: all_assets.add((url,cat))
            continue
        visited.add(url)
        page_n+=1
        ptype=page_type(url)

        _p(f"  {G3}[{page_n:>3}]{RS}  {G1}{ptype:<10}{RS}  {DW}{url[:60]}{RS}")

        res=raw_fetch(url)
        if not res["ok"]:
            err(f"  Failed ({res['status']}) — {res.get('error','?')}")
            continue
        html=res["text"]
        hdrs=res.get("headers",{})

        # first page: WAF + tech + security headers
        if first_page:
            first_page=False
            wafs=detect_waf(hdrs,html)
            if wafs: manifest["waf"]=wafs; warn(f"WAF detected: {', '.join(wafs)}")
            else: ok("No WAF detected")
            tech=fingerprint_tech(html,hdrs,url)
            manifest["technologies"]=tech
            if tech: hit(f"Tech: {' · '.join(tech[:6])}")
            sec_audit=audit_security_headers(hdrs)
            manifest["security_headers"]=sec_audit
            if sec_audit["missing"]:
                warn(f"Missing headers: {', '.join(h['label'] for h in sec_audit['missing'][:4])}")

        # parse
        parser=LinkParser(url)
        try: parser.feed(html)
        except: pass
        css_blocks,js_blocks=extract_inline(html)

        # collect all links for broken check
        manifest["all_links"].update(parser.links)

        # emails/phones from HTML
        h_emails,h_phones=scan_html_for_emails_phones(html)
        manifest["all_emails"]=list(set(manifest["all_emails"]+h_emails))
        manifest["all_phones"]=list(set(manifest["all_phones"]+h_phones))

        # file name
        fn=url_to_filename(url,page_n)
        if fn=="index.html" and page_n>1:
            slug=re.sub(r'[^a-zA-Z0-9]','_',p.path.strip("/"))[:28]
            fn=f"page_{page_n:03d}_{slug or 'page'}.html"
        write_text(folder,"pages",fn,html)

        # inline CSS
        for idx,blk in enumerate(css_blocks):
            if blk.strip():
                cname=f"{fn}_inline_{idx+1}.css"
                write_text(folder,"css",cname,blk)
                for cu in extract_css_urls(blk,url):
                    cat=asset_category(cu)
                    if cat and do_assets: all_assets.add((cu,cat))
                manifest["css"].append({"file":cname,"type":"inline","from":url})

        # inline JS scan
        for idx,blk in enumerate(js_blocks):
            if blk.strip():
                jname=f"{fn}_inline_{idx+1}.js"
                write_text(folder,"js",jname,blk)
                manifest["js"].append({"file":jname,"type":"inline","from":url})
                found=scan_js(blk,url)
                if found["secrets"]: manifest["all_secrets"].extend(found["secrets"])
                manifest["all_endpoints"]=list(set(manifest["all_endpoints"]+found["endpoints"]))
                manifest["all_emails"]=list(set(manifest["all_emails"]+found["emails"]))

        # external CSS
        for css_url in parser.css_links:
            if css_url in css_done: continue
            css_done.add(css_url)
            cr=raw_fetch(css_url,timeout=12)
            if cr["ok"]:
                cname=asset_safe_name(css_url)
                if not cname.endswith(".css"): cname+=".css"
                write_text(folder,"css",cname,cr["text"])
                for cu in extract_css_urls(cr["text"],css_url):
                    cat=asset_category(cu)
                    if cat and do_assets: all_assets.add((cu,cat))
                manifest["css"].append({"file":cname,"url":css_url,"type":"external"})

        # external JS
        for js_url in parser.js_links:
            if js_url in js_done: continue
            js_done.add(js_url)
            jp=urllib.parse.urlparse(js_url)
            if jp.netloc not in (base_host,""): continue
            jr=raw_fetch(js_url,timeout=12)
            if jr["ok"]:
                jname=asset_safe_name(js_url)
                if not jname.endswith(".js"): jname+=".js"
                write_text(folder,"js",jname,jr["text"])
                manifest["js"].append({"file":jname,"url":js_url,"type":"external"})
                found=scan_js(jr["text"],js_url)
                if found["secrets"]:
                    manifest["all_secrets"].extend(found["secrets"])
                    for s in found["secrets"]: vuln(f"SECRET: [{s['type']}] {s['value'][:50]}")
                manifest["all_endpoints"]=list(set(manifest["all_endpoints"]+found["endpoints"]))
                manifest["all_emails"]=list(set(manifest["all_emails"]+found["emails"]))
                step(f"JS → js/{jname}")

        # assets
        if do_assets:
            for img_url in parser.img_links|parser.srcset_links|parser.bg_links:
                cat=asset_category(img_url)
                if not cat: cat="images"
                if cat in("images","svg","assets"): all_assets.add((img_url,cat))
            for svg_url in parser.svg_links: all_assets.add((svg_url,"svg"))

        manifest["pages"].append({
            "url":url,"file":fn,"type":ptype,"status":res["status"],
            "size_kb":round(len(html.encode())/1024,2),
            "lines":html.count("\n")+1,"forms":parser.forms,
            "server":res.get("server","?"),"ct":res.get("ct","?"),
        })
        saved(f"Page → pages/{fn}  ({res['status']})")

        for link in parser.links:
            lp=urllib.parse.urlparse(link)
            ext=os.path.splitext(lp.path)[1].lower()
            if lp.netloc==base_host and link not in visited:
                if ext in SKIP_EXTS: continue
                if ext in (IMAGE_EXTS|SVG_EXTS|FONT_EXTS|DOC_EXTS|MEDIA_EXTS):
                    if do_assets:
                        cat=asset_category(link)
                        if cat: all_assets.add((link,cat))
                    continue
                queue.append(link)
        time.sleep(0.2)

    section_end()

    # ── ASSET DOWNLOAD ──────────────────────────────────────────
    if do_assets and all_assets:
        download_assets(folder,all_assets,manifest,workers=threads)

    # ── BROKEN LINK CHECK ───────────────────────────────────────
    if do_broken and manifest["all_links"]:
        broken=check_broken_links(manifest["all_links"])
        manifest["broken_links"]=broken

    # ── RECON SAVE ──────────────────────────────────────────────
    # deduplicate
    manifest["all_secrets"]=list({json.dumps(s,sort_keys=True):s for s in manifest["all_secrets"]}.values())
    manifest["all_endpoints"]=list(set(manifest["all_endpoints"]))
    manifest["all_emails"]=list(set(manifest["all_emails"]))
    manifest["all_phones"]=list(set(manifest["all_phones"]))
    manifest["all_links"]=list(manifest["all_links"])

    elapsed=time.time()-start_time
    manifest["elapsed_seconds"]=round(elapsed,1)
    info(f"Total time: {elapsed:.1f}s")

    return folder,manifest

# ════════════════════════════════════════════════════════════════════
#  MAIN MENU
# ════════════════════════════════════════════════════════════════════
def main():
    banner()
    while True:
        print(f"{G2}  ╔══════════════════════════════════════════════════╗{RS}")
        print(f"{G2}  ║  {W}Target Website {G1}(exit = quit)                 {G2}║{RS}")
        print(f"{G2}  ╚══════════════════════════════════════════════════╝{RS}")
        print(f"{G1}  ❯❯ {RS}",end="")
        try: raw=input().strip()
        except(KeyboardInterrupt,EOFError):
            print(f"\n\n{G3}  Crow leaving. Caw.{RS}\n"); sys.exit(0)
        if raw.lower() in("exit","quit","q"):
            print(f"\n{G3}  Crow leaving. Caw.{RS}\n"); sys.exit(0)
        if not raw: warn("Enter a valid URL."); continue
        if not raw.startswith(("http://","https://")): raw="https://"+raw

        print(f"{G2}  Max pages {DIM}[1-100, default 30]{RS}: ",end="")
        try:
            mp=input().strip(); max_p=int(mp) if mp.isdigit() else 30
            max_p=min(max(max_p,1),100)
        except: max_p=30

        print(f"{G2}  Threads {DIM}[2-15, default 6]{RS}: ",end="")
        try:
            th=input().strip(); threads=int(th) if th.isdigit() else 6
            threads=min(max(threads,2),15)
        except: threads=6

        print(f"""
{G2}  ╔══ Options ══════════════════════════════════════════╗{RS}
{G2}  ║  {G1}[1]{W} Full (assets + probe + recon)           {G2}║{RS}
{G2}  ║  {G1}[2]{W} Source + recon (no asset download)      {G2}║{RS}
{G2}  ║  {G1}[3]{W} Full + broken link check (slow)         {G2}║{RS}
{G2}  ║  {G1}[4]{W} Recon only (1 page, full analysis)      {G2}║{RS}
{G2}  ╚═════════════════════════════════════════════════════╝{RS}""")
        print(f"{G1}  Choice {DIM}[default: 1]{RS}: ",end="")
        try: ch=input().strip()
        except: ch="1"

        do_assets=ch not in("2","4")
        do_probe =ch not in("2",)
        do_broken=ch=="3"
        if ch=="4": max_p=1

        print(f"\n{G1}  ⚡ Target locked: {W}{raw}{RS}\n")

        try:
            folder,manifest=crawl(
                raw,max_pages=max_p,threads=threads,
                do_assets=do_assets,do_probe=do_probe,
                do_broken=do_broken,
            )
            save_manifest(folder,manifest)
            report_path=generate_html_report(folder,manifest)
            print_summary(folder,manifest,report_path)
        except KeyboardInterrupt:
            spin_stop()
            print(f"\n\n{YEL}  Scan interrupted.{RS}\n")

        print(f"\n{G1}  SK WEB Ready. {G2}Another target?{RS}\n")

if __name__=="__main__":
    main()

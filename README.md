# Mycelium

Passive subdomain and linked-domain enumeration tool. From a single FQDN, Mycelium queries 21 data sources, deduplicates results and produces an interactive HTML network graph alongside a console listing.

Designed with **TLP/PAP RED** compliance in mind: all sources are passive by default (third-party APIs and public datasets — no direct interaction with the target). Active probing (DNS resolution, reverse DNS) is opt-in via `--active`.

---

## Installation

```bash
git clone https://github.com/ruggdoll/mycelium
cd mycelium
pip install -r requirements.txt
```

---

## Usage

```
python3 mycelium.py <domain> [--depth N] [--active]
```

| Option | Description |
|--------|-------------|
| `--depth N` | Pivot on linked domains up to N levels deep (default: 1) |
| `--active` | Enable active dissectors: DNS resolution + reverse DNS lookup |

### Examples

```bash
# Basic passive enumeration
python3 mycelium.py example.com

# Pivot 2 levels deep into linked domains
python3 mycelium.py example.com --depth 2

# Full run with DNS resolution
python3 mycelium.py example.com --active

# With API keys loaded
export VT_API_KEY="..."
export GITHUB_TOKEN="..."
python3 mycelium.py example.com
```

### Output

Every run produces:
- **Console**: per-source status `[+]` / `[-]` / `[!]`, then a deduplicated listing of subdomains and linked domains
- **`<domain>.html`**: interactive network graph (pyvis) with the domain list as a sidebar

---

## Sources

Sources are queried in parallel. Workers without a configured API key are skipped silently (`[-]`). Unavailable sources are reported as `[!]` without crashing.

### Passive — no API key required

| Source | Data |
|--------|------|
| **Archive.org** | Wayback Machine CDX — URLs crawled by the web archive |
| **Certspotter** | Certificate transparency log issuances |
| **Columbus** | CT log aggregator |
| **CommonCrawl** | Open web crawl index — latest snapshot, up to 5000 results |
| **CRT.sh** | Certificate transparency search |
| **Hackertarget** | Passive DNS |
| **JLDC** | AnubisDB subdomain dataset |
| **RapidDNS** | DNS dataset |
| **Robtex** | Passive DNS forward + reverse (2-step) |
| **ThreatMiner** | Threat intelligence passive DNS |
| **URLScan** | Passive DNS from browser-based scans |

### Passive — API key required (free tiers available)

| Source | Variable(s) | Free tier | Data |
|--------|-------------|-----------|------|
| **AlienVault OTX** | `OTX_API_KEY` | unlimited | Passive DNS, threat intel |
| **Bevigil** | `BEVIGIL_API_KEY` | yes | **Subdomains extracted from Android APKs** — unique source |
| **BinaryEdge** | `BINARYEDGE_API_KEY` | 250 req/month | Passive DNS + internet scanning |
| **Censys** | `CENSYS_API_ID` + `CENSYS_API_SECRET` | 250 req/month | CT logs + internet scanning |
| **Chaos** | `CHAOS_API_KEY` | yes | ProjectDiscovery subdomain dataset |
| **Fullhunt** | `FULLHUNT_API_KEY` | yes | Attack surface aggregator |
| **GitHub** | `GITHUB_TOKEN` | unlimited | **Code search** — finds subdomains hardcoded in public repos, CI configs, env files |
| **SecurityTrails** | `SECURITYTRAILS_API_KEY` | 50 req/month | Historical passive DNS |
| **Shodan** | `SHODAN_API_KEY` | limited | Internet scanning, DNS data |
| **VirusTotal** | `VT_API_KEY` | 500 req/day | Passive DNS + crawl data |

```bash
export OTX_API_KEY="..."
export BEVIGIL_API_KEY="..."
export BINARYEDGE_API_KEY="..."
export CENSYS_API_ID="..."
export CENSYS_API_SECRET="..."
export CHAOS_API_KEY="..."
export FULLHUNT_API_KEY="..."
export GITHUB_TOKEN="..."
export SECURITYTRAILS_API_KEY="..."
export SHODAN_API_KEY="..."
export VT_API_KEY="..."
```

### Active — requires `--active`

| Technique | Description |
|-----------|-------------|
| DNS resolution | Resolves A/AAAA records for all discovered domains |
| Reverse DNS | PTR lookup on resolved IPs to discover additional hostnames |

---

## Graph output

The generated `<domain>.html` file contains:
- **Left panel**: interactive force-directed graph (pyvis/vis.js)
  - ⭐ Root domain (amber star, pinned)
  - ◆ Subdomains (blue diamonds)
  - ■ Linked domains (purple squares)
  - ▲ Pivot domains at depth ≥ 2 (amber triangles)
  - ● IPs (green = public, red = private) — only with `--active`
- **Right panel**: scrollable listing of subdomains and linked domains

---

## Credits

Inspired by:
- https://github.com/D3Ext/AORT
- https://github.com/gfek/Lepus
- https://github.com/ruggdoll/certific8

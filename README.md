# Mycelium

From a FQDN, enumerate related domains and subdomains using passive OSINT sources and produce an interactive network graph.

## Usage

```
python3 mycelium.py DOMAIN.TLD [--depth N] [--active]
```

| Option | Description |
|--------|-------------|
| `--depth N` | Pivot depth on linked domains (default: 1) |
| `--active` | Enable active dissectors (DNS resolution + reverse DNS). **Disabled by default to comply with TLP/PAP RED.** |

The tool always produces:
- A console listing of subdomains and linked domains
- A `DOMAIN.TLD.html` interactive graph (graph on the left, domain list on the right)

## Passive sources (no interaction with the target)

| Source | API key required |
|--------|-----------------|
| Archive.org | — |
| Certspotter | — |
| Columbus | — |
| CRT.sh | — |
| HackerTarget | — |
| JLDC | — |
| RapidDNS | — |
| Robtex | — |
| ThreatMiner | — |
| URLScan | — |
| AlienVault OTX | `OTX_API_KEY` |
| Chaos (ProjectDiscovery) | `CHAOS_API_KEY` |
| SecurityTrails | `SECURITYTRAILS_API_KEY` |
| Shodan | `SHODAN_API_KEY` |
| VirusTotal | `VT_API_KEY` |

API keys are read from environment variables. Workers without a configured key are skipped silently.

```bash
export OTX_API_KEY="..."
export VT_API_KEY="..."
export SECURITYTRAILS_API_KEY="..."
export CHAOS_API_KEY="..."
export SHODAN_API_KEY="..."
```

## Active dissectors (`--active` only)

- DNS resolution (A/AAAA records) for all discovered domains
- Reverse DNS on resolved IPs to discover additional hostnames

## Credits

Freely inspired from:
- https://github.com/D3Ext/AORT
- https://github.com/gfek/Lepus
- https://github.com/ruggdoll/certific8

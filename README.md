# Asymmetric Polymorphic Network Architecture (APNA)

Showcase whitepaper and rollout automation for high-availability Web3 node and RPC infrastructure.

## Repository layout

**Initial whitepaper (at repo root):**

| File | Description |
|------|-------------|
| **APNA-Whitepaper.html** | Main whitepaper. Open in a browser. |
| **APNA-Whitepaper.pdf** | PDF export. Regenerate with: `google-chrome --headless --disable-gpu --no-pdf-header-footer --print-to-pdf="APNA-Whitepaper.pdf" "file://$(pwd)/APNA-Whitepaper.html"` (run from this directory). |
| **Asymmetric-Polymorphic-Network-Architecture-Whitepaper.md** | Markdown source. |
| **infographic-*.svg**, **infographic-*.png** | Diagram sources and rendered images. |
| **inline_svgs.py**, **embed_svgs.py** | Whitepaper build scripts (run from this directory). |
| **HOWTO.md** | Rollout and configuration how-to (~40 min with AI prompts). |

**Tech implementation (in one folder):**

| Folder | Description |
|--------|-------------|
| **apna/** | Orchestrator (**morph.py**), config, states, Jinja2 templates, Ansible playbooks, and **apna/prompts/** (AI prompt templates for fast rollout). See **HOWTO.md**. |

## Quick summary

- **Asymmetric:** Differentiation by plane (control / data / RPC) and by function; limits blast radius and single-pattern-of-attack.
- **Polymorphic:** Diversity of topology per DC *and* dynamic change over time (morphing), unpredictable to an attacker — reduces pattern-stability-of-attack.
- **Grounded in:** Arista EOS, Juniper JunOS, EVPN/VXLAN, BGP/OSPF, bare-metal, Ansible/Python; no new hardware; morphing is control-plane/config, not data-plane hot path.

## Viewing the whitepaper

- **HTML:** Open **APNA-Whitepaper.html** in a browser.
- **PDF:** Use **APNA-Whitepaper.pdf** or print from the HTML (enable **Background graphics**).

## Rollout (~40 min)

1. Read **HOWTO.md**.
2. Use **apna/prompts/** with an AI to generate state files, templates, and Ansible inventory from your context.
3. Run `python apna/morph.py --apply` (after `pip install -r apna/requirements.txt` and configuring credentials).

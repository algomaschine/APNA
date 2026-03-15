# Asymmetric Polymorphic Network Architecture (APNA)

Showcase whitepaper and assets for high-availability Web3 node and RPC infrastructure.

## Contents

| File | Description |
|------|-------------|
| **APNA-Whitepaper.html** | **Main deliverable.** Single-page whitepaper with full design: typography (DM Sans, JetBrains Mono), dark theme, all infographics embedded. Open in a browser. |
| **APNA-Whitepaper.pdf** | PDF export. All process/algorithm diagrams (Figs. 1–4) are **embedded** in the HTML as inline SVG data, so they render in the PDF. Regenerate with: `google-chrome --headless --disable-gpu --no-pdf-header-footer --print-to-pdf="APNA-Whitepaper.pdf" "file://$(pwd)/APNA-Whitepaper.html"` (run from this directory). For best result, open the HTML in Chrome and use Print → Save as PDF with **Background graphics** enabled. |
| **Asymmetric-Polymorphic-Network-Architecture-Whitepaper.md** | Markdown source: concept, justification, tech grounding, feasibility, comparison table, references. |
| **infographic-topologies.svg** | Topology comparison: traditional symmetric vs APNA asymmetric+polymorphic (different shapes per DC). |
| **infographic-morphing.svg** | Morphing state machine (A → B → C → A), triggers, orchestrator. |
| **infographic-morphing-flow.svg** | **Algorithm flowchart:** 6-step morphing flow (State model → Transition decision → Config generation → Apply order → Verification → Attack-triggered morph; loop). |
| **infographic-transition-decision.svg** | **Step 2 illustrated:** Deterministic cycle vs unpredictable secure_random; entropy sources. |

## Quick summary

- **Asymmetric:** Differentiation by plane (control / data / RPC) and by function; limits blast radius and single-pattern-of-attack.
- **Polymorphic:** Diversity of topology per DC *and* dynamic change over time (morphing), unpredictable to an attacker — reduces pattern-stability-of-attack.
- **Grounded in:** Arista EOS, Juniper JunOS, EVPN/VXLAN, BGP/OSPF, bare-metal, Ansible/Python; no new hardware; morphing is control-plane/config, not data-plane hot path.

## Viewing

- **HTML:** Open `APNA-Whitepaper.html` in a browser. All infographics (algorithm flow, transition decision, topologies, state machine) are embedded inline so they appear in the page and in **Print to PDF**.
- **PDF:** Use the pre-generated `APNA-Whitepaper.pdf` or print from the HTML (enable **Background graphics** to keep the dark theme).
- **Re-embedding SVGs:** If you edit the `.svg` files, run `python3 embed_svgs.py` from this directory to embed them again into the HTML.

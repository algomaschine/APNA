# Asymmetric Polymorphic Network Architecture (APNA)
## A Moving-Target Approach for High-Availability Web3 Node & RPC Infrastructure

**Author:** Eduard Samokhvalov  
**Version:** 1.0  
**Date:** March 2025  

**Contact:**  
edward.samokhvalov@gmail.com · +7 499 119 23 66 · [eduardsamokhvalov.online](https://eduardsamokhvalov.online) · [github.com/algomaschine](https://github.com/algomaschine) · @EduardSam  

---

## Abstract

This whitepaper proposes **Asymmetric Polymorphic Network Architecture (APNA)** for large-scale distributed infrastructure hosting blockchain nodes and RPC services. APNA combines **asymmetric** treatment of traffic and failure domains (by role and plane) with **polymorphic** behaviour: intentional diversity of topology and segmentation *plus* controlled, dynamic change of that topology over time, unpredictable to an external or partially compromised observer. The goal is to reduce single-point-of-failure, single-pattern-of-attack, and *pattern-stability* for attackers—making reconnaissance and persistence harder without introducing operational bottlenecks. The design is grounded in technologies already in use in modern multi-DC environments: **EVPN/VXLAN**, **BGP/OSPF**, **Arista EOS** and **Juniper JunOS**, with automation via **Ansible** and **Python**.

---

## 1. Problem Statement and Demand Justification

### 1.1 Threat Landscape (2024–2025)

Network and infrastructure attacks have reached unprecedented scale and frequency:

- **Volume:** Cloudflare blocked **20.5 million DDoS attacks** in Q1 2025 alone—a **358% year-over-year increase** and roughly **96% of the total attacks blocked in all of 2024** [1].
- **Infrastructure targeting:** About **6.6 million** of those attacks targeted **network infrastructure directly** during an 18-day multi-vector campaign [1].
- **Intensity:** Q1 2025 saw approximately **700 hyper-volumetric attacks** exceeding 1 Tbps or 1 Bpps; later in 2025, attacks peaked at **4.8 Bpps** and **6.5 Tbps** [1][2].
- **Layer:** Network-layer DDoS attacks more than **tripled** year-over-year (e.g. 16.8M in Q1 2025, +509% YoY) [1].

Web3 and node infrastructure face additional risks: **malicious RPC nodes** used to falsify balances or manipulate state sync [3][4], and **CometBFT-style** vulnerabilities where syncing from untrusted RPC can lead to chain splits [5]. Infrastructure that presents a **static, uniform** topology and predictable addressing/routing is easier to probe, map, and attack repeatedly.

### 1.2 Limitation of Static, Symmetric Designs

In a traditional design:

- **Same topology template** is often applied across data centers and segments → one successful reconnaissance or exploit gives a blueprint for many segments.
- **Symmetric roles** (e.g. all leaves treated alike) → failure or compromise propagates in predictable ways.
- **Stable addressing and paths** → attackers can build accurate maps and time their actions.

**Moving Target Defense (MTD)** in networks addresses exactly this: by changing the “attack surface” over time, reconnaissance becomes stale and persistence harder [6][7][8]. The challenge is to do this **without** introducing unacceptable overhead or bottlenecks—a concern the present design explicitly addresses (Section 4).

---

## 2. Concept Definition

### 2.1 Asymmetric Component

**Asymmetric** here means **differentiation by function and plane**:

- **Control plane** vs **data plane** vs **RPC/edge plane** are treated differently: separate failure domains, path policies, and security postures.
- **Internal sync traffic** (node-to-node, DC-to-DC) is isolated from **public RPC** and from **management/automation**.
- **Path and failure policies** are not uniform: e.g. different BGP/OSPF policies or failover behaviour per plane so that one event does not homogenise the whole system.

This reduces **single-point-of-failure** and **single-pattern-of-attack** by ensuring that an attacker or failure in one role does not imply the same impact everywhere.

### 2.2 Polymorphic Component

**Polymorphic** has two parts:

1. **Diversity:** Intentional variation of topology and segmentation across data centers and clusters (no single global template). Segment A and Segment B are deliberately non-identical (e.g. different VNI ranges, different spine-leaf roles, or different overlay patterns).
2. **Dynamic change:** Topology and/or segmentation **change over time** according to policy (time windows, triggers, or pseudo-random schedules). The “shape” of the network is not fixed.

The changes are **orchestrated and deterministic** for the legitimate control plane and automation (e.g. Ansible, Python), but **unpredictable** to an external or partially compromised observer who cannot see the orchestration logic or full state. Thus the system is **constantly under change** in a way that makes it difficult for an attacker to **identify stable informational patterns**—where things are, how they are connected, and what to hit next. This reduces **pattern-stability-of-attack** as well as single-pattern-of-attack.

### 2.3 Combined Effect

- **Asymmetry** → limits blast radius and prevents one blueprint from applying everywhere.
- **Polymorphism (diversity + dynamic change)** → prevents an attacker from relying on a stable map; reconnaissance and persistence are both harder.

Together they form **Asymmetric Polymorphic Network Architecture (APNA)**.

---

## 3. Technology Grounding

APNA is designed to be implemented with the **same technology stack** typically used for large-scale Web3 and node infrastructure:

| Layer | Technology | Role in APNA |
|-------|------------|--------------|
| **L2/L3 overlay** | EVPN/VXLAN | Segment diversity (different VNIs, VLAN–VNI maps per DC); dynamic re-assignment of VNIs or segment membership under orchestration. |
| **Underlay routing** | BGP, OSPF | Asymmetric policies per plane (e.g. different communities, path preferences for RPC vs sync vs control); optional route/next-hop variation over time. |
| **Switches** | Arista EOS, Juniper JunOS | EVPN-VXLAN, BGP, and security features (ACLs, CoPP); configuration driven by automation. |
| **Automation** | Ansible, Python, Bash | Generate and push diverse configs per segment; drive morphing schedules and state transitions. |
| **Servers / NICs** | Bare-metal, Mellanox/Nvidia NICs | Consistent performance; no virtualisation overhead; tuning (e.g. interrupt affinity) per role. |
| **Orchestration** | Kubernetes, NodeOps | Integration points for service discovery and policy; RPC vs internal workloads on different segments. |

**Standards and practices:** EVPN-VXLAN security practices (control-plane security, first-hop security, zone-based policies) remain applicable [9][10]. APNA adds a **layer of diversity and dynamism** on top of these, rather than replacing them.

---

## 4. Feasibility, Overhead, and Absence of Bottlenecks

### 4.1 Why This Does Not Introduce Fundamental Overhead

- **Morphing is control-plane and configuration:** Changes are to EVPN/VXLAN mapping, BGP/OSPF policy, or segment membership—not to data-plane forwarding hardware in the hot path. Once converged, forwarding remains at line rate (Arista/Juniper ASIC-based).
- **No VM migration:** Unlike MTD approaches that rely on VM migration [11], APNA does not move workloads; it changes network segmentation and path/role assignment. Thus we avoid the performance and “often degrades security” pitfalls of migration-based MTD [11].
- **Predictable convergence:** BGP and EVPN are designed for re-convergence; changes can be batched and applied during maintenance windows or low-traffic periods to minimise churn. Orchestration (Ansible/Python) can enforce ordering and rollback.
- **Research alignment:** Adaptive MTD that applies reconfiguration only when needed (e.g. under attack) has been shown to greatly reduce latency overhead (e.g. 99.4% lower average latency vs baseline MTD) while preserving effectiveness [12]. APNA can adopt similar “intensity-based” or time-window-based morphing to limit impact.

### 4.2 What Can Be Varied (Without Breaking Connectivity)

- **VNI ↔ VLAN / segment mapping** (which VLANs map to which VNIs in which DC).
- **BGP communities or path preference** for different traffic classes (RPC vs sync vs control).
- **Which leaf pair or path is “primary”** for a given segment (failover roles).
- **ACL or security zone boundaries** (which VNIs are in which zone) over time.

Legitimate traffic is served by the same automation that applies the changes; endpoints can be updated via configuration or service discovery. The key is that **from the perspective of an external or partially compromised observer**, the mapping and timing appear unpredictable.

### 4.3 Illustration of Feasibility

- **Arista EOS / Juniper JunOS:** Both support EVPN-VXLAN, BGP, and programmatic configuration (e.g. eAPI, NETCONF). Ansible modules (e.g. arista.eos, junipernetworks.junos) can push different configs per device and per segment.
- **BGP/OSPF:** Re-convergence after policy or path change is well understood; morphing intervals can be chosen to allow full convergence (e.g. minutes) so that there is no mid-change packet loss for legitimate flows.
- **Automation:** A single “morphing” playbook or Python script can (i) select the next topology state from a predefined set or policy, (ii) generate the corresponding configs, (iii) apply them in a defined order, (iv) verify convergence. No new hardware is required.

Thus APNA is **feasible** with existing technology and **does not introduce inherent data-plane overhead or bottlenecks** when morphing is designed with convergence and optional intensity-based triggering in mind.

### 4.4 Implementation of the Morphing Mechanism (Exact Flow)

The morphing loop is implemented entirely in software on a dedicated orchestrator host (or as a container/service in the control plane), using existing automation and device APIs.

**1. State model.** A finite set of topology states is defined in advance (e.g. A, B, C). Each state is a data structure or file that fully describes, for the scope of morphing: VNI–VLAN mappings, BGP path preference or next-hop roles, and optionally ACL/zone boundaries. These can be Jinja2 templates or YAML/JSON that Ansible/Python fill and push.

**2. Transition decision.** On each tick (time window, e.g. every T minutes) or on trigger (e.g. “attack detected” from a DDoS or intrusion signal):

- **Deterministic cycle:** next_state = (current_state + 1) mod N. Simple, no extra entropy.
- **Unpredictable choice:** next_state = secure_random(0, N−1). The entropy source here is what makes the sequence unpredictable to an attacker (see 4.5).

**3. Config generation.** From the chosen state, the orchestrator generates device-specific configs (Arista EOS / Juniper JunOS) for all affected switches: EVPN-VXLAN, BGP, ACLs. Generation is deterministic given the state; only the *choice* of state is variable.

**4. Apply order.** Configs are pushed in a defined order (e.g. spines first, then leaves, or by dependency so that no transient blackhole appears). Ansible playbooks or a Python script calling eAPI/NETCONF perform the push; idempotency and check mode can be used for safety.

**5. Verification.** After push, the orchestrator checks that BGP/EVPN sessions are established and that convergence is complete (e.g. via device APIs or polling). Only then is the “current state” updated and the next morph scheduled.

**6. Attack-triggered morph (optional).** If an “attack detected” signal is available (e.g. from a DDoS mitigation system or IDS), the orchestrator can shorten the next morph interval or trigger an immediate transition to the next state, so that the network shape changes while the attack is in progress.

No custom hardware is required for this loop. Unpredictability depends on the **entropy source** used in step 2 when using random choice (see 4.5).

### 4.5 Entropy and Unpredictability: Is a Quantum Token Device Necessary?

**Short answer: no.** Unpredictability for the morphing schedule can be achieved with a **cryptographically secure pseudo-random number generator (CSPRNG)** fed by standard entropy:

- **OS entropy:** e.g. `/dev/urandom` (Linux), or `secrets` module in Python. An attacker who cannot access the orchestrator host cannot observe this stream; from outside, the sequence of states appears random.
- **HSM or hardware RNG:** For higher assurance, the orchestrator can pull entropy from a Hardware Security Module (HSM) or a dedicated hardware RNG (e.g. one-shot seed at boot). This protects against compromise of the host’s kernel entropy pool.

A **quantum random number generator (QRNG)** or “quantum token” device (e.g. USB QRNG that delivers bits from quantum noise) would provide **true** randomness instead of pseudo-randomness. That can be desirable in high-assurance or compliance-sensitive environments where “no deterministic algorithm could ever reproduce the sequence” is a requirement. For the APNA threat model—external or partially compromised observers who cannot see the orchestrator’s entropy or state—**CSPRNG with good seeding is sufficient**, and a quantum device is **optional hardening**, not a prerequisite. Implementation-wise: if a QRNG is used, the orchestrator simply reads bytes from it (e.g. via device API or `/dev/` node) instead of from `secrets` or `/dev/urandom` when deciding the next state; the rest of the morphing flow (steps 3–6) is unchanged.

---

## 5. Comparison: APNA vs Traditional Static Symmetric Architecture

| Dimension | Traditional static symmetric | APNA (this proposal) |
|-----------|-----------------------------|------------------------|
| **Topology** | Same template across DCs/segments | Intentional diversity per DC/segment; no single global template |
| **Change over time** | Static; changes only for maintenance or incidents | Controlled dynamic change (morphing) on schedule or trigger; unpredictable to attacker |
| **Role differentiation** | Often symmetric (all leaves similar) | Asymmetric by plane (control / data / RPC) and by function |
| **Failure blast radius** | Single failure pattern can repeat across segments | Contained by asymmetry; diversity prevents one blueprint for all |
| **Attacker reconnaissance** | Stable map; one scan can apply to many segments | Map goes stale; pattern identification difficult |
| **Persistence** | Long-lived mapping of targets | Harder; targets and paths shift |
| **Implementation** | Single “golden” config pattern | Automation generates diverse configs; morphing state machine drives changes |
| **Performance** | Baseline | No extra data-plane load; morphing is config/control-plane; optional intensity-based morphing to minimise churn |
| **Operational complexity** | Lower (one design to learn) | Higher (orchestration, state discipline); mitigated by automation and clear documentation |
| **Standards** | EVPN/VXLAN, BGP/OSPF as usual | Same; APNA adds diversity and dynamism on top |

---

## 6. Topology and Morphing: Visual Summary

Two infographics accompany this whitepaper:

1. **`infographic-topologies.svg`** — Compares a **traditional symmetric** multi-DC topology (same shape in each DC) with an **APNA** topology (different shapes per DC and distinct treatment of RPC vs sync vs control planes). Illustrates diversity and asymmetry.
2. **`infographic-morphing.svg`** — Shows the **morphing mechanism**: a small state machine (e.g. states A → B → C → A) with transitions driven by time or trigger; each state corresponds to a different VNI/segment mapping or path role assignment. Optional “attack detected” trigger to accelerate or trigger morphing.

Open the SVG files in the same directory with a browser or vector editor to view the diagrams.

---

## 7. References

[1] Cloudflare. “Targeted by 20.5 million DDoS attacks, up 358% year-over-year: Cloudflare’s 2025 Q1 DDoS Threat Report.” *Cloudflare Blog*, 27 Apr 2025. https://blog.cloudflare.com/ddos-threat-report-for-2025-q1  

[2] Cloudflare. “2025 Q4 DDoS threat report: A record-setting 31.4 Tbps attack caps a year of massive DDoS assaults.” *Cloudflare Blog*. https://blog.cloudflare.com/ddos-threat-report-2025-q4/  

[3] SlowMist. “Unveiling a New Scam: Malicious Modification of RPC Node Links to Steal Assets.” *Medium*, 2024. https://slowmist.medium.com/unveiling-a-new-scam-malicious-modification-of-rpc-node-links-to-steal-assets-2ca324200853  

[4] Cointelegraph / TradingView. “SlowMist uncovers crypto scam exploiting altered Ethereum nodes.” 2024.  

[5] CometBFT. “ASA-2024-009: State syncing validator from malicious node may lead to a chain split.” *GitHub Security Advisories*, 2024. https://github.com/cometbft/cometbft/security/advisories/GHSA-g5xx-c4hv-9ccc  

[6] J. Hong and D. Kim. “Toward Proactive, Adaptive Defense: A Survey on Moving Target Defense.” *IEEE Communications Surveys & Tutorials*, 2020. https://ieeexplore.ieee.org/document/8949517  

[7] Lei et al. “A Survey of Moving Target Defenses for Network Security.” *IEEE*, 2020. https://ieeexplore.ieee.org/document/9047923  

[8] S. N. Khan et al. “Moving Target Defense (MTD): Recent Advances and Future Research Challenges.” *IEEE Conference*, 2023. https://ieeexplore.ieee.org/document/9985073  

[9] Cisco. “Securing Network Infrastructure in VXLAN BGP EVPN Data Centers.” *Cisco DCN Whitepapers*. https://www.cisco.com/c/en/us/td/docs/dcn/whitepapers/securing-network-infrastructure-in-vxlan-bgp-evpn-data-centers.html  

[10] Juniper. “Security Policies for VXLAN,” “Understanding EVPN with VXLAN Data Plane Encapsulation.” *Juniper Documentation*.  

[11] M. Albanese et al. “Automated benchmark network diversification for realistic attack simulation with application to moving target defense.” *International Journal of Information Security*, 2021. https://link.springer.com/article/10.1007/s10207-021-00552-9  

[12] Performance and Security Evaluation of a Moving Target Defense in SDN (e.g. MADS). *IEEE*, 2023. https://ieeexplore.ieee.org/document/10027814  

---

## 8. Conclusion

**Asymmetric Polymorphic Network Architecture (APNA)** offers a concrete, technology-grounded approach to harden Web3 node and RPC infrastructure against pattern-based and reconnaissance-driven attacks:

- **Asymmetry** differentiates control, data, and RPC planes and limits blast radius.
- **Polymorphism** (diversity + dynamic, unpredictable change) makes it difficult for an attacker to identify stable informational patterns, reducing single-pattern and pattern-stability-of-attack.

The design is **feasible** with Arista EOS, Juniper JunOS, EVPN/VXLAN, BGP/OSPF, and automation (Ansible, Python), and is **explicitly designed to avoid data-plane overhead and bottlenecks** by keeping morphing in the control and configuration plane and by aligning with research on adaptive, intensity-aware MTD.

---

*Document prepared as a technical showcase for high-availability Web3 infrastructure roles. APNA is a design proposal; implementation details and morphing policies should be tailored to specific environments and risk assessments.*

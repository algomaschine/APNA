# APNA Rollout and Configuration — How-To

This guide explains how to roll out and configure **APNA** (Asymmetric Polymorphic Network Architecture) using the provided scripts and Ansible playbooks. It follows the morphing flow described in the whitepaper: state model → transition decision → config generation → apply order → verification.

**Quick rollout (~40 min):** Use the **AI prompt templates** in **apna/prompts/** (see apna/prompts/README.md). Fill in your context (vendor, spines/leaves, VNIs/VLANs) and paste the prompts into an AI to generate state files, Jinja2 templates, Ansible inventory, and scheduling. Run commands from the **repository root**.

---

## 1. Prerequisites

- **Python 3.8+** with `pyyaml` and `jinja2` (see `apna/requirements.txt`).
- **Ansible** (optional but recommended for apply): `ansible-core` and, for Arista, `arista.eos` collection.
- Access to your network devices (Arista EOS or Juniper JunOS) via SSH or eAPI/NETCONF.

Install Python deps:

```bash
cd apna
pip install -r requirements.txt
```

Install Ansible and Arista collection (if using Ansible apply):

```bash
pip install ansible-core
ansible-galaxy collection install arista.eos
```

---

## 2. Directory Layout

```
apna/
├── config/
│   └── orchestrator.yml    # Transition mode, interval, paths
├── states/
│   ├── state-a.yml         # State A: VNI-VLAN, BGP, ACL vars
│   ├── state-b.yml
│   └── state-c.yml
├── templates/
│   ├── eos-evpn.j2         # EVPN/VXLAN + BGP (Arista)
│   └── eos-acl.j2          # ACL snippet
├── generated/              # Rendered configs (created by morph.py)
├── data/
│   └── current_state.json  # Persisted current state (created by morph.py)
├── ansible/
│   ├── inventory.example.yml
│   ├── inventory.yml       # Your inventory (copy from example)
│   └── playbook-apply.yml  # Spines first, then leaves
├── morph.py                # Orchestrator entrypoint
└── requirements.txt
```

---

## 3. Configure the Orchestrator

Edit `apna/config/orchestrator.yml`:

| Option | Description |
|--------|-------------|
| `transition_mode` | `cycle` (A→B→C→A) or `random` (CSPRNG) |
| `morph_interval_seconds` | Used by scheduler (cron/systemd); morph.py runs once per invocation |
| `states` | List of state IDs; must match filenames `state-<id>.yml` |
| `states_dir`, `templates_dir`, `output_dir`, `state_file` | Paths (relative to config dir or absolute) |
| `ansible_playbook`, `ansible_inventory` | Set to run Ansible after generation; leave empty to skip |
| `attack_trigger_file` | Optional: if file exists, morph immediately and delete file (for IDS/DDoS hook) |

---

## 4. Define States

Each state is a YAML file in `states/` named `state-<id>.yml` (e.g. `state-a.yml`). Variables in the file are passed to Jinja2 templates.

**Example** (see `states/state-a.yml`):

- `state_id`, `description` — metadata.
- `vni_vlan_map` — mapping of VNI to VLAN for EVPN/VXLAN.
- `bgp` — e.g. `path_preference`, `local_pref`.
- `acl_profile` — profile name for ACL template.

Add or change keys as needed; reference them in `templates/*.j2` as `{{ variable }}`.

---

## 5. Customise Templates

Templates in `templates/` are Jinja2. They receive the state YAML plus `generated_at` (ISO timestamp).

- **eos-evpn.j2** — Arista EVPN/VXLAN and BGP snippet. Adjust VLAN/VNI blocks and BGP to match your design.
- **eos-acl.j2** — ACL; expand with real entries per `acl_profile`.

For Juniper, add `junos-*.j2` and render in `morph.py` (or add a second render pass), then use `junipernetworks.junos.junos_config` in Ansible.

---

## 6. Run the Orchestrator

From the repo root or from `apna/`:

```bash
# One morph: decide next state, generate configs, persist state (no Ansible)
python apna/morph.py

# Generate and apply via Ansible (spines then leaves)
python apna/morph.py --apply

# Only decide next state and save (no generation/apply)
python apna/morph.py --transition-only

# Show current state
python apna/morph.py --show-state
```

Config path defaults to `apna/config/orchestrator.yml`. Override with `--config /path/to/orchestrator.yml`.

**First run:** If `data/current_state.json` is missing, the first state in `states` is chosen, configs are generated for it, and that state is persisted.

---

## 7. Ansible Apply

1. Copy and edit inventory:
   ```bash
   cp apna/ansible/inventory.example.yml apna/ansible/inventory.yml
   ```
   Fill in `ansible_host`, credentials, and `ansible_network_os` (e.g. `eos`). Use `network_cli` or `httpapi` for Arista.

2. Set in `config/orchestrator.yml`:
   - `ansible_playbook: ../ansible/playbook-apply.yml`
   - `ansible_inventory: ../ansible/inventory.yml`

3. Run:
   ```bash
   python apna/morph.py --apply
   ```
   The playbook loads `generated/spine.cfg` and `generated/leaf.cfg` (from `generated_config_dir`) and pushes them to the spines and leaves groups in order.

---

## 8. Scheduling (Cron or Systemd)

To morph on a timer (e.g. every hour):

**Cron:**

```cron
0 * * * * cd /path/to/repo && python apna/morph.py --apply
```

**Systemd timer:** Use a oneshot unit that runs `python apna/morph.py --apply` and a timer unit with `OnCalendar=hourly`.

For attack-triggered morph, create the trigger file (e.g. from an IDS or DDoS mitigation hook):

```bash
touch /var/run/apna/trigger_morph
```

On the next run of `morph.py`, it will morph immediately (and delete the file if configured).

---

## 9. Verification (Optional)

The whitepaper mentions verification (BGP/EVPN convergence) after apply. You can:

- Add an Ansible task after the config push that runs `eos_command` / `junos_command` to check BGP/EVPN state.
- Or run a separate playbook that only checks and fails if convergence is not reached within a timeout.

Example (Arista):

```yaml
- name: Check BGP EVPN convergence
  arista.eos.eos_command:
    commands: "show bgp evpn summary"
  register: bgp_out
  failed_when: "'Estab' not in bgp_out.stdout | join"
```

---

## 10. Security and Operational Notes

- **Credentials:** Use Ansible Vault or a secrets manager for device passwords/API keys; do not commit them.
- **Idempotency:** Ansible and the generated configs are intended to be idempotent; re-running apply with the same state is safe.
- **Rollback:** Keep a copy of the previous state or previous generated configs; on failure, re-apply the previous state or restore from backup.
- **Staged rollout:** Test morph and apply in a lab first; then canary a single spine/leaf before rolling out to the full fabric.

---

## 11. Quick Reference

| Task | Command |
|------|--------|
| One morph (generate only) | `python apna/morph.py` |
| Morph and apply to devices | `python apna/morph.py --apply` |
| Only advance state | `python apna/morph.py --transition-only` |
| Show current state | `python apna/morph.py --show-state` |
| Manual Ansible apply | `ansible-playbook -i apna/ansible/inventory.yml apna/ansible/playbook-apply.yml -e "generated_config_dir=$(pwd)/apna/generated"` |

For the full design and rationale, see **whitepaper/APNA-Whitepaper.pdf** (or **whitepaper/APNA-Whitepaper.html** and **whitepaper/Asymmetric-Polymorphic-Network-Architecture-Whitepaper.md**).

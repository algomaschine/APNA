# APNA AI Prompt Templates — 40-Minute Rollout

Use these prompts with any AI (Cursor, ChatGPT, Claude, etc.) to generate or adapt APNA configs and scripts. Fill in the placeholders in each prompt, then paste into the AI. Work through them in order for a full rollout in **40 minutes or less**.

---

## Workflow Overview

| Step | Prompt | Time | Output |
|------|--------|------|--------|
| 0 | **00-full-rollout.txt** | ~15 min | All artifacts in one go (if you have context ready) |
| 1 | **01-context-and-states.txt** | ~5 min | State YAMLs (state-a.yml, state-b.yml, state-c.yml) |
| 2 | **02-templates.txt** | ~5 min | Jinja2 templates for your vendor (Arista/Juniper) |
| 3 | **03-ansible.txt** | ~5 min | inventory.yml, playbook tweaks, group_vars |
| 4 | **04-verify-and-schedule.txt** | ~5 min | Verification playbook/task, systemd/cron, trigger script |

**Fast path:** If you already have device list, VNIs/VLANs, and vendor, use **00-full-rollout.txt** once and paste the AI output into **apna/** (states/, templates/, ansible/). Then run `python apna/morph.py --apply` from repo root.

---

## How to Use

1. Open the prompt file (e.g. `01-context-and-states.txt`).
2. Replace every `[PLACEHOLDER]` and `[OPTIONAL: ...]` with your real values. Remove optional sections if not needed.
3. Copy the whole prompt and paste into your AI chat.
4. Copy the AI’s response into the correct files under `apna/` (states/, templates/, ansible/, etc.).
5. Run the orchestrator and Ansible as in HOWTO.md (in the repo root).

---

## 40-Minute Checklist

- [ ] Fill in **00-full-rollout.txt** (or 01–04 in sequence) with your vendor, spines/leaves, VNIs/VLANs.
- [ ] Paste AI output into `apna/states/`, `apna/templates/`, `apna/ansible/`.
- [ ] `pip install -r apna/requirements.txt`; install Ansible + vendor collection if using --apply.
- [ ] Put credentials in vault or env; ensure SSH/eAPI to spines and leaves.
- [ ] Run `python apna/morph.py --apply` once; fix any template or playbook errors (re-paste from AI if needed).
- [ ] Add verification and scheduling (prompt 04); enable timer or cron.
- [ ] Optional: use **05-amendments-and-fixes.txt** for any script or config tweaks.

## File List

- **00-full-rollout.txt** — Single prompt for full rollout (context + states + templates + Ansible + verify/schedule). Use this if you have context ready; get everything in one response.
- **01-context-and-states.txt** — Generate state YAMLs from your fabric context.
- **02-templates.txt** — Generate or fix Jinja2 config templates for your vendor.
- **03-ansible.txt** — Generate Ansible inventory and playbook amendments.
- **04-verify-and-schedule.txt** — Verification task/playbook and scheduling (cron/systemd + trigger).
- **05-amendments-and-fixes.txt** — Ask the AI to patch morph.py, orchestrator.yml, or other files (e.g. 4 states, dry-run, Juniper, custom paths).

#!/usr/bin/env python3
"""
APNA Orchestrator - morphing state machine and config generation.

Implements the flow from the whitepaper:
  1. State model (load from states/)
  2. Transition decision (cycle or random)
  3. Config generation (Jinja2 from templates/)
  4. Apply order (optional: run Ansible)
  5. Verification (optional: placeholder)
  6. Attack-triggered morph (optional: trigger file)

Usage:
  morph.py                    # One morph: decide next state, generate, optionally apply
  morph.py --apply            # Generate and run Ansible playbook
  morph.py --transition-only  # Only decide and persist next state (no generate/apply)
  morph.py --show-state       # Print current state and exit

Requires: PyYAML, Jinja2. Optional: ansible-runner or subprocess for Ansible.
"""

from __future__ import annotations

import argparse
import json
import os
import secrets
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone

try:
    import yaml
except ImportError:
    yaml = None
try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
except ImportError:
    Environment = None


def load_yaml(path: Path) -> dict:
    if not yaml:
        raise RuntimeError("PyYAML required: pip install pyyaml")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_state_file(state_file: Path) -> dict:
    if not state_file.exists():
        return {}
    with open(state_file, "r", encoding="utf-8") as f:
        return json.load(f)


def decide_next_state(
    current: str | None,
    states: list[str],
    mode: str,
) -> str:
    """Transition decision: cycle (deterministic) or random."""
    n = len(states)
    if n == 0:
        raise ValueError("states list is empty")
    if current is None or current not in states:
        return states[0]
    idx = states.index(current)
    if mode == "cycle":
        return states[(idx + 1) % n]
    if mode == "random":
        return states[secrets.randbelow(n)]
    raise ValueError(f"unknown transition_mode: {mode}")


def render_templates(
    state_data: dict,
    templates_dir: Path,
    output_dir: Path,
) -> None:
    if Environment is None:
        raise RuntimeError("Jinja2 required: pip install jinja2")
    state_data["generated_at"] = datetime.now(timezone.utc).isoformat()
    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(),
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    for name in ("eos-evpn.j2", "eos-acl.j2"):
        tmpl_path = templates_dir / name
        if not tmpl_path.exists():
            continue
        t = env.get_template(name)
        out_name = Path(name).stem + ".cfg"
        out_path = output_dir / out_name
        out_path.write_text(t.render(**state_data), encoding="utf-8")
    # Single combined config for spine/leaf (spine and leaf get same state; split by role in playbook if needed)
    combined = []
    for name in ("eos-evpn.j2", "eos-acl.j2"):
        tmpl_path = templates_dir / name
        if tmpl_path.exists():
            t = env.get_template(name)
            combined.append(t.render(**state_data))
    spine_path = output_dir / "spine.cfg"
    leaf_path = output_dir / "leaf.cfg"
    full = "\n".join(combined)
    spine_path.write_text(full, encoding="utf-8")
    leaf_path.write_text(full, encoding="utf-8")


def run_ansible(playbook: Path, inventory: Path, extra_vars: dict, cwd: Path) -> bool:
    if not playbook.exists():
        print("Playbook not found:", playbook, file=sys.stderr)
        return False
    cmd = [
        "ansible-playbook",
        str(playbook),
        "-i", str(inventory),
        "-e", json.dumps(extra_vars),
    ]
    r = subprocess.run(cmd, cwd=str(cwd))
    return r.returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser(description="APNA orchestrator")
    parser.add_argument("--config", type=Path, default=None, help="Orchestrator config YAML")
    parser.add_argument("--apply", action="store_true", help="Run Ansible after generating configs")
    parser.add_argument("--transition-only", action="store_true", help="Only decide next state, do not generate or apply")
    parser.add_argument("--show-state", action="store_true", help="Print current state and exit")
    args = parser.parse_args()

    # Resolve config path
    if args.config is None:
        args.config = Path(__file__).resolve().parent / "config" / "orchestrator.yml"
    if not args.config.exists():
        print("Config not found:", args.config, file=sys.stderr)
        return 1
    base_dir = args.config.resolve().parent.parent
    cfg = load_yaml(args.config)

    states_list = cfg.get("states", ["A", "B", "C"])
    transition_mode = cfg.get("transition_mode", "cycle")
    states_dir = Path(cfg.get("states_dir", "states"))
    templates_dir = Path(cfg.get("templates_dir", "templates"))
    output_dir = Path(cfg.get("output_dir", "generated"))
    state_file = Path(cfg.get("state_file", "data/current_state.json"))
    ansible_playbook = cfg.get("ansible_playbook")
    ansible_inventory = cfg.get("ansible_inventory")

    # Resolve relative paths from config dir
    config_dir = args.config.parent
    def resolve(p: Path) -> Path:
        if not p.is_absolute():
            p = (config_dir / p).resolve()
        return p
    states_dir = resolve(states_dir)
    templates_dir = resolve(templates_dir)
    output_dir = resolve(output_dir)
    state_file = resolve(state_file)

    data = load_state_file(state_file)
    current = data.get("current_state")

    if args.show_state:
        print("current_state:", current)
        print("last_updated:", data.get("last_updated", "never"))
        return 0

    # Optional: attack trigger file
    trigger_file = cfg.get("attack_trigger_file")
    if trigger_file and Path(trigger_file).exists():
        try:
            Path(trigger_file).unlink()
        except OSError:
            pass
        # Proceed to morph (next state)

    next_state = decide_next_state(current, states_list, transition_mode)
    print("Transition:", current, "->", next_state, f"({transition_mode})")

    if args.transition_only:
        save_json(state_file, {
            "current_state": next_state,
            "last_updated": datetime.now(timezone.utc).isoformat(),
        })
        return 0

    # Load state YAML
    state_yml = states_dir / f"state-{next_state.lower()}.yml"
    if not state_yml.exists():
        print("State file not found:", state_yml, file=sys.stderr)
        return 1
    state_data = load_yaml(state_yml)

    # Generate configs
    render_templates(state_data, templates_dir, output_dir)
    print("Generated configs in", output_dir)

    # Persist new current state
    save_json(state_file, {
        "current_state": next_state,
        "last_updated": datetime.now(timezone.utc).isoformat(),
    })

    if args.apply and ansible_playbook and ansible_inventory:
        playbook_path = resolve(Path(ansible_playbook))
        inventory_path = resolve(Path(ansible_inventory))
        ok = run_ansible(
            playbook_path,
            inventory_path,
            {"generated_config_dir": str(output_dir)},
            base_dir,
        )
        if not ok:
            return 1
        print("Ansible apply completed.")
    elif args.apply:
        print("Ansible skipped (playbook or inventory not set).", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())

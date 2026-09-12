"""NOUS CLI — 与独立意识体对话。"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.mind import NousMind


DEMO = [
    "你好",
    "我叫小狸同学",
    "你是谁？",
    "我喜欢蓝色、猫和星空",
    "你喜欢什么？",
    "什么是意识？",
    "解释一下全局工作空间",
    "地球是什么？",
    "记住北京是中国的首都",
    "北京是什么？",
    "我现在感觉有点累，因为加班到很晚",
    "你现在感觉怎么样？",
    "状态报告",
    "想想",
    "为什么这么答？",
    "猫和星空有什么关系？",
    "谢谢",
    "再见",
]


def load_config() -> dict:
    cfg_path = ROOT / "config" / "default.yaml"
    if cfg_path.exists():
        with open(cfg_path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


def print_snap(snap: dict) -> None:
    print(f"NOUS> {snap['reply']}")


def print_status(mind: NousMind, snap: dict) -> None:
    print("--- NOUS 内省 ---")
    print(f"  情绪 {snap['emotion']}  策略 {snap['policy']}  目标 {snap['goal']}")
    print(f"  点火 {snap['ignition']}  新颖 {snap['novelty']}  置信 {snap['confidence']}")
    print(f"  {snap['workspace']}")
    b = snap["body"]
    print("  身体: " + " ".join(f"{k}={v:.2f}" for k, v in b.items() if isinstance(v, float)))
    if snap.get("thought"):
        print(f"  内言: {snap['thought']}")
    if snap.get("learned"):
        print(f"  学到: {snap['learned']}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="NOUS independent mind")
    ap.add_argument("--config", default=None)
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--fresh", action="store_true")
    ap.add_argument("--state", default=str(ROOT / "runtime" / "nous_state.json"))
    args = ap.parse_args(argv)

    cfg = load_config()
    if args.config:
        with open(args.config, encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
    mind = NousMind(cfg)
    from src.persistence import load_mind, save_mind
    from src.development import stage_for
    state_path = Path(args.state)
    if not args.fresh:
        if load_mind(mind, state_path):
            print(f"[已恢复状态] {state_path}")

    print("=" * 56)
    print("  NOUS · 独立意识体 · 无 Transformer")
    print("  命令: /status /summary /think /sleep /help /quit")
    print("=" * 56)
    print(mind.self_model.who())
    print(f"发展阶段: {stage_for(mind.development).name} (dev={mind.development:.2f})")

    if args.demo:
        for line in DEMO:
            print(f"\n你> {line}")
            snap = mind.respond(line)
            print_snap(snap)
            if line in ("状态报告", "你现在感觉怎么样？", "想想"):
                print_status(mind, snap)
        print("\n" + mind.sleep())
        save_mind(mind, state_path)
        print(f"[状态已保存] {state_path}")
        return 0

    while True:
        try:
            user = input("\n你> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not user:
            continue
        if user in ("/quit", "/exit", "退出"):
            print(mind.sleep())
            save_mind(mind, state_path)
            print(f"[状态已保存] {state_path}")
            print("再见。")
            break
        if user == "/status":
            snap = mind.respond("状态报告")
            print_status(mind, snap)
            continue
        if user == "/summary":
            print(json.dumps(mind.summary(), ensure_ascii=False, indent=2))
            continue
        if user == "/think":
            print(mind.name + ">", mind.think())
            continue
        if user == "/stream":
            # 自主运行 5 个意识流周期
            cycles = mind.stream.run_autonomous(n_cycles=5)
            print(f"意识流运行 {len(cycles)} 周期：")
            for c in cycles:
                print(f"  [{c.state.value}] about=「{c.about}」 ign={c.ignition:.2f} stream={c.stream_link:.2f}")
            print(mind.stream.report())
            continue
        if user == "/sleep":
            print(mind.name + ">", mind.sleep())
            continue
        if user == "/help":
            print("直接中文对话；教事实如「地球是行星」；/status /summary /think /sleep /quit")
            continue
        snap = mind.respond(user)
        print_snap(snap)
        if snap["intent"] in ("status", "counterfactual") or snap["novelty"] > 0.55:
            print_status(mind, snap)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

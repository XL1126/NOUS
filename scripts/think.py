"""scripts/think.py — 自主思维演示。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.mind import NousMind


def main() -> int:
    mind = NousMind({"seed": 3})
    mind.respond("记住猫是哺乳动物")
    mind.respond("我喜欢星空")
    for i in range(5):
        t = mind.think()
        print(f"[think {i+1}] {t}")
        print(f"  need={mind.soma.dominant_need()} policy={mind.soma.policy()}")
    print(mind.ws.report())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

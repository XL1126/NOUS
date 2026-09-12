"""scripts/export_phenomenal.py — 导出现象/身体/行动状态到 runtime + index 面板。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.mind import NousMind
from src.persistence import load_mind


def main() -> int:
    mind = NousMind({"seed": 42})
    state = ROOT / "runtime" / "nous_state.json"
    if state.exists():
        load_mind(mind, state)
    # 走几回合让标记有动态
    for line in ["你好", "我叫观察者", "记住我喜欢猫", "什么是意识？", "状态报告"]:
        mind.respond(line)
    s = mind.summary()
    payload = {
        "name": s["name"],
        "turns": s["turns"],
        "development": s["development"],
        "emotion": s["emotion"],
        "policy": s["policy"],
        "need": s["need"],
        "body": s["body"],
        "phenomenal": s["phenomenal"],
        "phenomenal_report": s["phenomenal_report"],
        "integrated": s["integrated"],
        "maintenance": s["maintenance"],
        "action": s.get("action"),
        "action_narrative": s.get("action_narrative"),
        "boundary": s.get("boundary"),
        "vitality": s["vitality"],
        "age_turns": s["age_turns"],
        "mortality": s["mortality"],
        "dreams": s["dreams"],
        "workspace": s["workspace"],
        "goal": s["goal"],
        "identity": s["identity"],
    }
    out = ROOT / "runtime" / "phenomenal.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {out}")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

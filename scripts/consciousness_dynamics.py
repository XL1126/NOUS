"""scripts/consciousness_dynamics.py — 长程对话中意识指标是否成形。

衡量：整合、前反思自我、意识流连续、意向性是否稳定。
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.mind import NousMind


SCRIPT = [
    "你好",
    "我叫长程观察者",
    "记住我喜欢猫和星空",
    "猫是什么？",
    "什么是意识？",
    "解释一下全局工作空间",
    "地球是什么？",
    "我现在有点累",
    "状态报告",
    "此刻你在想什么？",
    "猫和星空有什么关系？",
    "如果能量很低会怎样？",
    "以后的你会怎样？",
    "你有意识吗？",
    "谢谢",
    "再见",
]


def main() -> int:
    m = NousMind({"seed": 99})
    rows = []
    for line in SCRIPT:
        r = m.respond(line)
        p = r.get("present") or {}
        rows.append({
            "turn": r["turn"],
            "about": p.get("about"),
            "integration": p.get("integration"),
            "min_self": p.get("min_self"),
            "stream": p.get("stream_link"),
            "presence": p.get("presence"),
            "figure_n": len(p.get("figure") or []),
        })
        print(f"T{r['turn']:02d} about={p.get('about')!s:8} integ={p.get('integration')} "
              f"self={p.get('min_self')} stream={p.get('stream_link')} fig={p.get('figure')}")

    first, last = rows[0], rows[-1]
    avg_i = sum(r["integration"] or 0 for r in rows) / len(rows)
    avg_s = sum(r["stream"] or 0 for r in rows) / len(rows)
    print("\n=== 意识动力学 ===")
    print(f"整合  first={first['integration']} last={last['integration']} avg={avg_i:.3f}")
    print(f"自我  first={first['min_self']} last={last['min_self']}")
    print(f"连续  first={first['stream']} last={last['stream']} avg={avg_s:.3f}")
    print(m.core.stream_summary(8))
    # 判定：必须形成非平凡意识场
    ok = (
        (last["min_self"] or 0) >= (first["min_self"] or 0)
        and avg_i > 0.25
        and all(r["about"] for r in rows)
        and len(m.core.moments) >= len(SCRIPT)
    )
    print("DYNAMICS_OK" if ok else "DYNAMICS_WEAK")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

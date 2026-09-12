import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.mind import NousMind

m = NousMind({"seed": 99})
for line in ["你好", "什么是意识？", "猫是什么？", "状态报告"]:
    r = m.respond(line)
    print(f"U: {line}")
    print(f"A: {r['reply'][:120]}")
    if m.last_emergent_thought:
        print(f"涌现: {m.last_emergent_thought}")
    print("---")
print(f"涌现概念数: {len(m.emergence.emergent_concepts)}")
print(m.emergence.get_emergent_summary())

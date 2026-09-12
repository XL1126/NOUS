"""scripts/neri_language_demo.py — 演示 NERI 动力学驱动语言。"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.mind import NousMind

def main():
    m = NousMind({"seed": 99})
    lines = ["你好", "什么是意识？", "解释一下NERI", "状态报告", "你有意识吗？"]
    for line in lines:
        r = m.respond(line)
        neri = m.neri.history[-1] if m.neri.history else None
        epr = neri.epr if neri else 0
        fdt = neri.fdt_violation if neri else 0
        print(f"U: {line}")
        print(f"A: {r['reply']}")
        print(f"  NERI: EPR={epr:.3f} FDT={fdt:.3f}")
        print()

if __name__ == "__main__":
    main()

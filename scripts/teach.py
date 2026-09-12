"""scripts/teach.py — 课程教学。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.mind import NousMind

CURRICULUM = [
    "你好",
    "我叫小狸同学",
    "我喜欢蓝色、猫和星空",
    "我讨厌香菜",
    "北京是中国的首都",
    "上海是一个大城市",
    "猫是哺乳动物",
    "地球是太阳系第三颗行星",
    "水是生命溶剂",
    "什么是意识？",
    "解释一下预测编码",
    "你现在感觉怎么样？",
    "状态报告",
    "谢谢",
]


def main() -> int:
    mind = NousMind({"seed": 7})
    for line in CURRICULUM:
        snap = mind.respond(line)
        print(f"U: {line}\nA: {snap['reply']}\n")
    print(json.dumps(mind.summary(), ensure_ascii=False, indent=2))
    print(mind.sleep())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

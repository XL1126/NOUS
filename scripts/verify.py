"""scripts/verify.py — NOUS 验收。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pytest
from src.mind import NousMind


def run_dialogue_smoke() -> None:
    mind = NousMind({"seed": 1})
    script = [
        "你好",
        "我叫小明",
        "你是谁？",
        "记住我喜欢猫",
        "你喜欢什么？",
        "什么是意识？",
        "地球是什么？",
        "猫是哺乳动物",
        "状态报告",
        "谢谢",
        "再见",
    ]
    for line in script:
        snap = mind.respond(line)
        assert snap["reply"], line
        assert 0 <= snap["body"]["energy"] <= 1
    s = mind.summary()
    assert s["turns"] == len(script)
    assert s["semantic_facts"] > 10
    assert "猫" in s["likes"] or any("猫" in x for x in s["likes"])
    print("OK dialogue smoke")


def main() -> int:
    print(">>> pytest")
    rc = pytest.main([str(ROOT / "tests"), "-q"])
    if rc != 0:
        return int(rc)
    print(">>> dialogue smoke")
    run_dialogue_smoke()
    print("ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

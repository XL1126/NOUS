"""NOUS 舰队 CLI。"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.fleet import Fleet
from src.train import train_mind, save_report, DEFAULT_CURRICULUM


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fleet", default=str(ROOT / "runtime" / "fleet"))
    sub = ap.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("spawn")
    sp.add_argument("--template", default="nous", choices=["nous", "lanxing", "moke", "nuanhe"])
    sp.add_argument("--name", default=None)

    st = sub.add_parser("train")
    st.add_argument("--agent", required=True)
    st.add_argument("--epochs", type=int, default=2)
    st.add_argument("--out", default=str(ROOT / "runtime" / "train_report.json"))

    sf = sub.add_parser("fork")
    sf.add_argument("--parent", required=True)
    sf.add_argument("--name", default=None)

    stk = sub.add_parser("talk")
    stk.add_argument("--a", required=True)
    stk.add_argument("--b", required=True)
    stk.add_argument("--seed", default="我们聊聊记忆和身体状态")
    stk.add_argument("--turns", type=int, default=4)

    sub.add_parser("list")

    args = ap.parse_args(argv)
    fleet = Fleet(args.fleet)

    if args.cmd == "spawn":
        inst = fleet.spawn(args.template, name=args.name)
        print(json.dumps(inst.snapshot(), ensure_ascii=False, indent=2))
        return 0
    if args.cmd == "train":
        inst = fleet.get(args.agent)
        report = train_mind(inst.mind, DEFAULT_CURRICULUM, epochs=args.epochs)
        inst.trained_turns += report.turns
        inst.save()
        save_report(report, Path(args.out))
        print(json.dumps(report.as_dict(), ensure_ascii=False, indent=2))
        return 0
    if args.cmd == "fork":
        inst = fleet.fork(args.parent, name=args.name)
        print(json.dumps(inst.snapshot(), ensure_ascii=False, indent=2))
        return 0
    if args.cmd == "talk":
        log = fleet.talk_together(args.a, args.b, args.seed, turns=args.turns)
        print(json.dumps(log, ensure_ascii=False, indent=2))
        return 0
    if args.cmd == "list":
        print(json.dumps(fleet.list(), ensure_ascii=False, indent=2))
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

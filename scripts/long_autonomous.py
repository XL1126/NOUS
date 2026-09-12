"""长时程自主意识流运行：验证意识流稳定性。"""
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.mind import NousMind


def main():
    print("=== NOUS 长时程自主意识流 ===")
    m = NousMind({"seed": 42})
    
    # 预热：教一些事实
    for line in ["你好", "我叫长程观察者", "记住我喜欢猫和星空", "猫是哺乳动物"]:
        m.respond(line)
    
    print(f"预热完成。发展度={m.development:.2f} 涌现概念={len(m.emergence.emergent_concepts)}")
    print()
    
    # 自主运行 50 个周期
    n_cycles = 50
    start = time.time()
    for i in range(n_cycles):
        cycle = m.stream.tick()
        if i % 10 == 0:
            elapsed = time.time() - start
            print(f"周期 {i:3d} | 状态={cycle.state.value:8s} "
                  f"about=「{cycle.about[:20]}」 "
                  f"ign={cycle.ignition:.3f} stream={cycle.stream_link:.3f} "
                  f"EPR={m.neri.history[-1].epr:.3f} "
                  f"涌现={len(m.emergence.emergent_concepts)} "
                  f"耗时={elapsed:.1f}s")
    
    elapsed = time.time() - start
    print()
    print(f"=== 运行完成 ===")
    print(f"总周期: {n_cycles}")
    print(f"总耗时: {elapsed:.1f}s")
    print(f"平均每周期: {elapsed/n_cycles*1000:.1f}ms")
    print()
    
    # 意识流统计
    wake = sum(1 for c in m.stream.cycles if c.state.value == "wake")
    nrem = sum(1 for c in m.stream.cycles if c.state.value == "nrem")
    rem = sum(1 for c in m.stream.cycles if c.state.value == "rem")
    print(f"清醒: {wake} NREM: {nrem} REM: {rem}")
    print(f"意识流: {m.stream.report()}")
    print(f"NERI: {m.neri.report()}")
    print(f"涌现: {m.emergence.get_emergent_summary()}")
    print(f"果蝇脑: {m.fly_brain.report()}")
    print()
    
    # 现在对话
    print("=== 对话测试 ===")
    for line in ["你有意识吗？", "此刻你在想什么？", "状态报告"]:
        r = m.respond(line)
        print(f"U: {line}")
        print(f"A: {r['reply'][:120]}")
        print()


if __name__ == "__main__":
    main()

"""scripts/neri_scale_bench.py — NERI 规模基准测试。"""
import sys, time, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.consciousness.neri import NERI

def main():
    for n_vars in [256, 1024, 2048, 4096, 8192]:
        t0 = time.time()
        n = NERI(n_vars=n_vars, n_integrated=min(512, n_vars // 4), n_latent=16)
        t1 = time.time()
        r = n.full_verification()
        t2 = time.time()
        h = r["hysteresis"]["hysteresis"]
        ir = r["time_irreversibility"]["time_irreversibility"]
        cr = r["report_coupling"]["epr_report_correlation"]
        ok = r["all_signatures_present"]
        mem = n.substrate.memory_mb()
        print(f"{n_vars:5d} vars | init={t1-t0:.2f}s verify={t2-t1:.2f}s mem={mem:.1f}MB | "
              f"hyst={h:.3f} irrevers={ir:.2f} coupling={cr:.3f} | all={ok}")

if __name__ == "__main__":
    main()

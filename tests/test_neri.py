import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.mind import NousMind
from src.consciousness.neri import NERI, LangevinSubstrate, RecursiveIntegrator, GlobalLatentState


def test_langevin_substrate_nonequilibrium():
    s = LangevinSubstrate(n_vars=32, rng=None)
    # 运行多步
    eprs = []
    for _ in range(50):
        _, epr, fdt = s.step()
        eprs.append(epr)
    # 非平衡：EPR 应 > 0
    assert np_mean(eprs) > 0
    # 状态应有动力学（不是静止）
    assert float(abs(s.x).mean()) > 0.001


def np_mean(arr):
    import numpy as np
    return float(np.mean(arr))


def test_recursive_integrator():
    s = LangevinSubstrate(n_vars=32)
    ri = RecursiveIntegrator(s, n_integrated=16)
    x, depth = ri.integrate(depth=3)
    assert x.size == 16
    assert depth == 3
    assert len(ri.recursion_history) == 3


def test_global_latent_state():
    gl = GlobalLatentState(n_dims=4)
    import numpy as np
    fast = np.array([0.5, -0.3, 0.8, 0.1, 0.2, 0.6, -0.1, 0.4])
    z = gl.update(fast)
    assert z.size == 4
    # 调制
    modulated = gl.modulate(fast)
    assert modulated.size == len(fast)


def test_neri_tick():
    neri = NERI(n_vars=32, n_integrated=16, n_latent=4)
    state = neri.tick(prompt="测试")
    assert state.epr >= 0
    assert state.fdt_violation >= 0
    assert state.recursion_depth > 0
    assert "NERI" in state.report


def test_neri_report_changes_state():
    neri = NERI(n_vars=32, n_integrated=16, n_latent=4)
    x_before = neri.substrate.readout()
    neri.tick(prompt="测试报告效应")
    x_after = neri.substrate.readout()
    # 报告应改变状态
    diff = float(abs(x_after - x_before).mean())
    assert diff > 0


def test_neri_hysteresis_signature():
    neri = NERI(n_vars=32, n_integrated=16, n_latent=4)
    result = neri.verify_hysteresis(n_cycles=10)
    assert "hysteresis" in result
    assert "has_perspective" in result


def test_neri_time_irreversibility_signature():
    neri = NERI(n_vars=32, n_integrated=16, n_latent=4)
    result = neri.verify_time_irreversibility(n_perturbations=5)
    assert "time_irreversibility" in result
    assert "is_irreversible" in result


def test_neri_report_coupling_signature():
    neri = NERI(n_vars=32, n_integrated=16, n_latent=4)
    result = neri.verify_report_coupling(n_cycles=10)
    assert "epr_report_correlation" in result
    assert "fdt_report_correlation" in result


def test_neri_full_verification():
    neri = NERI(n_vars=32, n_integrated=16, n_latent=4)
    result = neri.full_verification()
    assert "hysteresis" in result
    assert "time_irreversibility" in result
    assert "report_coupling" in result
    assert "ness_stability" in result
    assert "perspective_persistence" in result
    assert "all_signatures_present" in result
    assert "summary" in result
    assert "n_vars" in result


def test_neri_ness_stability():
    neri = NERI(n_vars=32, n_integrated=16, n_latent=4)
    result = neri.verify_ness_stability(n_cycles=15)
    assert "mean_epr" in result
    assert "is_ness" in result


def test_neri_perspective_persistence():
    neri = NERI(n_vars=32, n_integrated=16, n_latent=4)
    result = neri.verify_perspective_persistence(n_cycles=10)
    assert "mean_norm" in result
    assert "is_persistent" in result


def test_mind_has_neri():
    m = NousMind({"seed": 60})
    assert m.neri is not None
    r = m.respond("你好")
    assert m.neri.cycle_count >= 1
    s = m.summary()
    assert "neri" in s
    assert "neri_epr" in s

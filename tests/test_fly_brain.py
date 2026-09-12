import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.consciousness.fly_brain import FlyBrainInspired, FLY_REGIONS
import numpy as np


def test_fly_brain_regions():
    assert "central_complex" in FLY_REGIONS
    assert "mushroom_body" in FLY_REGIONS
    assert "fan_shaped_body" in FLY_REGIONS
    assert FLY_REGIONS["central_complex"].n_neurons > 0
    assert FLY_REGIONS["mushroom_body"].n_neurons > 0


def test_fly_brain_central_complex():
    fb = FlyBrainInspired()
    sensory = np.random.standard_normal(32)
    result = fb.update_central_complex(sensory)
    assert "heading" in result
    assert "ring_state" in result
    assert "winner" in result


def test_fly_brain_mushroom_body():
    fb = FlyBrainInspired()
    sensory = np.random.standard_normal(32)
    result = fb.update_mushroom_body(sensory)
    assert "sparsity" in result
    assert 0 <= result["sparsity"] <= 1
    assert result["active_kenyon"] <= result["total_kenyon"]


def test_fly_brain_fan_shaped_body():
    fb = FlyBrainInspired()
    result = fb.update_fan_shaped_body(arousal_input=0.8, sleep_pressure=0.2)
    assert "arousal" in result
    assert "sleep_gate" in result
    assert "state" in result


def test_fly_brain_dopaminergic():
    fb = FlyBrainInspired()
    result = fb.update_dopaminergic(reward=1.0, predicted_reward=0.5)
    assert "da_level" in result
    assert "prediction_error" in result
    assert result["prediction_error"] == 0.5  # 1.0 - 0.5


def test_fly_brain_full_update():
    fb = FlyBrainInspired()
    sensory = np.random.standard_normal(32)
    result = fb.full_update(
        sensory_input=sensory,
        arousal=0.6,
        sleep_pressure=0.3,
        reward=0.5,
        predicted_reward=0.4,
    )
    assert "central_complex" in result
    assert "mushroom_body" in result
    assert "fan_shaped_body" in result
    assert "dopaminergic" in result


def test_fly_brain_report():
    fb = FlyBrainInspired()
    fb.full_update(np.random.standard_normal(32))
    report = fb.report()
    assert "果蝇脑" in report

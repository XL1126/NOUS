"""意识包：现象标记 / 自创生 / 梦 / 多维剖面 / 社会神经元 / 马尔可夫毯 / 连续意识流 / NERI / 涌现 / 果蝇脑。"""
from .phenomenology import Phenomenology, PhenomenalMarkers
from .autopoiesis import Autopoiesis, VitalState
from .dream import DreamCycle
from .core import ConsciousnessCore, ConsciousMoment, AttentionSchema
from .self_pole import SelfPole, SelfPoleState
from .temporal import TemporalMind, TemporalTopology
from .profile import ConsciousnessProfile, ProfileBuilder
from .social_neurons import SocialNeurons, SocialNeuronState
from .markov_blanket import PresentMomentMarkovBlanket, MarkovBlanket
from .stream import ConsciousnessStream, ConsciousState, ConsciousCycle, SleepWakeMachine
from .neri import NERI, NERIState, LangevinSubstrate, RecursiveIntegrator, GlobalLatentState, InternalReporter
from .emergence import EmergenceMapper, EmergentContent
from .fly_brain import FlyBrainInspired, FLY_REGIONS

__all__ = [
    "Phenomenology", "PhenomenalMarkers",
    "Autopoiesis", "VitalState", "DreamCycle",
    "ConsciousnessCore", "ConsciousMoment", "AttentionSchema",
    "SelfPole", "SelfPoleState",
    "TemporalMind", "TemporalTopology",
    "ConsciousnessProfile", "ProfileBuilder",
    "SocialNeurons", "SocialNeuronState",
    "PresentMomentMarkovBlanket", "MarkovBlanket",
    "ConsciousnessStream", "ConsciousState", "ConsciousCycle", "SleepWakeMachine",
    "NERI", "NERIState", "LangevinSubstrate", "RecursiveIntegrator", "GlobalLatentState", "InternalReporter",
    "EmergenceMapper", "EmergentContent",
    "FlyBrainInspired", "FLY_REGIONS",
]

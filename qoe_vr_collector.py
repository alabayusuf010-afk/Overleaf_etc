"""qoe_vr_collector.py  —  PPGSEA/UFLA, 2026"""
from __future__ import annotations
import json, logging, os
from dataclasses import dataclass, field, asdict
from typing import List, Optional
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class NetworkMeas:
    timestamp: float = 0.0
    plr_pct: float = 0.0     # Packet Loss Rate (%)
    jitter_ms: float = 0.0   # Jitter std-dev (ms)
    delay_ms: float = 0.0    # One-way delay (ms)
    throughput_mbps: float = 0.0
    fps: float = 90.0

@dataclass
class PerceptualMeas:
    trial_id: str = ""
    user_role: str = "passive"  # passive | active | collaborative
    mtp_ms: float = 0.0
    ir_ms: float = 0.0
    mushra: float = 100.0
    ipq: float = 1.0
    acr_mos: Optional[float] = None  # ground truth

@dataclass
class QoEResult:
    trial_id: str = ""
    s_net: float = 0.0
    s_mtp: float = 0.0
    s_ir: float = 0.0
    s_audio: float = 0.0
    s_pres: float = 0.0
    u_r: float = 1.0
    qoe_vr: float = 0.0
    weights: List[float] = field(default_factory=lambda:[0.2]*5)

class QoEVRCollector:
    """Collect measurements and compute QoE_VR composite scores."""

    QOS_BOUNDS = {
        "plr_pct":        (0.0, 5.0),
        "jitter_ms":      (0.0, 50.0),
        "delay_ms":       (0.0, 150.0),
        "throughput_mbps":(0.0, 100.0),
        "fps":            (0.0, 90.0),
    }
    ROLE_W = {"passive": 0.40, "active": 0.80, "collaborative": 1.00}

    def __init__(self, k: float=0.30, tau0: float=20.0,
                 weights: Optional[List[float]]=None) -> None:
        self.k, self.tau0 = k, tau0
        self.w = weights or [0.20, 0.25, 0.25, 0.15, 0.15]
        assert abs(sum(self.w)-1.0) < 1e-6, "Weights must sum to 1"
        self._nets: List[NetworkMeas] = []
        self._percs: List[PerceptualMeas] = []

    # —— normalisation ————————————————————————————————
    def _norm(self, v: float, key: str, inv: bool=False) -> float:
        lo, hi = self.QOS_BOUNDS[key]
        r = (max(lo, min(hi, v)) - lo) / (hi - lo)
        return 1.0 + 4.0 * (1.0 - r if inv else r)

    # —— sub-scores ———————————————————————————————————
    def s_net(self, n: NetworkMeas) -> float:
        a = [0.25]*4
        terms = [
            self._norm(n.plr_pct,        "plr_pct",        inv=True),
            self._norm(n.jitter_ms,      "jitter_ms",      inv=True),
            self._norm(n.delay_ms,       "delay_ms",       inv=True),
            self._norm(n.fps,            "fps",            inv=False),
        ]
        return sum(ai*t for ai,t in zip(a,terms))

    def s_mtp(self, tau: float) -> float:
        return 4.0/(1.0+np.exp(self.k*(tau-self.tau0)))+1.0

    def s_ir(self, delta: float) -> float:
        if delta <= 50.0: return 5.0
        return float(np.clip(5.0 - (4.0/350.0)*(delta-50.0), 1.0, 5.0))

    def s_audio(self, m: float) -> float:
        return 1.0 + (max(0.0,min(100.0,m))/100.0)*4.0

    def s_pres(self, ipq: float) -> float:
        return 1.0 + max(0.0,min(1.0,ipq))*4.0

    # —— composite ————————————————————————————————————
    def compute(self, n: NetworkMeas, p: PerceptualMeas) -> QoEResult:
        ur   = self.ROLE_W.get(p.user_role, 1.0)
        subs = [self.s_net(n), self.s_mtp(p.mtp_ms),
                self.s_ir(p.ir_ms), self.s_audio(p.mushra),
                self.s_pres(p.ipq)]
        qvr  = ur * sum(wi*si for wi,si in zip(self.w, subs))
        return QoEResult(trial_id=p.trial_id,
                         s_net=round(subs[0],4),
                         s_mtp=round(subs[1],4),
                         s_ir=round(subs[2],4),
                         s_audio=round(subs[3],4),
                         s_pres=round(subs[4],4),
                         u_r=ur,
                         qoe_vr=round(qvr,4),
                         weights=list(self.w))

    def record_net(self, m: NetworkMeas)  -> None: self._nets.append(m)
    def record_perc(self, m: PerceptualMeas) -> None: self._percs.append(m)

    def process_all(self) -> List[QoEResult]:
        assert len(self._nets)==len(self._percs), "Buffer length mismatch"
        return [self.compute(n,p) for n,p in zip(self._nets,self._percs)]

    def save(self, results: List[QoEResult], path: str="./out") -> None:
        os.makedirs(path, exist_ok=True)
        fp = os.path.join(path,"qoe_vr_results.json")
        with open(fp,"w") as fh:
            json.dump([asdict(r) for r in results], fh, indent=2)
        logger.info("Saved %d results to %s", len(results), fp)
\end{lstlisting}

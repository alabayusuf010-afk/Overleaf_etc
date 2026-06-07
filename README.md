# QoEVRCollector Framework

[![Python Version](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Standards](https://img.shields.io/badge/Standards-ITU--T%20P.910%20%7C%20SG12-orange)](https://www.itu.int/)

An empirical framework designed to collect, compute, and validate multi-dimensional Quality of Experience (QoE) metrics for immersive Virtual Reality ($Q_oE_{\text{VR}}$) delivered over wireless network topologies.

---

## 📌 Research Context & Architecture

This software implementation supports a **sequential mixed-methods design** split into distinct execution phases. It provides programmatic infrastructure to ingest transmission-layer performance data (QoS) and experience-layer indicators to model perceived user degradation.

### Multi-Dimensional Data Structure
The framework monitors and clusters indicators into three primary groups to predict user perceptual experience:
* **Network QoS Group:** Monitors packet loss ratio (PLR), network jitter (ms), end-to-end control-loop delay (ms), and frame rate delivery (FPS).
* **VR Perceptual Group:** Tracks experimental Motion-to-Photon (MTP) latency, interaction-responsiveness latency, spatial audio assessments, and subjective IPQ presence ratings.
* **Context Modulation:** Leverages user action context metrics to apply distinct evaluation scalar multipliers ($U_r$) matching passive, active, or collaborative workflows.

---

## 🚀 Getting Started

### Prerequisites
Ensure your local environment satisfies the following baseline requirements:
```bash
pip install numpy

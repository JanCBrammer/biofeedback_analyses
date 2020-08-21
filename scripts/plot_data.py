#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author: Jan C. Brammer <jan.c.brammer@gmail.com>
"""

import matplotlib.pyplot as plt
from biofeedback_analyses.visualization_utils import plot_dataset
from pathlib import Path


DATADIR = r"C:\Users\JohnDoe\surfdrive\Biochill_RITE\20200818_v3.0.0\data"

eventpaths = list(Path(DATADIR).glob("*recordtrigger*"))
physiopaths = list(Path(DATADIR).glob("*recordsignal*"))

idx = 3
EVENTPATH = eventpaths[idx]
PHYSPATH = physiopaths[idx]


fig = plot_dataset(physiopath=PHYSPATH, eventpath=EVENTPATH,
                   physiochannels={"Breathing": 0},
                   continuous_events=["Feedback", "InterBeatInterval"],
                   discrete_events=["WaveStart", "ShotHit", "ShotMissed"])

plt.show()

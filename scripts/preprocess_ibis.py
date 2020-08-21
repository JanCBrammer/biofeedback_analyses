#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author: Jan C. Brammer <jan.c.brammer@gmail.com>
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mne.io import read_raw_edf
from biofeedback_analyses import event_utils, hrv_utils
from pathlib import Path


DATADIR = r"C:\Users\JohnDoe\surfdrive\Biochill_RITE\20200818_v3.0.0\data"

eventpaths = list(Path(DATADIR).glob("*recordtrigger*"))
physiopaths = list(Path(DATADIR).glob("*recordsignal*"))

idx = 3
EVENTPATH = eventpaths[idx]
PHYSPATH = physiopaths[idx]

data = read_raw_edf(PHYSPATH, preload=True)
resp = np.ravel(data.get_data(picks=0))

events = pd.read_csv(EVENTPATH, sep='\t')
events = event_utils.format_events(events)

# Original IBIs and associated samples. Multiple IBIs can be associated with
# the same sample since Polar belt can include multiple IBIs in a single notification.
ibis = event_utils.get_eventvalues(events, "InterBeatInterval")
ibis_samp = event_utils.get_eventtimes(events, "InterBeatInterval", as_sample=True)

ibis_corrected = hrv_utils.correct_ibis(ibis)
# Associate IBIs with a sample that represents the time of their occurence rather
# than the time of the Polar belt notification.
peaks_corrected = hrv_utils.ibis_to_rpeaks(ibis_corrected, events)

ibis_interpolated = hrv_utils.interpolate_ibis(peaks_corrected, ibis_corrected,
                                               np.arange(resp.size))

fig, (ax0, ax1, ax2, ax3) = plt.subplots(nrows=4, ncols=1, sharex=True)

ax0.scatter(ibis_samp, ibis, c="r")
ax0.plot(ibis_samp, ibis)
ax1.scatter(peaks_corrected, ibis_corrected, c="r")
ax1.plot(peaks_corrected, ibis_corrected)
ax2.plot(ibis_interpolated)
ax3.plot(resp)

plt.show()

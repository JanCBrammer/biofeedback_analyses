#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author: Jan C. Brammer <jan.c.brammer@gmail.com>
"""

import streamlit as st
import numpy as np
import pandas as pd
import numpy.ma as mask
from pathlib import Path
from biofeedback_analyses import resp_utils
from bokeh.plotting import figure
from bokeh.layouts import column
from biofeedback_analyses.app_config import (SFREQ, DATADIR_PROCESSED, SUBJECTS, SESSIONS)

st.beta_set_page_config(layout="wide")
st.title("Slow Breathing Intensity")


@st.cache
def median_inst_amp(paths):

    inst_amps = []

    for path in paths:

        data = pd.read_csv(path, sep="\t")
        inst_amp = np.ravel(data["inst_amp"])
        inst_amps.append(np.median(inst_amp))

    return np.mean(inst_amps)


subject = st.sidebar.selectbox("Select participant", SUBJECTS)

physiopaths = list(Path(f"{DATADIR_PROCESSED}/{subject}").glob(f"{subject}*biofeedback*"))

burst_threshold_low = median_inst_amp(physiopaths)
burst_threshold_high = st.sidebar.number_input("Upper burst threshold (x * median amplitude all session)",
                                               min_value=1., max_value=3., step=.5, value=1.5)
burst_threshold_high *= burst_threshold_low
burst_min_duration = st.sidebar.number_input("Minimum burst duration (seconds)", min_value=5, max_value=20, step=5)
burst_min_duration = int(np.rint(burst_min_duration * SFREQ))

plots = []
for i, session in enumerate(SESSIONS):    # plot all available sessions

    physiopath_session = [path for path in physiopaths if session in str(path)]
    if len(physiopath_session) != 1:
        continue

    title = str(physiopath_session[0].name[:22])
    if title[-1] == "A":
        title = title[:16] + "without_biofeedback"
    elif title[-1] == "B":
        title = title[:16] + "with_biofeedback"

    data = pd.read_csv(physiopath_session[0], sep="\t")
    resp_filt = np.ravel(data["resp_filt"])
    inst_amp = np.ravel(data["inst_amp"])
    sec = np.linspace(0, resp_filt.size / SFREQ, resp_filt.size)

    bursts = resp_utils.bursts_dual_threshold(inst_amp, burst_threshold_low,
                                              burst_threshold_high,
                                              min_duration=burst_min_duration)

    p = figure(tools="pan,box_zoom,wheel_zoom,reset", title=title,
               x_axis_label="Seconds", y_axis_label="Amplitude",
               plot_height=300, toolbar_location="right")
    p.line(sec, resp_filt, legend_label="breathing at 4 to 12 bpm")
    p.line(sec, inst_amp, line_color="orange", legend_label="instantaneous amplitude")
    p.line(mask.array(sec, mask=~bursts), mask.array(inst_amp, mask=~bursts),
           legend_label="bursts", line_color="red", line_width=3)    # mark bursts
    p.ray(x=0, y=burst_threshold_low, line_color="green",
          legend_label="median amplitude all sessions", line_width=2)
    p.ray(x=0, y=burst_threshold_high, line_color="green", line_dash="dashed",
          legend_label="upper burst threshold", line_width=3)

    p.legend.orientation = "horizontal"
    p.legend.location = "bottom_left"
    if i > 0:
        p.legend.visible = False

    plots.append(p)

st.bokeh_chart(column(*plots, sizing_mode="stretch_width"))

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author: Jan C. Brammer <jan.c.brammer@gmail.com>
"""

import streamlit as st
from pathlib import Path
from biopeaks.filters import moving_average
import pandas as pd
import numpy as np
from bokeh.plotting import figure
from bokeh.layouts import gridplot
from biofeedback_analyses.config import (DATADIR_PROCESSED, SUBJECTS, SESSIONS, SFREQ)
from biofeedback_analyses.biofeedback_utils import compute_biofeedback_score


st.beta_set_page_config(layout="wide")
st.title("Biofeedback Comparison")


def plot_dataset(original_resp_biofeedback_path,
                 ibis_path,
                 local_power_hrv_path,
                 local_power_hrv_target,
                 local_power_hrv_window):

    original_resp_biofeedback = np.ravel(pd.read_csv(original_resp_biofeedback_path,
                                                     sep="\t"))
    ibis = np.ravel(pd.read_csv(ibis_path, sep="\t"))
    local_power_hrv = np.ravel(pd.read_csv(local_power_hrv_path, sep="\t"))

    local_power_hrv_smooth = moving_average(local_power_hrv,
                                            local_power_hrv_window)
    local_power_hrv_biofeedback = compute_biofeedback_score(local_power_hrv_smooth,
                                                            local_power_hrv_target)

    sec = np.linspace(0, original_resp_biofeedback.size / SFREQ,
                      original_resp_biofeedback.size)

    plots = []

    p = figure(plot_height=150)
    p.line(sec[:ibis.size], ibis, legend_label="ibis", line_width=2,
           line_color="blue")
    p.xaxis.visible = False
    plots.append([p])

    p = figure(plot_height=150)
    p.line(sec[:local_power_hrv_smooth.size], local_power_hrv_smooth,
           legend_label="local_power_hrv_smooth", line_width=2,
           line_color="green")
    p.xaxis.visible = False
    plots.append([p])

    p = figure(plot_height=150)
    p.line(sec[:local_power_hrv_biofeedback.size], local_power_hrv_biofeedback,
           legend_label="local_power_hrv_biofeedback", line_width=2,
           line_color="orange")
    p.xaxis.visible = False
    plots.append([p])

    p = figure(plot_height=150)
    p.line(sec, original_resp_biofeedback,
           legend_label="original_resp_biofeedback", line_width=2,
           line_color="red")
    p.xaxis.axis_label = "Seconds"
    plots.append([p])

    for i, p in enumerate(plots):
        if i >= 1:
            p[0].x_range = plots[0][0].x_range    # link x-axes

    fig = gridplot(plots, sizing_mode="stretch_width")

    return fig


subject = st.sidebar.selectbox("Select participant", SUBJECTS)
session = st.sidebar.selectbox("Select session", SESSIONS)

window = st.sidebar.number_input("Local HRV power average window (sec)",
                                 min_value=1, max_value=15, step=1)
window = int(np.rint(window * SFREQ))
target = st.sidebar.number_input("Local HRV power target (msec)",
                                 min_value=25, max_value=250, step=10)

original_resp_biofeedback_path = list(Path(f"{DATADIR_PROCESSED}/{subject}").glob(f"{subject}_{session}*resp_biofeedback"))
ibis_path = list(Path(f"{DATADIR_PROCESSED}/{subject}").glob(f"{subject}_{session}*ibis"))
local_power_hrv_path = list(Path(f"{DATADIR_PROCESSED}/{subject}").glob(f"{subject}_{session}*hrv_biofeedback"))

fig = plot_dataset(*original_resp_biofeedback_path,
                   *ibis_path,
                   *local_power_hrv_path,
                   target, window)

st.bokeh_chart(fig)

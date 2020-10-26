#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author: Jan C. Brammer <jan.c.brammer@gmail.com>
"""

import streamlit as st
from pathlib import Path
import pandas as pd
import numpy as np
from bokeh.plotting import figure
from bokeh.layouts import gridplot
from bokeh.palettes import Colorblind as palette
from biofeedback_analyses import event_utils
from biofeedback_analyses.config import (DATADIR_PROCESSED, DATADIR_RAW,
                                         SUBJECTS, SESSIONS)


st.beta_set_page_config(layout="wide")
st.title("Raw Dataset Visualization")


def plot_dataset(biofeedback_path):

    biofeedback = pd.read_csv(biofeedback_path, sep="\t")
    sec = np.arange(biofeedback.shape[0])
    original_resp_biofeedback = np.ravel(biofeedback["original_resp_biofeedback"])
    local_power_hrv = np.ravel(biofeedback["local_power_hrv"])

    plots = []

    p = figure(plot_height=200)
    p.line(sec, original_resp_biofeedback, legend_label="original_resp_biofeedback")
    plots.append([p])

    p = figure(plot_height=200)
    p.line(sec, local_power_hrv, legend_label="local_power_hrv")
    plots.append([p])

    fig = gridplot(plots, sizing_mode="stretch_width")

    return fig


subject = st.sidebar.selectbox("Select participant", SUBJECTS)
session = st.sidebar.selectbox("Select session", SESSIONS)

biofeedback_path = list(Path(f"{DATADIR_PROCESSED}/{subject}").glob(f"{subject}_{session}*biofeedback*"))

if len(biofeedback_path) != 1 :
    raise IOError(f"{biofeedback_path}")

fig = plot_dataset(*biofeedback_path)

st.bokeh_chart(fig)

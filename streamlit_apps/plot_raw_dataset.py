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
from mne.io import read_raw_edf
from biofeedback_analyses import event_utils
from biofeedback_analyses.config import (DATADIR_PROCESSED, DATADIR_RAW,
                                         SUBJECTS, SESSIONS)


st.beta_set_page_config(layout="wide")
st.title("Raw Dataset Visualization")


def plot_dataset(physiopath, eventpath, physiochannels={}, continuous_events=[],
                 discrete_events=[]):
    """Visualize a dataset (recording session of one participant) consisting of
    an .edf file containing biosignal channel(s) and a .tsv file containing
    events that have been logged with Redis and synchronized with the
    biosignal(s).

    Parameters
    ----------
    physiopath : string, Path
        Path to .edf file containing the biosignal(s).
    eventpath : string, Path
        Path to .tsv file containing the events.
    physiochannels : dict, optional
        Dictionary containing the biosignals name as keys and corresponding
        channels (zero-based) as indices, by default {}
    continuous_events : list, optional
        List containing Redis keys of the events that will be plotted as
        continuous data streams alongside the biosignal(s), by default []
    discrete_events : list, optional
        List containing Redis keys of the events that will be plotted as
        vertical lines across all biosignal(s) and continuous events,
        by default []

    Returns
    -------
    Figure
    """
    data = read_raw_edf(physiopath, preload=True, verbose="error")
    sec = data.times
    events = pd.read_csv(eventpath, sep="\t")

    plots = []

    for name, idx in physiochannels.items():
        signal = np.ravel(data.get_data(picks=[idx]))
        p = figure(plot_height=200)
        p.line(sec, signal, legend_label=name)

        for name, color in zip(discrete_events, palette[8]):    # mark discrete events
            samp = event_utils.get_eventtimes(events, name, as_sample=True)
            p.ray(sec[samp], min(signal), length=0, angle=np.pi / 2,
                  color=color, line_width=2, legend_label=name)
        p.legend.orientation = "horizontal"
        p.legend.location = "top_left"
        plots.append([p])

    for name in continuous_events:
        samp = event_utils.get_eventtimes(events, name, as_sample=True)
        vals = event_utils.get_eventvalues(events, name)
        p = figure(plot_height=200, tools="pan,box_zoom,wheel_zoom,reset")
        p.scatter(sec[samp], vals, color="red", legend_label="sampling moments")
        p.line(sec[samp], vals, legend_label=name)

        for name, color in zip(discrete_events, palette[8]):    # mark discrete events
            samp = event_utils.get_eventtimes(events, name, as_sample=True)
            p.ray(sec[samp], min(vals), length=0, angle=np.pi / 2, color=color,
                  line_width=2)

        plots.append([p])

    for i, p in enumerate(plots):
        if i >= 1:
            p[0].x_range = plots[i - 1][0].x_range    # link x-axes
        if i != len(plots) - 1:
            p[0].xaxis.visible = False

    fig = gridplot(plots, sizing_mode="stretch_width")

    return fig


subject = st.sidebar.selectbox("Select participant", SUBJECTS)
session = st.sidebar.selectbox("Select session", SESSIONS)
continuous_events = st.sidebar.multiselect("Select continuous data streams",
                                           ["Feedback", "InterBeatInterval", "HeartRate"],
                                           ["Feedback", "InterBeatInterval"])
discrete_events = st.sidebar.multiselect("Select discrete events",
                                         ["GameStart", "LevelLoaded", "RadioStart", "WaveStart",
                                          "WaveSpawn", "RadioFinished", "ShotMissed", "ShotHit",
                                          "ZedApproached", "ZedCaptured", "GunReload", "WaveEnd",
                                          "RadioConfirm", "ZedAttack",
                                          "MarkerDispatchEvent-GlassPre2", "MarkerGlassBreak",
                                          "MarkerDispatchEvent-GlassPost1",
                                          "MarkerDispatchEvent-CarAlarmPre1",
                                          "MarkerDispatchEvent-CarAlarmPre2", "MarkerCarAlarmStart",
                                          "MarkerCarAlarmEnd", "RadioRequestRepeat",
                                          "MarkerDispatchEvent-CarAlarmPost1", "MarkerFireAlarmEnd",
                                          "MarkerFireAlarmStart", "GameEnd", "GameQuit"],
                                         ["WaveStart", "MarkerCarAlarmStart",
                                          "MarkerFireAlarmStart", "MarkerGlassBreak", "GameStart",
                                          "GameEnd"])

eventpath = list(Path(f"{DATADIR_PROCESSED}/{subject}").glob(f"{subject}_{session}*events*"))
physiopath = list(Path(f"{DATADIR_RAW}/{subject}").glob(f"{subject}_{session}*recordsignal*"))

if len(eventpath) != 1 or len(physiopath) != 1:
    raise IOError(f"{eventpath} {physiopath}")

fig = plot_dataset(*physiopath, *eventpath,
                   physiochannels={"Breathing": 0},
                   continuous_events=continuous_events,
                   discrete_events=discrete_events)

st.bokeh_chart(fig)

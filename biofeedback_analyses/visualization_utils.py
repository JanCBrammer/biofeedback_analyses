#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author: Jan C. Brammer <jan.c.brammer@gmail.com>
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from mne.io import read_raw_edf
from biofeedback_analyses import event_utils


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
    data = read_raw_edf(physiopath, preload=True)

    events = pd.read_csv(eventpath, sep='\t')
    events = event_utils.format_events(events)

    sec = data.times
    nrows = len(physiochannels) + len(continuous_events)
    fig, axes = plt.subplots(nrows=nrows, ncols=1, sharex=True)

    a = -1
    for name, idx in physiochannels.items():
        signal = np.ravel(data.get_data(picks=[idx]))
        a += 1
        ax = axes[a]
        ax.plot(sec, signal, c="k", label=name)
        ax.legend(loc="upper right")

    for name in continuous_events:
        samp = event_utils.get_eventtimes(events, name, as_sample=True)
        vals = event_utils.get_eventvalues(events, name)
        a += 1
        ax = axes[a]
        ax.scatter(sec[samp], vals, c="r", label="sampling moments")
        ax.plot(sec[samp], vals, c="k", label=name)
        ax.legend(loc="upper right")
    ax.set_xlabel("Seconds")    # x label only for last axes

    colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    for ax in axes:    # overlay discrete events over all continuous axes
        ymin, ymax = ax.get_ylim()
        for (name, color) in zip(discrete_events, colors):
            samp = event_utils.get_eventtimes(events, name, as_sample=True)
            ax.vlines(sec[samp], ymin=ymin, ymax=ymax, colors=color, alpha=.5)

    # Create custom legend for discrete events and add to figure instead of axes.
    labellines = []
    for (name, color) in zip(discrete_events, colors):
        labellines.append(mlines.Line2D([], [], color=color, label=name))
    fig.legend(handles=labellines, loc="upper right", title="Events")

    return fig

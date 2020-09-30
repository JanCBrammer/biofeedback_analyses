#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author: Jan C. Brammer <jan.c.brammer@gmail.com>
"""

import streamlit as st
from bokeh.plotting import figure
from bokeh.layouts import row, column
from bokeh.models import CDSView, ColumnDataSource, GroupFilter
from bokeh.transform import jitter, factor_cmap, factor_mark
import pandas as pd
from pathlib import Path
from biofeedback_analyses.config import DATADIR_PROCESSED, SUBJECTS


st.beta_set_page_config(layout="wide")
st.title("ABAB Progression")

summary_path = Path(DATADIR_PROCESSED).joinpath("summary_all_subjects")
tools = "pan,box_zoom,wheel_zoom,reset"
sessions = [f"sess-{str(i).zfill(2)}" for i in range(1, 11)]
conditions = ["cond-A", "cond-B"]
markers = factor_mark("cond", ["circle", "square"], conditions)
colors = factor_cmap("cond", ["lightsalmon", "deepskyblue"], conditions)


@st.cache
def load_data(path):

    print("Loading data!")
    df_summary = pd.read_csv(path, sep="\t")

    return df_summary


def instantiate_plots(src):

    plots = []
    series = {}
    aggregates = {}
    for c in src.column_names[4:]:    # instantiate plots
        serie = figure(plot_height=300, plot_width=750, title=c,
                       x_range=sessions, tools=tools)
        series[c] = serie
        aggregate = figure(plot_height=300, plot_width=250, x_range=conditions,
                           tools=tools)
        aggregates[c] = aggregate
        plots.append(row(serie, aggregate))

    return plots, series, aggregates


def populate_plots(src, series, aggregates):

    subjects = {}

    for subj in SUBJECTS:

        view = CDSView(source=src, filters=[GroupFilter(column_name="subj",
                                                        group=subj)])

        glyphs = []
        for c in src.column_names[4:]:    # populate plots

            serie_line = series[c].line(x="sess", y=c, source=src, view=view,
                                        muted_color="gray", muted_alpha=.2)

            serie_scatter = series[c].scatter(x="sess", y=c, source=src,
                                              view=view, size=15,
                                              marker=markers, color=colors, alpha=.5,
                                              muted_color="gray", muted_alpha=.2)
            aggregate_scatter = aggregates[c].scatter(x=jitter("cond", width=.4, range=aggregates[c].x_range), y=c,
                                                      source=src, view=view,
                                                      size=15, marker=markers,
                                                      color=colors, alpha=.5,
                                                      muted_color="gray", muted_alpha=.2)
            glyphs.append(serie_line)
            glyphs.append(serie_scatter)
            glyphs.append(aggregate_scatter)

        subjects[subj] = glyphs

    return subjects


def toggle_mute(subj, unmuted):

    for i in subjects[subj]:    # iterate over all glyphs of a given subject

        i.update(muted=not unmuted)


df = load_data(summary_path)
src = ColumnDataSource(df)
plots, series, aggregates = instantiate_plots(src)
subjects = populate_plots(src, series, aggregates)

unmuted = {}
for subj in SUBJECTS:
    unmuted[subj] = st.sidebar.checkbox(subj, value=True)

for key, val in unmuted.items():
    toggle_mute(key, val)

st.bokeh_chart(column(*plots))

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
tools = "pan,box_zoom,wheel_zoom,reset,box_select"

summary_path = Path(DATADIR_PROCESSED).joinpath("summary_all_subjects")
df_summary = pd.read_csv(summary_path, sep="\t")    # raises if file doesn't exist
src = ColumnDataSource(df_summary)

sessions = [f"sess-{str(i).zfill(2)}" for i in range(1, 11)]
conditions = ["cond-A", "cond-B"]
markers = factor_mark("cond", ["circle", "square"], conditions)
colors = factor_cmap("cond", ["lightsalmon", "deepskyblue"], conditions)

series = {}
aggregates = {}
plots = []
for c in src.column_names[4:]:
    serie = figure(plot_height=300, plot_width=750, title=c, x_range=sessions,
                   tools=tools)
    aggregate = figure(plot_height=300, plot_width=250, x_range=conditions,
                       tools=tools)
    series[c] = serie
    aggregates[c] = aggregate
    plots.append(row(serie, aggregate))

views = {}
for subj in SUBJECTS:

    views[subj] = CDSView(source=src, filters=[GroupFilter(column_name="subj",
                                                           group=subj)])
    for c in src.column_names[4:]:

        series[c].line(x="sess", y=c, source=src, view=views[subj])
        series[c].scatter(x="sess", y=c, source=src, view=views[subj], size=15,
                          marker=markers, color=colors, muted_alpha=0.2)

        aggregates[c].scatter(x="cond", y=jitter(c, width=1,
                                                 range=aggregates[c].x_range),
                              source=src, view=views[subj], size=15,
                              marker=markers, color=colors, alpha=.5)

st.bokeh_chart(column(*plots))

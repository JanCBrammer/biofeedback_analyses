#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author: Jan C. Brammer <jan.c.brammer@gmail.com>
"""

import hashlib
import dabest
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D
from config import DATA_HASH

sns.set_theme()


def validate_summary_data(subject, inputs, outputs, recompute):
    """Match the summary statistics which have been computed during this run of
    the analysis pipeline against the original summary statistics which have
    been used to render Figures 2 and 3 in doi.org/10.3389/fpsyg.2021.586553."""

    root = inputs["summary_path"][0]
    filename = inputs["summary_path"][1]
    summary_path = root.joinpath(filename)

    h = hashlib.new("md5")
    with open(summary_path, "rb") as file:
        block = file.read(512)
        while block:
            h.update(block)
            block = file.read(512)

    assert h.hexdigest() == DATA_HASH, f"The content of {summary_path} doesn't match the original data."


def plot_figure_2(subject, inputs, outputs, recompute):

    root = inputs["summary_path"][0]
    filename = inputs["summary_path"][1]
    summary_path = root.joinpath(filename)

    root = outputs["save_path"][0]
    filename = outputs["save_path"][1]
    save_path = root.joinpath(filename)

    df = pd.read_csv(summary_path, sep='\t')

    fig = plt.figure(figsize=(7, 5))

    gs = GridSpec(2, 3, figure=fig)
    ax0 = fig.add_subplot(gs[0, :2])
    ax1 = fig.add_subplot(gs[1, :2])
    ax2 = fig.add_subplot(gs[:, 2])


    sns.lineplot(x="sess", y="mean_resp_rate", hue="subj", data=df, ax=ax0,
                linewidth=1.5)
    sns.scatterplot(data=df, x="sess", y="mean_resp_rate", style="cond", ax=ax0,
                    s=55, zorder=3)

    participant_legend_entries = []
    participant_labels = [str(i) for i in range(1, 10)]
    participant_colors = sns.color_palette(n_colors=9)
    for label, color in zip(participant_labels, participant_colors):
        participant_legend_entries.append(Line2D([], [], color=color, label=label,
                                                linewidth=1.5))

    participant_legend = ax0.legend(handles=participant_legend_entries,
                                    bbox_to_anchor=(1, 1), loc="upper right",
                                    frameon=True, fontsize="xx-small", ncol=5,
                                    columnspacing=1, title="participant",
                                    facecolor="w")
    plt.setp(participant_legend.get_title(), fontsize="xx-small")
    participant_legend._legend_box.align = "left"
    ax0.add_artist(participant_legend)

    condition_legend_entries = []
    condition_labels = ["biofeedback", "no biofeedback"]
    condition_markers = ["X", "o"]
    for label, marker in zip(condition_labels, condition_markers):
        condition_legend_entries.append(Line2D([0], [0], marker=marker, color="w",
                                            label=label, markerfacecolor="b",
                                            markersize=7.5))
    condition_legend = ax0.legend(handles=condition_legend_entries,
                                bbox_to_anchor=(.375, 1), loc="upper right",
                                frameon=True, fontsize="xx-small", ncol=1,
                                handletextpad=0, title="condition",
                                facecolor="w")
    plt.setp(condition_legend.get_title(), fontsize="xx-small")
    condition_legend._legend_box.align = "left"
    ax0.add_artist(condition_legend)

    ax0.xaxis.set_ticklabels([])
    ax0.tick_params(axis="both", which="major", labelsize="medium")
    ax0.set_xlabel("")
    ax0.set_ylabel("mean breathing rate", fontsize="medium", fontweight="bold")


    sns.lineplot(x="sess", y="mean_original_resp_biofeedback", hue="subj", data=df,
                ax=ax1, linewidth=1.5)
    sns.scatterplot(data=df, x="sess", y="mean_original_resp_biofeedback",
                    style="cond", ax=ax1, s=55, zorder=3)

    ax1.set_xticklabels([str(i) for i in range(1, 11)])
    ax1.tick_params(axis="both", which="major", labelsize="medium")
    ax1.set_xlabel("training session", fontsize="medium", fontweight="bold")
    ax1.set_ylabel("mean biofeedback score", fontsize="medium", fontweight="bold")
    ax1.legend().remove()

    ax1.set_ylim(-.05, 1.05)


    # CORRELATION ##################################################################
    sns.scatterplot(data=df, x="mean_resp_rate", y="mean_original_resp_biofeedback",
                    hue="sess", ax=ax2, s=60, alpha=.6)
    sns.regplot(x="mean_resp_rate", y="mean_original_resp_biofeedback",
                data=df, order=2, scatter=False, ax=ax2)

    ax2.set_ylim(-.05, 1.05)
    ax2.set_xlim(5, 32)

    session_labels = [str(i) for i in range(1, 11)]
    session_colors = sns.color_palette(n_colors=10)
    session_legend_entries = []
    for label, color in zip(session_labels, session_colors):
        scatter = plt.scatter(0, 0, color=color, label=label)
        session_legend_entries.append(scatter)
    session_legend = ax2.legend(handles=session_legend_entries,
            bbox_to_anchor=(1, 1), loc="upper right", frameon=True,
            fontsize="xx-small", ncol=1, columnspacing=0,
            title="training\nsession", facecolor="w")
    plt.setp(session_legend.get_title(), fontsize="xx-small")

    ax2.tick_params(axis="both", which="major", labelsize="medium")
    ax2.set_xlabel("mean breathing rate", fontsize="medium", fontweight="bold")
    ax2.set_ylabel("mean biofeedback score", fontsize="medium", fontweight="bold")

    ax0.text(ax0.get_xbound()[0] - 2, ax0.get_ybound()[-1], "(A)", fontsize="large",
            fontweight="medium")
    ax2.text(ax2.get_xbound()[0] - 12.5, ax2.get_ybound()[-1], "(B)", fontsize="large",
            fontweight="medium")

    plt.subplots_adjust(wspace=.5, hspace=.05)
    fig.savefig(save_path, bbox_inches="tight", dpi=300)


def plot_figure_3(subject, inputs, outputs, recompute):

    root = inputs["summary_path"][0]
    filename = inputs["summary_path"][1]
    summary_path = root.joinpath(filename)

    root = outputs["save_path"][0]
    filename = outputs["save_path"][1]
    save_path = root.joinpath(filename)

    df = pd.read_csv(summary_path, sep='\t')

    fig, (ax0, ax1) = plt.subplots(nrows=2, ncols=1, figsize=(3.3, 7))

    est = dabest.load(df, idx=("cond-A", "cond-B"), x="cond", y="mean_resp_rate")
    n_nobiofeedback = est.data.loc[est.data["cond"] == "cond-A", "mean_resp_rate"].count()
    n_biofeedback = est.data.loc[est.data["cond"] == "cond-B", "mean_resp_rate"].count()
    est.mean_diff.plot(color_col="sess", ax=ax0, custom_palette="tab10",
                        raw_marker_size=6)
    ax0.set_xticklabels([f"no biofeedback\nN={n_nobiofeedback}",
                            f"biofeedback\nN={n_biofeedback}"])
    ax0.contrast_axes.set_xticklabels(["", "biofeedback\nminus\nno biofeedback"])
    ax0.contrast_axes.legend().remove()

    session_labels = [str(i) for i in range(1, 11)]
    session_colors = sns.color_palette(n_colors=10)
    session_legend_entries = []
    for label, color in zip(session_labels, session_colors):
        scatter = plt.scatter(0, 0, color=color, label=label)
        session_legend_entries.append(scatter)

    ax0.legend(handles=session_legend_entries,
                bbox_to_anchor=(0, 1), loc="lower left",
                frameon=True, fontsize="x-small", ncol=10,
                columnspacing=1, title="training session",
                title_fontsize="x-small",facecolor="w",
                handletextpad=0)


    est = dabest.load(df, idx=("cond-A", "cond-B"), x="cond", y="mean_original_resp_biofeedback")
    n_nobiofeedback = est.data.loc[est.data["cond"] == "cond-A", "mean_original_resp_biofeedback"].count()
    n_biofeedback = est.data.loc[est.data["cond"] == "cond-B", "mean_original_resp_biofeedback"].count()
    est.mean_diff.plot(color_col="sess", ax=ax1, custom_palette="tab10",
                        raw_marker_size=6, swarm_ylim=(-0.05, 1))
    ax1.set_xticklabels([f"no biofeedback\nN={n_nobiofeedback}",
                            f"biofeedback\nN={n_biofeedback}"])
    ax1.contrast_axes.set_xticklabels(["", "biofeedback\nminus\nno biofeedback"])
    ax1.contrast_axes.legend().remove()


    ax0.set_ylabel("mean breathing rate", fontsize="large", fontweight="bold")
    ax1.set_ylabel("mean biofeedback score", fontsize="large", fontweight="bold")
    ax0.contrast_axes.set_ylabel("mean difference")
    ax1.contrast_axes.set_ylabel("mean difference")


    ax0.text(ax0.get_xbound()[0] - .4, ax0.get_ybound()[-1] + .1, "(A)", fontsize="large",
            fontweight="medium")
    ax1.text(ax1.get_xbound()[0] - .4, ax1.get_ybound()[-1] + .1, "(B)", fontsize="large",
            fontweight="medium")

    plt.subplots_adjust(wspace=None, hspace=.3)
    fig.savefig(save_path, bbox_inches="tight", dpi=300)

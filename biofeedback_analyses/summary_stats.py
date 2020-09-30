#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author: Jan C. Brammer <jan.c.brammer@gmail.com>
"""

import numpy as np
import pandas as pd
from itertools import product
from pathlib import Path
from mne.io import read_raw_edf
from biofeedback_analyses import resp_utils, hrv_utils, event_utils
from biofeedback_analyses.config import SUBJECTS, SESSIONS, SFREQ


def get_row_idx(path, df):

    path = str(path)

    subj_stridx = path.index("subj-")
    subj = path[subj_stridx:subj_stridx + 7]
    sess_stridx = path.index("sess-")
    sess = path[sess_stridx:sess_stridx + 7]
    cond_stridx = path.index("cond-")
    cond = path[cond_stridx:cond_stridx + 6]
    row_idx = ((df["subj"] == subj) &
               (df["sess"] == sess) &
               (df["cond"] == cond))
    if sum(row_idx) != 1:
        raise IndexError

    return np.where(row_idx)[0]


def summary_instantiate(subject, inputs, outputs, recompute):

    root = outputs["save_path"][0]
    filename = outputs["save_path"][1]
    save_path = Path(root).joinpath(filename)

    computed = save_path.exists()   # Boolean indicating if file already exists.
    if computed and not recompute:    # only recompute if requested
        print(f"Not overwriting {save_path}.")
        return

    rows = list(product(SUBJECTS, SESSIONS))
    subjects = [row[0] for row in rows]
    sessions = [row[1][:7] for row in rows]
    conditions = [row[1][-6:] for row in rows]

    d = {"subj": subjects, "sess": sessions, "cond": conditions,
         "median_resp_amp": "", "median_resp_rate": "",
         "normalized_median_resp_power": "", "n_bursts": "",
         "mean_duration_bursts": "", "std_duration_bursts": "",
         "percent_bursts": "", "hrv_lf": "", "hrv_hf": "", "hrv_vlf": "",
         "hrv_lf_hf_ratio": "", "hrv_lf_nu": "", "hrv_hf_nu": "",
         "median_heart_period": ""}
    df = pd.DataFrame(data=d)
    df.to_csv(save_path, sep="\t", index=False)

    print(f"Saved {save_path}")


def summary_resp(subject, inputs, outputs, recompute):

    root = outputs["save_path"][0]
    filename = outputs["save_path"][1]
    save_path = Path(root).joinpath(f"{filename}")
    df_summary = pd.read_csv(save_path, sep="\t")    # raises if file doesn't exist

    root = inputs["physio_path"][0]
    filename = inputs["physio_path"][1]
    physio_paths = list(Path(root).joinpath(subject).glob(f"{subject}{filename}"))

    root = inputs["event_path"][0]
    filename = inputs["event_path"][1]
    event_paths = list(Path(root).joinpath(subject).glob(f"{subject}{filename}"))

    if not physio_paths:
        print(f"No files found for {subject}.")
        return

    for i, physio_path in enumerate(physio_paths):

        row_idx = get_row_idx(physio_path, df_summary)
        columns = ["median_resp_amp", "median_resp_rate"]
        computed = df_summary.loc[row_idx, columns].isna().values.sum() != len(columns)   # skip if all columns contain NaN (make sure to reserve NaN as place-holder for non-computed results)
        if computed and not recompute:
            print(f"Not re-computing {physio_path}.")
            if i < len(physio_paths) - 1:    # make sure to save updates only when values have been (re-) computed
                continue
            else:
                return

        # Find corresponding event_path
        event_path_idx = [i for i, j in enumerate(event_paths) if str(j.name)[:21] == str(physio_path.name)[:21]]
        if len(event_path_idx) != 1:
            print(f"Didn't find matching events for {physio_path.name}.")
            continue
        event_path = event_paths[event_path_idx[0]]
        events = pd.read_csv(event_path, sep='\t')

        data_raw = read_raw_edf(physio_path, preload=True, verbose="error")
        resp = np.ravel(data_raw.get_data(picks=[0]))

        beg = event_utils.get_eventtimes(events, "GameStart", as_sample=True)
        end = event_utils.get_eventtimes(events, "GameEnd", as_sample=True)
        if len(beg) < 1:
            print(f"Didn't find 'GameStart' event for {event_path.name}.")
            continue
        if len(beg) > 1:
            print(f"Found {len(beg)} 'GameStart' events for {event_path.name}.")
            beg = [beg[-1]]    # game was restarted, pick latest start
        if len(end) != 1:
            print(f"Found {len(end)} events matching 'GameEnd' for {event_path.name}.")
            continue
        beg, end = *beg, *end
        resp_game = resp[beg:end]
        resp_stats = resp_utils.compute_resp_stats(resp_game, SFREQ)

        for key, value in resp_stats.items():
            df_summary.loc[row_idx, key] = value

        df_summary.to_csv(save_path, sep="\t", index=False)
        print(f"Updated {save_path} with {physio_path}.")


def summary_biofeedback(subject, inputs, outputs, recompute):

    root = outputs["save_path"][0]
    filename = outputs["save_path"][1]
    save_path = Path(root).joinpath(f"{filename}")
    df_summary = pd.read_csv(save_path, sep="\t")    # raises if file doesn't exist

    root = inputs["physio_path"][0]
    filename = inputs["physio_path"][1]
    physio_paths = list(Path(root).joinpath(subject).glob(f"{subject}{filename}"))

    root = inputs["event_path"][0]
    filename = inputs["event_path"][1]
    event_paths = list(Path(root).joinpath(subject).glob(f"{subject}{filename}"))

    if not physio_paths:
        print(f"No files found for {subject}.")
        return

    burst_threshold_low = resp_utils.median_inst_amp(physio_paths)
    burst_threshold_high = 1.5 * burst_threshold_low
    burst_min_duration = int(np.rint(10 * SFREQ))

    for i, physio_path in enumerate(physio_paths):

        row_idx = get_row_idx(physio_path, df_summary)
        columns = ["normalized_median_resp_power", "n_bursts",
                   "mean_duration_bursts", "std_duration_bursts", "percent_bursts"]
        computed = df_summary.loc[row_idx, columns].isna().values.sum() != len(columns)   # skip if all columns contain NaN (make sure to reserve NaN as place-holder for non-computed results)
        if computed and not recompute:
            print(f"Not re-computing {physio_path}.")
            if i < len(physio_paths) - 1:    # make sure to save updates only when values have been (re-) computed
                continue
            else:
                return

        # Find corresponding event_path
        event_path_idx = [i for i, j in enumerate(event_paths) if str(j.name)[:21] == str(physio_path.name)[:21]]
        if len(event_path_idx) != 1:
            print(f"Didn't find matching events for {physio_path.name}.")
            continue
        event_path = event_paths[event_path_idx[0]]
        events = pd.read_csv(event_path, sep='\t')

        data = pd.read_csv(physio_path, sep="\t")
        inst_amp = np.ravel(data["inst_amp"])
        beg = event_utils.get_eventtimes(events, "GameStart", as_sample=True)
        end = event_utils.get_eventtimes(events, "GameEnd", as_sample=True)
        if len(beg) < 1:
            print(f"Didn't find 'GameStart' event for {event_path.name}.")
            continue
        if len(beg) > 1:
            print(f"Found {len(beg)} 'GameStart' events for {event_path.name}.")
            beg = [beg[-1]]    # game was restarted, pick latest start
        if len(end) != 1:
            print(f"Found {len(end)} events matching 'GameEnd' for {event_path.name}.")
            continue
        beg, end = *beg, *end
        inst_amp_game = inst_amp[beg:end]

        bursts = resp_utils.bursts_dual_threshold(inst_amp_game, burst_threshold_low,
                                                  burst_threshold_high,
                                                  min_duration=burst_min_duration)

        burst_stats = resp_utils.compute_burst_stats(bursts, SFREQ)
        for key, value in burst_stats.items():
            df_summary.loc[row_idx, key] = value

        biofeedback_stats = resp_utils.compute_biofeedback_stats(inst_amp_game,
                                                                 normalize_by=burst_threshold_low)
        for key, value in biofeedback_stats.items():
            df_summary.loc[row_idx, key] = value

        df_summary.to_csv(save_path, sep="\t", index=False)
        print(f"Updated {save_path} with {physio_path}.")


def summary_heart(subject, inputs, outputs, recompute):

    root = outputs["save_path"][0]
    filename = outputs["save_path"][1]
    save_path = Path(root).joinpath(f"{filename}")
    df_summary = pd.read_csv(save_path, sep="\t")    # raises if file doesn't exist

    root = inputs["physio_path"][0]
    filename = inputs["physio_path"][1]
    physio_paths = list(Path(root).joinpath(subject).glob(f"{subject}{filename}"))

    root = inputs["event_path"][0]
    filename = inputs["event_path"][1]
    event_paths = list(Path(root).joinpath(subject).glob(f"{subject}{filename}"))

    if not physio_paths:
        print(f"No files found for {subject}.")
        return

    for i, physio_path in enumerate(physio_paths):

        row_idx = get_row_idx(physio_path, df_summary)
        columns = ["hrv_lf", "hrv_hf", "hrv_vlf", "hrv_lf_hf_ratio",
                   "hrv_lf_nu", "hrv_hf_nu", "median_heart_period"]
        computed = df_summary.loc[row_idx, columns].isna().values.sum() != len(columns)   # skip if all columns contain NaN (make sure to reserve NaN as place-holder for non-computed results)
        if computed and not recompute:
            print(f"Not re-computing {physio_path}.")
            if i < len(physio_paths) - 1:    # make sure to save updates only when values have been (re-) computed
                continue
            else:
                return

        # Find corresponding event_path
        event_path_idx = [i for i, j in enumerate(event_paths) if str(j.name)[:21] == str(physio_path.name)[:21]]
        if len(event_path_idx) != 1:
            print(f"Didn't find matching events for {physio_path.name}.")
            continue
        event_path = event_paths[event_path_idx[0]]
        events = pd.read_csv(event_path, sep='\t')

        data = pd.read_csv(physio_path, sep="\t")
        ibis = np.ravel(data)
        beg = event_utils.get_eventtimes(events, "GameStart", as_sample=True)
        end = event_utils.get_eventtimes(events, "GameEnd", as_sample=True)
        if len(beg) < 1:
            print(f"Didn't find 'GameStart' event for {event_path.name}.")
            continue
        if len(beg) > 1:
            print(f"Found {len(beg)} 'GameStart' events for {event_path.name}.")
            beg = [beg[-1]]    # game was restarted, pick latest start
        if len(end) != 1:
            print(f"Found {len(end)} events matching 'GameEnd' for {event_path.name}.")
            continue
        beg, end = *beg, *end
        ibis_game = ibis[beg:end]

        hrv_stats = hrv_utils.compute_hrv_stats(ibis_game, SFREQ)

        for key, value in hrv_stats.items():
            df_summary.loc[row_idx, key] = value

        df_summary.to_csv(save_path, sep="\t", index=False)
        print(f"Updated {save_path} with {physio_path}.")

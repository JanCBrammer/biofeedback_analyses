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
from biofeedback_analyses import event_utils, resp_utils, hrv_utils
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
        return

    rows = list(product(SUBJECTS, SESSIONS))
    subjects = [row[0] for row in rows]
    sessions = [row[1][:7] for row in rows]
    conditions = [row[1][-6:] for row in rows]

    d = {"subj": subjects, "sess": sessions, "cond": conditions,
         "median_resp_amp": "", "median_resp_rate": ""}
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
    physio_paths = Path(root).joinpath(subject).glob(f"{subject}{filename}")

    for physio_path in physio_paths:

        data_raw = read_raw_edf(physio_path, preload=True, verbose="error")
        resp = np.ravel(data_raw.get_data(picks=[0]))
        resp_stats = resp_utils.compute_resp_stats(resp, SFREQ)

        row_idx = get_row_idx(physio_path, df_summary)

        for key, value in resp_stats.items():
            df_summary.loc[row_idx, key] = value

    df_summary.to_csv(save_path, sep="\t", index=False)

    print(f"Saved {save_path}")


def summary_heart(subject, inputs, outputs, recompute):
    pass


def summary_biofeedback(subject, inputs, outputs, recompute):
    pass

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author: Jan C. Brammer <jan.c.brammer@gmail.com>
"""

import pandas as pd
from itertools import product
from config import SUBJECTS, SESSIONS
from pathlib import Path
from preprocessing.pipeline import pipeline as preprocessing_pipeline
from summary_stats.pipeline import pipeline as summary_stats_pipeline


def setup_directories():

    WORKDIR = Path.cwd()

    DATADIR_RAW = WORKDIR.joinpath("raw")
    if not DATADIR_RAW.is_dir():
        print("Couldn't find \"raw\" data directory.")
        return

    DATADIR_PROCESSED = WORKDIR.joinpath("processed")
    try:
        DATADIR_PROCESSED.mkdir()
    except FileExistsError as _:
        print("Found existing \"processed\" directory during initialization."
              "Please remove or move the existing \"processed\" directory.")
    for subject in SUBJECTS:
        DATADIR_PROCESSED.joinpath(subject).mkdir()

    print(f"Instantiated directory for processed data at {DATADIR_PROCESSED}.")

    return DATADIR_RAW, DATADIR_PROCESSED


def setup_summary(DATADIR_PROCESSED):

    save_path = DATADIR_PROCESSED.joinpath("summary_all_subjects")

    if save_path.exists():
        print(f"Foud existing {save_path}. Please remove or move the existing file at {save_path}.")
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
         "median_heart_period": "", "coherence_lf": "", "coherence_hf": "",
         "median_original_resp_biofeedback": "", "median_local_power_hrv": "",
         "mean_original_resp_biofeedback": "", "mean_local_power_hrv": "",
         "rmssd": "", "mean_resp_rate": ""}
    df = pd.DataFrame(data=d)
    df.to_csv(save_path, sep="\t", index=False)

    print(f"Instantiated summary file at {save_path}.")


def run(pipeline):

    for task in pipeline:

        for subject in task["subjects"]:

            task["func"](subject,
                         task["inputs"],
                         task["outputs"],
                         task["recompute"])


def main():
    """Command line entry point."""
    print("Setting up directories.")
    DATADIR_RAW, DATADIR_PROCESSED = setup_directories()
    print("Running data processing pipeline.")
    run(preprocessing_pipeline(SUBJECTS, DATADIR_RAW, DATADIR_PROCESSED))
    setup_summary(DATADIR_PROCESSED)
    run(summary_stats_pipeline(SUBJECTS, DATADIR_RAW, DATADIR_PROCESSED))


if __name__ == "__main__":
    main()

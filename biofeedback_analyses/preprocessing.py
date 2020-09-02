#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author: Jan C. Brammer <jan.c.brammer@gmail.com>
"""

import pandas as pd
import numpy as np
from pathlib import Path
from mne.io import read_raw_edf
from biofeedback_analyses import event_utils, resp_utils, hrv_utils


def preprocess_events(subject, inputs, outputs, recompute):

    root = inputs["event_path"][0]
    subdir = inputs["event_path"][1]
    filename = inputs["event_path"][2]
    event_paths = Path(root).joinpath(f"{subdir}/{subject}").glob(filename)

    for event_path in event_paths:

        root = outputs["save_path"][0]
        subdir = outputs["save_path"][1]
        subj_sess_cond = event_path.name[:23]
        filename = f"{subj_sess_cond}{outputs['save_path'][2]}"
        save_path = Path(root).joinpath(f"{subdir}/{subject}/{filename}")

        computed = save_path.exists()   # Boolean indicating if file already exists.
        if computed and not recompute:    # only recompute if requested
            continue

        events = pd.read_csv(event_path, sep='\t')
        events = event_utils.format_events(events)

        events.to_csv(save_path, sep="\t", index=False)
        print(f"Saved {save_path}")


def preprocess_ibis(subject, inputs, outputs, recompute):

    root = inputs["event_path"][0]
    subdir = inputs["event_path"][1]
    filename = inputs["event_path"][2]
    event_paths = list(Path(root).joinpath(f"{subdir}/{subject}").glob(filename))

    root = inputs["physio_path"][0]
    subdir = inputs["physio_path"][1]
    filename = inputs["physio_path"][2]
    physio_paths = list(Path(root).joinpath(f"{subdir}/{subject}").glob(filename))

    assert len(event_paths) == len(physio_paths)

    for physio_path, event_path in zip(physio_paths, event_paths):
        # Make sure that the two paths pertain to the same recording.
        physio_name = physio_path.name
        event_name = event_path.name
        assert physio_name[:23] == event_name[:23]

        root = outputs["save_path"][0]
        subdir = outputs["save_path"][1]
        subj_sess_cond = physio_path.name[:23]
        filename = f"{subj_sess_cond}{outputs['save_path'][2]}"
        save_path = Path(root).joinpath(f"{subdir}/{subject}/{filename}")

        computed = save_path.exists()   # Boolean indicating if file already exists.
        if computed and not recompute:    # only recompute if requested
            continue

        data = read_raw_edf(physio_path, preload=True, verbose="error")
        resp = np.ravel(data.get_data(picks=0))

        events = pd.read_csv(event_path, sep='\t')

        # Original IBIs and associated samples. Multiple IBIs can be associated with
        # the same sample since Polar belt can include multiple IBIs in a single notification.
        ibis = event_utils.get_eventvalues(events, "InterBeatInterval")

        ibis_corrected = hrv_utils.correct_ibis(ibis)
        # Associate IBIs with a sample that represents the time of their occurence rather
        # than the time of the Polar belt notification.
        peaks_corrected = hrv_utils.ibis_to_rpeaks(ibis_corrected, events)

        ibis_interpolated = hrv_utils.interpolate_ibis(peaks_corrected,
                                                       ibis_corrected,
                                                       np.arange(resp.size))

        pd.Series(ibis_interpolated).to_csv(save_path, sep="\t", header=False,
                                            index=False, float_format="%.4f")
        print(f"Saved {save_path}")


def preprocess_biofeedback(subject, inputs, outputs, recompute):

    root = inputs["physio_path"][0]
    subdir = inputs["physio_path"][1]
    filename = inputs["physio_path"][2]
    physio_paths = Path(root).joinpath(f"{subdir}/{subject}").glob(filename)

    for physio_path in physio_paths:

        root = outputs["save_path"][0]
        subdir = outputs["save_path"][1]
        subj_sess_cond = physio_path.name[:23]
        filename = f"{subj_sess_cond}{outputs['save_path'][2]}"
        save_path = Path(root).joinpath(f"{subdir}/{subject}/{filename}")

        computed = save_path.exists()   # Boolean indicating if file already exists.
        if computed and not recompute:    # only recompute if requested
            continue

        data = read_raw_edf(physio_path, preload=True, verbose="error")
        resp = np.ravel(data.get_data(picks=0))
        sfreq = data.info["sfreq"]

        resp_filt = resp_utils.biofeedback_filter(resp, sfreq)
        inst_amp = resp_utils.instantaneous_amplitude(resp_filt)

        pd.DataFrame({"resp_filt": resp_filt,
                      "inst_amp": inst_amp}).to_csv(save_path, sep="\t",
                                                    header=True, index=False,
                                                    float_format="%.4f")
        print(f"Saved {save_path}")

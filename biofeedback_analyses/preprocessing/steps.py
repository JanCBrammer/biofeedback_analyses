#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author: Jan C. Brammer <jan.c.brammer@gmail.com>
"""

import pandas as pd
import numpy as np
from mne.io import read_raw_edf
from biofeedback_analyses.analysis_utils import event_utils, resp_utils, hrv_utils, biofeedback_utils


def preprocess_events(subject, inputs, outputs, recompute):

    root = inputs["event_path"][0]
    filename = inputs["event_path"][1]
    event_paths = root.joinpath(subject).glob(filename)

    for event_path in event_paths:

        root = outputs["save_path"][0]
        subj_sess_cond = event_path.name[:23]
        filename = f"{subj_sess_cond}{outputs['save_path'][1]}"
        save_path = root.joinpath(f"{subject}/{filename}")

        computed = save_path.exists()   # Boolean indicating if file already exists.
        if computed and not recompute:    # only recompute if requested
            continue

        events = pd.read_csv(event_path, sep='\t')
        events = event_utils.format_events(events)

        events.to_csv(save_path, sep="\t", index=False)
        print(f"Saved {save_path}")


def preprocess_ibis(subject, inputs, outputs, recompute):

    root = inputs["event_path"][0]
    filename = inputs["event_path"][1]
    event_paths = list(root.joinpath(subject).glob(filename))

    for event_path in event_paths:

        root = outputs["save_path"][0]
        subj_sess_cond = event_path.name[:23]
        filename = f"{subj_sess_cond}{outputs['save_path'][1]}"
        save_path = root.joinpath(f"{subject}/{filename}")

        computed = save_path.exists()   # Boolean indicating if file already exists.
        if computed and not recompute:    # only recompute if requested
            continue

        events = pd.read_csv(event_path, sep='\t')

        # Multiple IBIs can be associated with the same sample since Polar belt can include multiple IBIs in a single notification.
        ibis = event_utils.get_eventvalues(events, "InterBeatInterval")

        if ibis.size == 0:
            print(f"Didn't find InterBeatInterval events for {event_path}.")
            continue

        ibis_corrected = hrv_utils.correct_ibis(ibis)
        # Associate IBIs with a sample that represents the time of their occurrence (relative to breathing belt recording) rather
        # than the time of the Polar belt notification.
        peaks_corrected = hrv_utils.ibis_to_rpeaks(ibis_corrected, events)

        # Interpolate such that IBIs are aligned with respiration signal. Starting
        # at sample 0 (i.e., start of breathing belt recording) and ending at the sample that corresponds to the last recorded IBI.
        ibis_interpolated = hrv_utils.interpolate_ibis(peaks_corrected,
                                                       ibis_corrected,
                                                       range(peaks_corrected[-1]))

        pd.Series(ibis_interpolated).to_csv(save_path, sep="\t", header=True,
                                            index=False, float_format="%.4f")
        print(f"Saved {save_path}")


def preprocess_resp(subject, inputs, outputs, recompute):

    root = inputs["physio_path"][0]
    filename = inputs["physio_path"][1]
    physio_paths = root.joinpath(subject).glob(filename)

    for physio_path in physio_paths:

        root = outputs["save_path"][0]
        subj_sess_cond = physio_path.name[:23]
        filename = f"{subj_sess_cond}{outputs['save_path'][1]}"
        save_path = root.joinpath(f"{subject}/{filename}")

        computed = save_path.exists()   # Boolean indicating if file already exists.
        if computed and not recompute:    # only recompute if requested
            continue

        data = read_raw_edf(physio_path, preload=True, verbose="error")
        resp = np.ravel(data.get_data(picks=0))
        sfreq = data.info["sfreq"]

        resp_filt = biofeedback_utils.biofeedback_filter(resp, sfreq)
        inst_amp = resp_utils.instantaneous_amplitude(resp_filt)

        pd.DataFrame({"resp_filt": resp_filt,
                      "inst_amp": inst_amp}).to_csv(save_path, sep="\t",
                                                    header=True, index=False,
                                                    float_format="%.4f")
        print(f"Saved {save_path}")


def preprocess_hrv_biofeedback(subject, inputs, outputs, recompute):

    root = inputs["physio_path"][0]
    filename = inputs["physio_path"][1]
    physio_paths = list(root.joinpath(subject).glob(filename))

    for physio_path in physio_paths:

        root = outputs["save_path"][0]
        subj_sess_cond = physio_path.name[:23]
        filename = f"{subj_sess_cond}{outputs['save_path'][1]}"
        save_path = root.joinpath(f"{subject}/{filename}")

        computed = save_path.exists()   # Boolean indicating if file already exists.
        if computed and not recompute:    # only recompute if requested
            continue

        ibis = np.ravel(pd.read_csv(physio_path, sep='\t'))
        local_power_hrv = hrv_utils.compute_local_power(ibis)

        pd.DataFrame({"local_power_hrv": local_power_hrv}).to_csv(save_path, sep="\t",
                                                                  header=True, index=False,
                                                                  float_format="%.4f")
        print(f"Saved {save_path}")


def preprocess_resp_biofeedback(subject, inputs, outputs, recompute):

    root = inputs["event_path"][0]
    filename = inputs["event_path"][1]
    event_paths = list(root.joinpath(subject).glob(filename))

    for event_path in event_paths:

        root = outputs["save_path"][0]
        subj_sess_cond = event_path.name[:23]
        filename = f"{subj_sess_cond}{outputs['save_path'][1]}"
        save_path = root.joinpath(f"{subject}/{filename}")

        computed = save_path.exists()   # Boolean indicating if file already exists.
        if computed and not recompute:    # only recompute if requested
            continue

        events = pd.read_csv(event_path, sep='\t')
        biofeedback_values = event_utils.get_eventvalues(events, "Feedback")
        if biofeedback_values.size == 0:
            print(f"Didn't find Feedback events for {event_path}.")
            continue
        biofeedback_samples = event_utils.get_eventtimes(events, "Feedback", as_sample=True)
        # Interpolate such that biofeedback scores are aligned with respiration signal.
        # Starting at sample 0 and ending at the sample that corresponds to the last recorded biofeedback score.
        original_biofeedback = biofeedback_utils.interpolate_biofeedback(biofeedback_samples,
                                                                         biofeedback_values,
                                                                         range(biofeedback_samples[-1]))
        pd.DataFrame({"original_resp_biofeedback": original_biofeedback}).to_csv(save_path, sep="\t",
                                                                                 header=True, index=False,
                                                                                 float_format="%.4f")
        print(f"Saved {save_path}")

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


def preprocess_events(eventpath):

    events = pd.read_csv(eventpath, sep='\t')
    events = event_utils.format_events(events)

    return events


def preprocess_ibis(physpath, eventpath):

    data = read_raw_edf(physpath, preload=True, verbose="error")
    resp = np.ravel(data.get_data(picks=0))

    events = pd.read_csv(eventpath, sep='\t')

    # Original IBIs and associated samples. Multiple IBIs can be associated with
    # the same sample since Polar belt can include multiple IBIs in a single notification.
    ibis = event_utils.get_eventvalues(events, "InterBeatInterval")

    ibis_corrected = hrv_utils.correct_ibis(ibis)
    # Associate IBIs with a sample that represents the time of their occurence rather
    # than the time of the Polar belt notification.
    peaks_corrected = hrv_utils.ibis_to_rpeaks(ibis_corrected, events)

    ibis_interpolated = hrv_utils.interpolate_ibis(peaks_corrected, ibis_corrected,
                                                   np.arange(resp.size))

    return ibis_interpolated


def compute_instantaneous_breathing_amplitude(physpath):

    data = read_raw_edf(physpath, preload=True, verbose="error")
    resp = np.ravel(data.get_data(picks=0))
    sfreq = data.info["sfreq"]

    resp_filt = resp_utils.biofeedback_filter(resp, sfreq)

    inst_amp = resp_utils.instantaneous_amplitude(resp_filt)

    return inst_amp


def preprocess_subject(datadir, subject, recompute=False):

    rawdir = Path(datadir).joinpath(f"raw/{subject}")
    processeddir = Path(datadir).joinpath(f"processed/{subject}")

    physiopaths = rawdir.glob(f"{subject}*recordsignal*")
    eventpaths = rawdir.glob(f"{subject}*recordtrigger*")

    for physiopath, eventpath in zip(physiopaths, eventpaths):
        # Make sure that the two paths pertain to the same recording.
        physioname = physiopath.name
        eventname = eventpath.name
        assert physioname[:23] == eventname[:23]
        subj_sess_cond = physioname[:23]

        event_path = processeddir.joinpath(f"{subj_sess_cond}events")
        computed = event_path.exists()   # Boolean indicating if file already exists.
        if not computed or (computed and recompute):    # only recompute if requested
            events = preprocess_events(eventpath)
            events.to_csv(event_path, sep="\t", index=False)
            print(f"Saving {event_path}")

        ibis_path = processeddir.joinpath(f"{subj_sess_cond}ibis")
        computed = ibis_path.exists()
        if not computed or (computed and recompute):
            ibis = preprocess_ibis(physiopath, event_path)    # use preprocessed events
            pd.Series(ibis).to_csv(ibis_path, sep="\t", header=False,
                                   index=False, float_format="%.4f")
            print(f"Saving {ibis_path}")

        inst_amp_path = processeddir.joinpath(f"{subj_sess_cond}instant_resp_amp")
        computed = inst_amp_path.exists()
        if not computed or (computed and recompute):
            inst_amp = compute_instantaneous_breathing_amplitude(physiopath)
            pd.Series(inst_amp).to_csv(inst_amp_path, sep="\t", header=False,
                                       index=False, float_format="%.4f")
            print(f"Saving {inst_amp_path}")


def preprocess_subjects(datadir, recompute=False):

    rawdir = Path(datadir).joinpath("raw")
    subjects = rawdir.iterdir()
    subjects = [subject.stem for subject in subjects]

    for subject in subjects:

        # Validate that directory is a valid subject directory.
        if len(subject) != 7:
            continue
        if subject[:5] != "subj-":
            continue

        print(f"Preprocessing {subject}.")
        preprocess_subject(datadir, subject, recompute=recompute)

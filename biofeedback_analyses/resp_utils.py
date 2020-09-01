#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author: Jan C. Brammer <jan.c.brammer@gmail.com>
"""

import numpy as np
from scipy.signal import bessel, sosfiltfilt, hilbert
from biopeaks.resp import resp_extrema, resp_stats
from biopeaks.analysis_utils import find_segments


def biofeedback_filter(resp, sfreq):
    """Same filter used during real-time processing (biofeedback computation).
    """

    nyq = 0.5 * sfreq
    low = 4 / 60 / nyq
    high = 12 / 60 / nyq
    order = 2
    sos = bessel(order, [low, high], btype="bandpass", output="sos")

    resp_filt = sosfiltfilt(sos, resp)

    return resp_filt


def instantaneous_amplitude(signal):

    inst_amp = np.abs(hilbert(signal))

    return inst_amp


def bursts_dual_threshold(inst_amp, low, high, min_duration=0):

    above_low = inst_amp > low
    beg_low, end_low, duration_low = find_segments(above_low)
    above_high = np.where(inst_amp > high)[0]

    bursts = np.zeros(inst_amp.size, dtype=bool)

    for beg, end, duration in zip(beg_low, end_low, duration_low):

        if duration < min_duration:
            continue

        burst = np.arange(beg, end)
        if np.intersect1d(burst, above_high).size:
            bursts[beg:end] = True

    return bursts


def compute_resp_stats(resp, sfreq):

    stats = {}
    extrema = resp_extrema(resp, sfreq)
    _, rate, amp = resp_stats(extrema, resp, sfreq)
    stats["median_resp_rate"] = np.median(rate)
    stats["median_resp_amp"] = np.median(amp)

    return stats


def compute_biofeedback_stats(inst_amp, normalize_by):

    stats = {}
    stats["normalized_median_power"] = np.median(inst_amp) / normalize_by

    return stats


def compute_burst_stats(bursts, sfreq):

    change = np.diff(bursts)
    idcs, = change.nonzero()

    idcs += 1    # Get indices following the change.

    if bursts[0]:
        # If the first sample fulfills the condition, prepend a zero.
        idcs = np.r_[0, idcs]

    if bursts[-1]:
        # If the last sample fulfills the condition, append an index
        # corresponding to the length of signal
        idcs = np.r_[idcs, bursts.size]

    starts = idcs[0::2]
    ends = idcs[1::2]
    durations = ends - starts

    stats = {"n_bursts": len(durations),
             "duration_mean": np.mean(durations) / sfreq,
             "duration_std": np.std(durations) / sfreq,
             "percent_burst": 100 * np.sum(bursts) / len(bursts)}

    if not durations.size:
        stats.update((k, 0) for k in stats)

    return stats

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author: Jan C. Brammer <jan.c.brammer@gmail.com>
"""

import numpy as np
from biofeedback_analyses import event_utils
from biopeaks.filters import butter_lowpass_filter
from biopeaks.heart import correct_peaks
from scipy.interpolate import interp1d


def correct_ibis(ibis):
    """Correct artifacts in IBIs.
    For details see biopeaks.heart.correct_peaks().
    IMPORTANT: Polar H10 (H9) records IBIs in 1/1024 seconds format, i.e. not
    milliseconds. IBIs need to be transformed to milliseconds before being
    passed to this function (use event_utils.format_events()).

    Parameters
    ----------
    ibis : array
        IBIs in milliseconds.

    Returns
    -------
    ibis_corrected : array
        Corrected IBIs in milliseconds.
    """
    peaks = np.cumsum(ibis)
    peaks_corrected = correct_peaks(peaks, 1)

    ibis_corrected = np.ediff1d(peaks_corrected, to_begin=0)
    ibis_corrected[0] = ibis_corrected[1]

    return ibis_corrected


def ibis_to_rpeaks(ibis, events):
    """For each IBI, calculate the corresponding R-peak in samples.
    This allows for aligning the IBIs with the physiological recording.
    IMPORTANT: Polar H10 (H9) records IBIs in 1/1024 seconds format, i.e. not
    milliseconds. IBIs need to be transformed to milliseconds before being
    passed to this function (use event_utils.format_events()).

    Parameters
    ----------
    ibis : array
        IBIs in milliseconds.
    events : DataFrame
        Must be formatted with event_utils.format_events() prior to calling this function.

    Returns
    -------
    peaks_samp : array
        The samples at which R-peaks occur.
    """
    peaks_ms = np.cumsum(ibis)
    peaks_ms = peaks_ms - peaks_ms[0]    # start peaks at 0 milliseconds

    # Get number of samples per second (slope), and number of samples elapsed
    # between the start of the physiological recording and the first event in the
    # events file (intcpt).
    phys_sec = event_utils.get_eventtimes(events, "bitalino.synchronize", as_sample=False)
    phys_samp = event_utils.get_eventvalues(events, "bitalino.synchronize")
    slope, intcpt = np.polyfit(phys_sec, phys_samp, 1)
    # Convert peaks from milliseconds to seconds and then to samples.
    peaks_samp = np.rint(intcpt + (peaks_ms / 1000) * slope).astype(int)

    # Since peaks start at zero, the first peak has to be offset such that it
    # coincides with the first recorded IBI.
    ibis_samp = event_utils.get_eventtimes(events, "InterBeatInterval", as_sample=True)
    peaks_samp += (ibis_samp[0] - peaks_samp[0])
    assert ibis_samp[0] == peaks_samp[0]

    return peaks_samp


def interpolate_ibis(peaks, ibis, samples):
    """Interpolate IBIs between peaks over a range of samples.
    IMPORTANT: Polar H10 (H9) records IBIs in 1/1024 seconds format, i.e. not
    milliseconds. IBIs need to be transformed to milliseconds before being
    passed to this function (use event_utils.format_events()).

    Parameters
    ----------
    peaks : array
        The samples at which the R-peaks occur.
    ibis : array
        IBIs in milliseconds.
    samples : array
        Samples over which the IBIs will be interpolated.

    Returns
    -------
    ibis_filt : array
        IBIs interpolated over samples and lowpass filtered with highcut of 1 Hz.
    """
    f_interp = interp1d(peaks, ibis, bounds_error=False,
                        fill_value=(ibis[0], ibis[-1]))
    ibis_interpolated = f_interp(samples)

    # Smooth out edges left over from linear interpolation. Lowpass filtering
    # at 1 Hz preserves frequencies in the "very high frequency" (VHF) range of 0.4-0.9 Hz.
    ibis_filt = butter_lowpass_filter(ibis_interpolated, 1, 10, 12)

    return ibis_filt

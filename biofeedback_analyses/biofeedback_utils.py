#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author: Jan C. Brammer <jan.c.brammer@gmail.com>
"""

import numpy as np
from scipy.signal import bessel, sosfiltfilt
from scipy.interpolate import interp1d


def biofeedback_filter(resp, sfreq):
    """Filter respiration as during real-time biofeedback computation."""
    nyq = 0.5 * sfreq
    low = 4 / 60 / nyq
    high = 12 / 60 / nyq
    order = 2
    sos = bessel(order, [low, high], btype="bandpass", output="sos")
    resp_filt = sosfiltfilt(sos, resp)

    return resp_filt


def interpolate_biofeedback(biofeedback_samples, biofeedback_values,
                            interpolation_samples):
    """Interpolate recorded biofeedback scores over a range of samples."""
    f_interp = interp1d(biofeedback_samples, biofeedback_values,
                        bounds_error=False, fill_value=(biofeedback_values[0],
                                                        biofeedback_values[-1]))
    biofeedback_interpolated = f_interp(interpolation_samples)

    return biofeedback_interpolated


def compute_biofeedback_score(signal, target):
    """Compute biofeedback score.

    Use Hill equation [1] to compute biofeedback score. Biofeedback target is
    equivalent to K parameter.

    Parameters
    ----------
    signal : ndarray
        The physiological data to be transformed to biosignal scores.
    target : float
        The value of `signal` at which half of the maximum score (i.e., 1) is
        obtained. In units of `signal`.
    Returns
    -------
    biofeedback : ndarray
        Biofeedback values associated with `signal`. In the range [0, 1].
    References
    ----------
    [1] https://en.wikipedia.org/wiki/Hill_equation_(biochemistry)
    """
    Vmax = 1    # Upper limit of y values
    n = 3    # Hill coefficient, determines steepness of curve
    biofeedback = Vmax * signal**n / (target**n + signal**n)

    return biofeedback


def compute_original_resp_biofeedback_stats(original_resp_biofeedback):

    stats = {}
    stats["median_original_resp_biofeedback"] = np.median(original_resp_biofeedback)
    stats["mean_original_resp_biofeedback"] = np.mean(original_resp_biofeedback)

    return stats
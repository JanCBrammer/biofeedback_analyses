#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author: Jan C. Brammer <jan.c.brammer@gmail.com>
"""

import numpy as np
from biofeedback_analyses import event_utils
from biopeaks.filters import butter_lowpass_filter, moving_average
from biopeaks.heart import correct_peaks
from scipy.interpolate import interp1d
from scipy.signal import welch, coherence, find_peaks


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


def interpolate_ibis(peaks, ibis, interpolation_samples):
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
    interpolation_samples : array
        Samples over which the IBIs will be interpolated.

    Returns
    -------
    ibis_filt : array
        IBIs interpolated over samples and lowpass filtered with highcut of 1 Hz.
    """
    f_interp = interp1d(peaks, ibis, bounds_error=False,
                        fill_value=(ibis[0], ibis[-1]))
    ibis_interpolated = f_interp(interpolation_samples)

    # Smooth out edges left over from linear interpolation. Lowpass filtering
    # at 1 Hz preserves frequencies in the "very high frequency" (VHF) range of 0.4-0.9 Hz.
    ibis_filt = butter_lowpass_filter(ibis_interpolated, 1, 10, 12)

    return ibis_filt


def compute_hrv_stats(ibis, sfreq):

    stats = {}

    freqs, psd = welch(ibis, fs=sfreq, nperseg=4096)

    vlf_band = {"fmin": 0.003, "fmax": 0.04}
    lf_band = {"fmin": 0.04, "fmax": 0.15}
    hf_band = {"fmin": 0.15, "fmax": 0.40}

    vlf_idcs = np.logical_and(freqs >= vlf_band["fmin"], freqs < vlf_band["fmax"])
    lf_idcs = np.logical_and(freqs >= lf_band["fmin"], freqs < lf_band["fmax"])
    hf_idcs = np.logical_and(freqs >= hf_band["fmin"], freqs < hf_band["fmax"])

    # Integrate using the composite trapezoidal rule.
    vlf = np.trapz(y=psd[vlf_idcs], x=freqs[vlf_idcs])
    lf = np.trapz(y=psd[lf_idcs], x=freqs[lf_idcs])
    hf = np.trapz(y=psd[hf_idcs], x=freqs[hf_idcs])
    stats["hrv_vlf"] = vlf
    stats["hrv_lf"] = lf
    stats["hrv_hf"] = hf
    stats["hrv_lf_hf_ratio"] = lf / hf
    stats["hrv_lf_nu"] = (lf / (lf + hf)) * 100
    stats["hrv_hf_nu"] = (hf / (lf + hf)) * 100
    stats["median_heart_period"] = np.median(ibis)
    stats["rmssd"] = np.sqrt(np.mean(np.diff(ibis) ** 2))

    # plt.figure()

    # plt.plot(freqs[vlf_idcs], psd[vlf_idcs], c="r")
    # plt.plot(freqs[lf_idcs], psd[lf_idcs], c="b")
    # plt.plot(freqs[hf_idcs], psd[hf_idcs], c="g")

    # plt.show()

    return stats


def compute_coherence(resp, ibis, sfreq):

    freqs, coh = coherence(resp, ibis, sfreq, nperseg=1024)

    lf_band = {"fmin": 0.04, "fmax": 0.15}
    hf_band = {"fmin": 0.15, "fmax": 0.40}

    lf_idcs = np.logical_and(freqs >= lf_band["fmin"], freqs < lf_band["fmax"])
    hf_idcs = np.logical_and(freqs >= hf_band["fmin"], freqs < hf_band["fmax"])

    coh_lf = np.mean(coh[lf_idcs])
    coh_hf = np.mean(coh[hf_idcs])
    stats = {}
    stats["coherence_lf"] = coh_lf
    stats["coherence_hf"] = coh_hf

    return stats

    # plt.plot(freqs, coh)
    # plt.xlabel('frequency [Hz]')
    # plt.ylabel('Coherence')
    # plt.show()


def compute_local_power(ibis):
    """Compute local HRV power on interpolated IBI signal."""
    loc_max, _ = find_peaks(ibis)
    loc_min, _ = find_peaks(ibis * -1)
    loc_ext = np.concatenate((loc_max, loc_min))
    loc_ext.sort(kind="mergesort")

    loc_power = np.abs(np.ediff1d(ibis[loc_ext], to_begin=0))
    loc_power[0] = loc_power[1]

    f_interp = interp1d(loc_ext, loc_power, bounds_error=False,
                        fill_value=(loc_power[0], loc_power[-1]))
    inst_loc_power = f_interp(range(ibis.size))

    return inst_loc_power

    # fig, (ax0, ax1) = plt.subplots(nrows=2, ncols=1, sharex=True)
    # ax0.vlines(loc_ext, ymin=min(ibis), ymax=max(ibis), colors="m", alpha=.5)
    # ax0.plot(ibis)
    # ax1.vlines(loc_ext, ymin=min(inst_loc_power), ymax=max(inst_loc_power), colors="m", alpha=.5)
    # ax1.plot(inst_loc_power)
    # plt.show()


def compute_local_power_hrv_stats(local_power_hrv):

    stats = {}
    stats["median_local_power_hrv"] = np.median(local_power_hrv)
    stats["mean_local_power_hrv"] = np.mean(local_power_hrv)

    return stats
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author: Jan C. Brammer <jan.c.brammer@gmail.com>
"""

import numpy as np
import numpy.ma as mask
import matplotlib.pyplot as plt
from mne.io import read_raw_edf
from pathlib import Path
from scipy.signal import bessel, sosfiltfilt, hilbert


def bessel_bandpass_sos(lowcut, highcut, fs, order):

    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    sos = bessel(order, [low, high], btype="bandpass", output="sos")
    return sos


def compute_median_inst_amp(physiopaths):

    inst_amps = []

    for PHYSPATH in physiopaths:

        data = read_raw_edf(PHYSPATH, preload=True, verbose="warning")
        resp = np.ravel(data.get_data(picks=0))
        sfreq = data.info["sfreq"]

        sos = bessel_bandpass_sos(4 / 60, 12 / 60, sfreq, 2)
        resp_filt = sosfiltfilt(sos, resp)

        inst_amp = np.abs(hilbert(resp_filt))
        inst_amps.append(np.median(inst_amp))

    return np.mean(inst_amps)


def bursts_dual_threshold(signal, low, high, min_duration=0):

    above_low = signal > low
    beg_low = np.where(np.logical_and(np.logical_not(above_low[0:-1]), above_low[1:]))[0]
    end_low = np.where(np.logical_and(above_low[0:-1], np.logical_not(above_low[1:])))[0]
    above_high = np.where(signal > high)[0]

    bursts = np.zeros(signal.size, dtype=bool)

    for i, j in zip(beg_low, end_low):

        if j - i < min_duration:
            continue

        burst = np.arange(i, j)
        if list(np.intersect1d(burst, above_high)):
            bursts[i:j] = True

    return bursts


DATADIR = r"C:\Users\JohnDoe\surfdrive\Biochill_RITE\20200818_v3.0.0\data"
physiopaths = list(Path(DATADIR).glob("*recordsignal*"))[:2]


median_inst_amp = compute_median_inst_amp(physiopaths)

fig, ax = plt.subplots(nrows=len(physiopaths), ncols=1, sharex=False)

for i, PHYSPATH in enumerate(physiopaths):

    data = read_raw_edf(PHYSPATH, preload=True, verbose="error")
    resp = np.ravel(data.get_data(picks=0))
    sfreq = data.info["sfreq"]
    sec = data.times

    sos = bessel_bandpass_sos(4 / 60, 12 / 60, sfreq, 2)
    resp_filt = sosfiltfilt(sos, resp)

    inst_amp = inst_amp = np.abs(hilbert(resp_filt))
    print(np.median(inst_amp) / median_inst_amp)

    bursts = bursts_dual_threshold(inst_amp,
                                   median_inst_amp,
                                   2 * median_inst_amp,
                                   min_duration=int(np.rint(15 * sfreq)))

    ax[i].plot(sec, resp_filt)
    ax[i].plot(sec, inst_amp)
    ax[i].plot(mask.array(sec, mask=~bursts), mask.array(inst_amp, mask=~bursts), c="r")    # mark bursts
    ax[i].axhline(y=median_inst_amp)
    ax[i].axhline(y=2 * median_inst_amp)

plt.show()

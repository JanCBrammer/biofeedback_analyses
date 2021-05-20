#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author: Jan C. Brammer <jan.c.brammer@gmail.com>
"""

import numpy as np
import dateutil


def isotimes_to_relativetimes(df):
    """Convert the df's "timestamp" column from ISO timeformat to seconds
    elapsed since first timestamp.

    Parameters
    ----------
    df : DataFrame
        Containing three (or four) columns: event, value, timestamp,
        (physiosample).

    Returns
    -------
    df : DataFrame
        Mutated DataFrame.
    """
    isotimes = [dateutil.parser.parse(i) for i in df["timestamp"]]    # parser returns a datetime.datetime object
    # specify time in seconds relative to the first timestamp
    t_zero = isotimes[0]
    relativetimes = np.asarray([(i - t_zero).total_seconds() for i in isotimes])
    df["timestamp"] = relativetimes

    return df


def relativetimes_to_physiosamples(df, drop_rows_after_last_physiosample=False):
    """Convert the df's "timestamp" column to samples that are aligned with the
    synchronization samples from the physiological recording. Append the
    samples to the df in a "physiosample" column.

    Parameters
    ----------
    df : DataFrame
        Containing three columns: event, value, timestamp.
    drop_rows_after_last_physiosample : bool, optional
        Whether or not to drop the events that have been recorded after the
        physiological recording has been stopped.

    Returns
    -------
    df : DataFrame
        Mutated DataFrame containing four columns: event, value, timestamp,
        physiosample.
    """
    phys_sec = get_eventtimes(df, "bitalino.synchronize")
    phys_samp = get_eventvalues(df, "bitalino.synchronize")

    # Get number of samples per second (slope), and number of samples elapsed
    # between the start of the physiological recording and the first event in the
    # events file (intcpt).
    slope, intcpt = np.polyfit(phys_sec, phys_samp, 1)

    # Convert the seconds at which the events occur to their corresponding samples
    # in the physiological recording.
    events_samp = np.rint(intcpt + df["timestamp"] * slope).astype(int)
    df["physiosample"] = events_samp

    # Make sure that the conversion from seconds to samples is correct by asserting
    # that the "timestamp" entries and "physiosample" entires of the
    # "bitalino.synchronize" events are identical within a tolerance (rounding).
    assert np.allclose(phys_samp,
                       get_eventtimes(df, "bitalino.synchronize", as_sample=True),
                       atol=phys_samp.size)

    if drop_rows_after_last_physiosample:
        drop_idcs = list(np.where(events_samp > phys_samp.max())[0])
        df.drop(drop_idcs, inplace=True)
        df.reset_index(inplace=True, drop=True)

    return df


def specify_unityevents(df):
    """Replace the generic "UnityEvent" strings in the df's "event" column with
    the associated specific event strings in the df's "value" column.

    Parameters
    ----------
    df : DataFrame
        Containing three (or four) columns: event, value, timestamp,
        (physiosample).

    Returns
    -------
    df : DataFrame
        Mutated DataFrame.
    """
    unityevent_idcs = df["event"] == "UnityEvent"
    unityevent_names = df.loc[unityevent_idcs, "value"]
    # Specific event name is the third value of the semicolon-separated string.
    unityevent_names = [i.split(";")[2] for i in unityevent_names]
    df.loc[unityevent_idcs, "event"] = unityevent_names

    return df


def ibis_to_ms(df):
    """Convert IBIs in 1/1024 sec format to milliseconds.
    IMPORTANT: Polar H10 (H9) records IBIs in 1/1024 seconds format, i.e. not
    milliseconds!

    Parameters
    ----------
    df : DataFrame
        Containing three (or four) columns: event, value, timestamp,
        (physiosample).

    Returns
    -------
    df : DataFrame
        Mutated DataFrame.
    """
    ibis_idcs = df["event"] == "InterBeatInterval"
    ibis_ms = df.loc[ibis_idcs, "value"].to_numpy(dtype="int") / 1024 * 1000
    df.loc[ibis_idcs, "value"] = ibis_ms

    return df


def format_events(df):
    """Format the df for further processing.
    For details on the formatting steps see docstrings of
    isotimes_to_relativetimes(), relativetimes_to_physiosamples(),
    specify_unityevents(), and ibis_to_ms().

    Parameters
    ----------
    df : DataFrame
        Containing three columns: event, value, timestamp.

    Returns
    -------
    df : DataFrame
        Mutated DataFrame.
    """
    df = isotimes_to_relativetimes(df)
    df = relativetimes_to_physiosamples(df, drop_rows_after_last_physiosample=True)
    df = specify_unityevents(df)
    df = ibis_to_ms(df)

    return df


def get_eventtimes(df, event, as_sample=False):
    """Return all occurences of an event (in seconds or samples).
    Return df's entries of "timestamp" or "physiosample" column for a specific
    event.

    Parameters
    ----------
    df : DataFrame
        Containing four columns: event, value, timestamp, physiosample.
    event : string
        Name of the event.
    as_sample : bool, optional
        Whether to return occurences of event as samples. If False (default),
        return the occurences in seconds.

    Returns
    -------
    t : array
        All occurences of the requested event (either seconds or samples).
    """
    event_idcs = df["event"] == event
    if not as_sample:
        t = df.loc[event_idcs, "timestamp"]
        t = t.to_numpy(dtype=float)
    if as_sample:
        t = df.loc[event_idcs, "physiosample"]
        t = t.to_numpy(dtype=int)    # in case the timestamps have already been converted to samples

    return t


def get_eventvalues(df, event):
    """Return entires of df's "value" column for a specific event.

    Parameters
    ----------
    df : DataFrame
        Containing three (or four) columns: event, value, timestamp,
        (physiosample).
    event : string
        Name of the event.

    Returns
    -------
    v : array
        All entries of the df's "value" column for the requested event.
    """
    event_idcs = df["event"] == event
    v = df.loc[event_idcs, "value"].to_numpy(dtype=float)

    return v

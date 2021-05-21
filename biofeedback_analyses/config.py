#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author: Jan C. Brammer <jan.c.brammer@gmail.com>
"""

DATA_HASH = "b62db5c30043d6e1e34d3d91c346e649"  # MD5 hash of original data used for regression tests during re-runs of the analysis
SFREQ = 10
SUBJECTS = [f"subj-{str(i).zfill(2)}" for i in range(1, 10)]
sessions = [f"sess-{str(i).zfill(2)}" for i in range(1, 11)]
conditions = ["cond-A", "cond-B", "cond-B", "cond-A", "cond-B", "cond-A", "cond-B", "cond-A", "cond-B", "cond-A"]
SESSIONS = [f"{s}_{c}" for s, c in zip(sessions, conditions)]    # sessions and conditions are linked

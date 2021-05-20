#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author: Jan C. Brammer <jan.c.brammer@gmail.com>
"""

SFREQ = 10
SUBJECTS = [f"subj-{str(i).zfill(2)}" for i in range(1, 10)]
sessions = [f"sess-{str(i).zfill(2)}" for i in range(1, 11)]
conditions = ["cond-A", "cond-B", "cond-B", "cond-A", "cond-B", "cond-A", "cond-B", "cond-A", "cond-B", "cond-A"]
SESSIONS = [f"{s}_{c}" for s, c in zip(sessions, conditions)]    # sessions and conditions are linked

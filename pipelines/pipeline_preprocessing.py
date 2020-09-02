#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author: Jan C. Brammer <jan.c.brammer@gmail.com>
"""

import numpy as np
from biofeedback_analyses.preprocessing import (preprocess_events,
                                                preprocess_ibis,
                                                preprocess_biofeedback)


datadir = "C:/Users/JohnDoe/surfdrive/Biochill_RITE/20200818_v3.0.0/data"
subjects = [f"subj-{str(i).zfill(2)}" for i in np.arange(1, 2)]

pipeline = [

    {"func": preprocess_events,
     "subjects": subjects,
     "inputs": {"event_path": [datadir, "raw", "*recordtrigger*"]},
     "outputs": {"save_path": [datadir, "processed", "events"]},
     "recompute": False},

    {"func": preprocess_ibis,
     "subjects": subjects,
     "inputs": {"event_path": [datadir, "processed", "*events*"],
                "physio_path": [datadir, "raw", "*recordsignal*"]},
     "outputs": {"save_path": [datadir, "processed", "ibis"]},
     "recompute": True},

    {"func": preprocess_biofeedback,
     "subjects": subjects,
     "inputs": {"physio_path": [datadir, "raw", "*recordsignal*"]},
     "outputs": {"save_path": [datadir, "processed", "biofeedback"]},
     "recompute": False}

]


def run_pipeline(pipeline):

    for task in pipeline:

        for subject in task["subjects"]:

            task["func"](subject,
                         task["inputs"],
                         task["outputs"],
                         task["recompute"])


if __name__ == "__main__":

    run_pipeline(pipeline)

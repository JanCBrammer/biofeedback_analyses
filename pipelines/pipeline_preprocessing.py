#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author: Jan C. Brammer <jan.c.brammer@gmail.com>
"""

from pipelines.preprocessing import (preprocess_events,
                                     preprocess_ibis,
                                     preprocess_resp,
                                     preprocess_hrv_biofeedback,
                                     preprocess_resp_biofeedback)
from biofeedback_analyses.config import (SUBJECTS, DATADIR_RAW, DATADIR_PROCESSED)


pipeline = [

    {"func": preprocess_events,
     "subjects": SUBJECTS,
     "inputs": {"event_path": [DATADIR_RAW, "*recordtrigger*"]},
     "outputs": {"save_path": [DATADIR_PROCESSED, "events"]},
     "recompute": False},

    {"func": preprocess_ibis,
     "subjects": SUBJECTS,
     "inputs": {"event_path": [DATADIR_PROCESSED, "*events"]},
     "outputs": {"save_path": [DATADIR_PROCESSED, "ibis"]},
     "recompute": False},

    {"func": preprocess_resp,
     "subjects": SUBJECTS,
     "inputs": {"physio_path": [DATADIR_RAW, "*recordsignal*"]},
     "outputs": {"save_path": [DATADIR_PROCESSED, "resp"]},
     "recompute": False},

    {"func": preprocess_hrv_biofeedback,
     "subjects": SUBJECTS,
     "inputs": {"physio_path": [DATADIR_PROCESSED, "*ibis"]},
     "outputs": {"save_path": [DATADIR_PROCESSED, "hrv_biofeedback"]},
     "recompute": False},

    {"func": preprocess_resp_biofeedback,
     "subjects": SUBJECTS,
     "inputs": {"event_path": [DATADIR_PROCESSED, "*events"]},
     "outputs": {"save_path": [DATADIR_PROCESSED, "resp_biofeedback"]},
     "recompute": True}

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

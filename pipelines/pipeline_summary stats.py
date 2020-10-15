#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author: Jan C. Brammer <jan.c.brammer@gmail.com>
"""

from biofeedback_analyses.summary_stats import (summary_resp,
                                                summary_biofeedback,
                                                summary_heart,
                                                summary_instantiate,
                                                summary_coherence)
from biofeedback_analyses.config import SUBJECTS, DATADIR_RAW, DATADIR_PROCESSED


pipeline = [

    {"func": summary_instantiate,
     "subjects": [None],
     "inputs": None,
     "outputs": {"save_path": [DATADIR_PROCESSED, "summary_all_subjects"]},
     "recompute": False},

    {"func": summary_resp,
     "subjects": SUBJECTS,
     "inputs": {"event_path": [DATADIR_PROCESSED, "*events*"],
                "physio_path": [DATADIR_RAW, "*recordsignal*"]},
     "outputs": {"save_path": [DATADIR_PROCESSED, "summary_all_subjects"]},
     "recompute": False},

    {"func": summary_biofeedback,
     "subjects": SUBJECTS,
     "inputs": {"event_path": [DATADIR_PROCESSED, "*events*"],
                "physio_path": [DATADIR_PROCESSED, "*biofeedback*"]},
     "outputs": {"save_path": [DATADIR_PROCESSED, "summary_all_subjects"]},
     "recompute": False},

    {"func": summary_heart,
     "subjects": SUBJECTS,
     "inputs": {"event_path": [DATADIR_PROCESSED, "*events*"],
                "physio_path": [DATADIR_PROCESSED, "*ibis*"]},
     "outputs": {"save_path": [DATADIR_PROCESSED, "summary_all_subjects"]},
     "recompute": False},

    {"func": summary_coherence,
     "subjects": SUBJECTS,
     "inputs": {"resp_path": [DATADIR_RAW, "*recordsignal*"],
                "ibis_path": [DATADIR_PROCESSED, "*ibis*"]},
     "outputs": {"save_path": [DATADIR_PROCESSED, "summary_all_subjects"]},
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
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author: Jan C. Brammer <jan.c.brammer@gmail.com>
"""

from biofeedback_analyses.summary_stats import (summary_resp,
                                                summary_biofeedback,
                                                summary_heart,
                                                summary_instantiate)
from biofeedback_analyses.config import SUBJECTS, DATADIR_RAW, DATADIR_PROCESSED


pipeline = [

    {"func": summary_instantiate,
     "subjects": [None],
     "inputs": None,
     "outputs": {"save_path": [DATADIR_PROCESSED, "summary_all_subjects"]},
     "recompute": True},

    {"func": summary_resp,
     "subjects": SUBJECTS,
     "inputs": {"physio_path": [DATADIR_RAW, "*recordsignal*"]},
     "outputs": {"save_path": [DATADIR_PROCESSED, "summary_all_subjects"]},
     "recompute": True},

    {"func": summary_biofeedback,
     "subjects": SUBJECTS,
     "inputs": {"physio_path": [DATADIR_PROCESSED, "*biofeedback*"]},
     "outputs": {"save_path": [DATADIR_PROCESSED, "summary_all_subjects"]},
     "recompute": True},

    {"func": summary_heart,
     "subjects": SUBJECTS,
     "inputs": {"physio_path": [DATADIR_PROCESSED, "*ibis*"]},
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
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author: Jan C. Brammer <jan.c.brammer@gmail.com>
"""

from plotting.steps import (validate_summary_data,
                            plot_figure_2,
                            plot_figure_3)


def pipeline(SUBJECTS, DATADIR_RAW, DATADIR_PROCESSED):

    return [

        {"func": validate_summary_data,
         "subjects": [None],
         "inputs": {"summary_path": [DATADIR_PROCESSED, "summary_all_subjects"]},
         "outputs": None,
         "recompute": False},

        {"func": plot_figure_2,
         "subjects": [None],
         "inputs": {"summary_path": [DATADIR_PROCESSED, "summary_all_subjects"]},
         "outputs": {"save_path": [DATADIR_PROCESSED, "Figure2.png"]},
         "recompute": False},

        {"func": plot_figure_3,
         "subjects": [None],
         "inputs": {"summary_path": [DATADIR_PROCESSED, "summary_all_subjects"]},
         "outputs": {"save_path": [DATADIR_PROCESSED, "Figure3.png"]},
         "recompute": False}

    ]

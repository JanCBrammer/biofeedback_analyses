#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author: Jan C. Brammer <jan.c.brammer@gmail.com>
"""

from setuptools import setup, find_namespace_packages

setup(
    name="biofeedback_analyses",
    version="0.0.1",
    author="Jan C. Brammer",
    author_email="jan.c.brammer@gmail.com",
    packages=find_namespace_packages(exclude=["misc", "literature", "streamlit_apps"]),
    license="GPL-3.0",
    entry_points={
        "console_scripts": [
            "plot_figures=run_analysis:main"
            ]
        }
)

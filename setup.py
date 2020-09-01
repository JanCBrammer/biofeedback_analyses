from setuptools import setup, find_namespace_packages

setup(
    name="biofeedback_analyses",
    version="0.0.1",
    author="Jan C. Brammer",
    author_email="jan.c.brammer@gmail.com",
    packages=find_namespace_packages(exclude=["misc", "literature"]),
    python_requires=">=3.7",
    license="GPL-3.0",
)

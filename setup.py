#!/usr/bin/env python3

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="miet-schedule-api",
    version="0.1.0",
    author="Deka",
    author_email="dka@disroot.org",
    description="Небольшая библиотека для получения расписания групп МИЭТ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TheDIMONDK/miet_schedule_api",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.25.0",
    ],
)

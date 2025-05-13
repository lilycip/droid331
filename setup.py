#!/usr/bin/env python3
"""
Setup script for the Droid package.
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="droid",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Modular AI Agent for social media and content generation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/droid",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "droid=main:main",
            "droid-web=web.app:main",
            "droid-cli=run_cli:main",
            "droid-api=examples.custom_api:main",
            "droid-test-api=examples.test_custom_api:main",
            "droid-plugin=examples.custom_plugin:main",
            "droid-workflow=examples.custom_workflow:main",
        ],
    },
    include_package_data=True,
)
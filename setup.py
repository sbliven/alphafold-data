#!/usr/bin/env python

"""The setup script."""

from setuptools import find_packages, setup

with open("README.md") as readme_file:
    readme = readme_file.read()

with open("CHANGELOG.md") as history_file:
    history = history_file.read()

requirements = [
    "Click>=7.0",
]

setup_requirements = [
    "pytest-runner",
]

test_requirements = [
    "tox",
    "flake8",
    "black",
    "isort",
    "coverage",
    "pytest>=3",
    "pytest-runner>=5",
    "mypy",
]

doc_requirements = ["Sphinx>1.8", "myst-parser==0.13.5"]

dev_requirements = ["bump2version", "twine"]

setup(
    author="Spencer Bliven",
    author_email="spencer.bliven@gmail.com",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    description="Manages data files for Alphafold2",
    entry_points={
        "console_scripts": [
            "alphafold_data=alphafold_data.cli:main",
        ],
    },
    install_requires=requirements,
    extras_require={
        "tests": test_requirements,
        "docs": doc_requirements,
        "dev": dev_requirements + test_requirements + doc_requirements,
    },
    license="BSD license",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="alphafold_data",
    name="alphafold_data",
    packages=find_packages(include=["alphafold_data", "alphafold_data.*"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/sbliven/alphafold_data",
    version="0.1.0",
    zip_safe=False,
)

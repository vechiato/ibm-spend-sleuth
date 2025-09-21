#!/usr/bin/env python3
"""
IBM Spend Sleuth

A comprehensive Python toolkit for analyzing IBM Cloud billing data with advanced 
filtering, planning integration, and professional reporting capabilities.
"""

from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ibm-spend-sleuth",
    version="1.0.0",
    author="Marcus Vechiato",
    author_email="vechiato@gmail.com",
    description="Comprehensive IBM Cloud billing analysis with flexible filtering and planning integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vechiato/ibm-spend-sleuth",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.910",
        ],
    },
    entry_points={
        "console_scripts": [
            "ibm-billing-filter=src.filter_billing:main",
            "ibm-billing-quick=src.quick_analyzer:main",
            "ibm-billing-viz=src.visualize_billing:main",
            "ibm-billing-excel=src.generate_planning_excel:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
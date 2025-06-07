"""
Power Platform Utility

A PySide6-based GUI application for interfacing with Power Platform environments
using the PAC CLI (Power Platform CLI).
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="power-platform-utility",
    version="1.0.0",
    author="Power Platform Tools",
    author_email="admin@powerplatformtools.com",
    description="A PySide6-based GUI application for Power Platform CLI integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/powerplatformtools/power-platform-utility",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Tools",
        "Topic :: Office/Business",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "power-platform-utility=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["config/*.json"],
    },
)

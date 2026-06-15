#!/usr/bin/python3
"""Setup"""

from setuptools import find_packages, setup

version = "0.2.0"

with open("README.rst") as f:
    long_description = f.read()

setup(
    name="ofxstatement-otp",
    version=version,
    author="Peter Gyongyosi",
    author_email="gypeter@gmail.com",
    url="https://github.com/gyp/ofxstatement-otp",
    description=("ofxstatement plugin for the Hungarian bank OTP"),
    long_description=long_description,
    license="AGPLv3",
    keywords=["ofx", "banking", "statement"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Natural Language :: English",
        "Topic :: Office/Business :: Financial :: Accounting",
        "Topic :: Utilities",
        "Environment :: Console",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU Affero General Public License v3",
    ],
    packages=find_packages("src"),
    package_dir={"": "src"},
    entry_points={
        "ofxstatement": [
            "otp = ofxstatement_otp.otp:OtpPlugin",
            "otp_legacy = ofxstatement_otp.otp_legacy:OtpLegacyPlugin",
        ]
    },
    python_requires=">=3.9",
    install_requires=["ofxstatement>=0.9.0", "openpyxl>=3.0"],
    extras_require={"dev": ["pytest", "mypy", "black"]},
    include_package_data=True,
    zip_safe=True,
)

#!/usr/bin/python3
"""Setup
"""
from setuptools import find_packages
from distutils.core import setup

version = "0.1.1"

with open('README.rst') as f:
    long_description = f.read()

setup(name='ofxstatement-otp',
      version=version,
      author="Peter Gyongyosi",
      author_email="gypeter@gmail.com",
      url="https://github.com/gyp/ofxstatement-otp",
      description=("ofxstatement plugin for the Hungarian bank OTP"),
      long_description=long_description,
      license="AGPLv3",
      keywords=["ofx", "banking", "statement"],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Programming Language :: Python :: 3',
          'Natural Language :: English',
          'Topic :: Office/Business :: Financial :: Accounting',
          'Topic :: Utilities',
          'Environment :: Console',
          'Operating System :: OS Independent',
          'License :: OSI Approved :: GNU Affero General Public License v3'],
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=["ofxstatement", "ofxstatement.plugins"],
      entry_points={
          'ofxstatement':
          [
              'otp = ofxstatement.plugins.otp:OtpPlugin',
              'otp_legacy = ofxstatement.plugins.otp_legacy:OtpLegacyPlugin',
              'otp_legacy_credit = ofxstatement.plugins.otp_credit_legacy:OtpCreditLegacyPlugin'
          ]
          },
      install_requires=['ofxstatement', 'openpyxl', 'dataclasses'],
      include_package_data=True,
      zip_safe=True
      )

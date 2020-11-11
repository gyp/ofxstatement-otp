#!/usr/bin/python3
"""Setup
"""
from setuptools import find_packages
from distutils.core import setup

version = "0.0.6"

with open('README.rst') as f:
    long_description = f.read()

setup(name='ofxstatement-otp',
      version=version,
      author="Zoltan Nagy",
      author_email="abesto@abesto.net",
      url="https://github.com/abesto/ofxstatement-otp",
      description=("ofxstatement plugin for the Hungarian bank OTP"),
      long_description=long_description,
      license="GPLv3",
      keywords=["ofx", "banking", "statement"],
      classifiers=[
          'Development Status :: 3 - Alpha',
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
              'otp_credit = ofxstatement.plugins.otp_credit:OtpCreditPlugin'
          ]
          },
      install_requires=['ofxstatement'],
      include_package_data=True,
      zip_safe=True
      )

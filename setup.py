#!/usr/bin/env python

import os
from setuptools import find_packages, setup

requirements = ['tqdm', 'scipy', 'numpy', 'astropy', 'matplotlib', 'Pillow', 'opencv-python', 'wxPython']

with open("README.rst") as readme_file:
    readme = readme_file.read()

PACKAGE_PATH = os.path.abspath(os.path.join(__file__, os.pardir))

setup(
    name="LensMe",
    version="0.1.0",
    description="Lens webcam viedo stream",
    long_description=open('README.rst').read(),
    author="Dominik Zuercher",
    author_email="dominikz@phys.ethz.ch",
    url="https://github.com/DZuercher/LensMe",
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    install_requires=requirements,
    license="MIT License",
    zip_safe=False,
    keywords="LensMe",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.10",
    ],
    entry_points={
        'console_scripts': [
            "lensme = LensMe.main:main"
        ]
    }

)

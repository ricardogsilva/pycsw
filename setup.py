from setuptools import setup, find_packages

import pycsw


KEYWORDS = ("pycsw csw catalogue catalog metadata discovery search"
            " ogc iso fgdc dif ebrim inspire")

DESCRIPTION = "pycsw is an OGC CSW server implementation written in Python"

with open("README.txt") as f:
    LONG_DESCRIPTION = f.read()

setup(
    name="pycsw",
    version=pycsw.__version__,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    license="MIT",
    platforms="all",
    keywords=KEYWORDS,
    author="pycsw development team",
    author_email="tomkralidis@gmail.com",
    maintainer="Tom Kralidis",
    maintainer_email="tomkralidis@gmail.com",
    url="http://pycsw.org/",
    install_requires=[
        "lxml==3.5.0",
    ],
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "pycsw-admin = pycsw.admin:main",
        ]
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering :: GIS",
    ]
)

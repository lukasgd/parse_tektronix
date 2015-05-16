# -*- coding: utf-8 -*-
"""
Created on Sat May 16 13:38:03 2015

@author: Sebastian Theilenberg
"""

import os.listdir
import os.path
import numpy as np

from .parse_isf import read_curve


def read_isf(filename):
    """
    Reads and parses a single .isf file and returns it's timepoints and data
    as a 2d-numpy-array.
    """
    return read_isf_files(filename, additional=False)


def read_isf_files(filename, additional=True):
    """
    Reads and parses .isf files. Since multiple channels end up in different
    files, it is attempted to restore the whole data by searching for
    additional files.
    Returns the timepoints and data in a nd-numpy-array.
    """
    root, base = os.path.split(filename)
    base, ext = os.path.splitext(base)

    # check for right file type
    extensions = set(".isf")
    if ext.lower() not in extensions:
        raise ValueError("File type unkown.")

    # find additional files
    if additional:
        files = [f for f in os.listdir(root)
                 if f.endswith(ext) and f.startswith(base[:-1])
                 ]
        files.sort()
    else:
        files = [filename]

    # parse files
    data = []
    for f in files:
        data.append(read_curve(f))

    # remove datasets with different time domains
    if len(files) > 1:
        for d in data[1:]:
            if not _compare_parsed_data(data[0], d):
                del d

    # create time data
    res = _create_time_data(data[0])[None, :]

    # create single array
    for d in data:
        res = np.concatenate((res, d["data"][None, :]), axis=0)

    return res


def _compare_parsed_data(a, b):
    """
    Compares to parsed data sets based on their time domain.
    """
    for tag in ["XINCR", "XZERO", "NR_PT"]:
        if a[tag] != b[tag]:
            return False
    return True


def _create_time_data(data):
    """
    Creates a 1d-array of timepoints corresponding to data's points.
    """
    t = np.arange(data["data"].size)
    t = t * float(data["XINCR"]) + float(data["XZERO"])
    return t

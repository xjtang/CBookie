""" Module for IO of table files
"""
import csv
import ast

import numpy as np


def csv2list(_file, header=False, fixType=True):
    """ read a csv file based table to a list

    Args:
        file (str): path to input text file
        header (bool): first line header or not
        fixType (bool): convert data to correct type or not

    Returns:
        table (list): the table

    """
    # read file
    with open(_file, 'r') as f:
        reader = csv.reader(f)
        if header:
            next(reader)
        table = list(reader)

    # fix data type
    if fixType:
        for i, row in enumerate(table):
            for j, value in enumerate(row):
                try:
                    table[i][j] = ast.literal_eval(value)
                except:
                    pass

    # done
    return table


def csv2dict(_file, fixType=True):
    """ read a csv file based table to a dictionary

    Args:
        _file (str): path to input text file
        fixType (bool): convert data to correct type or not

    Returns:
        table (list): the table

    """
    # read file
    with open(_file, 'r') as f:
        reader = csv.DictReader(f)
        table = list(reader)

    # fix data type
    if fixType:
        for i, row in enumerate(table):
            for key in row:
                try:
                    table[i][key] = ast.literal_eval(table[i][key])
                except:
                    pass

    # done
    return table


def csv2ndarray(_file, header=True):
    """ read a csv file based table to a numpy array

    Args:
        _file (str): path to input text file
        header (bool): first line header or not

    Returns:
        array (ndarray): the numpy array

    """
    # read csv as list
    table = csv2list(_file)
    if not header:
        table = ['field{}'.format(x+1) for x in range(0, len(table[0]))] + table

    # convert list to numpy ndarray
    _type = np.array([type(x) for x in table[1]])
    _type[_type==str] = object
    array = np.array([tuple(x) for x in table[1:]],
                dtype=[(table[0][i], _type[i]) for i in range(len(table[0]))])

    # done
    return array

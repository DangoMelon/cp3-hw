# -*- coding: utf-8 -*-
"""
Created on Thu Aug 11 22:46:31 2021

@author: Gerardo A. Rivera Tello
email: grivera@igp.gob.pe
"""

from typing import List, Union, Any


def sum_values(*args: Union[int, float]) -> Union[int, float]:
    """
    Return the sum of any amount of given values

    Parameters
    ----------
    args : int or float
        Any amount of integer or floating-point numbers
        which will be added together

    Returns
    -------
    int or float
        The summation of the given numbers
    """
    sum = 0
    for val in args:
        sum += val
    return sum


def split_list(vlist: List[Any], chunksize: int) -> List[Any]:
    """
    Generator function that will return a chunked list according
    to the chunksize parameter

    Parameters
    ----------
    vlist : list
        The list of values that will be chunked
    chunksize : int
        The number of items per chunk

    Yields
    ------
    list
        A chunk of the input `vlist` with `chunksize` items

    """
    for i in range(0, len(vlist), chunksize):
        yield vlist[i : i + chunksize]


if __name__ == "__main__":

    with open("datos_tarea1.txt", "r") as f:
        # The whole text file could be read and converted to
        # float with this single line instead of looping
        # until we hit the EOF

        # data = [float(item) for item in f.readlines()]

        data = []
        while True:
            line = f.readline()
            if len(line) != 0:
                data.append(float(line))
            else:
                break

    data_sum = [sum_values(*item) for item in split_list(data, 10)]

    with open("resultado_suma.txt", "w") as f:
        f.write("\n".join([f"{val:014.10f}" for val in data_sum]))

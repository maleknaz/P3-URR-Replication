from __future__ import annotations

import os
import time
from functools import partial
from typing import Callable, Iterable

import numpy as np
import tqdm
from matplotlib import pyplot as plt
from numba import njit
from dataclasses import dataclass

from tqdm.contrib.concurrent import process_map, thread_map


@dataclass
class Statistics:
    mean: float
    median: float
    lower_quartile: float
    upper_quartile: float
    iqr: float
    minimum: float
    maximum: float
    count: int
    total: float

    def get_metric_6(self) -> tuple[float, float, float, float, float, float]:
        return self.mean, self.median, self.minimum, self.maximum, self.lower_quartile, self.upper_quartile


@njit(cache=True)
def _calc_col_stats_helper(col: np.ndarray) -> tuple[float, float, float, float, float, float, float, int, float]:
    q1 = np.quantile(col, 0.25)
    q3 = np.quantile(col, 0.75)
    return (
        float(np.mean(col)),
        float(np.median(col)),
        float(q1),
        float(q3),
        float(q3 - q1),
        float(np.min(col)),
        float(np.max(col)),
        len(col),
        float(np.sum(col))
    )


def calc_col_stats(col: np.ndarray | list) -> Statistics:
    """
    Compute statistics for a data column

    :param col: Input column (tested on 1D array)
    :return: Statistics
    """
    if isinstance(col, list):
        col = np.array(col)
    return Statistics(*_calc_col_stats_helper(col))


def plot(**kwargs) -> plt:
    """
    Pyplot configurator shorthand

    Example: plt_cfg(xlabel="X", ylabel="Y") is equivalent to plt.xlabel("X"); plt.ylabel("Y")
    """
    for k, args in kwargs.items():
        if isinstance(args, dict):
            getattr(plt, k)(**args)
        else:
            getattr(plt, k)(args)
    return plt


def mem(var: str):
    print(f'Memory usage for {var}: {eval(f"sys.getsizeof({var})") / 1024:.1f}KB')


def run_time(func: Callable, *args, **kwargs):
    name = getattr(func, '__name__', 'function')
    start = time.time_ns()
    iter = kwargs.pop('iter', 10)
    _ = [func(*args, **kwargs) for _ in range(iter)]
    ms = (time.time_ns() - start) / 1e6
    print(f'RT {name:30} {ms:6.1f} ms')


def smap(fn: Callable, lst: Iterable, *args, **kwargs) -> list:
    return [fn(i) for i in tqdm.tqdm(lst, position=0, leave=True)]


def pmap(fn: Callable, lst: Iterable, *args, **kwargs) -> list:
    tqdm_args = dict(position=0, leave=True, chunksize=1, tqdm_class=tqdm.tqdm, max_workers=os.cpu_count())
    return process_map(fn, lst, *args, **{**tqdm_args, **kwargs})


def tmap(fn: Callable, lst: Iterable, *args, **kwargs) -> list:
    tqdm_args = dict(position=0, leave=True, chunksize=1, tqdm_class=tqdm.tqdm, max_workers=os.cpu_count())
    return process_map(fn, lst, *args, **{**tqdm_args, **kwargs})


def tq(it: Iterable, desc: str, *args, **kwargs) -> tqdm:
    tqdm_args = dict(position=0, leave=True)
    return tqdm.tqdm(it, desc, *args, **{**tqdm_args, **kwargs})


def patch_tqdm():
    tqdm_args = dict(chunksize=1, position=0, leave=True, tqdm_class=tqdm.tqdm, max_workers=os.cpu_count())
    tq: Callable[[Iterable], tqdm.tqdm] = partial(tqdm.tqdm, position=0, leave=True)
    pmap = partial(process_map, **tqdm_args)
    tmap = partial(thread_map, **tqdm_args)
    return tq, pmap, tmap

# -*- coding: utf-8 -*-
"""
Created on Tue Aug 17 12:25:23 2021

@author: Gerardo A. Rivera Tello
email: grivera@igp.gob.pe
"""

import multiprocessing as mp
import time
from multiprocessing.queues import Queue
from typing import Tuple, Union

import matplotlib.pyplot as plt
import numpy as np


def generate_signal(
    xs: Union[int, float], xf: Union[int, float], f0: Union[int, float], n: int = 256
) -> Tuple[np.array, np.array]:
    """
    Generate a sinusoidal signal with random noise added  from a normal
    distribution.

    Parameters
    ----------
    xs, xf: int or float
        The start and end time
    f0: int or float
        The wave frequency
    n: int, optional
        The length of the generated signal

    Returns
    -------
    x, signal: np.array, np.array
        The time and signal values of the generated wave
    """
    x = np.linspace(xs, xf, n)
    fs = n / (xf - xs)
    f = f0 * fs
    sin = np.sin(2 * np.pi * x * f) + (np.random.rand(n) - 0.5)
    return x, sin


def mp_generate_signal(queue: Queue, *args, **kwargs) -> None:
    """
    This function is just a wrapper over generate_signal for
    multiprocessing usage
    """
    while True:
        print("generating data")
        queue.put(generate_signal(*args, **kwargs))
        time.sleep(0.1)


def compute_fft(signal: np.array) -> Tuple[np.array, np.array]:
    """
    Compute the FFT of the given signal

    Parameters
    ----------
    signal: np.array
        The signal from which to compute the FFT on

    Returns
    -------
    freq, fft: np.array, np.array
        The shifted frequency and FFT of the incoming signal
    """
    print("computing fft")
    fft = np.fft.fft(signal).real
    freq = np.fft.fftfreq(signal.size)
    return np.fft.fftshift(freq), np.fft.fftshift(fft)


def mp_compute_fft(inqueue: Queue, outqueue: Queue) -> None:
    """ "
    This function is just a wrapper over compute_fft for
    multiprocessing usage
    """
    while True:
        if inqueue.qsize() > 0:
            indata = inqueue.get()
            outdata = compute_fft(indata[1])
            outqueue.put((*indata, *outdata))


def mp_plotting(inqueue: Queue, freq: Union[int, float]) -> None:
    """
    This function aims to do the plotting of any set of data found
    in the incoming queue, in a separate process, using the
    multiprocessing library.
    """
    fig, axs = plt.subplots(nrows=2)
    xsignal, ysignal = [], []
    xfft, yfft = [], []
    (line_signal,) = axs[0].plot(xsignal, ysignal, c="r", lw=0.5)
    (line_fft,) = axs[1].plot(xfft, yfft, c="g", lw=0.5)
    axs[0].set_title(f"Original Signal {freq=} + random noise")
    axs[1].set_title("Real FFT")
    fig.tight_layout()
    plt.show(block=False)
    plt.pause(0.1)
    bg = fig.canvas.copy_from_bbox(fig.bbox)

    save_counter = 0

    while True:
        if inqueue.qsize() > 0:
            indata = inqueue.get()
            line_signal.set_data(indata[0], indata[1])
            line_fft.set_data(indata[2], indata[3])

            fig.canvas.restore_region(bg)

            axs[0].set_xlim(indata[0].min(), indata[0].max())
            axs[1].set_xlim(indata[2].min(), indata[2].max())

            signalstd = indata[1].std()
            fftstd = indata[3].std()
            axs[0].set_ylim(indata[1].min() - signalstd, indata[1].max() + signalstd)
            axs[1].set_ylim(indata[3].min() - fftstd, indata[3].max() + fftstd)

            fig.canvas.draw()
            fig.canvas.blit(fig.bbox)
            fig.canvas.flush_events()
            plt.pause(0.05)

            if save_counter == 0:
                fig.savefig("plot.png")
                save_counter += 1


if __name__ == "__main__":
    # Creating the data queues
    data_queue, fft_queue = mp.Queue(), mp.Queue()

    # Base frequency for the generated signal
    freq = 0.2

    # Creating 3 processes
    pdata = mp.Process(target=mp_generate_signal, args=(data_queue, -50, 50, freq))
    pfft = mp.Process(target=mp_compute_fft, args=(data_queue, fft_queue))
    pplot = mp.Process(target=mp_plotting, args=(fft_queue, freq))

    # Starting the processes
    pdata.start()
    pfft.start()
    pplot.start()

    # Checking if theres data to plot
    while True:
        try:
            if fft_queue.qsize() == 0:
                print("nothing to plot")
        except:
            pdata.join()
            pfft.join()
            pplot.join()

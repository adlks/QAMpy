from __future__ import division, print_function

import numpy as np

""" a number of convenience functions"""

def cabssquared(x):
    """Calculate the absolute squared of a complex number"""
    return x.real**2 + x.imag**2

def dB2lin(x):
    """
    Convert input from dB(m) units to linear units
    """
    return 10**(x/10)

def lin2dB(x):
    """
    Convert input from linear units to dB(m)
    """
    return 10*np.log10(x)

def ttanh(x, A, x0, w):
    """
    Calculate the hyperbolic tangent with a given amplitude, zero offset and
    width.

    Parameters
    ----------
    x : array_like
        Input array variable
    A : float
        Amplitude
    x0 : float
        Zero-offset
    w : float
        Width

    Returns
    -------
    array_like
        calculated array
    """
    return A * tanh((x - x0) / w)


def gauss(x, A, x0, w):
    """
    Calculate the Gaussian function with a given amplitude, zero offset and
    width.

    Parameters
    ----------
    x : array_like
        Input array variable
    A : float
        Amplitude
    x0 : float
        Zero offset
    w : float
        Width

    Returns
    -------
    array_like
        calculated array
    """
    return A * np.exp(-((x - x0) / w)**2 / 2.)


def supergauss(x, A, x0, w, o):
    """
    Calculate the Supergaussian functions with a given amplitude,
    zero offset, width and order.

    Parameters
    ----------
    x : array_like
        Input array variable
    A : float
        Amplitude
    x0 : float
        Zero offset
    w : float
        Width
    o : float
        order of the supergaussian

    Returns
    -------
    array_like
        calculated array
    """
    return A * np.exp(-((x - x0) / w)**(2 * o) / 2.)

def orthonormalize_signal(E, os=1):
    """
    Orthogonalizing signal using the Gram-Schmidt process _[1].

    Parameters
    ----------
    E : array_like
       input signal
    os : int, optional
        oversampling ratio of the signal

    Returns
    -------
    E_out : array_like
        orthonormalized signal

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Gram%E2%80%93Schmidt_process for more
       detailed description.
    """

    E = np.atleast_2d(E)
    E_out = np.zeros(E.shape, dtype=complex)
    for l in range(E.shape[0]):
        # Center
        real_out = E[l,:].real - E[l,:].real.mean()
        tmp_imag = E[l,:].imag - E[l,:].imag.mean()

        # Calculate scalar products
        mean_pow_inphase = np.mean(real_out**2)
        mean_pow_quadphase = np.mean(tmp_imag**2)
        mean_pow_imb = np.mean(real_out*tmp_imag)

        # Output, Imag orthogonal to Real part of signal
        sig_out = real_out / np.sqrt(mean_pow_inphase) +\
                                    1j*(tmp_imag - mean_pow_imb * real_out / mean_pow_inphase) / np.sqrt(mean_pow_quadphase)
        # Final total normalization to ensure IQ-power equals 1
        E_out[l,:] = sig_out - np.mean(sig_out[::os])
        E_out[l,:] = E_out[l,:] / np.sqrt(np.mean(np.abs(E_out[l,::os])**2))

    return E_out

def normalise_and_center(E):
    """
    Normalise and center the input field, by calculating the mean power for each polarisation separate and dividing by its square-root
    """
    if E.ndim > 1:
        for i in range(E.shape[0]):
            E[i] -= np.mean(E[i])
            P = np.sqrt(np.mean(cabssquared(E[i])))
            E[i] /= P
    else:
        E = E.real - np.mean(E.real) + 1.j * (E.imag-np.mean(E.imag))
        P = np.sqrt(np.mean(cabssquared(E)))
        E /= P
    return E

def sech(x, A, x0, w):
    """
    Calculate the hyperbolic secant function with a given
    amplitude, zero offset and width.

    Parameters
    ----------
    x : array_like
        Input array variable
    A : float
        Amplitude
    x0 : float
        Zero offset
    w : float
        Width

    Returns
    -------
    array_like
        calculated array
    """
    return A / np.cosh((x - x0) / w)


def factorial(n):
    """The factorial of n, i.e. n!"""
    if n == 0: return 1
    return n * factorial(n - 1)


def linspacestep(start, step, N):
    """
    Create an array of given length for a given start and step
    value.

    Parameters
    ----------
    start : float
        first value to start with
    step : float
        size of the step
    N : int
        number of steps

    Returns
    -------
    out : array_like
        array of length N from start to start+N*step (not included)
    """
    return np.arange(start, start + N * step, step=step)

def dump_edges(E, N):
    """
    Remove N samples from the front and end of the input field.
    """
    return E[N:-N]

def lfsr_int(seed, mask):
    """
    A linear feedback shift register, using Galois or internal XOR
    implementation.

    Parameters
    ----------
    seed : int
        an integer representing the list of bits as the starting point of the
        register. Length N
    mask : int
        Determines the polynomial of the shift register (length N+1). The
        first and last bit of the mask must be 1.

    Yields
    ------
    xor : int
        output bit of the register
    state : int
        state of the register
    """
    state = seed
    nbits = mask.bit_length() - 1
    while True:
        state = (state << 1)
        xor = state >> nbits
        #the modulus operation on has an effect if the last bit is 1
        if xor != 0:
            state ^= mask  #this performs the modulus operation
        yield xor, state

def lfsr_ext(seed, taps, nbits):
    """A Fibonacci or external XOR linear feedback shift register.

    Parameters
    ----------
    seed : int
        binary number denoting the input state registers
    taps  : list
        list of registers that are input to the XOR (length 2)
    nbits : int
        number of registers

    Yields
    ------
    xor : int
        output bit of the registers
    state : int
        state of the register
    """
    sr = seed
    while 1:
        xor = 0
        for t in taps:
            if (sr & (1 << (nbits - t))) != 0:
                xor ^= 1
        sr = (xor << nbits - 1) + (sr >> 1)
        yield xor, sr

def bool2bin(x):
    """
    Convert an array of boolean values into a binary number. If the input
    array is not a array of booleans it will be converted.
    """
    assert len(x) < 64, "array must not be longer than 63"
    x = np.asarray(x, dtype=bool)
    y = 0
    for i, j in enumerate(x):
        y += j << i
    return y


def find_offset(sequence, data):
    """
    Find index where binary sequence occurs fist in the binary data array

    Parameters
    ----------
    sequence : array_like
        sequence to search for inside the data
    data : array_like
        data array in which to find the sequence

    It is required that len(data) > sequence

    Returns
    -------
    idx : int
        index where sequence first occurs in data
    """
    assert len(data) > len(sequence), "data has to be longer than sequence"
    if not data.dtype == sequence.dtype:
        raise Warning("""data and sequence are not the same dtype, converting
        data to dtype of sequence""")
        data = data.astype(sequence.dtype)
    # using this string conversion method is much faster than array methods,
    # however it only finds the first occurence
    return data.tostring().index(sequence.tostring()) // data.itemsize


def rolling_window(data, size):
    """
    Reshapes a 1D array into a 2D array with overlapping frames. Stops when the
    last value of data is reached.

    Parameters
    ----------
    data : array_like
        Data array to segment
    size : int
        The frame size

    Returns
    -------
    out : array_like
        output segmented 2D array


    Examples
    >>> utils.rolling_window(np.arange(10), 3)
    array([[0, 1, 2],
            [1, 2, 3],
            [2, 3, 4],
            [3, 4, 5],
            [4, 5, 6],
            [5, 6, 7],
            [6, 7, 8],
            [7, 8, 9]])
    """
    shape = data.shape[:-1] + (data.shape[-1] - size + 1, size)
    strides = data.strides + (data.strides[-1], )
    return np.lib.stride_tricks.as_strided(data, shape=shape, strides=strides)

def rcos_time(t, beta, T):
    """Time response of a raised cosine filter with a given roll-off factor and width """
    return np.sinc(t / T) * np.cos(t / T * np.pi * beta) / (1 - 4 *
                                                            (beta * t / T)**2)

def rcos_freq(f, beta, T):
    """Frequency response of a raised cosine filter with a given roll-off factor and width """
    rc = np.zeros(f.shape[0], dtype=f.dtype)
    rc[np.where(np.abs(f) <= (1 - beta) / (2 * T))] = T
    idx = np.where((np.abs(f) > (1 - beta) / (2 * T)) & (np.abs(f) <= (
        1 + beta) / (2 * T)))
    rc[idx] = T / 2 * (1 + np.cos(np.pi * T / beta *
                                                     (np.abs(f[idx]) - (1 - beta) /
                                                      (2 * T))))
    return rc

def rrcos_freq(f, beta, T):
    """Frequency transfer function of the square-root-raised cosine filter with a given roll-off factor and time width/sampling period after _[1]

    Parameters
    ----------

    f   : array_like
        frequency vector
    beta : float
        roll-off factor needs to be between 0 and 1 (0 corresponds to a sinc pulse, square spectrum)

    T   : float
        symbol period

    Returns
    -------
    y   : array_like
       filter response

    References
    ----------
    ..[1] B.P. Lathi, Z. Ding Modern Digital and Analog Communication Systems
    """
    return np.sqrt(rcos_freq(f, beta, T))

def rrcos_time(t, beta, T):
    """Time impulse response of the square-root-raised cosine filter with a given roll-off factor and time width/sampling period after _[1]
    This implementation differs by a factor 2 from the previous.

    Parameters
    ----------

    t   : array_like
        time vector
    beta : float
        roll-off factor needs to be between 0 and 1 (0 corresponds to a sinc pulse, square spectrum)

    T   : float
        symbol period

    Returns
    -------
    y   : array_like
       filter response

    References
    ----------
    ..[1] https://en.wikipedia.org/wiki/Root-raised-cosine_filter
    """
    rrcos = 1/T*((np.sin(np.pi*t/T*(1-beta)) +  4*beta*t/T*np.cos(np.pi*t/T*(1+beta)))/(np.pi*t/T*(1-(4*beta*t/T)**2)))
    eps = abs(t[0]-t[1])/4
    idx1 = np.where(abs(t)<eps)
    rrcos[idx1] = 1/T*(1+beta*(4/np.pi-1))
    idx2 = np.where(abs(abs(t)-abs(T/(4*beta)))<eps)
    rrcos[idx2] = beta/(T*np.sqrt(2))*((1+2/np.pi)*np.sin(np.pi/(4*beta))+(1-2/np.pi)*np.cos(np.pi/(4*beta)))
    return rrcos

def bin2gray(value):
    """
    Convert a binary value to an gray coded value see _[1]. This also works for arrays.
    ..[1] https://en.wikipedia.org/wiki/Gray_code#Constructing_an_n-bit_Gray_code
    """
    return value^(value >> 1)

def convert_iqtosinglebitstream(idat, qdat, nbits):
    """
    Interleave a two bitstreams into a single bitstream with nbits per symbol. This can be used to create a combined PRBS signal from 2 PRBS sequences for I and Q channel. If nbits is odd we will use nbits//2 + 1 bits from the first stream and nbits//2 from the second.

    Parameters
    ----------
    idat    : array_like
        input data stream (1D array of booleans)
    qdat    : array_like
        input data stream (1D array of booleans)
    nbits   : int
        number of bits per symbol that we want after interleaving

    Returns
    -------
    output   : array_like
        interleaved bit stream
    """
    if nbits%2:
        N = [nbits//2+1, nbits//2]
    else:
        N = [nbits//2, nbits//2]
    idat_n = idat[:len(idat)-(len(idat)%N[0])]
    idat_n = idat_n.reshape(N[0], len(idat_n)/N[0])
    qdat_n = qdat[:len(qdat)-(len(qdat)%N[1])]
    qdat_n = qdat_n.reshape(N[1], len(qdat_n)/N[1])
    l = min(len(idat_n[0]), len(qdat_n[0]))
    return np.hstack([idat_n[:l], qdat_n[:l]]).flatten()
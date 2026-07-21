# analyze.py
import numpy as np
from scipy import signal

############################################################################################
# Functions to detrend the power and phase timeseries
############################################################################################

def power_detrend(power, datarate=50, cutoff=0.1):
    '''
    Detrend a raw power time series using a 6th order butterworth filter.

    Input
    -----
    power: High-rate raw power time series
    datarate: Cadence of the power timeseries in Hz (default=50)
    cutoff: High-pass cutoff frequency (default=0.1)

    Returns
    -------
    power_detrend: High-rate detrended power time series

    Notes
    -----
    - This function is most effient if input power time series is an array not a list.
    - Output is in relative units, so it will be oscillations around 1.
    '''

    sos = signal.butter(6, cutoff, 'low', fs=datarate, output='sos')
    trend = signal.sosfiltfilt(sos, power)

    power_detrend = power/trend
    
    return power_detrend


def phase_detrend(phase, datarate=50, cutoff=0.1):
    '''
    Detrend a raw power time series using a 6th order butterworth filter.

    Input
    -----
    phase: High-rate raw phase time series
    datarate: Cadence of the power timeseries in Hz (default=50)
    cutoff: High-pass cutoff frequency (default=0.1)

    Returns
    -------
    phase_detrend: High-rate detrended phase time series

    Notes
    -----
    - This function is most effient if input power time series is an array not a list.
    - Output should be purturbations around zero.
    '''

    sos = signal.butter(6, cutoff, 'high', fs=datarate, output='sos')
    phase_detrend = signal.sosfiltfilt(sos, phase)

    return phase_detrend

# def phase_detrend_bp(utime, phase, cutoff_low=0.0005, cutoff_high=0.1):
#     datarate = 1./np.mean(np.diff(utime))
#     sos = signal.butter(6, [cutoff_low, cutoff_high], 'bandpass', fs=datarate, output='sos')
#     phase_detrend = signal.sosfiltfilt(sos, phase)

#     return phase_detrend


############################################################################################
# Basic functions to caluclate scintillation indices, S_4 (power) and sigma_phi (phase)
############################################################################################

def S_4(power, window, datarate=1):
    '''
    Calculate the S4 (power) scintillation index
    
    Input
    -----
    power: detrended power time series
    window: window over which to calculate scintillation indices in seconds
    datarate: cadence of the input power time series in Hz

    Returns
    -------
    S4: power scintillation indices on a shifting window
    '''

    hw = int(window/2.*datarate)    # half window in points

    rw = np.lib.stride_tricks.sliding_window_view(power,hw*2)
    rw = np.delete(rw,len(rw)-1,0) # Delete last row for accurate results
    
    return np.concatenate(([np.nan]*hw,np.std(rw,axis=1,ddof=0) / abs(np.mean(rw,axis=1)), [np.nan]*hw), axis=None)


def sigma_phi(phase, window, datarate=1):
    '''
    Calculate the sigma_phi (phase) scintillation index
    
    Input
    -----
    phase: detrended phase time series
    window: window over which to calculate scintillation indices in seconds
    datarate: cadence of the input phase time series in Hz

    Returns
    -------
    sigma_phi: phase scintillation indices on a shifting window
    '''

    hw = int(window/2.*datarate)    # half window in points

    rw = np.lib.stride_tricks.sliding_window_view(phase,hw*2)
    rw = np.delete(rw,len(rw)-1,0) # Delete last row for accurate results
    
    return np.concatenate(([np.nan]*hw, np.std(rw, axis=1, ddof=0), [np.nan]*hw), axis=None)


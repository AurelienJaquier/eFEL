# pylint: disable=W0611, W0612, F0401, R0914, C0302

"""General tests of eFEL"""


"""
Copyright (c) 2015, Blue Brain Project/EPFL

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
  * Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.
  * Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in the
    documentation and/or other materials provided with the distribution.
  * Neither the name of the copyright holder nor the
    names of its contributors may be used to endorse or promote products
    derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

from pathlib import Path
import numpy

import pytest

from efel.io import load_ascii_input


testdata_dir = Path(__file__).parent / 'testdata'
meanfrequency1_url = testdata_dir / 'basic' / 'mean_frequency_1.txt'
ahptest1_url = testdata_dir / 'basic' / 'ahptest_1.txt'
tau20_0_url = testdata_dir / 'basic' / 'tau20.0.csv'
spikeoutsidestim_url = testdata_dir / 'basic' / 'spike_outside_stim.txt'
sagtrace1_url = testdata_dir / 'basic' / 'sagtrace_1.txt'
zeroISIlog1_url = testdata_dir / 'basic' / 'zero_ISI_log_slope_skip95824004.abf.csv'
derivwindow1_url = testdata_dir / 'basic' / 'derivwindow.txt'
dendriticAP_url = testdata_dir / 'basic' / 'dendritic_AP.txt'
burst1_url = testdata_dir / 'basic' / 'init_burst1.txt'
burst2_url = testdata_dir / 'basic' / 'init_burst2.txt'
burst3_url = testdata_dir / 'basic' / 'init_burst3.txt'
spiking_from_beginning_to_end_url = (
    testdata_dir
    / 'basic'
    / 'spiking_from_beginning_to_end.txt'
)


def load_data(data_name, interp=False, interp_dt=0.1):
    """Load data file"""
    trace = {}
    if data_name == 'mean_frequency1':
        stim_start = 500.0
        stim_end = 900.0
        time, voltage = load_ascii_input(meanfrequency1_url)
    elif data_name == 'tau20.0':
        stim_start = 100.0
        stim_end = 1000.0
        time, voltage = load_ascii_input(tau20_0_url)
        trace['decay_start_after_stim'] = [1.0]
        trace['decay_end_after_stim'] = [10.0]
    else:
        raise ValueError('Unknown data set name: %s' % data_name)

    trace['T'] = time
    trace['V'] = voltage
    trace['stim_start'] = [stim_start]
    trace['stim_end'] = [stim_end]

    if interp:
        time, voltage = interpolate(time, voltage, interp_dt)
    return trace, time, voltage, stim_start, stim_end


def test_import():
    """basic: Test importing of eFEL."""
    import efel


def test_version():
    """basic: Test if version number exists."""
    import efel
    efel.reset()

    assert efel.__version__ is not None


def test_setDependencyFileLocation_wrongpath():
    """basic: Test if setDependencyFileLocation fails if path doesn't exist."""
    import efel
    efel.reset()
    pytest.raises(
        Exception,
        efel.setDependencyFileLocation, "thisfiledoesntexist")


def test_setDependencyFileLocation():
    """basic: Test if setDependencyFileLocation works."""
    import efel
    efel.reset()
    dep_file = str(Path(__file__).parent / 'DependencyV5_LibV5peakindices.txt')
    efel.setDependencyFileLocation(dep_file)
    result = efel.getDependencyFileLocation()
    assert result == dep_file


def test_nonexisting_feature():
    """basic: Test nonexisting feature."""
    import efel
    efel.reset()

    trace = {}
    trace['T'] = numpy.arange(0, 100, 0.1)
    trace['V'] = numpy.ones(len(trace['T'])) * -80.0
    trace['stim_start'] = [25]
    trace['stim_end'] = [75]

    pytest.raises(
        RuntimeError,
        efel.getFeatureValues,
        [trace],
        ['nonexisting_feature'])


def test_failing_double_feature():
    """basic: Test failing double feature."""
    import efel
    efel.reset()

    trace = {}
    trace['T'] = numpy.arange(0, 100, 0.1)
    trace['V'] = numpy.ones(len(trace['T'])) * -80.0
    trace['stim_start'] = [25]
    trace['stim_end'] = [75]

    feature_value = efel.getFeatureValues(
        [trace],
        ['AP_amplitude'], raise_warnings=False)[0]['AP_amplitude']

    assert feature_value is None


def test_raise_warnings():
    """basic: Test raise_warnings"""

    import efel
    efel.reset()

    trace = {}
    trace['T'] = numpy.arange(0, 100, 0.1)
    trace['V'] = numpy.ones(len(trace['T'])) * -80.0
    trace['stim_start'] = [25]
    trace['stim_end'] = [75]

    import warnings

    with warnings.catch_warnings(record=True) as warning:
        warnings.simplefilter("always")
        feature_value = efel.getFeatureValues(
            [trace],
            ['AP_amplitude'])[0]['AP_amplitude']

        assert feature_value is None
        assert len(warning) == 1
        assert ("Error while calculating feature AP_amplitude" in
                str(warning[0].message))

    with warnings.catch_warnings(record=True) as warning:
        warnings.simplefilter("always")
        feature_value = efel.getFeatureValues(
            [trace],
            ['AP_amplitude'], raise_warnings=False)[0]['AP_amplitude']

        assert feature_value is None
        assert len(warning) == 0


def test_failing_int_feature():
    """basic: Test failing int feature"""

    import efel
    efel.reset()

    trace = {}
    trace['T'] = numpy.arange(0, 100, 0.1)
    trace['V'] = numpy.ones(len(trace['T'])) * -80.0
    trace['stim_start'] = [25]
    trace['stim_end'] = [75]

    feature_value = efel.getFeatureValues(
        [trace],
        ['burst_number'], raise_warnings=False)[0]['burst_number']

    assert feature_value is None


def test_empty_trace():
    """basic: Test results for empty trace"""

    import efel
    efel.reset()

    max_time = 3000.0
    stim_start = 700.0
    stim_end = 2700.0
    dt = 0.02

    time = numpy.arange(0.0, max_time, dt)
    voltage = -80.0 * numpy.ones(len(time))

    trace = {}

    trace['T'] = time
    trace['V'] = voltage
    trace['stim_start'] = [stim_start]
    trace['stim_end'] = [stim_end]

    features = [
        'time_to_last_spike',
        'inv_time_to_first_spike',
        'inv_first_ISI',
        'inv_second_ISI',
        'inv_third_ISI',
        'inv_fourth_ISI',
        'inv_fifth_ISI',
        'inv_last_ISI']

    # efel.getFeatureValues([trace], features)

    for feature, value in \
            efel.getFeatureValues([trace], features)[0].items():

        assert value[0] == 0.0


def test_multiprocessing_traces():
    """basic: Test multiprocessing map"""
    import efel
    efel.reset()

    stim_start = 31.2
    stim_end = 431.2
    time1, voltage1 = load_ascii_input(zeroISIlog1_url)

    trace1 = {}

    trace1['T'] = time1
    trace1['V'] = voltage1
    trace1['stim_start'] = [stim_start]
    trace1['stim_end'] = [stim_end]

    feature_name = 'peak_time'

    test_data_path = testdata_dir / 'basic' / 'AP_begin_indices_95810005.abf.csv'
    data2 = numpy.loadtxt(test_data_path)

    voltage2 = data2
    time2 = numpy.arange(len(voltage2)) * 0.1

    trace2 = {}

    trace2['T'] = time2
    trace2['V'] = voltage2
    trace2['stim_start'] = [stim_start]
    trace2['stim_end'] = [stim_end]

    feature_values_serial = efel.getFeatureValues(
        [trace1, trace2],
        [feature_name], raise_warnings=False)

    efel.reset()
    import multiprocessing
    pool = multiprocessing.Pool()

    feature_values_parallel = efel.getFeatureValues(
        [trace1, trace2],
        [feature_name], parallel_map=pool.map, raise_warnings=False)

    assert (
        list(feature_values_serial[0]['peak_time']) ==
        list(feature_values_parallel[0]['peak_time']))
    assert (
        list(feature_values_serial[1]['peak_time']) ==
        list(feature_values_parallel[1]['peak_time']))

    feature_values_async = efel.getFeatureValues(
        [trace1, trace2], [feature_name], parallel_map=pool.map_async,
        return_list=False, raise_warnings=False)
    assert isinstance(
        feature_values_async,
        multiprocessing.pool.MapResult)


def test_consecutive_traces():
    """basic: Test if features from two different traces give other results."""
    import efel
    efel.reset()

    stim_start = 31.2
    stim_end = 431.2
    time1, voltage1 = load_ascii_input(zeroISIlog1_url)

    trace1 = {}

    trace1['T'] = time1
    trace1['V'] = voltage1
    trace1['stim_start'] = [stim_start]
    trace1['stim_end'] = [stim_end]

    feature_name = 'peak_time'

    feature_values1 = \
        efel.getFeatureValues(
            [trace1],
            [feature_name], raise_warnings=False)

    test_data_path = testdata_dir / 'basic' / 'AP_begin_indices_95810005.abf.csv'
    data2 = numpy.loadtxt(test_data_path)

    voltage2 = data2
    time2 = numpy.arange(len(voltage2)) * 0.1

    trace2 = {}

    trace2['T'] = time2
    trace2['V'] = voltage2
    trace2['stim_start'] = [stim_start]
    trace2['stim_end'] = [stim_end]

    feature_values2 = \
        efel.getFeatureValues(
            [trace2],
            [feature_name], raise_warnings=False)

    assert (
        len(feature_values1[0][feature_name]) !=
        len(feature_values2[0][feature_name]))


def test_stimstart_stimend():
    """basic: Test exception when stimstart or stimend are wrong"""

    import efel
    efel.reset()

    stim_start = 500.0
    stim_end = 900.0
    time, voltage = load_ascii_input(meanfrequency1_url)
    trace = {}

    trace['T'] = time
    trace['V'] = voltage
    trace['stim_start'] = stim_start
    trace['stim_end'] = stim_end

    features = ['AP_begin_voltage']

    pytest.raises(
        Exception,
        efel.getFeatureValues, [trace], features)

    trace['stim_start'] = [stim_end]
    trace['stim_end'] = [stim_start]

    pytest.raises(
        Exception,
        efel.getFeatureValues, [trace], features)

    trace['stim_start'] = [stim_start, stim_end]
    trace['stim_end'] = [stim_end]

    pytest.raises(
        Exception,
        efel.getFeatureValues, [trace], features)

    del trace['stim_start']

    pytest.raises(
        Exception,
        efel.getFeatureValues, [trace], features)


def test_setDerivativeThreshold():
    """basic: Test setDerivativeThreshold"""

    import efel
    efel.reset()

    stim_start = 500.0
    stim_end = 900.0
    time, voltage = load_ascii_input(meanfrequency1_url)
    trace = {}

    trace['T'] = time
    trace['V'] = voltage
    trace['stim_start'] = [stim_start]
    trace['stim_end'] = [stim_end]

    features = ['AP_begin_voltage']

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features)
    AP_begin_voltage_orig = feature_values[0]['AP_begin_voltage'][1]

    efel.setDerivativeThreshold(5)
    feature_values = \
        efel.getFeatureValues(
            [trace],
            features)
    AP_begin_voltage = feature_values[0]['AP_begin_voltage'][1]
    numpy.testing.assert_allclose(AP_begin_voltage, -51.6400489995987)
    assert AP_begin_voltage != AP_begin_voltage_orig


def interpolate(time, voltage, new_dt):
    """Interpolate voltage to new dt"""

    interp_time = numpy.arange(time[0], time[-1] + new_dt, new_dt)
    interp_voltage = numpy.interp(interp_time, time, voltage)

    return interp_time, interp_voltage


def test_interpolate():
    """basic: Test interpolate"""

    import efel
    efel.reset()
    trace, time, voltage, stim_start, stim_end = load_data(
        'mean_frequency1', interp=True)

    features = ['time', 'voltage']

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features, raise_warnings=False)
    interp_time = feature_values[0]['time']
    interp_voltage = feature_values[0]['voltage']
    assert len(interp_time) == len(time)
    assert len(interp_voltage) == len(voltage)
    assert numpy.allclose(interp_voltage, voltage)


def test_zero_ISI_log_slope_skip():
    """basic: Test zero ISI_log_slope_skip"""

    import efel
    efel.reset()

    stim_start = 31.2
    stim_end = 431.2

    time, voltage = load_ascii_input(zeroISIlog1_url)
    trace = {}

    trace['T'] = time
    trace['V'] = voltage
    trace['stim_start'] = [stim_start]
    trace['stim_end'] = [stim_end]

    features = ['ISI_log_slope_skip']

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features, raise_warnings=False)
    assert feature_values[0]['ISI_log_slope_skip'] is None


def test_peak_indices():
    """basic: Test peak_indices."""
    import efel
    efel.reset()

    stim_start = 650.0
    stim_end = 900.0

    time, voltage = load_ascii_input(meanfrequency1_url)
    trace = {}

    trace['T'] = time
    trace['V'] = voltage
    trace['stim_start'] = [stim_start]
    trace['stim_end'] = [stim_end]

    features = ['peak_indices']

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features, raise_warnings=False)

    peak_indices = feature_values[0]['peak_indices']

    assert len(peak_indices) == 5


def test_min_AHP_indices():
    """basic: Test min_AHP_indices"""

    import efel
    efel.reset()

    stim_start = 650.0
    stim_end = 900.0

    time, voltage = load_ascii_input(meanfrequency1_url)
    trace = {}

    trace['T'] = time
    trace['V'] = voltage
    trace['stim_start'] = [stim_start]
    trace['stim_end'] = [stim_end]

    features = ['min_AHP_indices']

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features, raise_warnings=False)

    min_AHP_indices = feature_values[0]['min_AHP_indices']

    assert len(min_AHP_indices) == 5


def test_min_AHP_indices_strict():
    """basic: Test min_AHP_indices with strict_stiminterval"""

    import efel

    for strict, n_of_ahp in [(False, 17), (True, 16)]:
        efel.reset()
        efel.setIntSetting('strict_stiminterval', strict)

        stim_start = 700.0
        stim_end = 2700.0

        time, voltage = load_ascii_input(ahptest1_url)

        trace = {}

        trace['T'] = time
        trace['V'] = voltage
        trace['stim_start'] = [stim_start]
        trace['stim_end'] = [stim_end]

        features = ['min_AHP_indices', 'AHP_time_from_peak', 'peak_time']

        feature_values = \
            efel.getFeatureValues(
                [trace],
                features, raise_warnings=False)

        min_AHP_indices = feature_values[0]['min_AHP_indices']
        AHP_time_from_peak = feature_values[0]['AHP_time_from_peak']

        assert len(min_AHP_indices) == n_of_ahp
        assert len(AHP_time_from_peak) == n_of_ahp


def test_min_AHP_indices_single_peak():
    """basic: Test min_AHP_indices with a single peak."""

    import efel

    trace_file = testdata_dir / 'basic' / 'min_AHP_values_single_peak.txt'
    trace_values = numpy.loadtxt(trace_file)

    trace = {}
    trace["T"] = trace_values[:, 0]
    trace["V"] = trace_values[:, 1]
    trace["stim_start"] = [1950]
    trace["stim_end"] = [2050]

    feats = efel.getFeatureValues(
        [trace], ["min_AHP_values", "min_AHP_indices", "peak_indices"])

    assert len(feats[0]["peak_indices"]) == 1
    assert feats[0]["min_AHP_indices"] is None
    assert feats[0]["min_AHP_values"] is None


def test_strict_stiminterval():
    """basic: Test strict_stiminterval"""

    import efel

    for strict, n_of_spikes in [(False, 5), (True, 3)]:
        efel.reset()
        efel.setIntSetting("strict_stiminterval", strict)

        stim_start = 600.0
        stim_end = 750.0

        time, voltage = load_ascii_input(meanfrequency1_url)
        trace = {}

        trace['T'] = time
        trace['V'] = voltage
        trace['stim_start'] = [stim_start]
        trace['stim_end'] = [stim_end]

        features = ['peak_indices', 'peak_time', 'Spikecount']

        feature_values = \
            efel.getFeatureValues(
                [trace],
                features, raise_warnings=False)

        peak_indices = feature_values[0]['peak_indices']
        peak_time = feature_values[0]['peak_time']
        spikecount = feature_values[0]['Spikecount']

        assert len(peak_indices) == n_of_spikes
        assert len(peak_time) == n_of_spikes
        assert spikecount == n_of_spikes


def test_ISI_log_slope():
    """basic: Test ISI_log_slope"""

    import efel
    efel.reset()

    stim_start = 500.0
    stim_end = 900.0

    time, voltage = load_ascii_input(meanfrequency1_url)
    trace = {}

    trace['T'] = time
    trace['V'] = voltage
    trace['stim_start'] = [stim_start]
    trace['stim_end'] = [stim_end]

    features = ['ISI_values', 'ISI_log_slope']

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features, raise_warnings=False)
    isi_values = feature_values[0]['ISI_values']
    x_values = numpy.arange(0, len(isi_values)) + 1.0

    # fit
    log_x_values = numpy.log(x_values)
    log_isi_values = numpy.log(isi_values)
    slope, _ = numpy.polyfit(log_x_values, log_isi_values, 1)

    numpy.testing.assert_allclose(feature_values[0]['ISI_log_slope'][0], slope)


def test_ISI_values_noIgnore():
    """basic: Test test_ISI_values without Ignoring the first spike"""

    import efel
    efel.reset()

    stim_start = 500.0
    stim_end = 900.0

    time, voltage = load_ascii_input(meanfrequency1_url)
    trace = {}

    trace['T'] = time
    trace['V'] = voltage
    trace['stim_start'] = [stim_start]
    trace['stim_end'] = [stim_end]

    features = ['ISI_values']

    efel.setIntSetting("ignore_first_ISI", 0)

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features, raise_warnings=False)
    isi_values_no_ignore = feature_values[0]['ISI_values']

    efel.reset()
    efel.setIntSetting("ignore_first_ISI", 1)

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features, raise_warnings=False)
    isi_values = feature_values[0]['ISI_values']

    numpy.testing.assert_equal(len(isi_values) + 1, len(isi_values_no_ignore))


def test_ISI_semilog_slope():
    """basic: Test ISI_semilog_slope"""

    import efel
    efel.reset()

    stim_start = 500.0
    stim_end = 900.0

    time, voltage = load_ascii_input(meanfrequency1_url)
    trace = {}

    trace['T'] = time
    trace['V'] = voltage
    trace['stim_start'] = [stim_start]
    trace['stim_end'] = [stim_end]

    features = ['ISI_values', 'ISI_semilog_slope']

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features, raise_warnings=False)
    isi_values = feature_values[0]['ISI_values']
    x_values = numpy.arange(0, len(isi_values)) + 1.0

    # fit
    x_values = x_values
    log_isi_values = numpy.log(isi_values)
    slope, _ = numpy.polyfit(x_values, log_isi_values, 1)

    numpy.testing.assert_allclose(
        feature_values[0]['ISI_semilog_slope'][0], slope
    )


def test_AP_begin_indices1():
    """basic: Test AP_begin_indices 1"""
    import efel
    efel.reset()

    stim_start = 31.2
    stim_end = 431.2

    test_data_path = testdata_dir / 'basic' / 'AP_begin_indices_95810005.abf.csv'
    voltage = numpy.loadtxt(test_data_path)

    time = numpy.arange(len(voltage)) * 0.1

    trace = {}

    trace['V'] = voltage
    trace['T'] = time
    trace['stim_start'] = [stim_start]
    trace['stim_end'] = [stim_end]

    features = [
        'AP_begin_indices',
        'AP_amplitude',
        'peak_time',
        'AP_duration_half_width']

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features,
            raise_warnings=False)
    # Make sure the amount of peak_times, AP_begin_indices and AP_amplitude is
    # the same in this trace
    # There was originally an issue in this case due to the 'width' value
    # in AP_begin_indices, which caused a segmentation fault
    assert (
        len(feature_values[0]['AP_begin_indices']) ==
        len(feature_values[0]['AP_amplitude']))
    assert (
        len(feature_values[0]['AP_begin_indices']) ==
        len(feature_values[0]['peak_time']))
    assert (
        len(feature_values[0]['AP_begin_indices']) ==
        len(feature_values[0]['AP_duration_half_width']))


def test_AP_end_indices():
    """basic: Test AP end indices."""
    import efel
    efel.reset()

    stim_start = 31.2
    stim_end = 431.2

    test_data_path = testdata_dir / 'basic' / 'AP_begin_indices_95810005.abf.csv'
    voltage = numpy.loadtxt(test_data_path)

    time = numpy.arange(len(voltage)) * 0.1

    trace = {}

    trace['V'] = voltage
    trace['T'] = time
    trace['stim_start'] = [stim_start]
    trace['stim_end'] = [stim_end]

    features = [
        'AP_begin_indices',
        'peak_indices',
        'AP_end_indices']

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features,
            raise_warnings=False)

    begin_indices = feature_values[0]["AP_begin_indices"]
    peak_indices = feature_values[0]["peak_indices"]
    end_indices = feature_values[0]["AP_end_indices"]

    for begin, peak, end in zip(begin_indices, peak_indices, end_indices):
        # the voltage value for the end index should be closer than that of
        # begin index than the peak
        assert (abs(voltage[begin] - voltage[end])
                < abs(voltage[peak] - voltage[end]))
        assert end > begin

    efel.reset()

    efel.setDoubleSetting("DownDerivativeThreshold", -24)
    feature_values = \
        efel.getFeatureValues(
            [trace],
            features,
            raise_warnings=False)

    updated_end_indices = feature_values[0]["AP_end_indices"]

    for end_index, updated_end_index in zip(end_indices, updated_end_indices):
        assert end_index != updated_end_index


def test_mean_frequency1():
    """basic: Test mean_frequency 1"""

    import efel
    efel.reset()

    trace, time, voltage, stim_start, stim_end = load_data(
        'mean_frequency1', interp=True)

    features = ['mean_frequency', 'peak_time']

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features)

    peak_times = feature_values[0]['peak_time']

    stim_spikes = peak_times[numpy.where((stim_start <= peak_times)
                                         & (peak_times <= stim_end))]
    n_of_spikes = len(stim_spikes)

    mean_frequency = float(n_of_spikes) * 1000 / \
        (stim_spikes[-1] - stim_start)

    numpy.testing.assert_allclose(
        feature_values[0]['mean_frequency'][0],
        mean_frequency)


def test_ap_amplitude_outside_stim():
    """basic: Test AP amplitude with spike outside stim"""

    import efel
    efel.reset()

    stim_start = 700.0
    stim_end = 2700.0

    test_data_path = testdata_dir / 'basic' / 'spike_outside_stim.txt'
    data = numpy.loadtxt(test_data_path)

    time = data[:, 0]
    voltage = data[:, 1]

    trace = {}

    trace['T'] = time
    trace['V'] = voltage
    trace['stim_start'] = [stim_start]
    trace['stim_end'] = [stim_end]

    features = ['AP_amplitude', 'peak_time']

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features,
            raise_warnings=False)

    # Make sure AP_amplitude doesn't pick up the two spikes outside of
    # the stimulus
    # (which are present in peak_time)
    assert (
        len(feature_values[0]['AP_amplitude']) + 2 ==
        len(feature_values[0]['peak_time']))


def test_ap_amplitude_from_voltagebase1():
    """basic: Test AP_amplitude_from_voltagebase 1"""

    import efel
    efel.reset()

    stim_start = 500.0
    stim_end = 900.0

    time, voltage = load_ascii_input(meanfrequency1_url)

    trace = {}

    trace['T'] = time
    trace['V'] = voltage
    trace['stim_start'] = [stim_start]
    trace['stim_end'] = [stim_end]

    features = ['AP_amplitude_from_voltagebase',
                'peak_voltage', 'voltage_base']

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features)

    voltage_base = feature_values[0]['voltage_base'][0]
    for peak_voltage, ap_amplitude_from_voltagebase in zip(
            feature_values[0]['peak_voltage'],
            feature_values[0]['AP_amplitude_from_voltagebase']):
        numpy.testing.assert_allclose(peak_voltage - voltage_base,
                                      ap_amplitude_from_voltagebase)


def test_voltagebase1():
    """basic: Test voltagebase 1"""

    import efel
    efel.reset()

    trace, time, voltage, stim_start, stim_end = load_data(
        'mean_frequency1', interp=True)

    features = ['voltage_base']

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features)

    interp_time, interp_voltage = interpolate(time, voltage, 0.1)

    voltage_base = numpy.mean(interp_voltage[numpy.where(
        (interp_time >= 0.9 * stim_start) & (interp_time <= stim_start))])

    numpy.testing.assert_allclose(voltage_base,
                                  feature_values[0]['voltage_base'][0],
                                  rtol=0, atol=1e-8)


def test_voltagebase_median():
    """basic: Test voltagebase computation with median option"""

    import efel
    efel.reset()
    efel.setStrSetting("voltage_base_mode", "median")

    trace, time, voltage, stim_start, stim_end = load_data(
        'mean_frequency1', interp=True)

    features = ['voltage_base']

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features)

    interp_time, interp_voltage = interpolate(time, voltage, 0.1)

    voltage_base = numpy.median(interp_voltage[numpy.where(
        (interp_time >= 0.9 * stim_start) & (interp_time <= stim_start))])

    numpy.testing.assert_allclose(voltage_base,
                                  feature_values[0]['voltage_base'][0],
                                  rtol=0, atol=1e-8)


def test_currentbase():
    """basic: Test currentbase"""
    import efel
    efel.reset()

    data = numpy.loadtxt(testdata_dir / 'basic' / 'current.txt')
    current = data[:, 1]
    time = data[:, 0]
    stim_start = 2.0
    stim_end = 900.0  # not to be used

    trace = {'T': time, 'I': current,
             'stim_start': [stim_start], 'stim_end': [stim_end]}

    feature_values = efel.getFeatureValues([trace], ['current_base'])

    current_base = numpy.mean(current[numpy.where(
        (time >= 0.9 * stim_start) & (time <= stim_start))])

    # nt.set_trace()
    numpy.testing.assert_allclose(current_base,
                                  feature_values[0]['current_base'][0],
                                  rtol=0, atol=1e-8)


def test_currentbase_median():
    """basic: Test currentbase with median"""
    import efel
    efel.reset()
    efel.setStrSetting("current_base_mode", "median")

    data = numpy.loadtxt(testdata_dir / 'basic' / 'current.txt')
    current = data[:, 1]
    time = data[:, 0]
    stim_start = 2.0
    stim_end = 900.0  # not to be used

    trace = {'T': time, 'I': current,
             'stim_start': [stim_start], 'stim_end': [stim_end]}

    feature_values = efel.getFeatureValues([trace], ['current_base'])

    current_base = numpy.median(current[numpy.where(
        (time >= 0.9 * stim_start) & (time <= stim_start))])

    numpy.testing.assert_allclose(current_base,
                                  feature_values[0]['current_base'][0],
                                  rtol=0, atol=1e-8)


def test_getDistance1():
    """basic: Test getDistance 1"""

    import efel
    efel.reset()

    stim_start = 500.0
    stim_end = 900.0

    time, voltage = load_ascii_input(meanfrequency1_url)

    trace = {}

    trace['T'] = time
    trace['V'] = voltage
    trace['stim_start'] = [stim_start]
    trace['stim_end'] = [stim_end]

    numpy.testing.assert_allclose(
        3.09045815935,
        efel.getDistance(
            trace,
            'AP_amplitude',
            50,
            10))


def test_getDistance_error_dist():
    """basic: Test getDistance error_dist option"""

    import efel
    efel.reset()

    stim_start = 400.0
    stim_end = 500.0

    time, voltage = load_ascii_input(meanfrequency1_url)

    trace = {}

    trace['T'] = time
    trace['V'] = voltage
    trace['stim_start'] = [stim_start]
    trace['stim_end'] = [stim_end]

    score_normal = efel.getDistance(
        trace,
        'AP_amplitude',
        50,
        10)
    score_150 = efel.getDistance(
        trace,
        'AP_amplitude',
        50,
        10,
        error_dist=150)

    numpy.testing.assert_allclose(score_normal, 250)
    numpy.testing.assert_allclose(score_150, 150)


def test_getDistance_trace_check():
    """basic: Test getDistance trace_check option"""

    import efel
    efel.reset()

    dt = 0.1

    # voltage trace at constant -70 mV
    v = numpy.zeros(int(100 / dt)) - 70.0

    # create 'spikes' at 20, 40 and 60 ms
    v[int(20 / dt):int(25 / dt)] = 20.
    v[int(40 / dt):int(45 / dt)] = 20.
    v[int(60 / dt):int(65 / dt)] = 20.

    traces = []
    trace = {}
    trace['T'] = numpy.arange(len(v)) * dt
    trace['V'] = v
    trace['stim_start'] = [10]
    trace['stim_end'] = [70]
    traces.append(trace)

    numpy.testing.assert_allclose(
        efel.getDistance(trace, 'Spikecount', 0, 1), 3.0
    )

    trace['stim_end'] = [50]

    efel.reset()
    numpy.testing.assert_allclose(
        efel.getDistance(
            trace,
            'Spikecount',
            0,
            1,
            trace_check=False),
        3.0)

    efel.reset()
    numpy.testing.assert_allclose(
        efel.getDistance(trace, 'Spikecount', 0, 1), 250.0
    )


def test_APlast_amp():
    """basic: Test APlast_amp"""

    import efel
    efel.reset()

    stim_start = 500.0
    stim_end = 900.0

    time, voltage = load_ascii_input(meanfrequency1_url)

    trace = {}

    trace['T'] = time
    trace['V'] = voltage
    trace['stim_start'] = [stim_start]
    trace['stim_end'] = [stim_end]

    features = ['AP_amplitude', 'APlast_amp']

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features)

    APlast_amp = feature_values[0]['APlast_amp'][0]
    AP_amplitude = feature_values[0]['APlast_amp']
    assert APlast_amp == AP_amplitude[-1]


def test_APlast_width():
    """basic: Test APlast_width"""

    import efel
    efel.reset()

    stim_start = 500.0
    stim_end = 900.0

    time, voltage = load_ascii_input(meanfrequency1_url)

    trace = {}

    trace['T'] = time
    trace['V'] = voltage
    trace['stim_start'] = [stim_start]
    trace['stim_end'] = [stim_end]

    features = ['spike_half_width', 'APlast_width']

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features)

    APlast_width = feature_values[0]['APlast_width'][0]
    spike_half_width = feature_values[0]['spike_half_width']
    assert APlast_width == spike_half_width[-1]


def test_derivwindow1():
    """basic: Test DerivativeWindow."""
    import efel
    efel.reset()

    stim_start = 100.0
    stim_end = 1000.0

    time, voltage = load_ascii_input(derivwindow1_url)
    trace = {}

    trace['T'] = time
    trace['V'] = voltage
    trace['stim_start'] = [stim_start]
    trace['stim_end'] = [stim_end]

    features = ['AP_begin_voltage']

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features)

    AP_begin_voltage = feature_values[0]['AP_begin_voltage'][0]
    numpy.testing.assert_allclose(AP_begin_voltage, -45.03627393790836)

    efel.reset()
    efel.setDoubleSetting('interp_step', 0.01)
    feature_values = \
        efel.getFeatureValues(
            [trace],
            features)

    AP_begin_voltage = feature_values[0]['AP_begin_voltage'][0]
    numpy.testing.assert_allclose(AP_begin_voltage, -45.5055215)

    efel.reset()
    efel.setDoubleSetting('interp_step', 0.01)
    efel.setIntSetting('DerivativeWindow', 30)
    feature_values = \
        efel.getFeatureValues(
            [trace],
            features)

    AP_begin_voltage = feature_values[0]['AP_begin_voltage'][0]
    numpy.testing.assert_allclose(AP_begin_voltage, -45.505521563640386)


def test_spikecount1():
    """basic: Test Spikecount 1"""

    import efel
    efel.reset()

    stim_start = 500.0
    stim_end = 900.0

    time, voltage = load_ascii_input(meanfrequency1_url)

    trace = {}

    trace['T'] = time
    trace['V'] = voltage
    trace['stim_start'] = [stim_start]
    trace['stim_end'] = [stim_end]

    features = ['peak_indices', 'Spikecount']

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features)

    peak_indices = feature_values[0]['peak_indices']
    spikecount = feature_values[0]['Spikecount'][0]
    assert len(peak_indices) == spikecount


def test_spikecount_stimint1():
    """basic: Test Spikecount_stimint 1."""
    import efel
    efel.reset()

    stim_start = 700.0
    stim_end = 2700.0

    time, voltage = load_ascii_input(spikeoutsidestim_url)
    trace = {}

    trace['T'] = time
    trace['V'] = voltage
    trace['stim_start'] = [stim_start]
    trace['stim_end'] = [stim_end]

    features = ['peak_time', 'Spikecount_stimint', 'Spikecount']

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features)

    peak_times = feature_values[0]['peak_time']
    spikecount = feature_values[0]['Spikecount'][0]
    spikecount_stimint = feature_values[0]['Spikecount_stimint'][0]

    interval_peaktimes, = \
        numpy.where((peak_times >= stim_start) & (peak_times <= stim_end))

    assert (
        len(interval_peaktimes) ==
        spikecount_stimint)

    assert (
        spikecount ==
        spikecount_stimint + 2)


def test_ohmic_inputresistance():
    """basic: Test ohmic_input_resistance"""

    import efel
    efel.reset()

    stim_start = 500.0
    stim_end = 900.0

    time, voltage = load_ascii_input(meanfrequency1_url)

    trace = {}

    trace['T'] = time
    trace['V'] = voltage
    trace['stim_start'] = [stim_start]
    trace['stim_end'] = [stim_end]

    features = ['ohmic_input_resistance', 'voltage_deflection']

    stimulus_current = 10.0
    efel.setDoubleSetting('stimulus_current', stimulus_current)
    feature_values = \
        efel.getFeatureValues(
            [trace],
            features)

    voltage_deflection = feature_values[0]['voltage_deflection'][0]
    ohmic_input_resistance = feature_values[0]['ohmic_input_resistance'][0]
    assert (
        ohmic_input_resistance ==
        voltage_deflection /
        stimulus_current)


def test_sag_amplitude():
    """basic: Test sag_amplitude"""

    import efel
    efel.reset()

    stim_start = 800.0
    stim_end = 3800.0

    time, voltage = load_ascii_input(sagtrace1_url)

    trace = {}

    trace['T'] = time
    trace['V'] = voltage
    trace['stim_start'] = [stim_start]
    trace['stim_end'] = [stim_end]

    features = [
        'sag_amplitude',
        'steady_state_voltage_stimend',
        'minimum_voltage']

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features)

    steady_state_voltage_stimend = feature_values[
        0]['steady_state_voltage_stimend'][0]
    minimum_voltage = feature_values[0]['minimum_voltage'][0]
    sag_amplitude = feature_values[0]['sag_amplitude'][0]
    assert (
        sag_amplitude ==
        steady_state_voltage_stimend - minimum_voltage)


def test_sag_amplitude_pos_deflect():
    """basic: Test if sag_amplitude throws error on positive deflection"""

    import efel
    efel.reset()

    stim_start = 500.0
    stim_end = 900.0

    time, voltage = load_ascii_input(meanfrequency1_url)

    trace = {}

    trace['T'] = time
    trace['V'] = voltage
    trace['stim_start'] = [stim_start]
    trace['stim_end'] = [stim_end]

    features = ['sag_amplitude']

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features,
            raise_warnings=False)

    assert (feature_values[0]['sag_amplitude'] is None)


def test_sag_ratio1():
    """basic: Test sag_ratio1"""

    import efel
    efel.reset()

    stim_start = 800.0
    stim_end = 3800.0

    time, voltage = load_ascii_input(sagtrace1_url)

    trace = {}

    trace['T'] = time
    trace['V'] = voltage
    trace['stim_start'] = [stim_start]
    trace['stim_end'] = [stim_end]

    features = [
        'sag_ratio1',
        'sag_amplitude',
        'minimum_voltage',
        'voltage_base']

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features)

    sag_amplitude = feature_values[0]['sag_amplitude'][0]
    minimum_voltage = feature_values[0]['minimum_voltage'][0]
    voltage_base = feature_values[0]['voltage_base'][0]
    sag_ratio1 = feature_values[0]['sag_ratio1'][0]
    assert (
        sag_ratio1 ==
        sag_amplitude / (voltage_base - minimum_voltage))


def test_sag_ratio1_empty():
    """basic: Test sag_ratio1 on empty trace"""

    import efel
    efel.reset()

    max_time = 3000.0
    stim_start = 700.0
    stim_end = 2700.0
    dt = 0.02

    time = numpy.arange(0.0, max_time, dt)
    voltage = -80.0 * numpy.ones(len(time))

    trace = {}

    trace['T'] = time
    trace['V'] = voltage
    trace['stim_start'] = [stim_start]
    trace['stim_end'] = [stim_end]

    features = ['sag_ratio1']

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features,
            raise_warnings=False)

    assert feature_values[0]['sag_ratio1'] is None


def test_sag_ratio2():
    """basic: Test sag_ratio2"""

    import efel
    efel.reset()

    stim_start = 800.0
    stim_end = 3800.0

    time, voltage = load_ascii_input(sagtrace1_url)

    trace = {}

    trace['T'] = time
    trace['V'] = voltage
    trace['stim_start'] = [stim_start]
    trace['stim_end'] = [stim_end]

    features = [
        'sag_ratio2',
        'minimum_voltage',
        'steady_state_voltage_stimend',
        'voltage_base']

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features)

    steady_state_voltage_stimend = \
        feature_values[0]['steady_state_voltage_stimend'][0]
    minimum_voltage = feature_values[0]['minimum_voltage'][0]
    voltage_base = feature_values[0]['voltage_base'][0]
    sag_ratio2 = feature_values[0]['sag_ratio2'][0]
    assert (
        sag_ratio2 ==
        (voltage_base - steady_state_voltage_stimend) /
        (voltage_base - minimum_voltage))


def test_ohmic_input_resistance_vb_ssse():
    """basic: Test ohmic_input_resistance_vb_ssse"""

    import efel
    efel.reset()

    stim_start = 500.0
    stim_end = 900.0

    time, voltage = load_ascii_input(meanfrequency1_url)

    trace = {}

    trace['T'] = time
    trace['V'] = voltage
    trace['stim_start'] = [stim_start]
    trace['stim_end'] = [stim_end]

    features = ['ohmic_input_resistance_vb_ssse', 'voltage_deflection_vb_ssse']

    stimulus_current = 10.0
    efel.setDoubleSetting('stimulus_current', stimulus_current)
    feature_values = \
        efel.getFeatureValues(
            [trace],
            features)

    voltage_deflection = feature_values[0]['voltage_deflection_vb_ssse'][0]
    ohmic_input_resistance = \
        feature_values[0]['ohmic_input_resistance_vb_ssse'][0]
    assert (
        ohmic_input_resistance ==
        voltage_deflection /
        stimulus_current)


def test_spikecount2():
    """basic: Test Spikecount 2: test empty trace"""

    import efel
    efel.reset()

    stim_start = 500.0
    stim_end = 900.0

    time = numpy.arange(0, 1000.0, 0.1)
    voltage = numpy.ones(len(time)) * -80.0

    trace = {}

    trace['T'] = time
    trace['V'] = voltage
    trace['stim_start'] = [stim_start]
    trace['stim_end'] = [stim_end]

    features = ['Spikecount']

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features)

    spikecount = feature_values[0]['Spikecount'][0]
    assert spikecount == 0


def test_min_voltage_between_spikes1():
    """basic: Test min_voltage_between_spikes 1"""

    import efel
    efel.reset()

    stim_start = 500.0
    stim_end = 900.0

    time, voltage = load_ascii_input(meanfrequency1_url)

    trace = {}

    trace['T'] = time
    trace['V'] = voltage
    trace['stim_start'] = [stim_start]
    trace['stim_end'] = [stim_end]

    features = ['min_voltage_between_spikes', 'peak_indices', 'voltage']

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features)

    peak_indices = feature_values[0]['peak_indices']
    min_voltage_between_spikes = feature_values[
        0]['min_voltage_between_spikes']
    fel_voltage = feature_values[0]['voltage']

    for index, min_voltage_between_spikes_value in zip(
            list(range(len(peak_indices[:-1]))),
            min_voltage_between_spikes):
        numpy.testing.assert_allclose(
            numpy.min(
                fel_voltage[
                    peak_indices[index]:peak_indices[
                        index +
                        1]]),
            min_voltage_between_spikes_value)


def test_getFeatureNames():
    """basic: Test getting all feature names"""
    import efel
    efel.reset()
    import json

    test_data_path = testdata_dir.parent / 'featurenames.json'
    with open(test_data_path, 'r') as featurenames_json:
        expected_featurenames = json.load(featurenames_json)
    assert set(efel.getFeatureNames()) == set(expected_featurenames)


def test_getFeatureNameExists():
    """basic: Test FeatureNameExists"""
    import efel
    efel.reset()
    assert efel.FeatureNameExists('voltage_base')
    assert not efel.FeatureNameExists('voltage_base_wrong')


def test_steady_state_voltage1():
    """basic: Test steady_state_voltage"""

    import efel
    efel.reset()

    trace, time, voltage, stim_start, stim_end = load_data(
        'mean_frequency1', interp=True)

    features = ['steady_state_voltage']

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features)[0]

    steady_state_voltage = numpy.mean(voltage[numpy.where(time >= stim_end)])

    numpy.testing.assert_allclose(steady_state_voltage,
                                  feature_values['steady_state_voltage'][0])


def test_steady_state_voltage_stimend():
    """basic: Test steady_state_voltage_stimend"""

    import efel
    efel.reset()

    trace, time, voltage, stim_start, stim_end = load_data(
        'mean_frequency1', interp=True)

    features = ['steady_state_voltage_stimend']

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features)[0]

    stim_duration = stim_end - stim_start
    begin_time = stim_end - 0.1 * stim_duration
    end_time = stim_end
    steady_state_voltage_stimend = numpy.mean(voltage[numpy.where(
        (time < end_time) & (time >= begin_time)
    )])

    numpy.testing.assert_allclose(
        steady_state_voltage_stimend,
        feature_values['steady_state_voltage_stimend'][0]
    )


def test_maximum_voltage_from_voltagebase():
    """basic: Test maximum_voltage_from_voltagebase"""

    import efel
    efel.reset()

    trace, time, voltage, stim_start, stim_end = load_data(
        'mean_frequency1', interp=True)

    features = ['maximum_voltage_from_voltagebase', 'voltage_base']

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features)[0]

    maximum_voltage = numpy.max(voltage[numpy.where(
        (time <= stim_end) & (time >= stim_start)
    )])

    voltage_base = feature_values['voltage_base'][0]

    maximum_voltage_from_voltagebase = maximum_voltage - voltage_base

    numpy.testing.assert_allclose(
        maximum_voltage_from_voltagebase,
        feature_values['maximum_voltage_from_voltagebase'][0])


def decay_time_constant_after_stim(time, voltage, interval_start,
                                   interval_end, stim_start, stim_end):
    """decay_time_constant_after_stim numpy implementation"""

    def get_index(ts, t):
        """get_index"""
        return next(i for i in range(len(ts)) if ts[i] >= t)

    interval_indices = numpy.where(
        (time >= interval_start) & (time < interval_end))
    stim_start_index = get_index(time, stim_start)
    interval_time = time[interval_indices] - stim_end
    interval_voltage = abs(
        voltage[interval_indices] -
        voltage[stim_start_index])

    # fit
    log_interval_voltage = numpy.log(interval_voltage)
    slope, _ = numpy.polyfit(interval_time, log_interval_voltage, 1)

    tau = -1. / slope
    return abs(tau)


def test_decay_time_constant_after_stim1():
    """basic: Test decay_time_constant_after_stim 1"""

    import efel
    efel.reset()

    trace, time, voltage, stim_start, stim_end = load_data(
        'mean_frequency1', interp=True)

    features = ['decay_time_constant_after_stim']

    feature_values = efel.getFeatureValues([trace], features)[0]

    expected = decay_time_constant_after_stim(
        time,
        voltage,
        stim_end + 1.0,
        stim_end + 10.0,
        stim_start,
        stim_end)

    numpy.testing.assert_allclose(
        expected,
        feature_values['decay_time_constant_after_stim'][0])


def test_decay_time_constant_after_stim2():
    """basic: Test decay_time_constant_after_stim 2"""

    import efel
    efel.reset()

    trace, time, voltage, stim_start, stim_end = load_data(
        'tau20.0', interp=True)

    features = ['decay_time_constant_after_stim']

    feature_values = efel.getFeatureValues([trace], features)[0]

    numpy.testing.assert_allclose(
        19.9,
        feature_values['decay_time_constant_after_stim'][0], rtol=0, atol=1e-1)


def test_multiple_decay_time_constant_after_stim():
    """basic: Test multiple_decay_time_constant_after_stim"""

    import efel
    efel.reset()

    trace, time, voltage, stim_start, stim_end = load_data(
        'mean_frequency1', interp=True)

    features = ['multiple_decay_time_constant_after_stim']

    efel.setDoubleSetting("multi_stim_start", [stim_start])
    efel.setDoubleSetting("multi_stim_end", [stim_end])

    feature_values = efel.getFeatureValues([trace], features)[0]

    expected = decay_time_constant_after_stim(
        time,
        voltage,
        stim_end + 1.0,
        stim_end + 10.0,
        stim_start,
        stim_end)

    numpy.testing.assert_allclose(
        expected,
        feature_values['multiple_decay_time_constant_after_stim'][0])


def sag_time_constant(
        time, voltage, min_v, steady_state_v, sag_ampl, stim_start, stim_end):
    """sag_time_constant numpy implementation"""
    # select t, v in stimulus interval
    start_idx = numpy.where(time == stim_start)[0][0]
    end_idx = numpy.where(time == stim_end)[0][0]
    vinterval = voltage[start_idx:end_idx]
    tinterval = time[start_idx:end_idx]

    # get start decay
    start_decay = numpy.argmin(vinterval)

    # get end decay
    v90 = steady_state_v - 0.1 * sag_ampl
    end_decay = numpy.where(
        (tinterval > tinterval[start_decay]) & (vinterval >= v90)
    )[0][0]

    v_reference = vinterval[end_decay]

    # select t, v in decay interval
    interval_indices = numpy.arange(start_decay, end_decay)
    interval_time = tinterval[interval_indices]
    interval_voltage = abs(vinterval[interval_indices] - v_reference)

    # get tau
    log_interval_voltage = numpy.log(interval_voltage)
    slope, _ = numpy.polyfit(interval_time, log_interval_voltage, 1)
    tau = abs(1. / slope)

    return tau


def test_sag_time_constant():
    """basic: Test sag_time_constant"""

    import efel
    efel.reset()

    interp_dt = 0.1

    stim_start = 800.0
    stim_end = 3800.0
    time, voltage = load_ascii_input(sagtrace1_url)
    time, voltage = interpolate(time, voltage, interp_dt)

    trace = {}
    trace['T'] = time
    trace['V'] = voltage
    trace['stim_start'] = [stim_start]
    trace['stim_end'] = [stim_end]

    features = [
        'minimum_voltage',
        'steady_state_voltage_stimend',
        'sag_time_constant',
        'sag_amplitude'
    ]
    feature_values = efel.getFeatureValues([trace], features)[0]

    min_v = feature_values['minimum_voltage'][0]
    steady_state_v = feature_values['steady_state_voltage_stimend'][0]
    sag_ampl = feature_values['sag_amplitude'][0]

    expected = sag_time_constant(
        time,
        voltage,
        min_v,
        steady_state_v,
        sag_ampl,
        stim_start,
        stim_end)

    numpy.testing.assert_allclose(
        expected,
        feature_values['sag_time_constant'][0])


def test_getmeanfeaturevalues():
    """basic: Test getMeanFeatureValues"""

    import efel
    efel.reset()

    stim_start = 500.0
    stim_end = 900.0

    time, voltage = load_ascii_input(meanfrequency1_url)

    trace = {}

    trace['T'] = time
    trace['V'] = voltage
    trace['stim_start'] = [stim_start]
    trace['stim_end'] = [stim_end]

    feature_values = \
        efel.getFeatureValues(
            [trace],
            ['AP_amplitude', 'BPAPHeightLoc1'], raise_warnings=False)

    mean_feature_values = efel.getMeanFeatureValues(
        [trace], [
            'AP_amplitude', 'BPAPHeightLoc1'], raise_warnings=False)

    assert (numpy.mean(feature_values[0]['AP_amplitude']) ==
            mean_feature_values[0]['AP_amplitude'])


def test_mean_AP_amplitude():
    """basic: Test mean_AP_amplitude"""

    import efel
    efel.reset()

    stim_start = 500.0
    stim_end = 900.0

    time, voltage = load_ascii_input(meanfrequency1_url)

    trace = {}

    trace['T'] = time
    trace['V'] = voltage
    trace['stim_start'] = [stim_start]
    trace['stim_end'] = [stim_end]

    feature_values = \
        efel.getFeatureValues(
            [trace],
            ['AP_amplitude', 'mean_AP_amplitude'], raise_warnings=False)

    assert (numpy.mean(feature_values[0]['AP_amplitude']) ==
            feature_values[0]['mean_AP_amplitude'])


def test_unfinished_peak():
    """basic: Test if unfinished peak doesn't break Spikecount"""

    import efel
    efel.setIntSetting('strict_stiminterval', True)

    dt = 0.1
    v = numpy.zeros(int(100 / dt)) - 70.0
    v[int(20 / dt):int(25 / dt)] = 20.
    v[int(40 / dt):int(45 / dt)] = 20.
    v[int(60 / dt):int(65 / dt)] = 20.

    trace = {}
    trace['T'] = numpy.arange(len(v)) * dt
    trace['V'] = v
    trace['stim_start'] = [10]
    trace['stim_end'] = [70]

    traces_results = efel.getFeatureValues([trace], ['Spikecount'])
    spikecount = traces_results[0]['Spikecount'][0]

    assert spikecount == 3

    # When the signal at the end of the trace is larger than the threshold,
    # Spikecount and possibly other features cannont be estimated.
    v[int(80 / dt):] = -19

    traces_results = efel.getFeatureValues([trace], ['Spikecount'])
    spikecount = traces_results[0]['Spikecount'][0]

    assert spikecount == 3


def rise_time_perc(
    time, voltage,
    AP_begin_indices,
    peak_indices,
    rise_start_perc,
    rise_end_perc
):
    """AP_rise_time numpy implementation with percentages"""
    rise_times = []
    AP_amp = voltage[peak_indices] - voltage[AP_begin_indices]
    begin_voltages = AP_amp * rise_start_perc + voltage[AP_begin_indices]
    end_voltages = AP_amp * rise_end_perc + voltage[AP_begin_indices]

    for AP_begin_indice, peak_indice, begin_v, end_v in zip(
        AP_begin_indices, peak_indices, begin_voltages, end_voltages
    ):
        voltage_window = voltage[AP_begin_indice:peak_indice]

        new_begin_indice = AP_begin_indice + numpy.min(
            numpy.where(voltage_window >= begin_v)[0]
        )
        new_end_indice = AP_begin_indice + numpy.max(
            numpy.where(voltage_window <= end_v)[0]
        )

        rise_times.append(time[new_end_indice] - time[new_begin_indice])

    return numpy.array(rise_times)


def test_rise_time_perc():
    """basic: Test AP rise time percentage"""

    import efel
    efel.reset()
    trace, time, voltage, stim_start, stim_end = load_data(
        'mean_frequency1', interp=True
    )

    trace['rise_start_perc'] = [0.2]
    trace['rise_end_perc'] = [0.8]

    features = ['AP_rise_time', 'AP_begin_indices', 'peak_indices']

    feature_values = efel.getFeatureValues(
        [trace], features, raise_warnings=False
    )
    ap_rise_time = feature_values[0]['AP_rise_time']
    AP_begin_indices = feature_values[0]['AP_begin_indices']
    peak_indices = feature_values[0]['peak_indices']

    expected = rise_time_perc(
        time, voltage, AP_begin_indices, peak_indices, 0.2, 0.8
    )

    for exp, rise_time in zip(expected, ap_rise_time):
        numpy.testing.assert_allclose(exp, rise_time)


def test_fall_time():
    """basic: Test AP fall time"""

    import efel
    efel.reset()
    trace, time, voltage, stim_start, stim_end = load_data(
        'mean_frequency1', interp=True
    )

    features = ['AP_fall_time', 'AP_end_indices', 'peak_indices']

    feature_values = efel.getFeatureValues(
        [trace], features, raise_warnings=False
    )
    ap_fall_time = feature_values[0]['AP_fall_time']
    AP_end_indices = feature_values[0]['AP_end_indices']
    peak_indices = feature_values[0]['peak_indices']

    # works because we have the same interpolation as in efel
    expected = time[AP_end_indices] - time[peak_indices]

    numpy.testing.assert_allclose(ap_fall_time, expected)


def test_slow_ahp_start():
    """basic: Test AHP_depth_abs_slow with a custom after spike start time"""

    import efel
    efel.reset()
    trace, time, voltage, stim_start, stim_end = load_data(
        'mean_frequency1', interp=True
    )

    trace['sahp_start'] = [12.0]

    features = ['AHP_depth_abs_slow', 'peak_indices']

    feature_values = efel.getFeatureValues(
        [trace], features, raise_warnings=False
    )
    peak_indices = feature_values[0]['peak_indices']
    ahp_depth_abs_slow = feature_values[0]['AHP_depth_abs_slow']

    expected = []
    for i in range(1, len(peak_indices) - 1):
        new_start_time = time[peak_indices[i]] + trace['sahp_start'][0]
        new_idx = numpy.min(numpy.where(time >= new_start_time)[0])
        expected.append(numpy.min(voltage[new_idx:peak_indices[i + 1]]))

    for exp, ahp_slow in zip(expected, ahp_depth_abs_slow):
        numpy.testing.assert_allclose(exp, ahp_slow)


def test_AP_peak_upstroke():
    """basic: Test AP_peak_upstroke (maximum peak rise rate)"""

    import efel
    efel.reset()
    trace, time, voltage, stim_start, stim_end = load_data(
        'mean_frequency1', interp=True
    )

    features = ['AP_peak_upstroke', 'peak_indices', 'AP_begin_indices']

    feature_values = efel.getFeatureValues(
        [trace], features, raise_warnings=False
    )
    peak_indices = feature_values[0]['peak_indices']
    ap_begin_indices = feature_values[0]['AP_begin_indices']
    ap_peak_upstroke = feature_values[0]['AP_peak_upstroke']

    expected = []
    # compute dv/dt  omit dx and /2 that cancel out in division
    dv = (
        [voltage[1] - voltage[0]]
        + list(voltage[2:] - voltage[:-2])
        + [voltage[-1] - voltage[-2]]
    )
    dt = (
        [time[1] - time[0]]
        + list(time[2:] - time[:-2])
        + [time[-1] - time[-2]]
    )
    dvdt = numpy.array(dv) / numpy.array(dt)
    # compute ap peak upstroke
    for apbi, pi in zip(ap_begin_indices, peak_indices):
        expected.append(numpy.max(dvdt[apbi:pi]))

    for exp, pus in zip(expected, ap_peak_upstroke):
        numpy.testing.assert_allclose(exp, pus, rtol=0, atol=1e-6)


def test_AP_peak_downstroke():
    """basic: Test AP_peak_downstroke (minimum peak fall rate)"""

    import efel
    efel.reset()
    trace, time, voltage, stim_start, stim_end = load_data(
        'mean_frequency1', interp=True
    )

    features = ['AP_peak_downstroke', 'peak_indices', 'min_AHP_indices']

    feature_values = efel.getFeatureValues(
        [trace], features, raise_warnings=False
    )
    peak_indices = feature_values[0]['peak_indices']
    min_ahp_indices = feature_values[0]['min_AHP_indices']
    ap_peak_downstroke = feature_values[0]['AP_peak_downstroke']

    expected = []
    # compute dv/dt  omit dx and /2 that cancel out in division
    dv = (
        [voltage[1] - voltage[0]]
        + list(voltage[2:] - voltage[:-2])
        + [voltage[-1] - voltage[-2]]
    )
    dt = (
        [time[1] - time[0]]
        + list(time[2:] - time[:-2])
        + [time[-1] - time[-2]]
    )
    dvdt = numpy.array(dv) / numpy.array(dt)
    # compute ap peak downstroke
    for ahpi, pi in zip(min_ahp_indices, peak_indices):
        expected.append(numpy.min(dvdt[pi:ahpi]))

    for exp, pds in zip(expected, ap_peak_downstroke):
        numpy.testing.assert_allclose(exp, pds, rtol=0, atol=1e-6)


def test_min_between_peaks_indices():
    """basic: Test min_between_peaks_indices"""

    import efel
    efel.reset()

    stim_start = 200.0
    stim_end = 1200.0

    time, voltage = load_ascii_input(dendriticAP_url)
    trace = {}

    trace['T'] = time
    trace['V'] = voltage
    trace['stim_start'] = [stim_start]
    trace['stim_end'] = [stim_end]

    features = ['min_AHP_indices', 'min_between_peaks_indices']

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features, raise_warnings=False)

    min_AHP_indices = feature_values[0]['min_AHP_indices'][0]
    min_btw_peaks_indices = feature_values[0]['min_between_peaks_indices'][0]

    assert min_AHP_indices < min_btw_peaks_indices


def test_min_between_peaks_values():
    """basic: Test min_between_peaks_values"""

    import efel
    efel.reset()

    stim_start = 200.0
    stim_end = 1200.0

    time, voltage = load_ascii_input(dendriticAP_url)
    time, voltage = interpolate(time, voltage, 0.1)
    trace = {}

    trace['T'] = time
    trace['V'] = voltage
    trace['stim_start'] = [stim_start]
    trace['stim_end'] = [stim_end]

    features = ['min_between_peaks_values', 'peak_indices']

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features, raise_warnings=False)

    min_btw_peaks_value = feature_values[0]['min_between_peaks_values'][0]
    peak_idx = feature_values[0]['peak_indices'][0]

    expected = numpy.min(voltage[peak_idx:])

    numpy.testing.assert_allclose(min_btw_peaks_value, expected)


def test_AP_width_between_threshold():
    """basic: Test AP_width_between_threshold"""

    import efel
    efel.reset()

    threshold = -48
    efel.setDoubleSetting("Threshold", threshold)
    stim_start = 200.0
    stim_end = 1200.0

    time, voltage = load_ascii_input(dendriticAP_url)
    time, voltage = interpolate(time, voltage, 0.1)
    trace = {}

    trace['T'] = time
    trace['V'] = voltage
    trace['stim_start'] = [stim_start]
    trace['stim_end'] = [stim_end]

    features = [
        'AP_width_between_threshold',
        'peak_indices',
        'min_between_peaks_indices'
    ]

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features, raise_warnings=False)

    AP_width = feature_values[0]['AP_width_between_threshold'][0]
    peak_idx = feature_values[0]['peak_indices'][0]
    min_after_peak_idx = feature_values[0]['min_between_peaks_indices'][0]

    t0 = time[:peak_idx][voltage[:peak_idx] > threshold][0]
    t1 = time[peak_idx:min_after_peak_idx][
        voltage[peak_idx:min_after_peak_idx] < threshold
    ][0]

    numpy.testing.assert_allclose(AP_width, t1 - t0)


def test_AP_width_between_threshold_strict():
    """basic: Test AP_width_between_threshold with strict interval"""

    import efel
    efel.reset()
    efel.setIntSetting('strict_stiminterval', True)

    threshold = -48
    efel.setDoubleSetting("Threshold", threshold)
    stim_start = 200.0
    stim_end = 1200.0

    time, voltage = load_ascii_input(dendriticAP_url)
    time, voltage = interpolate(time, voltage, 0.1)
    trace = {}

    trace['T'] = time
    trace['V'] = voltage
    trace['stim_start'] = [stim_start]
    trace['stim_end'] = [stim_end]

    features = ['AP_width_between_threshold']

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features, raise_warnings=False)

    AP_width = feature_values[0]['AP_width_between_threshold']

    assert AP_width is None


def py_mean_freq(peak_time, burst_ISI_indices):
    """Python implementation of burst_mean_freq."""
    # There is a discrepancy between peak_time indices and ISI_burst indices
    # because 1st ISI value is ignored.
    if burst_ISI_indices is None:
        return None
    # if no burst detected, do not consider all peaks in a single burst
    elif len(burst_ISI_indices) == 0:
        return []
    burst_mean_freq = []
    burst_index_tmp = burst_ISI_indices
    burst_index = numpy.insert(
        burst_index_tmp, burst_index_tmp.size, len(peak_time) - 1
    )
    burst_index = burst_index.astype(int)

    # 1st burst
    span = peak_time[burst_index[0]] - peak_time[0]
    # + 1 because 1st ISI is ignored
    N_peaks = burst_index[0] + 1
    burst_mean_freq.append(N_peaks * 1000 / span)

    for i, burst_idx in enumerate(burst_index[:-1]):
        if burst_index[i + 1] - burst_idx != 1:
            span = peak_time[burst_index[i + 1]] - peak_time[burst_idx + 1]
            N_peaks = burst_index[i + 1] - burst_idx
            burst_mean_freq.append(N_peaks * 1000 / span)

    return burst_mean_freq


def test_burst_mean_freq():
    """basic: Test burst_mean_freq"""
    urls = [burst1_url, burst2_url, burst3_url]
    expected_values = [[254.77707006363633, 8.282259400363523], None, []]

    for i, (url, expected_value) in enumerate(zip(urls, expected_values)):
        import efel
        efel.reset()

        time, voltage = load_ascii_input(url)
        time, voltage = interpolate(time, voltage, 0.1)
        trace = {}

        trace['T'] = time
        trace['V'] = voltage
        if i in [0, 1]:
            trace['stim_start'] = [250]
            trace['stim_end'] = [1600]
        elif i == 2:
            trace['stim_start'] = [800]
            trace['stim_end'] = [2150]

        features = ['burst_mean_freq', 'burst_ISI_indices', 'peak_time']

        feature_values = \
            efel.getFeatureValues(
                [trace],
                features, raise_warnings=False)

        burst_mean_freq = feature_values[0]['burst_mean_freq']
        burst_ISI_indices = feature_values[0]['burst_ISI_indices']
        peak_time = feature_values[0]['peak_time']

        burst_mean_freq_py = py_mean_freq(peak_time, burst_ISI_indices)

        if i == 1:
            assert burst_mean_freq == burst_mean_freq_py
            assert burst_mean_freq is None
        else:
            numpy.testing.assert_allclose(burst_mean_freq, burst_mean_freq_py)
            numpy.testing.assert_allclose(burst_mean_freq, expected_value)


def test_segfault_in_AP_begin_width():
    """basic: Test AP_begin_width with spike before stim and up to the end"""

    import efel
    efel.reset()

    stim_start = 20.0
    stim_end = 140.0
    trace = {}

    trace['T'], trace['V'] = load_ascii_input(
        spiking_from_beginning_to_end_url)
    trace['stim_start'] = [stim_start]
    trace['stim_end'] = [stim_end]

    features = ['AP_begin_width']

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features, raise_warnings=False)

    expected_values = [
        4.2, 7.4, 3.3, 10.8, 4.5, 5.6, 7.2, 3.4, 3.5, 3.6, 3.6]
    numpy.testing.assert_allclose(
        feature_values[0]['AP_begin_width'], expected_values)


def py_interburst_voltage(burst_ISI_idxs, peak_idxs, t, v):
    """Python implementation of interburst_voltage"""
    interburst_voltage = []
    for idx in burst_ISI_idxs:
        ts_idx = peak_idxs[idx]
        t_start = t[ts_idx] + 5
        start_idx = numpy.argwhere(t < t_start)[-1][0]

        te_idx = peak_idxs[idx + 1]
        t_end = t[te_idx] - 5
        end_idx = numpy.argwhere(t > t_end)[0][0]

        interburst_voltage.append(numpy.mean(v[start_idx:end_idx + 1]))

    return numpy.array(interburst_voltage)


def test_interburst_voltage():
    """basic: Test interburst_voltage"""
    import efel
    efel.reset()

    time, voltage = load_ascii_input(burst1_url)
    time, voltage = interpolate(time, voltage, 0.1)

    trace = {}
    trace['T'] = time
    trace['V'] = voltage
    trace['stim_start'] = [250]
    trace['stim_end'] = [1600]

    features = ['interburst_voltage', 'burst_ISI_indices', 'peak_indices']

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features, raise_warnings=False)

    interburst_voltage = feature_values[0]['interburst_voltage']
    burst_ISI_indices = feature_values[0]['burst_ISI_indices']
    peak_indices = feature_values[0]['peak_indices']

    interburst_voltage_py = py_interburst_voltage(
        burst_ISI_indices, peak_indices, time, voltage
    )

    numpy.testing.assert_allclose(interburst_voltage, interburst_voltage_py)
    numpy.testing.assert_allclose(interburst_voltage, -63.234682)


def five_point_stencil_derivative(arr):
    """Five point stencil derivative."""
    first = arr[1] - arr[0]
    second = (arr[2] - arr[0]) / 2.
    middle = (-arr[4:] + 8 * arr[3:-1] - 8 * arr[1:-3] + arr[:-4]) / 12.
    second_to_last = (arr[-1] - arr[-3]) / 2.
    last = arr[-1] - arr[-2]

    return numpy.hstack([first, second, middle, second_to_last, last])


def py_time_constant(time, voltage, stim_start, stim_end):
    """Python implementation of time_constant."""
    min_derivative = 5e-3
    decay_start_min_length = 5  # number of indices
    min_length = 10  # number of indices
    t_length = 70  # in ms

    # get start and middle indices
    stim_start_idx = numpy.where(time >= stim_start)[0][0]
    # increment stimstartindex to skip a possible transient
    stim_start_idx += 10
    stim_middle_idx = numpy.where(time >= (stim_start + stim_end) / 2.)[0][0]

    # get derivative
    t_interval = time[stim_start_idx:stim_middle_idx]
    dv = five_point_stencil_derivative(voltage[stim_start_idx:stim_middle_idx])
    dt = five_point_stencil_derivative(t_interval)
    dvdt = dv / dt

    # find start and end of decay
    # has to be over deriv threshold for at least a given number of indices
    pass_threshold_idxs = numpy.append(
        -1, numpy.argwhere(dvdt > -min_derivative).flatten()
    )
    length_idx = numpy.argwhere(
        numpy.diff(pass_threshold_idxs) > decay_start_min_length
    )[0][0]
    i_start = pass_threshold_idxs[length_idx] + 1

    # find flat (end of decay)
    flat_idxs = numpy.argwhere(dvdt[i_start:] > -min_derivative).flatten()
    # for loop is not optimised
    # but we expect the 1st few values to be the ones we are looking for
    for i in flat_idxs:
        i_flat = i + i_start
        i_flat_stop = numpy.argwhere(
            t_interval >= t_interval[i_flat] + t_length
        )[0][0]
        if numpy.mean(dvdt[i_flat:i_flat_stop]) > -min_derivative:
            break

    dvdt_decay = dvdt[i_start:i_flat]
    t_decay = time[stim_start_idx + i_start:stim_start_idx + i_flat]
    v_decay_tmp = voltage[stim_start_idx + i_start:stim_start_idx + i_flat]
    v_decay = abs(v_decay_tmp - voltage[stim_start_idx + i_flat])

    if len(dvdt_decay) < min_length:
        return None

    # -- golden search algorithm -- #
    from scipy.optimize import minimize_scalar

    def numpy_fit(x, t_decay, v_decay):
        new_v_decay = v_decay + x
        log_v_decay = numpy.log(new_v_decay)
        (slope, _), res, _, _, _ = numpy.polyfit(
            t_decay, log_v_decay, 1, full=True
        )
        range = numpy.max(log_v_decay) - numpy.min(log_v_decay)
        return res / (range * range)

    max_bound = min_derivative * 1000.
    golden_bracket = [0, max_bound]
    result = minimize_scalar(
        numpy_fit,
        args=(t_decay, v_decay),
        bracket=golden_bracket,
        method='golden',
    )

    # -- fit -- #
    log_v_decay = numpy.log(v_decay + result.x)
    slope, _ = numpy.polyfit(t_decay, log_v_decay, 1)

    tau = -1. / slope
    return abs(tau)


def test_time_constant():
    """basic: Test time constant with python implementation"""

    import efel
    efel.reset()

    stim_start = 800.0
    stim_end = 3800.0

    time, voltage = load_ascii_input(sagtrace1_url)

    trace = {}
    trace['T'] = time
    trace['V'] = voltage
    trace['stim_start'] = [stim_start]
    trace['stim_end'] = [stim_end]
    time, voltage = interpolate(time, voltage, 0.1)

    features = ["time_constant"]

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features, raise_warnings=False)

    time_cst = feature_values[0]["time_constant"]
    assert len(time_cst) == 1

    py_tau = py_time_constant(time, voltage, stim_start, stim_end)

    # some difference because precision difference
    # between efel and python implementation
    numpy.testing.assert_allclose(time_cst, py_tau, rtol=1e-3)


def test_depolarized_base():
    """basic: Test depolarized base"""

    import efel
    efel.reset()

    trace, time, voltage, stim_start, stim_end = load_data(
        'mean_frequency1', interp=True)

    features = ["depolarized_base", "AP_begin_time", "AP_duration"]

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features, raise_warnings=False)

    depolarized_base = feature_values[0]['depolarized_base']
    AP_begin_times = feature_values[0]['AP_begin_time']
    AP_durations = feature_values[0]['AP_duration']

    py_dep_base = []
    for i, (AP_begin, AP_dur) in enumerate(
        zip(AP_begin_times[:-1], AP_durations[:-1])
    ):
        dep_start_time = AP_begin + AP_dur
        dep_end_time = AP_begin_times[i + 1]
        start_idx = numpy.argwhere(time > dep_start_time)[0][0] - 1
        end_idx = numpy.argwhere(time > dep_end_time)[0][0] - 1

        py_dep_base.append(numpy.mean(voltage[start_idx:end_idx]))

    numpy.testing.assert_allclose(depolarized_base, py_dep_base)


def test_AP_duration():
    """basic: Test AP duration"""

    import efel
    efel.reset()

    trace, time, voltage, stim_start, stim_end = load_data(
        'mean_frequency1', interp=True)

    features = ["AP_duration", "AP_begin_indices", "AP_end_indices"]

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features, raise_warnings=False)

    AP_begin_indices = feature_values[0]['AP_begin_indices']
    AP_end_indices = feature_values[0]['AP_end_indices']
    AP_durations = feature_values[0]['AP_duration']

    # works here because we use the same interpolation as in efel
    py_AP_dur = time[AP_end_indices] - time[AP_begin_indices]

    numpy.testing.assert_allclose(AP_durations, py_AP_dur)


def test_AP_rise_rate():
    """basic: Test AP rise rate"""

    import efel
    efel.reset()

    trace, time, voltage, stim_start, stim_end = load_data(
        'mean_frequency1', interp=True)

    features = ["AP_rise_rate", "AP_begin_indices", "peak_indices"]

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features, raise_warnings=False)

    AP_begin_indices = feature_values[0]['AP_begin_indices']
    peak_indices = feature_values[0]['peak_indices']
    AP_rise_rate = feature_values[0]['AP_rise_rate']

    # works here because we use the same interpolation as in efel
    py_AP_rise_rate = (voltage[peak_indices] - voltage[AP_begin_indices]) / (
        time[peak_indices] - time[AP_begin_indices]
    )

    numpy.testing.assert_allclose(AP_rise_rate, py_AP_rise_rate)


def test_AP_fall_rate():
    """basic: Test AP fall rate"""

    import efel
    efel.reset()

    trace, time, voltage, stim_start, stim_end = load_data(
        'mean_frequency1', interp=True)

    features = ["AP_fall_rate", "AP_end_indices", "peak_indices"]

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features, raise_warnings=False)

    AP_end_indices = feature_values[0]['AP_end_indices']
    peak_indices = feature_values[0]['peak_indices']
    AP_fall_rate = feature_values[0]['AP_fall_rate']

    # works here because we use the same interpolation as in efel
    py_AP_fall_rate = (voltage[AP_end_indices] - voltage[peak_indices]) / (
        time[AP_end_indices] - time[peak_indices]
    )

    numpy.testing.assert_allclose(AP_fall_rate, py_AP_fall_rate)


def test_fast_AHP():
    """basic: Test fast AHP"""

    import efel
    efel.reset()

    trace, time, voltage, stim_start, stim_end = load_data(
        'mean_frequency1', interp=True)

    features = ["fast_AHP", "AP_begin_indices", "min_AHP_indices"]

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features, raise_warnings=False)

    AP_begin_indices = feature_values[0]['AP_begin_indices']
    min_AHP_indices = feature_values[0]['min_AHP_indices']
    fast_AHP = feature_values[0]['fast_AHP']

    # works here because we use the same interpolation as in efel
    py_fast_AHP = voltage[AP_begin_indices[:-1]] - voltage[
        min_AHP_indices[:-1]
    ]

    numpy.testing.assert_allclose(fast_AHP, py_fast_AHP)


def check_change_feature(change_name, base_name):
    """Test for a 'change' feature

    E.g. change_name='AP_duration_change', base_name='AP_duration'
    """

    import efel
    efel.reset()

    trace, time, voltage, stim_start, stim_end = load_data(
        'mean_frequency1', interp=True)

    features = [change_name, base_name]

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features, raise_warnings=False)

    base = feature_values[0][base_name]
    change = feature_values[0][change_name]

    py_change = (base[1:] - base[0]) / base[0]

    numpy.testing.assert_allclose(change, py_change)


def test_AP_amplitude_change():
    """basic: Test AP amplitude change"""

    check_change_feature("AP_amplitude_change", "AP_amplitude")


def test_AP_duration_change():
    """basic: Test AP duration change"""

    check_change_feature("AP_duration_change", "AP_duration")


def test_AP_rise_rate_change():
    """basic: Test AP rise rate change"""

    check_change_feature("AP_rise_rate_change", "AP_rise_rate")


def test_AP_fall_rate_change():
    """basic: Test AP fall rate change"""

    check_change_feature("AP_fall_rate_change", "AP_fall_rate")


def test_fast_AHP_change():
    """basic: Test fast AHP change"""

    check_change_feature("fast_AHP_change", "fast_AHP")


def test_AP_duration_half_width_change():
    """basic: Test AP duration half width change"""

    check_change_feature(
        "AP_duration_half_width_change", "AP_duration_half_width"
    )


def test_steady_state_hyper():
    """basic: Test steady state hyper"""

    import efel
    efel.reset()

    stim_start = 800.0
    stim_end = 3800.0

    time, voltage = load_ascii_input(sagtrace1_url)

    trace = {}

    trace['T'] = time
    trace['V'] = voltage
    trace['stim_start'] = [stim_start]
    trace['stim_end'] = [stim_end]

    time, voltage = interpolate(time, voltage, 0.1)

    features = ["steady_state_hyper"]

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features, raise_warnings=False)

    steady_state_hyper = feature_values[0]['steady_state_hyper']

    # works here because we use the same interpolation as in efel
    stim_end_idx = numpy.argwhere(time >= stim_end)[0][0]
    expected = numpy.mean(voltage[stim_end_idx - 35:stim_end_idx - 5])

    numpy.testing.assert_allclose(steady_state_hyper, expected)


def test_amp_drop_first_second():
    """basic: Test amp drop first second"""

    import efel
    efel.reset()

    trace, time, voltage, stim_start, stim_end = load_data(
        'mean_frequency1', interp=True)

    features = ["amp_drop_first_second", "peak_voltage"]

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features, raise_warnings=False)

    amp_drop_first_second = feature_values[0]['amp_drop_first_second']
    peak_voltage = feature_values[0]['peak_voltage']

    numpy.testing.assert_allclose(
        amp_drop_first_second, peak_voltage[0] - peak_voltage[1]
    )


def test_amp_drop_first_last():
    """basic: Test amp drop first last"""

    import efel
    efel.reset()

    trace, time, voltage, stim_start, stim_end = load_data(
        'mean_frequency1', interp=True)

    features = ["amp_drop_first_last", "peak_voltage"]

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features, raise_warnings=False)

    amp_drop_first_last = feature_values[0]['amp_drop_first_last']
    peak_voltage = feature_values[0]['peak_voltage']

    numpy.testing.assert_allclose(
        amp_drop_first_last, peak_voltage[0] - peak_voltage[-1]
    )


def test_amp_drop_second_last():
    """basic: Test amp drop second last"""

    import efel
    efel.reset()

    trace, time, voltage, stim_start, stim_end = load_data(
        'mean_frequency1', interp=True)

    features = ["amp_drop_second_last", "peak_voltage"]

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features, raise_warnings=False)

    amp_drop_second_last = feature_values[0]['amp_drop_second_last']
    peak_voltage = feature_values[0]['peak_voltage']

    numpy.testing.assert_allclose(
        amp_drop_second_last, peak_voltage[1] - peak_voltage[-1]
    )


def test_max_amp_difference():
    """basic: Test max amp difference"""

    import efel
    efel.reset()

    trace, time, voltage, stim_start, stim_end = load_data(
        'mean_frequency1', interp=True)

    features = ["max_amp_difference", "peak_voltage"]

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features, raise_warnings=False)

    max_amp_difference = feature_values[0]['max_amp_difference']
    peak_voltage = feature_values[0]['peak_voltage']

    expected = numpy.max(peak_voltage[:-1] - peak_voltage[1:])

    numpy.testing.assert_allclose(
        max_amp_difference, expected
    )


def test_AP_amplitude_diff():
    """basic: Test AP amplitude diff"""

    import efel
    efel.reset()

    trace, time, voltage, stim_start, stim_end = load_data(
        'mean_frequency1', interp=True)

    features = ["AP_amplitude_diff", "AP_amplitude"]

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features, raise_warnings=False)

    AP_amplitude_diff = feature_values[0]['AP_amplitude_diff']
    AP_amplitude = feature_values[0]['AP_amplitude']

    expected = AP_amplitude[1:] - AP_amplitude[:-1]

    numpy.testing.assert_allclose(
        AP_amplitude_diff, expected
    )


def test_AHP_depth_diff():
    """basic: Test AHP depth diff"""

    import efel
    efel.reset()

    trace, time, voltage, stim_start, stim_end = load_data(
        'mean_frequency1', interp=True)

    features = ["AHP_depth_diff", "AHP_depth"]

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features, raise_warnings=False)

    AHP_depth_diff = feature_values[0]['AHP_depth_diff']
    AHP_depth = feature_values[0]['AHP_depth']

    expected = AHP_depth[1:] - AHP_depth[:-1]

    numpy.testing.assert_allclose(
        AHP_depth_diff, expected
    )


def test_AHP_depth_slow():
    """basic: Test AHP depth slow"""

    import efel
    efel.reset()

    trace, time, voltage, stim_start, stim_end = load_data(
        'mean_frequency1', interp=True)

    features = ["AHP_depth_slow", "AHP_depth_abs_slow", "voltage_base"]

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features, raise_warnings=False)

    AHP_depth_slow = feature_values[0]["AHP_depth_slow"]
    AHP_depth_abs_slow = feature_values[0]["AHP_depth_abs_slow"]
    voltage_base = feature_values[0]["voltage_base"]

    expected = AHP_depth_abs_slow - voltage_base

    numpy.testing.assert_allclose(
        AHP_depth_slow, expected
    )


def py_burst_indices(ISI_values):
    """python implementation of burst_begin_indices and burst_end_indices"""
    if len(ISI_values) < 2:
        return None, None

    burst_factor = 2
    median_count = 0
    burst_begin_indices = [0]
    burst_end_indices = []

    for i, ISI in enumerate(ISI_values[1:], start=1):
        median = numpy.median(ISI_values[median_count:i])
        in_burst = len(burst_end_indices) == 0 or (
            burst_begin_indices[-1] > burst_end_indices[-1])

        if in_burst and ISI > (burst_factor * median):
            burst_end_indices.append(i)
            median_count = i

        if ISI < (ISI_values[i - 1] / burst_factor):
            if in_burst:
                burst_begin_indices[-1] = i
            else:
                burst_begin_indices.append(i)
            median_count = i

    in_burst = len(burst_end_indices) == 0 or (
        burst_begin_indices[-1] > burst_end_indices[-1])

    if in_burst:
        burst_end_indices.append(len(ISI_values))

    return burst_begin_indices, burst_end_indices


def test_burst_indices():
    """basic: Test burst_begin_indices and burst_end_indices"""
    import efel
    efel.reset()
    efel.setIntSetting('ignore_first_ISI', 0)

    time, voltage = load_ascii_input(burst1_url)
    time, voltage = interpolate(time, voltage, 0.1)

    trace = {}
    trace['T'] = time
    trace['V'] = voltage
    trace['stim_start'] = [250]
    trace['stim_end'] = [1600]

    features = ['burst_begin_indices', 'burst_end_indices', 'all_ISI_values']

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features, raise_warnings=False)

    burst_begin_indices = feature_values[0]['burst_begin_indices']
    burst_end_indices = feature_values[0]['burst_end_indices']
    all_ISI_values = feature_values[0]['all_ISI_values']

    burst_begin_py, burst_end_py = py_burst_indices(
        all_ISI_values
    )

    numpy.testing.assert_allclose(burst_begin_indices, burst_begin_py)
    numpy.testing.assert_allclose(burst_begin_indices, [0, 4])
    numpy.testing.assert_allclose(burst_end_indices, burst_end_py)
    numpy.testing.assert_allclose(burst_end_indices, [3, 5])


def test_strict_burst_mean_freq():
    """basic: Test strict_burst_mean_freq"""
    import efel
    efel.reset()
    efel.setIntSetting('ignore_first_ISI', 0)

    time, voltage = load_ascii_input(burst1_url)
    time, voltage = interpolate(time, voltage, 0.1)

    trace = {}
    trace['T'] = time
    trace['V'] = voltage
    trace['stim_start'] = [250]
    trace['stim_end'] = [1600]

    features = [
        'burst_begin_indices',
        'burst_end_indices',
        'peak_time',
        'strict_burst_mean_freq'
    ]

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features, raise_warnings=False)

    burst_begin_indices = feature_values[0]['burst_begin_indices']
    burst_end_indices = feature_values[0]['burst_end_indices']
    peak_time = feature_values[0]['peak_time']
    strict_burst_mean_freq = feature_values[0]['strict_burst_mean_freq']

    if burst_begin_indices is None or burst_end_indices is None:
        mean_freq_py = None
    else:
        mean_freq_py = (
            (burst_end_indices - burst_begin_indices + 1) * 1000 / (
                peak_time[burst_end_indices] - peak_time[burst_begin_indices]
            )
        )

    numpy.testing.assert_allclose(strict_burst_mean_freq, mean_freq_py)
    numpy.testing.assert_allclose(
        strict_burst_mean_freq, [254.77707006, 97.08737864]
    )


def test_strict_burst_number():
    """basic: Test strict_burst_number"""
    import efel
    efel.reset()
    efel.setIntSetting('ignore_first_ISI', 0)

    time, voltage = load_ascii_input(burst1_url)
    time, voltage = interpolate(time, voltage, 0.1)

    trace = {}
    trace['T'] = time
    trace['V'] = voltage
    trace['stim_start'] = [250]
    trace['stim_end'] = [1600]

    features = ['strict_burst_number', 'strict_burst_mean_freq']

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features, raise_warnings=False)

    strict_burst_number = feature_values[0]['strict_burst_number']
    strict_burst_mean_freq = feature_values[0]['strict_burst_mean_freq']

    numpy.testing.assert_allclose(
        strict_burst_number, strict_burst_mean_freq.size
    )
    numpy.testing.assert_allclose(strict_burst_number, 2)


def py_strict_interburst_voltage(burst_begin_idxs, peak_idxs, t, v):
    """Python implementation of interburst_voltage"""
    interburst_voltage = []
    for idx in burst_begin_idxs[1:]:
        ts_idx = peak_idxs[idx - 1]
        t_start = t[ts_idx] + 5
        start_idx = numpy.argwhere(t < t_start)[-1][0]

        te_idx = peak_idxs[idx]
        t_end = t[te_idx] - 5
        end_idx = numpy.argwhere(t > t_end)[0][0]

        interburst_voltage.append(numpy.mean(v[start_idx:end_idx + 1]))

    return numpy.array(interburst_voltage)


def test_strict_interburst_voltage():
    """basic: Test strict_interburst_voltage"""
    import efel
    efel.reset()
    efel.setIntSetting('ignore_first_ISI', 0)

    time, voltage = load_ascii_input(burst1_url)
    time, voltage = interpolate(time, voltage, 0.1)

    trace = {}
    trace['T'] = time
    trace['V'] = voltage
    trace['stim_start'] = [250]
    trace['stim_end'] = [1600]

    features = [
        'strict_interburst_voltage', 'burst_begin_indices', 'peak_indices'
    ]

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features, raise_warnings=False)

    strict_interburst_voltage = feature_values[0]['strict_interburst_voltage']
    burst_begin_indices = feature_values[0]['burst_begin_indices']
    peak_indices = feature_values[0]['peak_indices']

    strict_interburst_voltage_py = py_strict_interburst_voltage(
        burst_begin_indices, peak_indices, time, voltage
    )

    numpy.testing.assert_allclose(
        strict_interburst_voltage, strict_interburst_voltage_py
    )
    numpy.testing.assert_allclose(strict_interburst_voltage, -63.234682)


def test_AP_width_spike_before_stim_start():
    """basic: Test AP_width with a spike before stim start"""
    import efel
    efel.reset()

    stim_start = 700.0
    stim_end = 2700.0

    time, voltage = load_ascii_input(spikeoutsidestim_url)

    trace = {}

    trace['T'] = time
    trace['V'] = voltage
    trace['stim_start'] = [stim_start]
    trace['stim_end'] = [stim_end]

    features = ['AP_width']

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features)

    ap_width = feature_values[0]['AP_width']

    assert len(ap_width) == 15

    efel.setIntSetting('strict_stiminterval', 1)
    feature_values = \
        efel.getFeatureValues(
            [trace],
            features)

    ap_width = feature_values[0]['AP_width']

    assert len(ap_width) == 13


def py_adp_peak_amplitude(v, min_AHP_indices, min_between_peaks_indices):
    """Python implementation of ADP_peak_amplitude

    v should be interpolated
    """
    min_v_indices = min_between_peaks_indices[:len(min_AHP_indices)]
    if len(min_v_indices) != len(min_AHP_indices):
        raise ValueError(
            "min_AHP_indices and min_between_peaks_indices"
            "should have the same size"
        )

    # faster than numpy.array([
    #   numpy.max(v[i:j + 1]) for (i, j) in zip(min_AHP_indices, min_v_indices
    # )])
    reductions = numpy.column_stack((min_AHP_indices, min_v_indices)).ravel()
    adp_peak_v = numpy.maximum.reduceat(v, reductions)[::2]

    min_AHP_values = v[min_AHP_indices]

    return adp_peak_v - min_AHP_values


def test_ADP_peak_amplitude():
    """basic: Test ADP_peak_amplitude"""
    import efel
    efel.reset()
    efel.setIntSetting('strict_stiminterval', True)

    stim_start = 250.0
    stim_end = 1600.0

    time, voltage = load_ascii_input(burst2_url)

    _, interp_voltage = interpolate(time, voltage, 0.1)

    trace = {}

    trace['T'] = time
    trace['V'] = voltage
    trace['stim_start'] = [stim_start]
    trace['stim_end'] = [stim_end]

    features = [
        "min_AHP_indices",
        "min_between_peaks_indices",
        "ADP_peak_values",
        "ADP_peak_amplitude"
    ]

    feature_values = efel.getFeatureValues(
        [trace],
        features,
        raise_warnings=False
    )

    min_AHP_indices = feature_values[0]["min_AHP_indices"]
    min_between_peaks_indices = feature_values[0]["min_between_peaks_indices"]
    adp_peak_values = feature_values[0]["ADP_peak_values"]
    adp_peak_amplitude_efel = feature_values[0]["ADP_peak_amplitude"]

    adp_peak_amplitude_py = py_adp_peak_amplitude(
        interp_voltage, min_AHP_indices, min_between_peaks_indices
    )
    adp_peak_amplitude_py2 = adp_peak_values - interp_voltage[min_AHP_indices]

    numpy.testing.assert_allclose(
        adp_peak_amplitude_py, adp_peak_amplitude_efel
    )
    numpy.testing.assert_allclose(
        adp_peak_amplitude_py2, adp_peak_amplitude_efel, atol=1e-10
    )


def py_interburst_min_values(v, peak_indices, burst_end_indices):
    """min voltage between burst and next peak"""
    if peak_indices is None or burst_end_indices is None:
        return None

    interburst_min = [
        numpy.min(
            v[peak_indices[i]:peak_indices[i + 1]]
        ) for i in burst_end_indices if i + 1 < len(peak_indices)
    ]

    return numpy.array(interburst_min)


def py_time_to_interburst_min(
    v, t, peak_indices, burst_end_indices, peak_time
):
    """time from burst last peak to min between burst and next peak"""
    if peak_indices is None or burst_end_indices is None:
        return None

    time_to_interburst_min = [
        t[peak_indices[i] + numpy.argmin(
            v[peak_indices[i]:peak_indices[i + 1]]
        )] - peak_time[i]
        for i in burst_end_indices if i + 1 < len(peak_indices)
    ]

    return numpy.array(time_to_interburst_min)


def test_interburst_min_values():
    """basic: Test interburst_min_values"""
    urls = [burst1_url, burst2_url, burst3_url]
    for i, url in enumerate(urls):
        import efel
        efel.reset()

        time, voltage = load_ascii_input(url)

        _, interp_voltage = interpolate(time, voltage, 0.1)

        trace = {}

        trace['T'] = time
        trace['V'] = voltage
        if i in [0, 1]:
            trace['stim_start'] = [250]
            trace['stim_end'] = [1600]
        elif i == 2:
            trace['stim_start'] = [800]
            trace['stim_end'] = [2150]

        features = [
            "peak_indices",
            "burst_end_indices",
            "interburst_min_values",
        ]

        feature_values = efel.getFeatureValues(
            [trace],
            features,
            raise_warnings=False
        )

        peak_indices = feature_values[0]["peak_indices"]
        burst_end_indices = feature_values[0]["burst_end_indices"]
        interburst_min_values = feature_values[0]["interburst_min_values"]

        interburst_min_py = py_interburst_min_values(
            interp_voltage, peak_indices, burst_end_indices
        )

        # convert to float so that None edge case get converted to nan
        # and can pass in assert_allclose
        interburst_min_py = numpy.array(interburst_min_py, dtype=numpy.float64)
        interburst_min_values = numpy.array(
            interburst_min_values, dtype=numpy.float64
        )

        numpy.testing.assert_allclose(
            interburst_min_py, interburst_min_values
        )


def test_time_to_interburst_min():
    """basic: Test time_to_interburst_min"""
    urls = [burst1_url, burst2_url, burst3_url]
    for i, url in enumerate(urls):
        import efel
        efel.reset()

        time, voltage = load_ascii_input(url)

        interp_time, interp_voltage = interpolate(time, voltage, 0.1)

        trace = {}

        trace['T'] = time
        trace['V'] = voltage
        if i in [0, 1]:
            trace['stim_start'] = [250]
            trace['stim_end'] = [1600]
        elif i == 2:
            trace['stim_start'] = [800]
            trace['stim_end'] = [2150]

        features = [
            "peak_indices",
            "burst_end_indices",
            "peak_time",
            "time_to_interburst_min",
        ]

        feature_values = efel.getFeatureValues(
            [trace],
            features,
            raise_warnings=False
        )

        peak_indices = feature_values[0]["peak_indices"]
        peak_time = feature_values[0]["peak_time"]
        burst_end_indices = feature_values[0]["burst_end_indices"]
        time_to_interburst_min = feature_values[0]["time_to_interburst_min"]

        time_to_interburst_min_py = py_time_to_interburst_min(
            interp_voltage,
            interp_time,
            peak_indices,
            burst_end_indices,
            peak_time,
        )

        # convert to float so that None edge case get converted to nan
        # and can pass in assert_allclose
        time_to_interburst_min_py = numpy.array(
            time_to_interburst_min_py, dtype=numpy.float64
        )
        time_to_interburst_min = numpy.array(
            time_to_interburst_min, dtype=numpy.float64
        )

        numpy.testing.assert_allclose(
            time_to_interburst_min_py, time_to_interburst_min
        )


def py_postburst_min_values(t, v, peak_indices, burst_end_indices, stim_end):
    """min voltage between burst and next peak"""
    if peak_indices is None or burst_end_indices is None:
        return None

    postburst_min = [
        numpy.min(
            v[peak_indices[i]:peak_indices[i + 1]]
        ) for i in burst_end_indices if i + 1 < len(peak_indices)
    ]
    if len(postburst_min) < len(burst_end_indices):
        if t[burst_end_indices[-1]] < stim_end:
            end_idx = numpy.where(t >= stim_end)[0][0]
            postburst_min.append(numpy.min(
                v[peak_indices[burst_end_indices[-1]]:end_idx]
            ))
        else:
            postburst_min.append(numpy.min(
                v[peak_indices[burst_end_indices[-1]]:]
            ))

    return numpy.array(postburst_min)


def test_postburst_min_values():
    """basic: Test interburst_min_values"""
    urls = [burst1_url, burst2_url, burst3_url]
    for i, url in enumerate(urls):
        import efel
        efel.reset()
        # use this to have all spikes in burst for burst3_url case
        efel.setDoubleSetting('strict_burst_factor', 4.0)

        time, voltage = load_ascii_input(url)

        interp_time, interp_voltage = interpolate(time, voltage, 0.1)

        trace = {}

        trace['T'] = time
        trace['V'] = voltage
        if i in [0, 1]:
            trace['stim_start'] = [250]
            trace['stim_end'] = [1600]
        elif i == 2:
            trace['stim_start'] = [800]
            trace['stim_end'] = [2150]

        features = [
            "peak_indices",
            "burst_end_indices",
            "postburst_min_values",
        ]

        feature_values = efel.getFeatureValues(
            [trace],
            features,
            raise_warnings=False
        )

        peak_indices = feature_values[0]["peak_indices"]
        burst_end_indices = feature_values[0]["burst_end_indices"]
        postburst_min_values = feature_values[0]["postburst_min_values"]

        postburst_min_py = py_postburst_min_values(
            interp_time,
            interp_voltage,
            peak_indices,
            burst_end_indices,
            trace["stim_end"][0]
        )

        # convert to float so that None edge case get converted to nan
        # and can pass in assert_allclose
        postburst_min_py = numpy.array(postburst_min_py, dtype=numpy.float64)
        postburst_min_values = numpy.array(
            postburst_min_values, dtype=numpy.float64
        )

        numpy.testing.assert_allclose(
            postburst_min_py, postburst_min_values
        )


def test_spikes_per_burst_diff():
    """basic: Test spikes_per_burst_diff"""
    import efel
    efel.reset()

    time, voltage = load_ascii_input(burst1_url)
    time, voltage = interpolate(time, voltage, 0.1)

    trace = {}
    trace['T'] = time
    trace['V'] = voltage
    trace['stim_start'] = [250]
    trace['stim_end'] = [1600]

    features = ['spikes_per_burst_diff']

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features, raise_warnings=False)

    spikes_per_burst_diff = feature_values[0]['spikes_per_burst_diff']
    assert list(spikes_per_burst_diff) == [1]


def test_spikes_in_burst1_burst2_diff():
    """basic: Test spikes_in_burst1_burst2_diff"""
    import efel
    efel.reset()

    time, voltage = load_ascii_input(burst1_url)
    time, voltage = interpolate(time, voltage, 0.1)

    trace = {}
    trace['T'] = time
    trace['V'] = voltage
    trace['stim_start'] = [250]
    trace['stim_end'] = [1600]

    features = ['spikes_in_burst1_burst2_diff']

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features, raise_warnings=False)

    spikes_in_burst1_burst2_diff = feature_values[0][
        'spikes_in_burst1_burst2_diff'
    ]
    assert list(spikes_in_burst1_burst2_diff) == [1]


def test_spikes_in_burst1_burstlast_diff():
    """basic: Test spikes_in_burst1_burstlast_diff"""
    import efel
    efel.reset()

    time, voltage = load_ascii_input(burst1_url)
    time, voltage = interpolate(time, voltage, 0.1)

    trace = {}
    trace['T'] = time
    trace['V'] = voltage
    trace['stim_start'] = [250]
    trace['stim_end'] = [1600]

    features = ['spikes_in_burst1_burstlast_diff']

    feature_values = \
        efel.getFeatureValues(
            [trace],
            features, raise_warnings=False)

    spikes_in_burst1_burstlast_diff = feature_values[0][
        'spikes_in_burst1_burstlast_diff'
    ]
    assert list(spikes_in_burst1_burstlast_diff) == [1]

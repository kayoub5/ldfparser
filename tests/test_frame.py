import pytest

from ldfparser import LinFrame, LinSignal
from ldfparser.encoding import LinSignalType, LogicalValue, PhysicalValue

@pytest.mark.unit
def test_frame_raw_encoding():
	signal1 = LinSignal('Signal_1', 8, 0)
	signal2 = LinSignal('Signal_2', 4, 0)
	signal3 = LinSignal('Signal_3', 1, 0)

	frame = LinFrame(1, 'Frame_1', 2, {0: signal1, 8: signal2, 15: signal3})
	content = frame.raw({
		'Signal_1': 100,
		'Signal_2': 10,
		'Signal_3': 1
	})

	assert list(content) == [100, 10 | 1 << 7]

@pytest.mark.unit
def test_frame_raw_encoding_array():
	signal1 = LinSignal('Signal_1', 16, [0, 0])
	frame = LinFrame(1, 'Frame_1', 2, {0: signal1})
	content = frame.raw({
		'Signal_1': [1, 2]
	})
	assert list(content) == [1, 2]

@pytest.mark.unit
def test_frame_raw_encoding_array2():
	signal1 = LinSignal('Signal_1', 16, [0, 0])
	signal2 = LinSignal('Signal_2', 8, 0)
	frame = LinFrame(1, 'Frame_1', 3, {0: signal1, 16: signal2})
	content = frame.raw({
		'Signal_1': [1, 2],
		'Signal_2': 3
	})
	assert list(content) == [1, 2, 3]

@pytest.mark.unit
def test_frame_raw_decoding_array():
	signal1 = LinSignal('Signal_1', 16, [0, 0])
	frame = LinFrame(1, 'Frame_1', 2, {0: signal1})
	assert frame.parse_raw(bytearray([1, 2])) == {"Signal_1": [1, 2]}

@pytest.mark.unit
def test_frame_raw_decoding_array2():
	signal1 = LinSignal('Signal_1', 16, [0, 0])
	signal2 = LinSignal('Signal_2', 8, 0)
	frame = LinFrame(1, 'Frame_1', 3, {0: signal1, 16: signal2})
	assert frame.parse_raw(bytearray([1, 2, 3])) == {"Signal_1": [1, 2], "Signal_2": 3}

@pytest.mark.unit
def test_frame_raw_encoding_out_of_range():
	signal1 = LinSignal('Signal_1', 8, 0)
	signal2 = LinSignal('Signal_2', 4, 0)
	signal3 = LinSignal('Signal_3', 1, 0)

	frame = LinFrame(1, 'Frame_1', 2, {0: signal1, 8: signal2, 15: signal3})
	with pytest.raises(Exception) as e:
		content = frame.raw({
			'Signal_1': 100,
			'Signal_2': 30,
			'Signal_3': 1
		})

@pytest.mark.unit
def test_frame_signals_overlapping():
	signal1 = LinSignal('Signal_1', 8, 0)
	signal2 = LinSignal('Signal_2', 4, 0)
	signal3 = LinSignal('Signal_3', 1, 0)

	with pytest.raises(ValueError) as e:
		frame = LinFrame(1, 'Frame_1', 2, {0: signal1, 7: signal2, 15: signal3})

@pytest.mark.unit
def test_frame_signal_out_of_frame():
	signal1 = LinSignal('Signal_1', 8, 0)
	signal2 = LinSignal('Signal_2', 4, 0)

	with pytest.raises(ValueError) as e:
		frame = LinFrame(1, 'Frame_1', 2, {0: signal1, 14: signal2})

@pytest.mark.integration
def test_frame_encode_data():
	motorSpeed = LinSignal('MotorSpeed', 7, 0)
	motorValues = [LogicalValue(0, 'off'), PhysicalValue(1, 99, 1, 0, 'rpm'), PhysicalValue(100, 128, 0, 100)]

	temperature = LinSignal('Temperature', 8, 255)
	temperatureValues = [LogicalValue(0, 'MEASUREMENT_ERROR'), PhysicalValue(1, 255, 1, -50, 'C')]

	errorState = LinSignal('Error', 1, 0)
	errorValues = [LogicalValue(0, 'NO_ERROR'), LogicalValue(1, 'ERROR')]

	converters = {
		'MotorSpeed': LinSignalType('MotorSpeedType', motorValues),
		'Temperature': LinSignalType('TemperatureType', temperatureValues),
		'Error': LinSignalType('ErrorType', errorValues)
	}

	frame = LinFrame(1, 'Status', 2, {0: motorSpeed, 7: errorState, 8: temperature})
	content = frame.data(
		{
			'Temperature': -30,
			'MotorSpeed': '50rpm',
			'Error': 'NO_ERROR'
		}, 
		converters
	)
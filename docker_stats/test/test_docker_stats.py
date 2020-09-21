import os,sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from unittest.mock import patch
from input_data import *
import pytest
import conf
import docker_stats

@pytest.mark.parametrize('data,table,output',[(prepared['empty_data'],table['substreams'],message['success']),
                                              (prepared['empty_data'],table['stats'],message['success']),
                                              (prepared['nonempty_stats'],table['fake_table'],message['failure']),
                                              (prepared['nonempty_substreams'],table['substreams'],message['success']),
                                              (prepared['nonempty_stats'],table['stats'],message['success'])])
def test_write_into_table(data, table, output):
    actual_output = docker_stats.write_into_table(data, table)
    expected_output = output.format(table)
    assert actual_output == expected_output


@pytest.mark.parametrize('data,result',
                         [(all_data['valid_data'], prepared_data['nonempty_data']),
                          (all_data['invalid_data'], prepared_data['nonempty_data']),
                          (all_data['empty_data'], prepared_data['empty_data'])])
def test_prepare_data(data,result):
    actual_output = docker_stats.prepare_data(data)
    expected_output = result
    assert actual_output == expected_output


@patch('requests.get')
def test_get_docker_image_data(mocked_request):
    mocked_request.return_value.json.return_value = response
    expected_value = response['results']
    actual_value = docker_stats.get_docker_image_data()
    assert actual_value == expected_value


@pytest.mark.parametrize('all_data, prepared_data, test_output, write_message',
                         [(all_data['valid_data'],prepared_data['nonempty_data'],output['valid'],handler_message['success']),
                          (all_data['invalid_data'],prepared_data['empty_data'],output['invalid'],handler_message['failure'])])
@patch('docker_stats.write_into_table')
@patch('docker_stats.prepare_data')
@patch('docker_stats.get_docker_image_data')
def test_handler(mock_get_data, mock_prepared_data, mock_write, all_data, prepared_data, test_output, write_message):
    mock_get_data.return_value = all_data
    mock_prepared_data.return_value = prepared_data
    mock_write.side_effect = write_message
    actual_output = docker_stats.handler('event','context')
    expected_output = test_output
    assert actual_output == expected_output

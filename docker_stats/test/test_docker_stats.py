"""
testing all functions of docker stats is
working as expected or not in terms of
different inputs
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from unittest.mock import patch
import pytest
import conf
import docker_stats
from input_data import *

@pytest.mark.parametrize('date,data,result',
                         [(date,all_data['single'], substreams['single']),
                          (date,all_data['multiple'], substreams['multiple']),
                          (date,all_data['empty'], substreams['empty'])])
def test_store_substreams(date,data,result):
    "testing whether this function is returning right sort of output"
    actual_output = docker_stats.store_substreams(date,data)
    expected_output = result
    assert actual_output == expected_output

@pytest.mark.parametrize('date,data,result',
                         [(date,all_data['single'], stats['single']),
                          (date,all_data['multiple'], stats['multiple']),
                          (date,all_data['empty'], stats['empty'])])
def test_store_image_stats(date,data,result):
    "testing whether this function is returning right sort of output"
    actual_output = docker_stats.store_image_stats(date,data)
    expected_output = result
    assert actual_output == expected_output

@pytest.mark.parametrize('all_data, substreams_data, stats_data, test_output, write_message',
                         [(all_data['single'],substreams['single'],stats['single'],
                           output['valid'],handler_message['success']),
                          (all_data['single'],substreams['single'],stats['single'],
                           output['invalid'],handler_message['failure'])])
@patch('streams_common_functions.write_into_table')
@patch('docker_stats.store_image_stats')
@patch('docker_stats.store_substreams')
@patch('streams_common_functions.get_current_docker_data')
def test_handler(mock_get_data, mock_store_substreams, mock_store_stats, mock_write,
                 all_data, substreams_data, stats_data, test_output, write_message):
    "testing handler function behavior in terms of different inputs"
    mock_get_data.return_value = all_data
    mock_store_substreams.return_value = substreams_data
    mock_store_stats.return_value = stats_data
    mock_write.side_effect = write_message
    actual_output = docker_stats.handler('event','context')
    expected_output = test_output
    assert actual_output == expected_output

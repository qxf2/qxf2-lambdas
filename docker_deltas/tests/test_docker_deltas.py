"""
Testing working behaviors of all the functions
in docker deltas into different sort of inputs.
"""
import os
import sys
from unittest.mock import patch
import pytest
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from input_data import date,substreams_data,new_substreams,amend_stats,handler_stats,handler_substreams,deltas,message,output,docker_stats
import docker_deltas
import streams_common_functions

@pytest.mark.parametrize('date,current_day_substreams,new_substreams,\
                          yesterday_images_stats,test_output',
                          [(date['yesterday'],substreams_data['today_substreams'],
                          new_substreams,docker_stats['single_stats'],
                          amend_stats['new_yesterday_stats'])])
def test_amend_yesterday_images_stats(date,current_day_substreams,new_substreams,
                                      yesterday_images_stats,test_output):
    "testing whether amend function giving right output or not"
    actual_output = docker_deltas.amend_yesterday_images_stats(date,current_day_substreams,
                                                               new_substreams,
                                                               yesterday_images_stats)
    expected_output = test_output
    assert actual_output == expected_output

@pytest.mark.parametrize('current_day_substreams,previous_day_substreams,test_output',
                         [(substreams_data['today_substreams'],
                          substreams_data['yesterday_substreams'],
                          new_substreams)])
def test_extract_new_substreams(current_day_substreams, previous_day_substreams,test_output):
    "testing could we extract right substream or not"
    actual_output = docker_deltas.extract_new_substreams(current_day_substreams,
                                                         previous_day_substreams)
    assert actual_output == test_output

@pytest.mark.parametrize('substreams,stats,new_substreams,amended_stats,test_output',
                         [(handler_substreams,handler_stats,new_substreams,
                          amend_stats['new_yesterday_stats'],deltas['nonzero_delta'])])
@patch('docker_deltas.amend_yesterday_images_stats')
@patch('docker_deltas.extract_new_substreams')
@patch('streams_common_functions.read_docker_table')
@patch('streams_common_functions.read_substreams')
def test_calculate_image_deltas(mock_get_stream,mock_get_stats,mock_new_substream,mock_amend_data,\
                                substreams,stats,new_substreams,amended_stats,test_output):
    "testing could we get the right calculated delta or not"
    mock_get_stream.side_effect = substreams
    mock_get_stats.side_effect = stats
    mock_new_substream.return_value = new_substreams
    mock_amend_data.return_value = amended_stats
    actual_output = docker_deltas.calculate_image_deltas()
    expected_output = test_output
    assert actual_output == expected_output

@pytest.mark.parametrize('deltas, writing_message, test_output',
                         [(deltas['nonzero_delta'],message['writing_success'],output['success']),
                          (deltas['nonzero_delta'],message['writing_failure'],output['failure'])])
@patch('streams_common_functions.write_into_table')
@patch('docker_deltas.calculate_image_deltas')
def test_handler(mock_get_deltas, mock_write, deltas, writing_message, test_output):
    "testing handler function behavior into different inputs"
    mock_get_deltas.return_value = deltas
    mock_write.return_value = writing_message.format('docker_deltas')
    actual_output = docker_deltas.handler('event','context')
    expected_output = test_output
    assert actual_output == expected_output

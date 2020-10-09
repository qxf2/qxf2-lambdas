"""
    testing github stats functions working behavior with
    different sort of inputs
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from unittest.mock import patch
from input_data import *
import pytest
import conf
import github_stats

@pytest.mark.parametrize('data,result',
                         [(all_data['single'], substreams['single']),
                          (all_data['multiple'], substreams['multiple']),
                          (all_data['empty'], substreams['empty'])])
def test_store_substreams(data,result):
    "testing the function is returning right substream data or not"
    actual_output = github_stats.store_substreams(current_date,data)
    expected_output = result
    assert actual_output == expected_output

@pytest.mark.parametrize('all_data, substreams_data, stats_data, test_output, write_message',
                         [(all_data['single'],substreams['single'],stats['single'],
                           output['success'],handler_message['success']),
                          (all_data['single'],substreams['single'],stats['single'],
                           output['failure'],handler_message['failure'])])
@patch('streams_common_functions.write_into_table')
@patch('github_stats.store_repo_stats')
@patch('github_stats.store_substreams')
@patch('streams_common_functions.get_all_repos')
def test_handler(mock_get_data, mock_store_substreams, mock_store_stats, mock_write,
                 all_data, substreams_data, stats_data, test_output, write_message):
    "testing handler function is working with different inputs well or not"
    mock_get_data.return_value = all_data
    mock_store_substreams.return_value = substreams_data
    mock_store_stats.return_value = stats_data
    mock_write.side_effect = write_message
    actual_output = github_stats.handler('event','context')
    expected_output = test_output
    assert actual_output == expected_output

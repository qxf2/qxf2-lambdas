import os,sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from unittest.mock import patch
from input_data import *
import pytest
import conf
import github_stats

@pytest.mark.parametrize('data,table,output',[(prepared_substreams['nonempty_data'],table['substreams'],message['success']),
                                              (prepared_stats['nonempty_data'],table['stats'],message['success']),
                                              (prepared_substreams['nonempty_data'],table['fake_table'],message['failure']),
                                              (prepared_stats['nonempty_data'],table['fake_table'],message['failure'])])
def test_write_into_table(data, table, output):
    actual_output = github_stats.write_into_table(data, table)
    expected_output = output.format(table)
    assert actual_output == expected_output

@pytest.mark.parametrize('date,data,result',
                         [('18-Sep-2020', all_data['nonempty_data'], prepared_substreams['nonempty_data']),
                          ('18-Sep-2020', all_data['empty_data'], prepared_substreams['empty_data'])])
def tests_prepare_substreams(date, data, result):
    actual_output = github_stats.prepare_substreams(date, data)
    expected_output = result
    assert actual_output == expected_output

@pytest.mark.parametrize('date,data,result',
                         [('18-Sep-2020', all_data['nonempty_data'], prepared_stats['nonempty_data']),
                          ('18-Sep-2020', all_data['empty_data'], prepared_stats['empty_data'])])
def tests_prepare_stats(date, data, result):
    actual_output = github_stats.prepare_stats(date, data)
    expected_output = result
    assert actual_output == expected_output

def test_get_all_repos():
    output = github_stats.get_all_repos()
    assert len(output) == data_length

@pytest.mark.parametrize('all_data, prepared_substreams, prepared_stats, test_output, write_message',
                         [(all_data['nonempty_data'],prepared_substreams['nonempty_data'],prepared_stats['nonempty_data'],output['success'],handler_message['success']),
                          (all_data['nonempty_data'],prepared_substreams['nonempty_data'],prepared_stats['nonempty_data'],output['failure'],handler_message['failure'])])
@patch('github_stats.write_into_table')
@patch('github_stats.prepare_stats')
@patch('github_stats.prepare_substreams')
@patch('github_stats.get_all_repos')
def test_handler(mock_get_data, mock_prepared_substreams, mock_prepared_stats, mock_write, all_data, prepared_substreams, prepared_stats, test_output, write_message):
    mock_get_data.return_value = all_data
    mock_prepared_substreams.return_value = prepared_substreams
    mock_prepared_stats.return_value = prepared_stats
    mock_write.side_effect = write_message
    actual_output = github_stats.handler('event','context')
    expected_output = test_output
    assert actual_output == expected_output
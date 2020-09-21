import os,sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from unittest.mock import patch
from input_data import *
import pytest
import conf
import streams_common_functions

@pytest.mark.parametrize('deltas,table,output',[(deltas['nonzero_delta'],'docker_deltas',message['writing_success']),
                                                (deltas['zero_delta'],'docker_deltas',message['writing_success']),
                                                (deltas['nonzero_delta'],'dummy_table',message['writing_failure'])])
def test_write_into_table(deltas, table, output):
    actual_output = streams_common_functions.write_into_table(deltas, table)
    expected_output = output.format(table)
    assert actual_output == expected_output

def test_read_docker_table():
    pass

def test_read_substreams():
    pass

@pytest.mark.parametrize('substream_data,key,output',[(response_substreams,key['docker'],substreams['today_substreams'])])
def test_extract_substream_names(substream_data, key, output):
    actual_output = streams_common_functions.extract_substream_names(substream_data, key)
    expected_output = output
    assert actual_output == expected_output
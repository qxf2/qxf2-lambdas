"""
Tests for the URL filtering lambda
> get_url logic
    - correct url
    - incorrect url
> lambda_handler
    - correct url
    - incorrect url
    - multiple urls
    - correct channel
    - incorrect channel
    - Qxf2Bot user
    - Not bot user
> post_to_newsletter
    - single url
    - multiple url
"""


import json
import os
import pytest
import url_filtering_lambda_rohini.url_filtering_lambda_rohini as url_filter
from unittest import mock
from unittest.mock import patch

TEST_DATA = [("This is a URL: https://qxf2.com",["https://qxf2.com"]),
            ("This is NOT a URL http:/qxf2.com",[]),
            ("Message with multiple urls https://qxf2.com and https://chessbase.com", ["https://qxf2.com", "https://chessbase.com"])]


@pytest.mark.parametrize("sentence,expected", TEST_DATA)
def test_get_url(sentence, expected):
    "Test if the URL is getting filtered correctly by get_url"
    result = url_filter.get_url(sentence)

    assert result == expected


@pytest.mark.parametrize("sentence,expected", TEST_DATA)
@patch('url_filtering_lambda_rohini.url_filtering_lambda_rohini.post_to_newsletter')
@patch('url_filtering_lambda_rohini.url_filtering_lambda_rohini.clean_message')
@patch('url_filtering_lambda_rohini.url_filtering_lambda_rohini.get_message_contents')
def test_url_filter(mock_message_contents, mock_clean_message, mock_post, sentence, expected):
    "Verify that filtered URLs are working ok within the lambda handler"
    result_status_code = "This is from the test"
    mock_post.return_value = result_status_code
    mock_clean_message.return_value = sentence
    channel = "19:f33e901e871d4c3c9ebbbbee66e59ebe@thread.skype"
    os.environ['ETC_CHANNEL'] = channel
    mock_message_contents.return_value = {'msg': sentence,
                                        'chat_id': channel,
                                        'user_id': 'blah'}
    result = url_filter.lambda_handler({}, {})
    expected_status_code = result_status_code if expected else ''

    assert result['body'] == json.dumps(expected)
    assert result['statusCode'] == expected_status_code

@patch('url_filtering_lambda_rohini.url_filtering_lambda_rohini.get_message_contents')
def test_wrong_channel(mock_message_contents):
    "Verify that URLs are not filtered unless it is the etc channel"
    channel = "etc channel"
    os.environ['ETC_CHANNEL'] = channel
    mock_message_contents.return_value = {'msg': "See https://qxf2.com",
                                        'chat_id': "NOT etc channel",
                                        'user_id': 'blah'}
    result = url_filter.lambda_handler({}, {})

    assert result['body'] == json.dumps([])
    assert result['statusCode'] == ''

@patch('url_filtering_lambda_rohini.url_filtering_lambda_rohini.get_message_contents')
def test_qxf2_bot_user(mock_message_contents):
    "Ensure messages sent by Qxf2 Bot are not being processed"
    Qxf2Bot_USER = "Qxf2Bot"
    channel = "etc channel"
    os.environ['ETC_CHANNEL'] = channel
    os.environ['Qxf2Bot_USER'] = Qxf2Bot_USER
    mock_message_contents.return_value = {'msg': "See https://qxf2.com",
                                        'chat_id': channel,
                                        'user_id': Qxf2Bot_USER}
    result = url_filter.lambda_handler({}, {})

    assert result['body'] == json.dumps([])
    assert result['statusCode'] == ''


@pytest.mark.parametrize("sentence,expected", TEST_DATA)
@patch('requests.post')
def test_multiple_url_post(mock_post, sentence, expected):
    "Verify that post_to_newsletter is called the correct number of times"
    if expected == []:
        test_status_code = ""
    else:
        test_status_code = 'Via test!'
    mock_response = mock.MagicMock()
    mock_response.status_code = test_status_code
    mock_post.return_value = mock_response
    result = url_filter.post_to_newsletter(expected)
    assert result == test_status_code
    assert mock_post.call_count == len(expected)

@patch('requests.post')
def test_post_multiple(mock_post):
    "Verify if post_to_newsletter returns accurate response if one or more URLs in a list of multiple URLs fail to be posted"
    multiple_url_list = ["https://qxf2.com", "https://skype.com"]
    success_status_code = 'Posted Successfully'
    failure_status_code = "Failed to post"

    #mock response for successfull post 
    mock_response_success = mock.MagicMock()
    mock_response_success.status_code = success_status_code

    #mock response for unsuccessfull post
    mock_response_failure = mock.MagicMock()
    mock_response_failure.status_code = failure_status_code

    #mock the first post to fail and second post to pass
    mock_post.side_effect = [mock_response_failure,mock_response_success]

    result = url_filter.post_to_newsletter(multiple_url_list)
    assert result == failure_status_code,"Expected post_to_newsletter to return failed response but it did not"
    assert mock_post.call_count == len(multiple_url_list),f"Expected exactly {len(multiple_url_list)} calls to post to newsletter but got {mock_post.call_count}"

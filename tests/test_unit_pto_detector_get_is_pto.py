import responses
import requests

@responses.activate
def test_unit_get_is_pto_score_1():
    """
    Unit test for pto_score == 1
    """
    responses.add(
        responses.POST,
        url='https://practice-testing-ai-ml.qxf2.com/is-pto',
        body='{"message":"I am on PTO today","score":1}',
        match=[
            responses.urlencoded_params_matcher({'message':'I am on PTO today'})
        ]
    )
    resp = requests.post("https://practice-testing-ai-ml.qxf2.com/is-pto", data={'message':'I am on PTO today'})
    assert resp.status_code == 200
    assert resp.text == '{"message":"I am on PTO today","score":1}'
    assert resp.json()['score'] == 1

@responses.activate
def test_unit_get_is_pto_score_0():
    """
    Unit test for pto_score == 0
    """
    responses.add(
        responses.POST,
        url='https://practice-testing-ai-ml.qxf2.com/is-pto',
        body='{"message":"I am happy today","score":0}',
        match=[
            responses.urlencoded_params_matcher({'message':'I am happy today'})
        ]
    )
    resp = requests.post("https://practice-testing-ai-ml.qxf2.com/is-pto", data={'message':'I am happy today'})
    assert resp.status_code == 200
    assert resp.text == '{"message":"I am happy today","score":0}'
    assert resp.json()['score'] == 0
# conftest.py
"""
Defining pytest session details
"""
import pytest
import time

def pytest_sessionstart(session):
    """
    pytest session start
    """
    session.results = dict()

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Running wrapper method
    """
    outcome = yield
    result = outcome.get_result()

    if result.when == 'call':
        item.session.results[item] = result

def pytest_sessionfinish(session,exitstatus):
    """
    pytest session finish
    """
    print(f'\n---------printing test results------------')
    reporter = session.config.pluginmanager.get_plugin('terminalreporter')
    duration = time.time() - reporter._sessionstarttime
    passed_amount = sum(1 for result in session.results.values() if result.passed)
    failed_amount = sum(1 for result in session.results.values() if result.failed)
    print(f'=== {passed_amount} passed and {failed_amount} failed tests in {duration} seconds===')
    print(f'------------------------------------------')

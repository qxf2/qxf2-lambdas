"""
Helper methods for generic utils
"""
import os
import sys
import time
import logging
import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def wait(wait_time):
    "Performs wait for time provided"
    return time.sleep(wait_time)

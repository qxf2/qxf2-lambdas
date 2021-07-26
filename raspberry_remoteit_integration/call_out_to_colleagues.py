"""
Module to play voice on raspberry pi
"""
import os

os.system(
    "espeak -ven-us+f3 -s 125 --stdout 'Hi, one of our colleague is on the Jitsi call. \
    Please join if you are free and want to have a quick chat' | aplay 2>/dev/null"
)

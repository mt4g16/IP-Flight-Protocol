# -*- coding: utf-8 -*-
"""
Created on Sun Feb 16 22:59:19 2020

@author: Matteo
"""

from tlog_interpreter import process_tlog
from data_processor import process_data
from data_plots import make_plots
from data_panels import make_panels

def process_flight():
    process_tlog()
    process_data()
    make_plots()
    make_panels()
    
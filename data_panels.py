# -*- coding: utf-8 -*-
"""
Created on Sun Feb 16 17:18:05 2020

@author: Matteo
"""

import ADRpy
from ADRpy import mtools4acdc as adrpytools
import os
import io
import pandas as pd
from data_parse import wp_timestamps, parse
from flight_planner import wp_list
import matplotlib
from data_plots import plot_dir
import sys

def make_panels():
        
    cwd = os.getcwd()
    plot_dir()
    filename = '\\temp.csv'
    file = cwd+filename
    
    print('Generating flight data panels...')
    #progress bar code
    count = 0
    n = len(wp_list()[3])
    
    
    if os.path.isdir(r'Flight Plots\\Panels') != True:
        os.mkdir(r'Flight Plots\\Panels')
    
    
    for speed in wp_list()[3]:
        filename2 = r'Flight Plots\\Panels\\TargetSpeed_%s.png' %(speed)
#        file2 = cwd+filename
        
        wp_times = wp_timestamps()[speed][1]
        
        start = wp_times[0]
        end = wp_times[-1]
        m_df = parse(start, end)
        
        start_time = m_df['timestamp'].iloc[0]
        end_time = m_df['timestamp'].iloc[-1]
#        total_time = end_time - start_time
        
        m_df['timestamp'] -= start_time
        
        m_df.to_csv('temp.csv', index=False)
        
        test_leg1 = wp_times[3] - start_time # waypoint 4
        test_leg2 = wp_times[4] - start_time # waypoint 6
        
        timeline = ['timestamp', 'Time (s)', 0, 100]
        
        panels = [
        #    ['Angles (deg)', 'True AoA', 'Pitch angle'],
            ['Altitude (m)', 'VFR_HUD.alt'],
            ['Body rotation rates (rad/s)', 'SIMSTATE.roll', 'SIMSTATE.pitch', 'SIMSTATE.yaw'],
            ['Speed (m/s)', 'VFR_HUD.airspeed'],
            ['Throttle (%)', 'VFR_HUD.throttle']
        ]
        
        timeseriescsvfile = file
        
        #timeseriescsvfile = os.path.join(ADRpy.__path__[0], "data", "sample_takeoff_data.csv")
        #
        markers = [[test_leg1, test_leg2], ['grey','grey']]
        
        figpars = [[10, 6, 300], [8, 8, 8], 1]
        
        figobj, axes, flightdata = adrpytools.fdrplot(
            timeseriescsvfile, timeline, panels, markers, figpars)
        
        figobj.savefig(filename2)
        
        #progress bar code
        j = (count + 1) / n
        sys.stdout.write('\r')
        sys.stdout.write("[%-40s] %d%%" % ('='*int(40*j), 100*j))
        sys.stdout.flush()
        count += 1
        
    print()
    print('Done')
    os.remove('temp.csv')
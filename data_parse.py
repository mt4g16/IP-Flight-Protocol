# -*- coding: utf-8 -*-
"""
Created on Thu Feb 13 23:04:17 2020

@author: Matteo
"""

import os
import pandas as pd
from flight_planner import wp_list

def parse(start, end):
    df = pd.read_csv(r'flight_log.csv')
    df = df[(df['timestamp'] >= start) & (df['timestamp'] <= end)]
    return df

def wp_timestamps():
    cwd = os.getcwd()
    filename = '\\Extracted_data\\STATUSTEXT.csv'
    raw_wp = pd.read_csv(cwd+filename)
    
    
    waypoint_list = wp_list()[0]
    repeats = wp_list()[2]
    test_speeds = wp_list()[3]
    
    
    waypoint_indices = []
    for waypoint in waypoint_list:
        indexNames = list(raw_wp[raw_wp['STATUSTEXT.text'] == waypoint].index)
        waypoint_indices.extend(indexNames)
    
    wp1 = raw_wp.iloc[waypoint_indices]
    #print(wp1.shape[0])
    
    total_length = wp1.shape[0]
    tests = len(test_speeds)
    interval = total_length/tests

    flight_data = {}
    start = 0
    end = interval
    

    for speed in test_speeds:
        wp_timestamps = []
        
        df1 = wp1.iloc[int(start):int(end)]
        df1 = df1.sort_index()
        
        interval2 = int(df1.shape[0] / (repeats + 1)) # repeat plus original circuit

        start2 = 0
        end2 = interval2
        
        for circuit in range(repeats + 1):
            df2 = df1.iloc[int(start2):int(end2)]
            wp_timestamps.append(list(df2['timestamp']))
            
            start2 += interval2
            end2 += interval2
            

        flight_data[speed] = wp_timestamps
        
        start += interval
        end += interval

    return flight_data
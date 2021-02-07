# -*- coding: utf-8 -*-
"""
Created on Sat Feb 15 01:09:45 2020

@author: Matteo
"""

from flight_planner import wp_list
from data_parse import wp_timestamps, parse
from math import sin, cos, acos, radians, atan, degrees, tan, sqrt
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
from scipy import integrate


waypoint_list = wp_list()[0]
repeats = wp_list()[2]
test_speeds = wp_list()[3]
TL_index1 = 3
TL_index2 = 4


m = 3.4 #mass of aircraft
c = 0.25
b = 1.8
#S = c*b
S = 0.58
AR = b**2/S
W = m*9.81
rho = 1.225

'''
make exo_calc save to csv and then write a few lines of codes at the top to 
check if tthe csv exists, if not run eexp_calc.
Have the rest of the functinos read from the csv.
'''

def process_data():
    gs_df = pd.read_csv(r'flight_log.csv')
    flight_data = []
    
    print('Processing flight data from log...')
    #progress bar code
    count = 0
    n = len(test_speeds * (repeats+1))
    
    for speed in test_speeds:
        for trial in range(repeats + 1):
            wp_times = wp_timestamps()[speed][trial]
#            start_time = wp_times[0]
            test_leg1 = wp_times[TL_index1] # waypoint 4
            test_leg2 = wp_times[TL_index2] # waypoint 6
            
            TL_duration = test_leg2 - test_leg1
            test_leg1 += TL_duration*0.4 # start analysis 20% into glide
            
            duration = TL_duration*0.6
            
            h = height_change(gs_df, test_leg1, test_leg2)
            
            glide_dist = glide_length(gs_df, test_leg1, test_leg2)
            WindRun_dist = sqrt((glide_dist**2)-(h**2))
            
            V_mean = average_airspeed(gs_df, test_leg1, test_leg2)
            GPS_dist = dist_change(gs_df, test_leg1, test_leg2)
            
            d = WindRun_dist
            
            a = atan(h/d) # glide angle
            L_D = d/h
            L = W/(cos(a)+tan(a)*sin(a))
            D = L * tan(a)
            C_L = L/(0.5*rho*(V_mean**2)*S)
            C_D = D/(0.5*rho*(V_mean**2)*S)
            
            aoa = angle_of_attack(gs_df, test_leg1, test_leg2)
            
#            print("GPS Dist: %s, Integral Dist: %s" %(d, d2))
            
            flight_data.append([duration, h, V_mean, glide_dist, GPS_dist, WindRun_dist,  a, L_D, L, D, C_L, C_D, aoa])
    
            #progress bar code
            j = (count + 1) / n
            sys.stdout.write('\r')
            sys.stdout.write("[%-40s] %d%%" % ('='*int(40*j), 100*j))
            sys.stdout.flush()
            count += 1
        
    
    df = pd.DataFrame(flight_data, columns=['duration', 'h', 'V_mean', 'glide_dist', 'GPS_dist', 'WindRun_dist', 'a', 'L_D', 'L', 'D', 'C_L', 'C_D', 'aoa'])
    
    df.to_csv('processed_data.csv')

def angle_of_attack(df=pd.read_csv(r'flight_log.csv'), x1=1581881029.1452532, x2=1581881042.1173089):
    df = parse(x1, x2)
    w = df["AIRSPEED_AUTOCAL.vz"]
    x = df["AIRSPEED_AUTOCAL.vy"] # y is the forward velocity, I dont think this is in the body frame
    df['aoa'] = np.degrees(np.arctan(w/x))

    return(df["aoa"].mean())
    

def height_change(df, x1, x2):
    start_index = df.iloc[(df['timestamp']-x1).abs().argsort()[:1]]
    end_index = df.iloc[(df['timestamp']-x2).abs().argsort()[:1]]
    
    height1 = start_index['VFR_HUD.alt'].tolist()[0]
    height2 = end_index['VFR_HUD.alt'].tolist()[0]
    return height1 - height2

def average_airspeed(df, x1, x2):
    df = parse(x1, x2)
    return df["VFR_HUD.airspeed"].mean()

def dist_change(df, x1, x2):
    start_index = df.iloc[(df['timestamp']-x1).abs().argsort()[:1]]
    end_index = df.iloc[(df['timestamp']-x2).abs().argsort()[:1]]
    
    lat1 = radians((start_index['GLOBAL_POSITION_INT.lat'].tolist()[0])/10**7)
    lon1 = radians((start_index['GLOBAL_POSITION_INT.lon'].tolist()[0])/10**7)
    
    lat2 = radians((end_index['GLOBAL_POSITION_INT.lat'].tolist()[0])/10**7)
    lon2 = radians((end_index['GLOBAL_POSITION_INT.lon'].tolist()[0])/10**7)
    
    dist = 6371 * 1000 * acos(sin(lat1)*sin(lat2) + cos(lat1)*cos(lat2)*cos(lon1 - lon2))
    
    return dist

def glide_length(df, x1, x2):
    df = parse(x1, x2)
#    df['timestamp'] = (df['timestamp']- x1)
    glide_dist = np.trapz(list(df['VFR_HUD.airspeed']), x=list(df['timestamp']))
    return glide_dist
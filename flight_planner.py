# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 18:39:35 2020

@author: Matteo
"""
from math import cos, sin, radians, degrees, asin, acos, atan2
import csv
import numpy as np
import os
import pandas


cwd = os.getcwd()

# 100metres longitude difference is 0.0014276 degrees

ground_station_version = 'QGC WPL 110'


altitude = 250
test_speeds = [13, 15, 17, 19, 21, 23, 25, 27]
repeats = 4

wind_dir = 270 #  easterly wind
scale = 1
length = 300
origin = (50.9532600, -1.3672507)

w12 = 150
TL_dist = 300
TL_descent = altitude - (TL_dist/100)*50 #descend 50m for every 100m
w45 = 100
return_leg = 2*w12 + TL_dist + w45

# waypoint_type, latitiude, longitude, altitude
home = ['h', origin[0], origin[1], 8.999671]

circuit_blueprint = [['w1', 0, 0, altitude],
                     ['w2', w12, 90, altitude],
                     ['w25', w12, 90, altitude],
                     ['dcsTS'],
                     ['w4', TL_dist, 90, TL_descent],
                     ['dcs', 0.0, 0.0, 0.0, 0, 100, altitude],
                     ['w5', w45, 90, altitude],
                     ['w6', 100, 45, altitude],
                     ['w7', 100, 315, altitude],
                     ['w8', return_leg, 270, altitude],
                     ['w9', 100, 225, altitude],
                     ['dj']]

def dcs_pos():
    output = []
    for index, wp in enumerate(circuit_blueprint):
        if wp[0][:3] == 'dcs':
            output.append(index)
    return output


def wind_correction(wind_dir):
    starting_angle = circuit_blueprint[1][2]
    wind_correction = wind_dir - starting_angle
    circuit_blueprint[1][2] = wind_dir
    count = 0
#    print(wind_correction)
    for point in circuit_blueprint:
        if (count > 1) and (point[0][:1] == 'w'):
            new_bearing = point[2] + wind_correction
            if new_bearing < 360:
                point[2] = new_bearing
            else:
                point[2] = new_bearing - 360
        count += 1
    return circuit_blueprint
               

def coord_calc(in_lat, in_lon, distance, bearing):
    d = distance
    R = 6371 * 1000
    Ad = d/R
    theta = radians(bearing)
    
    la1 = radians(in_lat)
    lo1 = radians(in_lon)
    
    la2 = asin(sin(la1)*cos(Ad)+cos(la1)*sin(Ad)*cos(theta))
    lo2 = lo1 + atan2(sin(theta)*sin(Ad)*cos(la1), cos(Ad)-sin(la1)*sin(la2))
    
    return(degrees(la2), degrees(lo2))

def circuit_maker():
    master = []
    count = 0
    working_list = wind_correction(wind_dir)
    for point in working_list:
        if point[0][:1] == 'w':
            if point[1] == point[2] == 0:
                master.append(['w', origin[0], origin[1], point[3]])
            else:
#                print(point[0])
                lat, lon = coord_calc(master[count-1][1], master[count-1][2], point[1], point[2])
                master.append(['w', lat, lon, point[3]])
            count += 1
    
    for change in dcs_pos():
        master.insert(change, working_list[change])
        
    master.append(['dj'])
    return master


def flight_plan():
    master = []
    master.append(entry_row(home))
    repeat_wp = 1
    
    dcs_index = next(i for i,v in enumerate(circuit_blueprint) if 'dcsTS' in v)
    
    for u in test_speeds:
#        circuit = [w1, w2, dcs1, w4, dcs2, w6, w7, dcs3, w9, w10, w11, w12, dj]
        circuit = circuit_maker()
#        print(circuit)
        circuit[dcs_index] = dcs_creator(u)
        circuit[len(circuit_blueprint)-1] = dj_creator(repeat_wp)
        for event in circuit:
            master.append(entry_row(event))
        repeat_wp += len(circuit)
    master.append(entry_row(rtl_creator()))
    return master


def dcs_creator(speed):
    output = ['dcs', 0.0, 0.0, 0.0]
    output.extend([speed, 0.001])
    return output


def dj_creator(waypoint):
    output = ['dj', 0, 0, 0]
    output.extend([waypoint, repeats])
    return output


def rtl_creator():
    output = ['rtl', 0, 0, 0]
    return output


def entry_row(wp):
    output = []
#    output.append(circuit.index(wp))
    if str(wp[0]) == 'h':
        output.extend([1, 0, 16, 0, 0, 0, 0])
    if str(wp[0]) == 'w':
        output.extend([0, 3, 16, 0.0, 0.0, 0.0, 0.0])
    if str(wp[0]) == 'dcs':
        output.extend([0, 3, 178, 0.0, wp[4], wp[5], 0.0])
    if str(wp[0]) == 'dj':
        output.extend([0, 3, 177, wp[4], wp[5], 0.0, 0.0])
    if str(wp[0]) == 'rtl':
        output.extend([0, 3, 17, 0.0, 0.0, 0.0, 0.0]) # rtl=20, loiter=17
    output.extend([wp[1], wp[2], wp[3], 1])
    return output


def flight_plan_writer():
    'FlightPlan [15, 20, 25] 4R.waypoints'
    filename = 'FlightPlan %s %sR.waypoints' %(str(test_speeds), repeats+1)
    """Write the list to csv file."""
    with open(cwd+'\\'+filename, "w") as f:
        f.write(ground_station_version)
        f.write("\n")

    master = flight_plan()

    pd = pandas.DataFrame(master)
    pd.to_csv(filename, mode='a', header=False)
#    if count == 1:
#        return len(pd.index)
    
def wp_list():
    actual_waypoints = []

    for index, item in enumerate(circuit_blueprint):
        if item[0][:1] == 'w':
            actual_waypoints.append(index+1)

#    print(actual_waypoints)

    all_waypoints = []
    start_end = []
    blueprint_len = len(circuit_blueprint) 
    circuit_count = 0
    for n in test_speeds:
        start_end.append(actual_waypoints[0] + circuit_count)
        start_end.append(actual_waypoints[-1] + circuit_count)
        for wp in actual_waypoints:
            all_waypoints.append(wp + circuit_count)
        circuit_count += blueprint_len


    text_output = []
    for wp in all_waypoints:
        text_output.append('Mission: ' + str(wp) + ' WP')        
    

    return text_output, start_end, repeats, test_speeds

def save_plan():
    filename = 'FlightPlan %s %sR.txt' %(str(test_speeds), repeats+1)
    with open(filename, "w") as text_file:
        text_file.write('altitude = ' + str(altitude))
        text_file.write('\n')
        text_file.write('test_speeds = ' + str(test_speeds))
        text_file.write('\n')
        text_file.write('repeats = ' + str(repeats))
        text_file.write('\n')
        text_file.write('circuit_blueprint = ' + str(circuit_blueprint))


def run_plan():
    flight_plan_writer()
    save_plan()


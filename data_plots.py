# -*- coding: utf-8 -*-
"""
Created on Sat Feb 15 22:46:59 2020

@author: Matteo
"""
from flight_planner import wp_list
from data_parse import wp_timestamps, parse
from math import sin, cos, acos, radians, atan, degrees, tan, pi
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import shutil
from data_processor import AR
from scipy import stats

def plot_dir():
    if os.path.isdir('Flight Plots') != True:
        os.mkdir('Flight Plots')

def make_plots():
    plot_dir()
    df = pd.read_csv('processed_data.csv', index_col=0)
    print()
    print('Generating flight plots...')
    plot_CL_V(df)
    plot_CD_CL2(df)
    plot_LD_V(df)
    plot_CL_CD(df)
    plot_CL_alpha(df)
    
def plot_CL_V(df):
    fig, ax = plt.subplots()
#    ax.scatter(df['V_mean'], df['C_L'])
    
    x = df['V_mean']
    y = df['C_L']
    
    p = np.poly1d(np.polyfit(x, y, 1))
    t = np.linspace(15, 25, 200)
    

    ax.set_xlabel('Velocity (m/s)', fontsize=10, labelpad=10)
    ax.set_ylabel(r'$C_L$', rotation=0, fontsize=12, labelpad=15)

    ax.set_ylim(0.15, 0.28)
    ax.set_xlim(19, 24)
    
    plt.plot(x, y, 'o')
    plt.plot(t, p(t), '-', color='blue')
    
#    plt.show()
    fig.savefig(r'Flight Plots\\CL vs Velocity', dpi=300)
    plt.close(fig)


def plot_CL_CD(df):
    fig, ax = plt.subplots()
#    ax.scatter(df['V_mean'], df['C_L'])
    
    x = df['C_D']
    y = df['C_L']
    
    p = np.poly1d(np.polyfit(x, y, 1))
    t = np.linspace(0, 0.15, 200)
    

    ax.set_xlabel(r'$C_D$', fontsize=12, labelpad=10)
    ax.set_ylabel(r'$C_L$', rotation=0, fontsize=12, labelpad=15)

    ax.set_ylim(0, 0.3)
    ax.set_xlim(0, 0.1)
    
    plt.plot(x, y, 'o')
    plt.plot(t, p(t), '-', color='blue')
    
#    plt.show()
    fig.savefig(r'Flight Plots\\CL vs CD (Drag Polar)', dpi=300, bbox_inches = "tight")
    plt.close(fig)
    

def plot_CD_CL2(df):
    fig, ax = plt.subplots()

    x = df['C_L']**2
    y = df['C_D']
    
    print(stats.pearsonr(x, y))
    
    p = np.poly1d(np.polyfit(x, y, 1))
    t = np.linspace(0, 0.08, 200)
    
    ax.set_xlabel(r'$C_L^2$', fontsize=12, labelpad=10)
    ax.set_ylabel(r'$C_D$', rotation=0, fontsize=12, labelpad=15)
    
#    ax.set_ylim(0.025, 0.06)
#    ax.set_xlim(0, 0.08)
    
    plt.plot(x, y, 'o')
    plt.plot(t, p(t), '-', color='blue')    
    
    C_D0 = round(p[0], 3)
    slope = p[1]
    
    e = (1/(pi*AR*slope))
    e = round(e, 3)
#    plt.show()
#    plt.text(0.05, 0.030, str(p))
    plt.text(0.05, 0.035, r'$C_{D_{0}} = %s$' %(C_D0) + '\n' + r'$e = %s$' %(e))
    plt.text(0.05, 0.03, r'$C_D = %s + %sC_L^2$' %(C_D0, round(slope, 3)))
    plt.tight_layout()
    fig.savefig(r'Flight Plots\\CD vs CL Squared', dpi=300, bbox_inches = "tight")
    plt.close(fig)


def plot_LD_V(df):
    fig, ax = plt.subplots()
    
    x = df['V_mean']
    y = df['L_D']
    
    p = np.poly1d(np.polyfit(x, y, 2))
    t = np.linspace(18, 26, 200)
    
    
    ax.set_xlabel('Velocity (m/s)', fontsize=10, labelpad=10)
    ax.set_ylabel(r'$\frac{L}{D}$', rotation=0, fontsize=14, labelpad=15)
    
#    ax.set_ylim(4, 5.5)
#    ax.set_xlim(19, 24)
    
    plt.plot(x, y, 'o')
    plt.plot(t, p(t), '-', color='blue')     
    
#    plt.show()
    fig.savefig(r'Flight Plots\\Lift to Drag Ratio vs Velocity.png', dpi=300)
    plt.close(fig)

def plot_CL_alpha(df):
    fig, ax = plt.subplots()
    
    x = df['aoa']
    y = df['C_L']
    
    p = np.poly1d(np.polyfit(x, y, 1))
    t = np.linspace(-20, 20, 400)
    
    CL0 = round(p[0], 2)
    ZeroLift = round((-p[0]/p[1]), 2)
    
    ax.set_xlabel('Angle of Attack (deg)', fontsize=10, labelpad=10)
    ax.set_ylabel(r'$C_L}$', rotation=0, fontsize=14, labelpad=15)
    
#    ax.set_ylim(4, 5.5)
#    ax.set_xlim(0, 15)
    
    ax.spines['left'].set_position(('data', 0.0))
    ax.spines['bottom'].set_position(('data', 0.0))
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4])
    ax.set_xticks([-20, -15, -10, -5, 5, 10, 15, 20])
    
    plt.text(5, 0.2, r'$C_{L_{0}} = %s$' %(CL0))
    plt.text(5, 0.4, 'Zero Lift AoA = %s deg' %(ZeroLift))
    
#    plt.plot(x, y, 'o')
    plt.plot(t, p(t), '-', color='blue')     
#    plt.show()
    fig.savefig(r'Flight Plots\\CL vs Angle of Attack.png', dpi=300)
    plt.close(fig)

#plots()

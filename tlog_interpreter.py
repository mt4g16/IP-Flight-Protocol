import pandas as pd
import os
import shutil
import subprocess
import sys
import glob


def find_log():
    extension = 'tlog'
    result = glob.glob('*.{}'.format(extension))
    return str(result[0])

def iden_types():
    output = subprocess.getoutput("python mavlogdump.py --show-types " + find_log())
#    output = subprocess.getoutput("python mavlogdump.py --show-types test.tlog")
    types = output.splitlines()
    return types

def gen_data():
    print('')
    print('Identifying recorded data types in time log...')
    types = iden_types()
    print('Generating data extract files...')
    #progress bar code
    count = 0
    n = len(types)
    
    for i in types:
        file_out = str(i) + '.csv'
        args = 'python mavlogdump.py --format csv --types ' + i + ' ' + find_log() + ' > ' + file_out
        subprocess.getoutput(args)
        
        #progress bar code
        j = (count + 1) / n
        sys.stdout.write('\r')
        sys.stdout.write("[%-40s] %d%%" % ('='*int(40*j), 100*j))
        sys.stdout.flush()
        count += 1



def sort_dir():
    print('')
    print('Sorting directory...')
    os.mkdir('Extracted_data')
    cwd = os.getcwd()
    types = iden_types()
    
    #progress bar code
    count = 0
    n = len(types)

    for i in types:
        src = cwd + '\\' + i + '.csv'
        dst = cwd + '\\Extracted_data'
        shutil.move(str(src), str(dst))

        #progress bar code
        j = (count + 1) / n
        sys.stdout.write('\r')
        sys.stdout.write("[%-40s] %d%%" % ('='*int(40*j), 100*j))
        sys.stdout.flush()
        count += 1        
        

def clean():
    print('')
    print('Generating useful data...')
    
    df1 = pd.read_csv(r'Extracted_data\GLOBAL_POSITION_INT.csv',sep=',', header=0, index_col='timestamp')
    df2 = pd.read_csv(r'Extracted_data\SIMSTATE.csv',sep=',', header=0, index_col='timestamp')
    df3 = pd.read_csv(r'Extracted_data\RAW_IMU.csv',sep=',', header=0, index_col='timestamp')
    df4 = pd.read_csv(r'Extracted_data\VFR_HUD.csv',sep=',', header=0, index_col='timestamp')
    df5 = pd.read_csv(r'Extracted_data\AHRS3.csv',sep=',', header=0, index_col='timestamp')
    df6 = pd.read_csv(r'Extracted_data\AIRSPEED_AUTOCAL.csv',sep=',', header=0, index_col='timestamp')    
    
    result = pd.concat([df1, df2, df3, df4, df5, df6], axis=1, sort=False)
    print('Interpolating data...')
    result = result.interpolate()
    result = result.iloc[1:]
    result.to_csv('flight_log.csv',sep=',')
    print("Outputted log file saved as 'flight_log.csv'...")
    print('Done')


def process_tlog():
    gen_data()
    sort_dir()
    clean()

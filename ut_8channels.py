import pandas as pd
import numpy as np
import os
import argparse
import pandas as pd


class Ut8channels:
    '''
    Class that read unstructured bytes sequence and outputs them in a structured way.
    ''' 
    SENSORS_NUMBER = 8  
    HEADER_BYTES = 4
    SENSOR_BYTES = 1
    CTP_BYTES = 3
    DATA_BYTES = 2044     

    def __init__(self, filename):
            self.filename = filename

    def read_utd(self):
        '''
        This function reads the raw-file of the ultrasonic scanning and returns a structured dataframe.

        '''
        sensors = [[] for _ in range(Ut8channels.SENSORS_NUMBER)]
        raw_data = open(self.filename, 'rb')
        while True:  
            raw_data.read(Ut8channels.HEADER_BYTES) 
            sensor_bytes = raw_data.read(Ut8channels.SENSOR_BYTES)
            raw_data.read(Ut8channels.CTP_BYTES) 
            data_bytes = raw_data.read(Ut8channels.DATA_BYTES)
            data_array = np.frombuffer(data_bytes, dtype = np.uint8) # Interpret a buffer (bytes) as a 1-dimensional array
            output_array = ((data_array.astype(np.int16) - 0x80)/(0x80-1)) # Data normalization [-1, 1]
            try:
                sensors[ord(sensor_bytes)].append(output_array) # Get the number that represents the sensor
            except:
                break

        dataframe = pd.DataFrame(sensors).transpose()
        column_names = ['sensor {}'.format(c+1) for c in range(Ut8channels.SENSORS_NUMBER)]
        dataframe.set_axis(column_names, axis=1, inplace=True)
        
        return dataframe
   
def parse_filename(arg):
    if os.path.isfile(arg) and arg.endswith('.utd'):
        return arg
    else:
        argparse.ArgumentError()  

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Export .utd to csv')
    parser.add_argument('filename', type=parse_filename, help='Target .utd file.')
    args = parser.parse_args()
    ut_raw_data = Ut8channels(args.filename)
    ut_dataframe = ut_raw_data.read_utd()
    pd.set_option('display.max_colwidth', -1)
    ut_dataframe.to_csv('{}.csv'.format(args.filename[:-4]), index=True) 

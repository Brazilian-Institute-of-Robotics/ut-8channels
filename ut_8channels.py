import pandas as pd
import numpy as np
import os
import argparse
import xlsxwriter


class Ut8channels:
    '''
    Class that read unstructured bytes sequence and outputs them in a structured way.
    ''' 
    SENSORS_NUMBER = 8  
    HEADER_BYTES = 4
    SENSOR_BYTES = 1
    CTP_BYTES = 3
    ENCODER_BYTES = 3
    DATA_BYTES = 1017 # for 1 kB A-scan length
    # DATA_BYTES = 2041 # for 2 kB A-scan length
    MAX_BYTE_VALUE = 0xFF
    MIN_BYTE_VALUE = 0x00

    def __init__(self, filename):
            self.filename = filename

    def read_utd(self):
        '''
        This function reads the ut raw file and returns a list of lists with a-scans.

        '''
        sensors = [[] for _ in range(Ut8channels.SENSORS_NUMBER)]
        raw_data = open(self.filename, 'rb')
        while True:  
            header_bytes = raw_data.read(Ut8channels.HEADER_BYTES)
            sensor_bytes = raw_data.read(Ut8channels.SENSOR_BYTES)
            ctp_bytes = raw_data.read(Ut8channels.CTP_BYTES) 
            encoder_bytes = raw_data.read(Ut8channels.ENCODER_BYTES)
            data_bytes = raw_data.read(Ut8channels.DATA_BYTES)
            data_array = np.frombuffer(data_bytes, dtype = np.uint8) # Interpret a buffer (bytes) as a 1-dimensional array
            output_array = (2*((data_array - Ut8channels.MIN_BYTE_VALUE)/
                (Ut8channels.MAX_BYTE_VALUE - Ut8channels.MIN_BYTE_VALUE))-1).round(2) # Data normalization [-1, 1]
            try:
                sensors[ord(sensor_bytes)].append(output_array) # Get the number that represents the sensor
            except:
                break
        return sensors

    def export_to_excel(self, sensors, output_path):
        sheet_names = ['sensor {}'.format(c+1) for c in range(Ut8channels.SENSORS_NUMBER)]
        workbook = xlsxwriter.Workbook(output_path)
        for i, sheet in enumerate(sheet_names):
            worksheet = workbook.add_worksheet(sheet)
            for col, ascan in enumerate(sensors[i]):
                worksheet.write_column(0, col, ascan)
        workbook.close()          
   
def parse_filename(arg):
    if os.path.isfile(arg) and arg.endswith('.utd'):
        return arg
    else:
        argparse.ArgumentError()  

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Export .utd to xlsx')
    parser.add_argument('filename', type=parse_filename, help='Target .utd file.')
    args = parser.parse_args()
    ut_raw_data = Ut8channels(args.filename)
    ut_sensors = ut_raw_data.read_utd()
    ut_raw_data.export_to_excel(ut_sensors, output_path='{}.xlsx'.format(args.filename[:-4]))

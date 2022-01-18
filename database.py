import csv
import os


class CSVdb:

    datetime_format = '%Y%m%d'
    time_format = '%H:%M:%S'
    delimiter = ';'

    def __init__(self, filename:str, colnames:list):
        self._filename = filename
        self._colnames = colnames

    def appendData(self, data:list) -> None:
        
        if type(data[0]) == list:
            single_row = False
        else:
            single_row = True

        if single_row:
            assert len(data) == len(self._colnames)
        else:
            row_length_checker = ['error' for row in data if len(row) != len(self._colnames)]
            assert 'error' not in row_length_checker


        with open(self._filename, 'a', newline = '') as f:
            writer = csv.writer(f, delimiter = self.delimiter)

            if single_row:
                writer.writerow(data)
            else:
                for row in data:
                    writer.writerow(row)            

    def getData(self, get_header = False) -> list:
        data = []

        try:
            with open(self._filename, 'r', newline = '') as f:
                reader = csv.reader(f, delimiter = self.delimiter)
                header = next(reader)
                if get_header:
                    data.append(header)
                for row in reader:
                    data.append(row)

        except StopIteration: #if csv file is empty
            pass

        return data
    
    def overwriteFile(self, new_data:list) -> None:
        assert len(new_data) > 0
        with open(self._filename, 'w', newline = '') as f:
            writer = csv.writer(f, delimiter = self.delimiter)

            for row in new_data:
                writer.writerow(row)

    def convertToDataDict(self, data:list) -> dict:
        data_dict = {}
        for i, col in enumerate(self._colnames):
            data_dict[col] = data[i]

        return data_dict

    @staticmethod
    def getFilenames(contains:str) -> list:
        filenames = [file for file in os.listdir() if contains in file]
        #receipt_date_strings = [file_path.split('_')[1][:-4] for file_path in receipt_files]
        return filenames


  

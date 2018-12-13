#!/usr/bin/python3.6
import sys, os, getopt, errno
import logging
import getpass
import socket
from optparse import OptionParser
import pandas as pd
import time, datetime
from datetime import date
from dateutil.relativedelta import relativedelta
import ntpath
import pyarrow.parquet as pq
import xlrd

# NOTE: this tool is specialized for processing wamp excel only, program must be modified to be used for other excel
#       the uniqueness of wamp excel is it contains multiple sheets that share same column names, and hence can be merged into a single csv
# https://stackoverflow.com/questions/39714267/how-to-use-pd-melt-for-two-rows-as-headers
# This util will read into an excel file and export all its sheets to local as a merged csv and also save the csv as a parquet in local
# New version will post the generated csv onto hdfs as parquet
# Usage: python3.6 ./Excel2csv.py -e data\Historic_WAMP_Rates-Novantas_20181107.xlsx -c ..\csv_out\Historic_WAMP_Rates-Novantas_20181107.csv
# This version changes from using pandas to using xlrd to parse excel
# There is a bug in pandas <= 0.22, since pandas uses xlrd to parse excel file
# refer to this post https://www.blog.pythonlibrary.org/2014/04/30/reading-excel-spreadsheets-with-python-and-xlrd/
class Excel2csv():

    # __init__: initialize the class, processing provided parameter, initialize log
    def __init__(self, input=None, output=None):
        self.process_options(input, output)
        self.create_log_directory()
        self.config_logger()

    # process_options: process the provided parameters to ensure correct command format
    def process_options(self, input, output):
        '''
        Process the Options that the user provided
        either via commandline or
        as constructor parameters.
        '''

        #        self.logger.info('=============================================================================================')

        parser = OptionParser()

        parser.add_option("-e", "--input", dest="input_path", help="input excel file path", metavar="PATH")
        parser.add_option("-c", "--output", dest="output_path", help="output csv file path", metavar="OUTPUT")
        parser.add_option("-q", "--quiet", action="store_false", dest="verbose", default=True,
                          help="don't print status messages to stdout")

        (options, args) = parser.parse_args()

        if not options.input_path:
            if not input:
                parser.error('input excel file path not provided (-e option)')
            else:
                options.input_path = input

        if not os.path.exists(options.input_path):
            parser.error('input path does not exist (-e option)')

        options.input_path = options.input_path.rstrip('/').rstrip('\\')

        if not options.output_path:
            options.output_path = output

        # if not os.path.exists(options.output_path) or not os.path.isdir(options.output_path):
        # os.makedirs(options.output_path)

        self.options = options

        if os.path.isfile(options.input_path):
            self.options.input_is_file = True
        else:
            self.options.input_is_file = False

    # config_logger: create a new logger for the class
    def config_logger(self):
        logger = os.path.basename(__file__).split(".")[0]
        global logger_location
        logger_location = os.getcwd() + '/log/' + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + '.log'
        print("logger_location:" + logger_location)
        logging.basicConfig(filename=logger_location, format='%(asctime)s %(levelname)s %(message)s')
        self.logger = logging.getLogger(logger)
        self.logger.setLevel(logging.INFO)

    # create_path_if_not_exists: a general function to create the path if not exists
    def create_path_if_not_exists(self, p):

        if not os.path.exists(os.path.dirname(p)):
            try:
                self.logger.info('Creating path ' + os.path.dirname(p))
                os.makedirs(os.path.dirname(p))
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise

    # create_log_directory: to create a specific log folder for this class
    def create_log_directory(self):
        if not os.path.exists(os.getcwd() + '/log'):
            try:
                os.makedirs(os.getcwd() + '/log')
                print('Log location created:' + os.getcwd() + '/log')
            except OSError as ex:
                print(str(ex))
                pass

    # extract2csv: the actual function of extract excel sheets and merge/save them to one single csv
    def extract2csv(self):

        start_time = time.time()

        excelfile = self.options.input_path


        xls = xlrd.open_workbook(excelfile)
        nsheet = xls.nsheets

        csv_name = self.options.output_path.split("/")[-1].split(".")[0].replace(" - ", "_").replace(" ", "_")

        # final dataframe row index
        idx_df = 0

        # sheet index
        idx = 0

        columns=['wampproduct', 'wamp_date', 'wampregion', 'region_search_phrase', 'wamp', 'date_pull']
        df = pd.DataFrame(columns=columns)

        df_csv = pd.DataFrame(columns=columns)


        #to change to using while?  number of sheets: xls.nsheets
        while idx < nsheet:

            sheet = xls.sheet_by_index(idx).name
            #df = pd.read_excel(xls, sheet_name=idx)
            # rename index to wamp_date and make a column
            #
            # df = pd.melt(df, id_vars=['wampproduct', 'wamp_date', 'wampregion', 'region_search_phrase', 'wamp', 'date_pull'],
            #              var_name='wampregion', value_name='wamp')
            #
            # df = pd.melt(df, id_vars=['wampproduct', 'wamp_date', 'wampregion', 'region_search_phrase', 'wamp',
            #                           'date_pull'],
            #             var_name='wampregion', value_name = 'wampregion')
            #
            #              var_name='wampregion', value_name = 'region_search_phrase',
            #              var_name='wampregion', value_name = 'wamp',
            #              var_name='wampregion', value_name = 'date_pull')

            #df.index.rename('wamp_date', inplace=True)

            if (sheet != 'Internet '):
                print("Processing " + sheet)

                cur_sheet = xls.sheet_by_index(idx)

                #wampproduct = pd.read_excel(excelfile, nrows=1, header=None, usecols=[1], sheet_name=idx)

                #wampproduct = wampproduct.loc[0, 0]
                #the following are to be continue with debug to find out the cell's value and generate the df to be appended to df_csv

                # The current wamp file format is
                # wamp_date   MA	RI	NH	CT	VT	PGH	COM	DE	PHI	NJ	NYCAP	NYCENT	NYHUD	NYW	TOL	CLE	MI	FOOTPRINT
                # 01/01/10	1.75	1.66	1.80	1.46	1.69	1.73	1.64	1.64	1.74	1.71	1.68	1.74	1.68	1.87	1.77	2.04	2.05	1.76
                # for each row, interim df should be generated as
                # df['wampproduct'] = cur_sheet.cell(0,1).split("'")[1]
                # df['wamp_date']:
                #    raw_date = cur_sheet.cell(row_idx, 0)
                #    y, m, d, h, i, s = xlrd.xldate_as_tuple(raw_date, 0)
                #    wamp_date = ("{0}-{1}-{2}".format(y, m, d))
                # df['end_of_month_dt']:
                #   if today.month == 12:
                #         end_of_month_dt = '{0:%Y-%m-%d}'.format(date(today.year, today.month, 31))
                #   else:
                #         end_of_month_dt = '{0:%Y-%m-%d}'.format(date(today.year, today.month + 1, 1) - relativedelta(days=1))
                # df['c_date']: today, '{0:%Y%m}'.format(today)
                # df['wampregion']: cur_sheet.cell(row_idx, col_idx), col_idx = 1 ~ num_cols-1
                # The needed df:
                # wampproduct, wamp_date, wampregion, region_search_phrase, wamp, date_pull

                today = date.today()
                date_pull = '{0:%Y%m}'.format(today)

                if today.month == 12:
                    end_of_month_dt = '{0:%Y-%m-%d}'.format(date(today.year, today.month, 31))
                else:
                    end_of_month_dt = '{0:%Y-%m-%d}'.format(date(today.year, today.month + 1, 1) - relativedelta(days=1))

                wampproduct = cur_sheet.cell(0,1)
                wampproduct = str(wampproduct).split("'")[1]

                num_cols = cur_sheet.ncols  # Number of columns
                num_rows = cur_sheet.nrows  # Number of rows, each row share the same wamp_date

                for row_idx in range(2, num_rows - 1):  # Iterate through rows, starting with row 3

                    raw_date = cur_sheet.cell(row_idx, 0)
                    raw_date_extract = str(raw_date).split(":")[1]
                    y, m, d, h, i, s = xlrd.xldate_as_tuple(float(raw_date_extract), 0)
                    wamp_date = ("{0}-{1}-{2}".format(y, m, d))

                    for col_idx in range(1, num_cols - 1):  # Iterate through columns
                        cell_obj = cur_sheet.cell(row_idx, col_idx)  # Get cell object by row, col
                        wampregion = str(cur_sheet.cell(1, col_idx)).split("'")[1] # for region, it is always the row 2
                        region_search_phrase = wampregion
                        wamp = cell_obj.value
                        
                        #list = [wampproduct, wamp_date, wampregion, region_search_phrase, wamp, date_pull, end_of_month_dt]
                        list = {"wampproduct":wampproduct, "wamp_date": wamp_date, "wampregion":wampregion, "region_search_phrase":region_search_phrase, "wamp":wamp, "date_pull":date_pull, "end_of_month_dt": end_of_month_dt}
                        # add each cell to df
                        # df['wampproduct'] = wampproduct
                        # df['wamp_date'] = wamp_date
                        # df['wampregion'] = wampregion
                        # df['region_search_phrase'] = region_search_phrase
                        # df['wamp'] = wamp
                        # df['date_pull'] = date_pull
                        # df['end_of_month_dt'] = end_of_month_dt

                        #current issue: how to create one row dataframe and append it to the final df?
                        df_csv = df_csv.append(list, ignore_index=True)

                idx = idx + 1
            else:
                print("Skipping " + sheet)
                idx = idx + 1

        print("exporting to csv now...")
        # Now, with all the sheets merged into one, it can be exported to csv now:
        print("csv name: %s" % self.options.output_path)

        # if there is a file with the same name, delete it first

        physical_file = (os.getcwd() + self.options.output_path).replace("..", "")
        if os.path.exists(physical_file):
            os.remove(physical_file)
            self.logger.info("Original self.options.output_path + '.csv' is removed")

        # Now save the df_csv to csv at the needed location
        print("Generated csv file: " + physical_file)

        # write the csv without the sequence number in the first column
        df_csv.to_csv(physical_file, index=False)

        elapsed_time = time.time() - start_time

        print("Total Time Cost on Comparing the two Parquet files(seconds): " + str(elapsed_time))

    def run(self):
        start_time = time.time()

        self.extract2csv()

        stop_time = time.time()
        elapsed_time = stop_time - start_time

        self.logger.info(
            '=============================================================================================')
        self.logger.info('Report for the session')

        self.logger.info('Log location for this session: ' + logger_location)
        self.logger.info('Job/report processed by: ' + getpass.getuser() + ' on host: ' + socket.gethostname())
        self.logger.info(
            '=============================================================================================')
        print('\nDone!')


def run_from_cmd():
    Excel2csv().run()


if __name__ == "__main__":
    Excel2csv().run()

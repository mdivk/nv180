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


# NOTE: this tool is specialized for processing wamp excel only, program must be modified to be used for other excel
#       the uniqueness of wamp excel is it contains multiple sheets that share same column names, and hence can be merged into a single csv
# https://stackoverflow.com/questions/39714267/how-to-use-pd-melt-for-two-rows-as-headers
# This util will read into an excel file and export all its sheets to local as a merged csv and also save the csv as a parquet in local
# New version will take parameter instead of reading a hardcoded excel
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
            parser.error('input path does not exist (-p option)')

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
        excelfile = ''
        # cur_script = os.path.basename(__file__).split(".")[0]

        start_time = time.time()

        # df = pd.DataFrame()
        # excelfile = '../data/Historic WAMP Rates - Novantas_20180807.xlsx'
        excelfile = self.options.input_path

        xls = pd.ExcelFile(excelfile)

        csv_name = self.options.output_path.split("/")[-1].split(".")[0].replace(" - ", "_").replace(" ", "_")

        # sheet index
        idx = 0

        df_csv = pd.DataFrame()

        for sheet in xls.sheet_names:

            df = pd.read_excel(xls, sheet_name=idx)

            print("Processing " + sheet)

            if df.empty:
                idx = idx + 1
                continue

            cur_sheet = sheet.replace(" ", "_")  # get the current sheet's name and replace space with underscore

            product = pd.read_excel(excelfile, nrows=1, header=None, usecols=[1], sheet_name=idx)

            product = product.loc[0, 0]

            today = date.today()
            date_pull = '{0:%Y%m}'.format(today)

            if today.month == 12:
                eom = '{0:%Y-%m-%d}'.format(date(today.year, today.month, 31))
            else:
                eom = '{0:%Y-%m-%d}'.format(date(today.year, today.month + 1, 1) - relativedelta(days=1))

            df = pd.read_excel(excelfile, header=1)

            # rename index to p_date and make a column
            df.index.rename('p_date', inplace=True)
            df = df.reset_index()

            # add product to df
            df['product'] = product

            # melt
            #, product, p_date, region, p_value, c_date, eom
            #0, CD Short - Term WAMP, 2010-01-01, MA, 0.8763918845487475, 201812, 2018-12-31

            df = pd.melt(df, id_vars=['product', 'p_date'], var_name='region', value_name='p_value')

            # add c_date and eom to data frame
            df['c_date'] = date_pull
            df['eom'] = eom

            df_csv = df_csv.append(df)

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


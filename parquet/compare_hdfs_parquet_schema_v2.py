#!/opt/cloudera/parcels/Anaconda/bin/python
#Author: Raymond Xie
#Date: 20181031
#Revisited: 20181105
#Added feature: allow folder as parameter
import sys, getopt
import time
import os
import pprint
import pyspark
from pyspark.conf import SparkConf
from pyspark.context import SparkContext
from pyspark.sql import SQLContext
import re

#
# parquet_hdfs_1 = "hdfs://nameservice1/client/nova/scenarios/warehouse/pricetek_ibbk/tdb_histscen_2/part-00001-6fa2e019-96e5-4280-b2fc-994917013a6a-c000.snappy.parquet"
# parquet_hdfs_2 = "hdfs://nameservice1/client/nova/scenarios/warehouse/pricetek_ibbk/tdb_histscen_2/part-00002-6fa2e019-96e5-4280-b2fc-994917013a6a-c000.snappy.parquet"
# parquet_hdfs_3 = "hdfs://nameservice1/client/nova/scenarios/warehouse/pricetek_key/scen_output_final2_14/part-00000-512be7b3-7a99-4da6-989b-daf06a273be8-c000.snappy.parquet"
#


# Check the given parameter
import subprocess
def validate_hdfs_path(location):

    regex_folder = "Found [1-9]\d* items"
    regex_file = ".parquet"
    regex_error = "No such file"

     # Check if location exists
    str = subprocess.Popen(['hdfs', 'dfs', '-ls', location], stdout=subprocess.PIPE).communicate()[0]

    if (re.search(regex_error, str) is None):
        if(re.search(regex_folder, str) is None):
            #File found
            return 0
        elif(re.search(regex_folder, str).end()):
            #Folder found
            return 1
    else:
        return 2
 

def get_hdfs_parquet(location):
    x = subprocess.Popen(['hdfs', 'dfs', '-ls', location], stdout=subprocess.PIPE).communicate()[0]
    first_file = x.split(" ")[-1] #indeed this is the last parquet in the first path which is determined to be a folder

    return first_file

def main(argv):
    first = ''
    second = ''

    first_parquet = ''
    second_parquet = ''

    start_time = time.time()
    try:
        opts, args = getopt.getopt(argv, "hf:s:", ["ffile=", "sfile="])
    except getopt.GetoptError:
        print('schemecomp_linux.py -f <first_parquet> -s <second_parquet>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('schemecomp_linux.py -f <first_parquet> -s <second_parquet>')
            sys.exit()
        elif opt in ("-f", "--ffile"):
            first = arg
        elif opt in ("-s", "--sfile"):
            second = arg

    print("Validating first given parameter: " + first)

    x = validate_hdfs_path(first)
    #print('Validating result: ' + str(x))

    if x == 0:
        print("First Parquet: %s" % first)
        first_parquet = first
    elif x == 1:
        print("First given parameter is a folder, first Parquet(will be picked up for comparison) in the folder is: %s" % get_hdfs_parquet(first))
        first_parquet = get_hdfs_parquet(first)
    else:
        print(first + " does not exist. Please check the URI")



    print("Validating second given parameter: " + second)

    y = validate_hdfs_path(second)

    if y == 0:
        print("Second Parquet: %s" % second)
        second_parquet = second
    elif y == 1:
        print("Second Parquet in the given folder is: %s" % get_hdfs_parquet(second))
        second_parquet = get_hdfs_parquet(first)
    else:
        print(second + " does not exist. Please check the URI")



    print("==========================================================")
    print("First Parquet: %s" %first_parquet)
    print("Second Parquet: %s" %second_parquet)
    print("==========================================================")

#    exit (0)

    conf = SparkConf()
    conf.setMaster('yarn-cluster')
    #conf.setMaster('local')
    conf.setAppName('parquet schema comparison')
    sc = SparkContext.getOrCreate()

    sqlContext = SQLContext(sc)

    print('Reading first parquet into data frame pDF1')
    pDF1 = sqlContext.read.parquet(first_parquet)
    
    print('Reading second parquet into data frame pDF2')
    pDF2 = sqlContext.read.parquet(second_parquet)

    print("=========================================================")
    print("***************Schema Comparison Summary*****************")
    print("=========================================================")
    print("Schema for first parquet:")
    print(pDF1.dtypes)

    print("=========================================================")
    print("Schema for second parquet:")
    print(pDF2.dtypes)

    def diff(first, second):
        second = set(second)
        return [item for item in first if item not in second]

    dl1_names = list(pDF1.schema.names)
    dl2_names = list(pDF2.schema.names)

    print("=========================================================")
    print("schema comparison result:")
    print("=========================================================")
    dl1Notdl2 = diff(dl1_names, dl2_names)
    print(str(len(dl1Notdl2)) + " columns in first df but not in second")
    pprint.pprint(dl1Notdl2)
    print("=========================================================")
    dl2Notdl1 = diff(dl2_names, dl1_names)
    print(str(len(dl2Notdl1)) + " columns in second df but not in first")
    pprint.pprint(dl2Notdl1)

    if (len(dl2Notdl1) == 0 and len(dl1Notdl2) == 0):
        print("The two parquets have same schema.")

    elapsed_time = time.time() - start_time

    print("Total Time Cost on Comparing the two Parquet files(seconds): " +  str(elapsed_time))

if __name__ == "__main__":
    main(sys.argv[1:])



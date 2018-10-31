#!/opt/cloudera/parcels/Anaconda/bin/python
import sys, getopt
import time
import os
import pprint
import pyspark
from pyspark.conf import SparkConf
from pyspark.context import SparkContext
from pyspark.sql import SQLContext

def main(argv):
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
            first_parquet = arg
        elif opt in ("-s", "--sfile"):
            second_parquet = arg

    print("First Parquet: %s" %first_parquet)
    print("Second Parquet: %s" %second_parquet)

    conf = SparkConf()
    conf.setMaster('yarn-cluster')
    #conf.setMaster('local')
    conf.setAppName('parquet schema comparison')
    sc = SparkContext.getOrCreate()

    sqlContext = SQLContext(sc)

    pDF1 = sqlContext.read.parquet(first_parquet)
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

    elapsed_time = time.time() - start_time

    print("Total Time Cost on Comparing the two Parquet files(seconds): " +  str(elapsed_time))

if __name__ == "__main__":
    main(sys.argv[1:])


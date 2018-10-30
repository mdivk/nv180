#!/usr/bin/python3.6
#Author: Raymond Xie
#Date: 20181030
import sys, getopt
import time
import os
import pprint
import pyarrow.parquet as pq

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

    print('Input file is "', first_parquet)
    print('Output file is "', second_parquet)

    first_parquet_size = os.path.getsize(first_parquet)
    second_parquet_size = os.path.getsize(second_parquet)

    df1 = pq.read_pandas(first_parquet).to_pandas()
    df2 = pq.read_pandas(second_parquet).to_pandas()

    # rdd1 = sc.parallelize(df1.schema)
    # schema1 = rdd1.toDF()

    # df1.columns[i]

    print("Schema Comparison Summary")
    print("=========================================================")
    print("Schema for first parquet file:")
    print(df1.dtypes)

    print("=========================================================")
    print("Schema for second parquet file:")
    print(df2.dtypes)

    def diff(first, second):
        second = set(second)
        return [item for item in first if item not in second]

    dl1_names = list(df1.columns.values)
    dl2_names = list(df2.columns.values)

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

    print("=========================================================")
    print("First parquet file's size: " + str(first_parquet_size))
    print("Second parquet file's size: " + str(second_parquet_size))
    print("=========================================================")
    print("Total Time Cost on Comparing the two Parquet files: " + time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))

if __name__ == "__main__":
    main(sys.argv[1:])


#!/usr/bin/python
#Note: there could be some issue when running this in Linux because of the EOL is different in Linux than in Windows
#Note: datacompy seems to have some bug, anyway, it is convenient if it can be fixed.

import sys, getopt
import datacompy
import pyarrow.parquet as pq
import time
import os


def main(argv):
    first_parquet = ''
    second_parquet = ''

    start_time = time.time()
    try:
        opts, args = getopt.getopt(argv, "hf:s:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print('schemecomp_linux.py -f <first_parquet> -s <second_parquet>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('schemecomp_linux.py -f <first_parquet> -s <second_parquet>')
            sys.exit()
        elif opt in ("-f", "--ifile"):
            first_parquet = arg
        elif opt in ("-s", "--ofile"):
            second_parquet = arg

    print('Input file is "', first_parquet)
    print('Output file is "', second_parquet)

    first_parquet_size = os.path.getsize(first_parquet)
    second_parquet_size = os.path.getsize(second_parquet)

#=========================================
#List Schema below:
    print("The Schema of first parquet:")
    print("=========================================")
    table1 = pq.read_table(first_parquet)
    for x in table1:
        print(str(x.field.name) + ":" + str(x.field.type))
    print("\n")
    print("The Schema of second parquet:")
    print("=========================================")
    table2 = pq.read_table(second_parquet)
    for y in table1:
        print(str(y.field.name) + ":" + str(y.field.type))

    df1 = pq.read_pandas(first_parquet).to_pandas()
    df2 = pq.read_pandas(second_parquet).to_pandas()

    compare = datacompy.Compare(
        df1,
        df2,
        on_index=True,
        abs_tol=0,  # Optional, defaults to 0
        rel_tol=0,  # Optional, defaults to 0
        df1_name='first_parquet',  # Optional, defaults to 'df1'
        df2_name='second_parquet'  # Optional, defaults to 'df2'
    )
    compare.matches(ignore_extra_columns=False)
    # False

    # This method prints out a human-readable report summarizing and sampling differences
    print(compare.report())

    elapsed_time = time.time() - start_time

    print("First parquet file's size: " + str(first_parquet_size))
    print("Second parquet file's size: " + str(second_parquet_size))

    print("Total Time Cost on Comparing the two Parquet files: " + time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))

if __name__ == "__main__":
    main(sys.argv[1:])

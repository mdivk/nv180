import scala.io.Source
import org.apache.spark.sql._
import sys.process._

//Note: usage below with an external file passed into as parameter in the spark shell argument, the command starts with the "(":
//(echo 'val args = List("v201902", "audit_10_dim_gaps.txt", "_audit_dim_gaps.xlsx")' ; cat audit_10_dim_gaps2excel.scala ; cat) | spark2-shell --packages com.crealytics:spark-excel_2.11:0.11.0

//First clean up the old excel
val excel_file = args(0) + "_audit_" + args(2)

println(excel_file)
s"hdfs dfs -rm $excel_file".!

var single_table = ""
val filename = args(1)

for (line <- Source.fromFile(filename).getLines) {
    println("Processing: " + line)
    var q = "select * from Citz0063." + args(0) + "_audit_" + line
    println(q)
    if(line contains "dim_"){
      single_table = "cur_" + line}
    else { single_table = line}

    var df = spark.sql(q)
    df.write.format("com.crealytics.spark.excel").option("dataAddress", "'" + single_table + "'!A1").option("useHeader", "true").mode("append").save(excel_file)
}

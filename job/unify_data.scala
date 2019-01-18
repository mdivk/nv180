// spark-shell --packages com.databricks:spark-csv_2.11:1.2.0

import org.apache.spark.sql._
import org.apache.spark.sql.types._
import org.apache.spark.rdd._

val partcol_natural = "${PARTITIONCOL}"
val partcol_lc = "${PARTITIONCOL}".toLowerCase().replaceAll("[$~ ,;{}()=-]","_")
val delimiter = "${DELIMITER}"
val date_pull_proxy = "${DATE_PULL_PROXY}"

var df = sqlContext.emptyDataFrame

try { 

  val fs = org.apache.hadoop.fs.FileSystem.get(new java.net.URI("/"), sc.hadoopConfiguration)
  val filelist = fs.listStatus(new org.apache.hadoop.fs.Path("${SOURCEFOLDER}"))

  filelist.map(folder => {
    println("Attempting to process " + folder.getPath.toString)
    val cur2 = sqlContext.load("com.databricks.spark.csv", Map("path" -> folder.getPath.toString, "header" -> "true", "delimiter" -> delimiter, "inferSchema" -> "true"))

    if (df == sqlContext.emptyDataFrame)
      df = cur2
    else
      df = df.unionAll(cur2)
  })
 
 
  for (col <- df.columns) { df = df.withColumnRenamed(col, col.trim().toLowerCase().replaceAll("[$~ ,;{}()=-]","_")) }

  // add date_pull
  df = df.select(col("*"), concat(substring(col(date_pull_proxy), 1, 4), substring(col(date_pull_proxy), 6, 2)).as("date_pull"))
 
  if (partcol_lc == "")
    df.write.mode(SaveMode.Overwrite).parquet("${PARQUETNAME}")
  else
    df.write.mode(SaveMode.Overwrite).partitionBy(partcol_lc).parquet("${PARQUETNAME}")

  df.schema.foreach(x=>println(x.name + "," + x.dataType + "," + x.nullable ))
  System.exit(0)
  
} catch {
  case e : Throwable => e.printStackTrace
}

System.exit(-1)

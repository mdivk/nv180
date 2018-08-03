import java.util.Properties
import org.apache.spark.sql.SaveMode

// connect with MySQL
val jdbcUrl = "jdbc:mysql://${jdbchostname}:${jdbcport}/${jdbcdatabase}"
val connectionProperties = new Properties()
connectionProperties.setProperty("user", "${jdbcusername}")
connectionProperties.setProperty("password", "${jdbcpassword}")
connectionProperties.setProperty("driver", "${jdbcdriver}")

val df = spark.read.parquet("<path to the parquet>") // need to be cfged
df.createOrReplaceTempView("inputTable")

// need to be cfged
val query = """
select
  
"""

try {
  val res = spark.sql(query)
  res.show

  val resTable = s"${version}_${client}_${file_name}_xxxxx" // need to be cfged
  res.createOrReplaceTempView(resTable)

  // save the auditing tables into MySQL
  spark.table(resTable)
    .write
    .mode(SaveMode.Overwrite)
    .jdbc(jdbcUrl, resTable, connectionProperties)

  System.exit(0)
} catch {
  case e: Throwable => e.printStackTrace
}

System.exit(-1)

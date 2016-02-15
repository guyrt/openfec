import org.apache.spark.sql.functions._

// Get the data from raw JSON files.
val sqlContext = new org.apache.spark.sql.SQLContext(sc)
val headers = sqlContext.jsonFile("wasb://fecfilings@openfecdata.blob.core.windows.net/raw_headers/*.json")

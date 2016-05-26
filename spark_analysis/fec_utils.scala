import scala.collection.mutable.ArrayBuffer

// Reduce rows of boolean arrays to see if any value is ever false.
def IdentifyNonNullEmpty(row : Object, row2 : Object) : Object = {
    val row_ = row.asInstanceOf[ArrayBuffer[Boolean]];
    val row2_ = row2.asInstanceOf[ArrayBuffer[Boolean]];
    return row_.zip(row2_).map(x => x._1 && x._2);
}

// Return boolean sequence where true means elemtn in row is null or empty.
def NullEmptyMapper(row : org.apache.spark.sql.Row) : Seq[Boolean] = {
    return row.toSeq.map(xx => xx == null || xx.asInstanceOf[String].length == 0)
}

// val nonNullEmpty = rawFilings.where($"clean_linetype" === "SB").rdd.map(NullEmptyMapper).reduce(IdentifyNonNullEmpty)

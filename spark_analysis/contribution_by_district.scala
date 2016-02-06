import org.apache.spark.sql.functions._

val sqlContext = new org.apache.spark.sql.SQLContext(sc)
val records = sqlContext.jsonFile("wasb://fecfilings@openfecdata.blob.core.windows.net/raw_filings/*.json")
records.registerTempTable("records")

// Process zcta -> committee mappings.
val zip_to_committee = sc.textFile("wasb://fecfilings@openfecdata.blob.core.windows.net/raw_mappings/zip_to_district.csv")
case class ZipToCommittee(zcta: String, district: Int, state: String)

val zip_to_committee_DF = zip_to_committee
    .map(z => z.split(","))
    .filter(z => z(0) != "state_code") // get rid of header.
    .map(z => ZipToCommittee("%05d" format z(1).toInt, z(2).toInt, z(3)))
    .toDF
    .cache()

val num_committees_in_zip = zip_to_committee_DF
    .groupBy("zcta", "state")
    .agg($"zcta", count("district"))
    .withColumnRenamed("COUNT(district)", "NumDistricts")

// Produce clean records.

val contribution_by_zip = records
    .where($"clean_linetype" === "SA")
    .where($"CONTRIBUTION_AMOUNT_{F3L_Bundled}" > 0)

contribution_by_zip.cache()

case class FixedContribution(state: String, zipCode: String, contribution: Double, filerCommitteeId: String)

val records_clean = contribution_by_zip 
    .select($"CONTRIBUTOR_ZIP", $"CONTRIBUTION_AMOUNT_{F3L_Bundled}", $"CONTRIBUTOR_STATE", $"FILER_COMMITTEE_ID_NUMBER")
    .map(z => Array(z(0).asInstanceOf[String], z(1), z(2), z(3)))
    .filter(z => z(0).asInstanceOf[String] == 5 || z(0).asInstanceOf[String].length == 9)
    .map(z => Array(z(0).asInstanceOf[String].substring(0, 5), z(1), z(2), z(3)))
    .filter(z => z(0) != "")
    .filter(z => z(1) != null)
    .map(z => FixedContribution(z(2).asInstanceOf[String], z(0).asInstanceOf[String], z(1).asInstanceOf[String].toDouble, z(3).asInstanceOf[String]))
    .toDF


val records_by_zip = records_clean
    .groupBy("state", "zipCode", "filerCommitteeId")
    .agg($"state", $"zipCode", $"filerCommitteeId", sum("contribution"))
    .withColumnRenamed("SUM(contribution)", "contributions")

// print a few samples.
records_by_zip.take(10).foreach(println)

// Get committee -> candidate -> House District.

var committees = sqlContext.jsonFile("wasb://fecfilings@openfecdata.blob.core.windows.net/raw_mappings/committee.json")
committees.registerTempTable("committees")

var candidates = sqlContext.jsonFile("wasb://fecfilings@openfecdata.blob.core.windows.net/raw_mappings/candidate.json")
candidates.registerTempTable("candidates")

val house_candidates = candidates
    .where($"CAND_OFFICE" === "H")
    .where($"CAND_PCC" !== "")
    .select($"CAND_PCC", $"CAND_NAME", $"CAND_OFFICE_DISTRICT", $"CAND_OFFICE_ST", $"CAND_PTY_AFFILIATION")


val contributions_with_candidate = records_by_zip.join(house_candidates, records_by_zip("filerCommitteeId") === house_candidates("CAND_PCC"))

// see rough amounts
contributions_with_candidate.agg(sum("contributions")).show()
records_by_zip.agg(sum("contributions")).show()


val records_reduce = records_by_zip
    .join(num_committees_in_zip, records_by_zip("zipCode") === num_committees_in_zip("zcta"), "left_outer")
    .selectExpr("*", "coalesce(NumDistricts, 1) AS NumDistrictsNotNull")
    .selectExpr("*", "coalesce(contributions, 1) AS contributionsAdjusted")

records_reduce.groupBy($"NumDistricts").count().show()

// Build out set of matches and non-matches.
// Get matches and non-matches.
val zip_to_committee_renamed = zip_to_committee_DF.withColumnRenamed("state", "_state").withColumnRenamed("zcta", "_zcta")
val records_by_district_matches = records_reduce.join(zip_to_committee_renamed, (records_reduce("state") === zip_to_committee_renamed("_state")) && (records_reduce("zcta") === zip_to_committee_renamed("_zcta")))
val records_by_district_nomatches = records_reduce
    .join(zip_to_committee_renamed, (records_reduce("state") === zip_to_committee_renamed("_state")) && (records_reduce("zcta") === zip_to_committee_renamed("_zcta")), "left")
    .selectExpr("*", "coalesce(_state, \"\") AS _state2")
    .where($"_state2" === "")

records_by_district_nomatches.groupBy("state").count().orderBy($"count" * -1).show()

// the non-matches are hard. 
// Get zip -> county && zip -> district.

// Get county -> district
// Get county -> #districts
// County -> district, #districts.



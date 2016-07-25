import org.apache.spark.sql.functions._
import org.apache.spark.sql.SaveMode

//
// This script produces a stream that preps data to understand the type of contributor
// each PAC represents.
//
// This script intentionally uses DataFrame. One of my aims with this project was to learn more
// about DataFrames, so I avoided using SQL directly. 
//

// Get the data from raw JSON files.
val sqlContext = new org.apache.spark.sql.SQLContext(sc)
val records = sqlContext.jsonFile("wasb://fecfilings@openfecdata.blob.core.windows.net/raw_filings/20160630.json")

var sa_contributions = records
    .where((lower($"FORM_TYPE") === "sa11c") ||(lower($"FORM_TYPE") === "sa11b"))
    .where($"CONTRIBUTION_AMOUNT_{F3L_Bundled}" > 0)

sa_contributions = sa_contributions
    .where($"BACK_REFERENCE_SCHED_NAME" === "")

sa_contributions.cache()

// get contribution by donor.
val contributionsByDonor = sa_contributions
    .groupBy("DONOR_COMMITTEE_FEC_ID", "DONOR_CANDIDATE_FEC_ID", "FILER_COMMITTEE_ID_NUMBER")
    .agg(sum("CONTRIBUTION_AMOUNT_{F3L_Bundled}"), count("CONTRIBUTION_AMOUNT_{F3L_Bundled}"))

// get committees
var committees = sqlContext.jsonFile("wasb://fecfilings@openfecdata.blob.core.windows.net/raw_mappings/committee.json")

// get candidates.
var candidates = sqlContext.jsonFile("wasb://fecfilings@openfecdata.blob.core.windows.net/raw_mappings/candidate.json")

val candidatesWithPCC = candidates.where($"CAND_PCC" !== "")

val contributionsWithCandidate = contributionsByDonor.join(candidatesWithPCC, contributionsByDonor("FILER_COMMITTEE_ID_NUMBER") === candidatesWithPCC("CAND_PCC"), "left_outer")

contributionsWithCandidate.repartition(1).write.mode(SaveMode.Overwrite).format("json").save("wasb://fecfilings@openfecdata.blob.core.windows.net/processed_output/PAC_by_candidate.json")

import org.apache.spark.sql.functions._

//
// This script produces a stream that computes the flow of donations from House districts
// to candidates in other House races.
//
// This script intentionally uses DataFrame. One of my aims with this project was to learn more
// about DataFrames, so I avoided using SQL directly. 
//

// Get the data from raw JSON files.
val sqlContext = new org.apache.spark.sql.SQLContext(sc)
val records = sqlContext.jsonFile("wasb://fecfilings@openfecdata.blob.core.windows.net/raw_filings/*.json")

// Process zcta -> committee mappings.
val zip_to_district = sc.textFile("wasb://fecfilings@openfecdata.blob.core.windows.net/raw_mappings/zip_to_district.csv")
case class ZipToCommittee(zcta: String, district: Int, state: String)

// produce a cached copy of the zcta to Houes district data. 
val zip_to_district_DF = zip_to_district
    .map(z => z.split(","))
    .filter(z => z(0) != "state_code") // get rid of header.
    .map(z => ZipToCommittee("%05d" format z(1).toInt, z(2).toInt, z(3))) // z(1) is padded out.
    .toDF
    .cache()

val num_districts_in_zip = zip_to_district_DF
    .groupBy("zcta", "state")
    .agg($"zcta", count("district"))
    .withColumnRenamed("COUNT(district)", "NumDistricts")

//
// Produce clean records.
//

// Limit to SA type records with a contribution amount. 
val sa_contributions = records
    .where($"clean_linetype" === "SA")
    .where($"CONTRIBUTION_AMOUNT_{F3L_Bundled}" > 0)

sa_contributions.cache()

// Project to subset of columns and fix 9-digit zip codes.
// We remove rows with bad zipcodes.
// Note that I do jump RDDs here for a bit.
case class FixedContribution(state: String, zipCode: String, contribution: Double, filerCommitteeId: String)
val records_clean = sa_contributions 
    .select($"CONTRIBUTOR_ZIP", $"CONTRIBUTION_AMOUNT_{F3L_Bundled}", $"CONTRIBUTOR_STATE", $"FILER_COMMITTEE_ID_NUMBER")
    .map(z => Array(z(0).asInstanceOf[String], z(1), z(2), z(3)))
    .filter(z => z(0).asInstanceOf[String].length == 5 || z(0).asInstanceOf[String].length == 9)
    .map(z => Array(z(0).asInstanceOf[String].substring(0, 5), z(1), z(2), z(3)))
    .filter(z => z(0) != "")
    .filter(z => z(1) != null)
    .map(z => FixedContribution(z(2).asInstanceOf[String], z(0).asInstanceOf[String], z(1).asInstanceOf[String].toDouble, z(3).asInstanceOf[String]))
    .toDF

// Roll up contributions by recipient, state, and zip.
val records_by_zip = records_clean
    .groupBy("state", "zipCode", "filerCommitteeId")
    .agg($"state", $"zipCode", $"filerCommitteeId", sum("contribution"))
    .withColumnRenamed("SUM(contribution)", "contributions")

// print a few samples.
records_by_zip.take(10).foreach(println)

//
// Get committee -> candidate -> House District.
//
var committees = sqlContext.jsonFile("wasb://fecfilings@openfecdata.blob.core.windows.net/raw_mappings/committee.json")
committees.registerTempTable("committees")

var candidates = sqlContext.jsonFile("wasb://fecfilings@openfecdata.blob.core.windows.net/raw_mappings/candidate.json")
candidates.registerTempTable("candidates")

// Limit to house races.
val house_candidates = candidates
    .where($"CAND_OFFICE" === "H")
    .where($"CAND_PCC" !== "")
    .select($"CAND_PCC", $"CAND_NAME", $"CAND_OFFICE_DISTRICT", $"CAND_OFFICE_ST", $"CAND_PTY_AFFILIATION")


//
// Join records to House candidates. This will eliminate many records for other races.
//
val contributions_with_candidate = records_by_zip.join(house_candidates, records_by_zip("filerCommitteeId") === house_candidates("CAND_PCC"))

// see rough amount contributed to House candidates.
contributions_with_candidate.agg(sum("contributions")).show()
records_by_zip.agg(sum("contributions")).show()


//
// Get the number of districts per zip code. We use this to avoid double counting contributions.
//
val records_reduce = records_by_zip
    .join(num_districts_in_zip, records_by_zip("zipCode") === num_districts_in_zip("zcta"), "left_outer")
    .selectExpr("*", "coalesce(NumDistricts, 1) AS NumDistrictsNotNull")
    .selectExpr("*", "coalesce(contributions, 1) / coalesce(NumDistricts, 1) AS contributionsAdjusted")

// TODO - put this division back in somewhere. It should show up on both of our records_by_district_*matches dfs.

records_reduce.groupBy($"NumDistricts").count().show()

// Build out set of matches and non-matches.
// Get matches and non-matches.
val zip_to_committee_renamed = zip_to_district_DF.withColumnRenamed("state", "_state").withColumnRenamed("zcta", "_zcta")
val _records_by_district_matches = records_reduce
    .join(zip_to_committee_renamed, (records_reduce("state") === zip_to_committee_renamed("_state")) && (records_reduce("zcta") === zip_to_committee_renamed("_zcta")))

val records_by_district_nomatches = records_reduce
    .join(zip_to_committee_renamed, (records_reduce("state") === zip_to_committee_renamed("_state")) && (records_reduce("zcta") === zip_to_committee_renamed("_zcta")), "left")
    .selectExpr("*", "coalesce(_state, \"\") AS _state2")
    .where($"_state2" === "")

// the non-matches are hard. 

// for states with 1 district, just fix them.
val states_one_district = sc
    .parallelize(Array("ND", "SD", "AK", "DE", "MT", "VT", "WY"))
    .toDF
    .selectExpr("1 AS _zcta", "1 AS district", "_1 AS _state")

val records_from_single_rep_states = records_by_district_nomatches
    .select($"state", $"zipCode", $"filerCommitteeId", $"contributions", $"zcta", $"NumDistricts", $"NumDistrictsNotNull", $"contributionsAdjusted")
    .join(states_one_district, records_by_district_nomatches("state") === states_one_district("_state"))

val records_by_district_matches = _records_by_district_matches.unionAll(records_from_single_rep_states)


// a strategy:
// Get zip -> city/state && zip -> district.
// Get city/state -> district
// Get city/state -> #districts
// city/state -> district, #districts.

// match to candidate.
val records_by_district_matches_with_candidate = records_by_district_matches
    .join(house_candidates, records_by_district_matches("filerCommitteeId") === house_candidates("CAND_PCC"))


records_by_district_matches_with_candidate.cache()

// Group by source and target district and state.
val cross_contributions = records_by_district_matches_with_candidate
    .groupBy($"CAND_OFFICE_DISTRICT", $"CAND_OFFICE_ST", $"state", $"district")
    .agg($"CAND_OFFICE_DISTRICT", $"CAND_OFFICE_ST", $"state", $"district", count("contributions"), sum("contributions"))

cross_contributions.where($"CAND_OFFICE_DISTRICT" === "11").where($"CAND_OFFICE_ST" === "NC").orderBy($"SUM(contributions)" * -1).show(50)

cross_contributions.repartition(1).save("wasb://fecfilings@openfecdata.blob.core.windows.net/processed_output/cross_contributions.json", "json")


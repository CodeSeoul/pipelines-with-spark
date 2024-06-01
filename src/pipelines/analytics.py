from typing import Dict

from pyspark.sql import DataFrame
from pyspark.sql.functions import max, avg


def get_accreditation_stats_per_university(tables: Dict[str, DataFrame]):
    joined_data = tables["accreditation"] \
        .join(tables["university_accreditation"], tables["accreditation"].id == tables["university_accreditation"].accreditation_id,  "inner") \
        .join(tables["university"], tables["university"].id == tables["university_accreditation"].university_id)
    
    output = joined_data.groupBy("name").agg(max("score"), avg("score"))
    return output

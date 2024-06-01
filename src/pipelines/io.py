from pathlib import Path
from typing import Dict

from pyspark.sql import SparkSession, DataFrame
import pyspark.sql.functions as f


def cleanup(output_path: str="output"):
    if not Path(output_path).exists():
        return
    for path in Path(output_path).iterdir():
        if path.is_file():
            path.unlink()
        else:
            cleanup(path)
    Path(output_path).rmdir()



def read_inputs(spark: SparkSession, data_path: str="data/All India Survey on Higher Education"):
    """
    Reads from our data into various data "tables" as dataframes. Outputs a dictionary with keys
    of the name of the type of data and values of dataframes combining all years. Note that each
    dataframe has the year added from the file name.
    """

    spark.udf.register("filename", lambda x: x.rsplit("/", 1)[-1])

    tables: Dict[str, DataFrame] = {}
    for path in Path(data_path).glob("*.csv"):
        # Create a dataframe from the file
        # Read in CSV headers
        # Parse the year out of the file name and add it as a column
        dataframe = spark.read.option("header", "true") \
            .format("csv") \
            .load(str(path)) \
            .withColumn("file_year", f.split(f.element_at(f.split(f.input_file_name(), "/"), -1), "_")[0])
        # Parse out the name of the type of data from the file name
        data_name = "_".join(path.name.removesuffix(".csv").split("_")[2:])

        # In our table dictionary, store the dataframe for the data type
        if data_name in tables.keys():
            # If we already have a dataframe, union it
            tables[data_name] = tables[data_name].union(dataframe)
        else:
            # Otherwise, set it as the dataframe
            tables[data_name] = dataframe
    
    return tables
    


def dump_output(dataframes: Dict[str, DataFrame], output_path: str="output"):
    # Make sure the output path exists
    output_dir = Path(output_path)
    output_dir.mkdir(exist_ok=True)

    for name, dataframe in dataframes.items():
        # Use Pandas to write things to a single CSV instead of HDFS-like things
        dataframe.toPandas().to_csv(output_dir / f"{name}.csv", index=False)

from pyspark.sql import SparkSession
from pipelines.example import pipeline


def main():
    # Create a SparkSession
    spark = SparkSession.builder \
        .appName("ExampleApplication") \
        .getOrCreate()

    # Call your application logic or function and pass the SparkSession
    pipeline(spark)

    # Stop the SparkSession when done
    spark.stop()

if __name__ == "__main__":
    main()

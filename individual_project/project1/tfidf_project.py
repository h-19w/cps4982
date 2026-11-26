import re
import os
import math
from pyspark import SparkConf, SparkContext
from pyspark.sql.session import SparkSession

def removeSomeTexts(text):
    return re.sub(r"[^a-z-'\s]",'', text)

spark = SparkSession.builder.appName('MyTf-Idf').getOrCreate()
sc = spark.sparkContext

# 1. READ FROM HDFS (novels))
data = sc.wholeTextFiles('hdfs://localhost:9000/input')
numFiles = data.count()
print(f"Total files processed: {numFiles}")

# 2. COMPUTE WORD COUNT
wordcount = data.flatMap(lambda x: [((os.path.basename(x[0]), removeSomeTexts(i.lower())), 1) for i in re.split('\W+', x[1])]) \
        .reduceByKey(lambda a, b: a + b)\
        .map(lambda x: (x[0][1],(x[0][0],x[1])))\
        .filter(lambda x: x[0] != '')

# 3. CALCULATE TF (Term Frequency)
tf = wordcount.map(lambda x: (x[0],(x[1][0], 1+math.log10((x[1][1]) ))))

# 4. CALCULATE IDF (Inverse Document Frequency)
idf = wordcount.map(lambda x: (x[0], 1))\
        .reduceByKey(lambda x, y: x + y)\
        .map(lambda x: (x[0], math.log10(numFiles / (x[1]))))

# 5. COMBINE TF AND IDF
tfidf = tf.join(idf).map(lambda x: (x[1][0][0], (x[0], x[1][0][1] * x[1][1]))).sortByKey()\
        .map(lambda x:(x[1][0], (x[0], x[1][1]))).filter(lambda x: x[0]!='')\
        .sortByKey()

# 6. SAVE AS PARQUET TO HDFS (This is the file the website needs)
# Ensure you delete the output folder first if it exists!
lines = tfidf.map(lambda x: (x[0], x[1][0], x[1][1])).toDF()
lines.write.mode("overwrite").parquet('hdfs://localhost:9000/output/ParquetIndex')

print("TF-IDF Index successfully saved to HDFS at /output/Parquet!")

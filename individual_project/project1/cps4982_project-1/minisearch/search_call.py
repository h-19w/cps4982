# https://www.ajihuo.com/pycharm/4197.html

from pyspark import SparkConf, SparkContext 
from pyspark.sql import SparkSession, SQLContext 
import os, re, sys, math

#read data from local file system
spark = SparkSession.builder.master('local').appName('searchcall').getOrCreate()
#read data from docker container
#spark = SparkSession.builder.appName('MySearch')\
#	.config("spark.hadoop.dfs.client.use.datanode.hostname", "true").getOrCreate()
sc = spark.sparkContext

#172.31.13.156
sql = SQLContext(sc)
tfidf_RDD = sql.read.parquet("hdfs://localhost:9000/output/ParquetIndex").rdd.map(lambda x: (x['_1'],(x['_2'],x['_3'])))
#data in hdfs file format
#tfidf_RDD = sql.read.parquet("hdfs://172.31.13.156:9000/user/root/output/bookpico-tfidf").rdd.map(lambda x: (x['_2'],(x['_1'],x['_3'])))

#You can also submit the job to a spark cluster, e.g.: 
#spark = SparkSession.builder.master('spark://johnzhang10:7077').appName('searchcall').getOrCreate()
#sc = spark.sparkContext 
#sql = SQLContext(sc) 
#Be careful, in case of spark cluster, the tf-idf index should be in an HDFS, e.g.: 
#tfidf_RDD=sql.read.parquet(‘hdfs://johnzhang10:9000/output/tfidf_500m_index’)

# parquet files are not compatible for ubuntu and windows system


def tokenize(s): 
      return re.split("\\W+", s.lower())

def search(query, topN):

        tokens = sc.parallelize(tokenize(query)).map(lambda x: (x, 1) ).collectAsMap()
        print(tokens)

        bcTokens = sc.broadcast(tokens)
        print(bcTokens)

        joined_tfidf = tfidf_RDD.map(lambda x: (x[0], bcTokens.value.get(x[0], '-'), x[1]) ).filter(lambda x: x[1] != '-' ) 
        print(joined_tfidf.take(20))

        scount = joined_tfidf.map(lambda a: a[2]).aggregateByKey((0,0), (lambda acc, value: (acc[0] + value, acc[1] + 1)),
                                                                 (lambda acc1, acc2: (acc1[0] + acc2[0], acc1[1] + acc2[1])) )
        print(scount.take(20))

        scores = scount.map(lambda x: (x[1][0]*x[1][1]/len(tokens), x[0])).top(topN) ##sorted by top
        #scores = scount.filter(lambda x: x[1][1] == len(tokens)).map(lambda x: (x[1][0], x[0])).top(topN) ##sorted by top
        print(scores)
        return topN, scores

def read_file(f):
        print(f)
        filename = "minisearch/static/gutenberg/" + f
        print(filename)
        data = sc.textFile(filename)
        content = data.collect()
        return content

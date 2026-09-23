import java.util.Collections;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.input.FileSplit;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.log4j.BasicConfigurator;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;

public class InvertedIndex {
  

    public static class MyMapper extends Mapper<LongWritable, Text, Text, Text> {

        private String pattern = "[^a-zA-Z]";//only find keyword with 26 English characters

        @Override
        protected void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException {
            // get file name
            FileSplit fileSplit = (FileSplit) context.getInputSplit();
            // convert each line to a String
            String line = value.toString();
            // replace punctuations with space, only keep english words defined with the pattern
            line = line.replaceAll(pattern, " ");
            line = line.toLowerCase();
            // split String to be individual words
            String[] words = line.split("\\s+");
            // initialize each word frequency as 1,  let (word,fileName) as our key
            // save word frequency 1 as Text, consisting with the output of Combiner
            for (String word : words) {
                if (word.length() > 0) {
                    context.write(new Text(word + "," + fileSplit.getPath().getName()), new Text("1"));
                }
            }
        }
    }

    public static class MyCombiner extends Reducer<Text, Text, Text, Text> {
        protected void reduce(Text key, Iterable<Text> values, Context context) throws IOException, InterruptedException {
            // initialize each word frequency to be 0
            Integer count = 0;
            // Accumulate same word within the same file
            for (Text value : values) {
                count += Integer.parseInt(value.toString());
            }
            // split word and filename in each key
            // find the index of coma first in order to split them
            Integer splitIndex = key.find(",");
            // save as (fileName,count) as value this time, use ":" as delimiter
            context.write(
                    new Text(key.toString().substring(0, splitIndex)),
                    new Text(count + ":"+ key.toString().substring(splitIndex+1)));
        }
    }

    public static class MyReducer extends Reducer<Text, Text, Text, Text> {
        protected void reduce(Text key, Iterable<Text> values, Context context) throws IOException, InterruptedException {
            // count is used for counting how many files has this word, and initialized to be 0
            Integer count = 0;
            // save value (filename and word frequency) with a List
            ArrayList<String> fileList = new ArrayList<String>();

            // for the same word, save each key(filename+word frequency) to a List，and count plus 1
            for (Text value : values) {
                fileList.add(value.toString());
                count += 1;
            }

            //todo, sort fileList, the inverted index for ranking purpose
         


	// todo: sort fileList, the inverted index
	   Collections.sort(fileList, (a, b) -> {
		int countA = Integer.parseInt(a.split(":")[0]);
		int countB = Integer.parseInt(b.split(":")[0]);
		return countB - countA; // descending
		});	
            // finally, output result, each word per line
            // the output format is:
            //word, followed by a list of filename and word frequency, split by a \t
            context.write(key, new Text(String.join("\t", fileList)));
        }
    }

    //Main
    //This program calculate tdidf and also do inverted index as well
    public static void main(String[] args) throws Exception {
        if (args.length != 2) {
            System.err.println("Usage: InvertedIndex <input path> <output path>");
            System.exit(-1);
        }

        BasicConfigurator.configure();


        // create configuration object
        Configuration conf = new Configuration();

        //create a hdfs file system object
        FileSystem hdfs = FileSystem.get(conf);

        // create Job instance
        Job job = Job.getInstance(conf, "Inverted Index");
        // set run Job class
        job.setJarByClass(InvertedIndex.class);
        // set Mapper class
        job.setMapperClass(MyMapper.class);
        // set Combiner class
        job.setCombinerClass(MyCombiner.class);
        // set Reducer class
        job.setReducerClass(MyReducer.class);
        // set Map output <Key, value>
        job.setMapOutputKeyClass(Text.class);
        job.setOutputValueClass(Text.class);
        // set Reduce output <Key, value>
        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(Text.class);

        // set up input and output path
        FileInputFormat.setInputPaths(job, new Path(args[0]));
        Path outpath = new Path(args[1]);
        if(hdfs.exists(outpath)){
            hdfs.delete(outpath, true);
        }
        FileOutputFormat.setOutputPath(job, outpath);

        // submit job
        boolean b = job.waitForCompletion(true);
        if(!b) {
            System.out.println("InvertedIndex task failed!");
        }
    }
}

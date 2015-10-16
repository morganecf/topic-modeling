// http://nlp.stanford.edu/software/tmt/0.3/
 
// tells Scala where to find the TMT classes
import scalanlp.io._;
import scalanlp.stage._;
import scalanlp.stage.text._;
import scalanlp.text.tokenize._;
import scalanlp.pipes.Pipes.global._;
 
import edu.stanford.nlp.tmt.stage._;
import edu.stanford.nlp.tmt.model.lda._;
import edu.stanford.nlp.tmt.model.llda._;
 
// load the model 
val modelPath = file("../data/llda-cvb0-1000-docs-all-subreddits-filtered-part-37");
val lldaModel = LoadCVB0LabeledLDA(modelPath);
val model = lldaModel.asCVB0LDA;
 

//println("Writing top terms to "+output+"-top-terms.csv");
val topTerms = QueryTopTerms(lldaModel, 500);
CSVFile("/home/evan/reddit_topics/1000-docs-all-subreddits-filtered-part-37-top-terms.csv").write(topTerms);

//Works
//TSVFile(outputPath).write(perDocTopicDistributions);
//val topTerms = QueryTopTopics(model, dataset, perDocWordTopicDistributions);
/*val source = CSVFile("../data/twitter/llda_tweets.party.csv") ~> IDColumn(1);
//val source = TSVFile(inputPath) ~> IDColumn(1);
val text = {
	source ~> 
	Column(2) ~> 
	TokenizeWith(model.tokenizer.get)
}

// turn text into dataset ready to be used by LDA 
val dataset = LDADataset(text,model.termIndex);

// Base name of output files to generate
val output = file(modelPath, source.meta[java.io.File].getName.replaceAll(".csv",""));

println("Writing document distributions to "+output+"-document-topic-distributions.csv");
val perDocTopicDistributions = InferCVB0DocumentTopicDistributions(model, dataset);
CSVFile(output+"-document-topic-distributuions.csv").write(perDocTopicDistributions);

println("Writing topic usage to "+output+"-usage.csv");
val usage = QueryTopicUsage(model, dataset, perDocTopicDistributions);
CSVFile(output+"-usage.csv").write(usage);

println("Estimating per-doc per-word topic distributions");
val perDocWordTopicDistributions = EstimatePerWordTopicDistributions(
  model, dataset, perDocTopicDistributions);

*/

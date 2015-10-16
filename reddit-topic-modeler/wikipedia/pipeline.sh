##### NEW ROUND OF REDDIT DATA 

## Label the collapsed components in data/collapsed-components/ - separately to avoid having duplicates with different ids
cut -f1 collapsed-subreddit-components.tsv | awk '{print NR"\t"$0}' > ../id-mapping_subreddits.tsv
cat collapsed-subreddit-components.tsv | awk '{split($0, a, "\t"); for (i in a) { if(i>1) { print NR"\t"a[i] }}}' > ../id-mapping_wikipages.tsv
# Get the last id of the current labeling 
wc -l ../id-mapping_subreddits.tsv 
# happens to be 58894 - now continue labeling the wikipedia components starting with this label 
cat collapsed-wikipedia-components.tsv | awk  '{split($0, a, "\t"); for (i in a) print NR+58894"\t"a[i]}' >> ../id-mapping_wikipages.tsv 

# Make a separate id mapping for just the first wikipage (the parent) of each component 
cat collapsed-wikipedia-components.tsv | awk  '{split($0, a, "\t"); print NR+58894"\t"a[1]}' >> ../id-mapping_wikipages-parent.tsv 

# to check that the first two steps worked out, these should both have the same number of lines:
cut -f1 --complement collapsed-subreddit-components.tsv | awk '{split($0, a, "\t"); for (i in a) print NR"\t"a[i]}' | cut -f1 | sort -u | wc -l
cut -f1 collapsed-subreddit-components.tsv | awk '{print NR"\t"$0}' | wc -l

## Generate the reddit data - all submissions, all comments, #words >= 500 

# Go through all dumped data 
python src/reddit_content.py data/collapsed-components/mapping.tsv data/current-wd/reddit-content_all.tsv -1 -1 9999
# Keep docs with number of words >= 500 
cat reddit-content_all.tsv | awk '{if(NF>=500) print $0}' > reddit-content.tsv
# Get just the subreddits 
cut -f1 reddit-content.tsv > subreddits.txt

## Generate Wikipedia data

# First get all the wikipages we need 
python wiki_pages_needed.py ../collapsed-components/mapping.tsv ../collapsed-components/collapsed-subreddit-components.tsv ../collapsed-components/collapsed-wikipedia-components.tsv subreddits.txt wikipages_needed.txt
# Now run the content extraction script 
python src/wiki_content.py data/current-wd/wikipages_needed.txt data/current-wd/wikipedia-content.tsv

## Label the Reddit data 

# get list of subreddit names 
cut -f1 reddit-content.tsv > subreddits.txt
# get list of labels
python label.py subreddits.txt reddit > label-to-subreddit-mapping.tsv
# get just the data 
cut --complement -f1 reddit-content.tsv > reddit-data.tsv
# now combine labels with data - make sure they have the same number of lines first 
cut -f1 label-to-subreddit-mapping.tsv > reddit-labels.txt
wc -l reddit-labels.txt; wc -l reddit-data.tsv
paste -d'\t' reddit-labels.txt reddit-data.tsv > reddit-data-labeled.tsv

## Label wikipedia data 

# Get just the wikipage names 
cut -f1 wikipedia-content.tsv > wikipages.txt
# Get just the data
cut --complement -f1 wikipedia-content.tsv > wikipedia-data.txt
# Label the page names 
python label.py wikipages.txt wikipedia > label-to-wikipage-mapping.tsv
# Now label the data 
cut -f1 label-to-wikipage-mapping.tsv > wiki-labels.txt
wc -l wiki-labels.txt; wc -l wikipedia-data.txt 
paste -d'\t' wiki-labels.txt wikipedia-data.txt > wikipedia-data-labeled.tsv

## Aggregate wikipedia data

# Sort by the first column 
sort -nk1 wikipedia-data-labeled.tsv > wikipedia-data-labeled_sorted.tsv
# Aggregate by label 
python aggregate_data.py wikipedia-data-labeled_sorted.tsv > wikipedia-data-labeled_aggregated.tsv
# Make sure there's the same number of documents as there are unique labels
wc -l wikipedia-data-labeled_aggregated.tsv; cut -f1 wikipedia-data-labeled_aggregated.tsv | sort -u | wc -l 

# Create separate wiki/reddit wikipedia data files
python separate_reddit_from_wiki.py reddit-labels.txt wikipedia-data-labeled_aggregated.tsv wikipedia-data_reddit.tsv wikipedia-data_wiki.tsv

# Check that wiki-reddit labels are a proper subset of reddit labels 
cut -f1 wikipedia-data_reddit.tsv > test_labels.txt ; cut -f1 reddit-data-labeled.tsv >> test_labels.txt
# The following two outputs should be the same
wc -l reddit-data-labeled.tsv; sort -u test_labels.txt | wc -l
rm -f test_labels.txt

# Now remove reddit documents that don't appear in wiki-reddit data 
cut -f1 wikipedia-data_reddit.tsv > wiki-reddit-labels.txt
python remove_reddit_with_no_wiki.py reddit-data-labeled.tsv wiki-reddit-labels.txt > reddit-data-labeled_reduced.tsv
# Reddit data should now be the same size as wiki-reddit data 
wc -l reddit-data-labeled_reduced.tsv; wc -l wikipedia-data_reddit.tsv

# Reduce wikipedia-only data - take documents that have >= 1000 words 
cat wikipedia-data_wiki.tsv | awk '{if(NF>=1000) print $0}' > wikipedia-data_wiki_reduced.tsv

## Create the null model data

cat wikipedia-data_wiki_reduced.tsv > null-data.tsv 
cat wikipedia-data_reddit.tsv >> null-data.tsv 
# check that each document has a unique label - these 2 commands should be the same
wc -l null-data.tsv ; cut -f1 null-data.tsv | sort -u | wc -l

## Get Reddit TF, IDF, and TF-IDF lists 

# Get the unique word list with counts 
cut -f1 --complement reddit-data.tsv | tr [:space:] '\n' | sort | uniq -c > tfidf-stats/reddit-words.txt
# Only allow words that appear at least 50 times in corpus
cat tfidf-stats/reddit-words.txt | awk '{if($1>=50) print $2}' > tfidf-stats/reddit-words_count_gt_50.txt
# Create the word lists -- in tfidf-stats/
python calculate_tfidf.py reddit-data.tsv reddit-words_count_gt_50.txt reddit-TF.tsv reddit-IDF.tsv reddit-TFIDF.tsv 
# Sort the IDF from most common to least common words 
sort -g -k2 reddit-IDF.tsv > reddit-IDF_sorted.tsv
# Sort the TFIDF from least common to most common
sort -g -k1 -r reddit-TFIDF.tsv > reddit-TFIDF_sorted.tsv

## Get wikipedia TF, IDF, TF-IDF lists 

# Get the unique word list with counts 
cut -f1 --complement null-data.tsv | tr [:space:] '\n' | sort | uniq -c > tfidf-stats/wiki-words.txt
# Only allow words that appear at least 50 times in corpus
cat tfidf-stats/wiki-words.txt | awk '{if($1>=50) print $2}' > tfidf-stats/wiki-words_count_gt_50.txt
# Create the word lists -- in tfidf-stats/
python calculate_tfidf.py ../null-data.tsv wiki-words_count_gt_50.txt wiki-TF.tsv wiki-IDF.tsv wiki-TFIDF.tsv 
# Sort the IDF from most common to least common words 
sort -g -k2 wiki-IDF.tsv > wiki-IDF_sorted.tsv
# Sort the TFIDF from least common to most common
sort -g -k1 -r wiki-TFIDF.tsv > wiki-TFIDF_sorted.tsv

## Find the intersection of these lists 
## TODO 

## Reduce the null model vocabulary to the top words (count > 50), and format as [label] w1...wn
python reduce_vocab.py tfidf-stats/wiki-words_count_gt_50.txt null-data.tsv > null-data_formatted_reduced-vocab.txt
# get word counts before and after to compare
wc null-data.tsv ; wc null-data_formatted_reduced-vocab.txt		
# 77,142,226 and 71,522,454, so the top words (71,107) comprise 92.7% of the total vocabulary 
# make sure the vocabulary size is really what we want it to be 
cut -f1 --complement null-data_formatted_reduced-vocab.txt | tr [:space:] '\n' | sort | uniq -c | wc -l
# should be the same as 
wc -l tfidf-stats/wiki-words_count_gt_50.txt

## Create the full model data 

# Sort both files by label 
sort -nk1 wikipedia-data_reddit.tsv > wikipedia-data_reddit_sorted.tsv
sort -nk1 reddit-data-labeled_reduced.tsv > reddit-data-labeled_reduced_sorted.tsv
# Compare the two to make sure they align line-by-line 
cut -f1 wikipedia-data_reddit_sorted.tsv | head -100; cut -f1 reddit-data-labeled_reduced_sorted.tsv | head -100; 
# Now merge 
cut -f1 --complement wikipedia-data_reddit.tsv > wikipedia-data_reddit_no_labels.tsv
paste -d' ' reddit-data-labeled_reduced_sorted.tsv wikipedia-data_reddit_no_labels.tsv > full-data_reddit.tsv
# Make sure each line/document has a unique label
cut -f1 full-data_reddit.tsv | sort -u | wc -l; wc -l full-data_reddit.tsv
# Now add the wikipedia data to the full data 
cat full-data_reddit.tsv > full-data.tsv
cat wikipedia-data_wiki_reduced.tsv >> full-data.tsv
# Make sure each line/document in full data has a unique label
cut -f1 full-data.tsv | sort -u | wc -l; wc -l full-data.tsv		# 6311 documents/topics

## Now reduce the full model vocabulary to top wiki/reddit words with count > 50
cat tfidf-stats/wiki-words_count_gt_50.txt > rw_words_temp.txt
cat tfidf-stats/reddit-words_count_gt_50.txt >> rw_words_temp.txt
sort -u rw_words_temp.txt > reddit-wiki-words_count_gt_50.txt
# compare the vocabs 
wc -l rw_words_temp.txt; wc -l reddit-wiki-words_count_gt_50.txt	# 140,803 and 99,862 - intersection is ~40,000
rm -f rw_words_temp.txt

python reduce_vocab.py reddit-wiki-words_count_gt_50.txt full-data.tsv > full-data_formatted_reduced-vocab.txt
# compare the number of words before and after
wc full-data.tsv; wc full-data_formatted_reduced-vocab.txt			
# 183,262,298 and 174,317,600 - so top 99,862 word types comprise 95.1% of vocabulary
# make sure vocabulary in data is really unique 
cut -f1 --complement full-data_formatted_reduced-vocab.txt | tr [:space:] '\n' | sort | uniq -c | wc -l

## Run Naive Bayes - from wikipedia/ root dir

# FULL
python src/MLmodels.py --train NB --data data/current-wd/full-data_formatted_reduced-vocab.txt --dir models/naive_bayes/april29/full
# NULL
python src/MLmodels.py --train NB --data data/current-wd/null-data_formatted_reduced-vocab.txt --dir models/naive_bayes/april29/null

## Run LLDA 

# Reformat labels - need to be 0-indexed properly, save mapping of old to new ids in second arg
python format-llda.py full-data_formatted_reduced-vocab.txt full-data_llda.txt full-mapping-llda.tsv
python format-llda.py null-data_formatted_reduced-vocab.txt null-data_llda.txt null-mapping-llda.tsv

# cat full-data_formatted_reduced-vocab.txt | awk '{print NR-1"\t"$1}' > full-mapping-llda.tsv
# cut -f1 -d' ' --complement full-data_formatted_reduced-vocab.txt | awk '{print "["NR-1"]"" "$0}' > full-data_llda.txt
# cat null-data_formatted_reduced-vocab.txt | awk '{print NR-1"\t"$1}' > null-mapping-llda.tsv
# cut -f1 -d' ' --complement null-data_formatted_reduced-vocab.txt | awk '{print "["NR-1"]"" "$0}' > null-data_llda.txt

### THE CORRECT ID MAPPINGS TO USE ARE
	## id-mapping_wikipages.tsv
	## id-mapping_subreddits.tsv


# Zip 
cp full-data_llda.txt ../../JGibbsLLDA/src/data/
# in JGibbsLLDA/src/data/:
gzip full-data_llda.txt

cp null-data_llda.txt ../../JGibbsLLDA/src/data/
# in JGibbsLLDA/src/data/:
gzip null-data_llda.txt

# Run 
# FULL
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx200G jgibblda.LDA -est -ntopics 6311 -dfile full-data_llda.txt.gz -dir data/ -model full-model-apr27
# NULL
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx150G jgibblda.LDA -est -ntopics 6311 -dfile null-data_llda.txt.gz -dir data/ -model null-model-apr27

## Run SVM 
#FULL
python src/MLmodels.py --train SVM --data data/current-wd/full-data_formatted_reduced-vocab.txt --dir models/svm/full
#NULL
python src/MLmodels.py --train SVM --data data/current-wd/null-data_formatted_reduced-vocab.txt --dir models/svm/null

### Inference

# First create the mapping in page \t gid \t doc-type format, where doc-type is wikipedia or reddit
cat id-mapping_subreddits.tsv | awk '{print $0"\treddit"}' > id-mapping.tsv 
cat id-mapping_wikipages-parent.tsv | awk '{print $0"\twiki"}' >> id-mapping.tsv

# Now run inference on the test link data 

## Naive Bayes FULL 
python MLmodels.py --data test-url-data-427.tsv --model naive_bayes/april29/full/NBmodel.pkl --vectorizer naive_bayes/april29/full/vectorizer.pkl --mapping id-mapping.tsv --dir naive_bayes/april29/full/test-results/

## Naive Bayes NULL
python MLmodels.py --data test-url-data-427.tsv --model naive_bayes/april29/null/NBmodel.pkl --vectorizer naive_bayes/april29/null/vectorizer.pkl --mapping id-mapping.tsv --dir naive_bayes/april29/null/test-results/

## SVM FULL
python MLmodels.py --data test-url-data-427.tsv --model svm/full/SVMmodel.pkl --vectorizer svm/full/vectorizer.pkl --mapping id-mapping.tsv --dir svm/full/test-results/

## SVM NULL 
python MLmodels.py --data test-url-data-427.tsv --model svm/null/SVMmodel.pkl --vectorizer svm/null/vectorizer.pkl --mapping id-mapping.tsv --dir svm/null/test-results/

## LLDA FULL
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' jgibblda.LDA -inf -dir data/full/ -model full-model-apr27 -twords 50 -dfile test-url-data-427.txt.gz

## LLDA NULL 
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' jgibblda.LDA -inf -dir data/null/ -model full-model-apr27 -twords 50 -dfile test-url-data-427.txt.gz


## Get LLDA accuracy 
python llda-results.py null/test-url-data-427.txt.null-model-apr27.theta test-url-data-427.tsv null-mapping-llda.test.tsv
python llda-results.py full/test-url-data-427.txt.full-model-apr27.theta test-url-data-427.tsv full-mapping-llda.test.tsv


# unit tests 
# inf
# java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' jgibblda.LDA -inf -niters 150 -dir data/full/ -model full-model-apr27 -twords 50 -dfile test3.txt.gz

# # est
# java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' jgibblda.LDA -est -ntopics 30 -dfile test-30.txt.gz -dir data/ -model full-test-30


###### SECOND PASS AT TOPIC MODEL BUILDING #######

# changed current-wd to april-work
# now working in may-work

# Remove all words that appear in >= 70% of documents (just the top 112 words, apparently)
tail -69449 word-percentages_sorted.tsv > words-to-keep.tsv
cut -f1 words-to-keep.tsv > words-to-keep.txt
python reduce_vocab.py words-to-keep.txt full-data_reddit.tsv > full-data_reddit_formatted_reduced.txt

# Format wiki data in same way 
cut -f1 wikipedia-data_wiki_reduced.tsv > wiki-labels.txt 
cut -f1 --complement wikipedia-data_wiki_reduced.tsv > wiki-data.txt 
cat wiki-labels.txt | awk '{print "["$0"]"}' > wiki-labels_bracketed.txt 
paste -d" " wiki-labels_bracketed.txt wiki-data.txt > wiki-data_formatted.txt 

# Create the full data 
cat full-data_reddit_formatted_reduced.txt > full-data.txt
cat wiki-data_formatted.txt >> full-data.txt

# Relabel 
python format-llda.py full-data.txt full-data_llda.txt full-mapping-llda.tsv

# Run estimation 
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx150G jgibblda.LDA -est -ntopics 6311 -dfile full-data_llda.txt.gz -dir data/full -model full-model-may8

# relabel 

#### Build logistic regression model
python MLmodels.py --train LR --data ../data/may-work/version2/full-data.txt --dir log/full/
python MLmodels.py --train LR --data ../data/april-work/null-data_formatted_reduced-vocab.txt --dir log/null

#### Getting link data
split -l 100 urls-to-crawl1.tsv
for f in x*; do python ../../get-urls.py $f & done ;
# aggregating them - in each dir:
touch url-data.tsv; for f in dat.*; do cat $f >> url-data.tsv; done;

#### Testing link data
# NB FULL
python MLmodels.py --data test-url-data-511.tsv --model naive_bayes/april29/full/NBmodel.pkl --vectorizer naive_bayes/april29/full/vectorizer.pkl --mapping id-mapping.tsv --WRmapping reddit-wiki-mapping.tsv --num_topics 6311 --dir naive_bayes/april29/full/test-results-511/
# NB NULL
python MLmodels.py --data test-url-data-511.tsv --model naive_bayes/april29/null/NBmodel.pkl --vectorizer naive_bayes/april29/null/vectorizer.pkl --mapping id-mapping.tsv --WRmapping reddit-wiki-mapping.tsv --num_topics 6311 --dir naive_bayes/april29/null/test-results-511/

# SVM FULL
python MLmodels.py --data test-url-data-511.tsv --model svm/full/SVMmodel.pkl --vectorizer svm/full/vectorizer.pkl --mapping id-mapping.tsv --WRmapping reddit-wiki-mapping.tsv --num_topics 6311 --dir svm/full/test-results-511/
# SVM NULL
python MLmodels.py --data test-url-data-511.tsv --model svm/null/SVMmodel.pkl --vectorizer svm/null/vectorizer.pkl --mapping id-mapping.tsv --WRmapping reddit-wiki-mapping.tsv --num_topics 6311 --dir svm/null/test-results-511/

# Logistic Regression FULL
python MLmodels.py --data test-url-data-511.tsv --model log/full/SVMmodel.pkl --vectorizer log/full/vectorizer.pkl --mapping id-mapping.tsv --WRmapping reddit-wiki-mapping.tsv --num_topics 6311 --dir log/full/test-results-511/
# Logistic Regression NULL
python MLmodels.py --data test-url-data-511.tsv --model log/null/SVMmodel.pkl --vectorizer log/null/vectorizer.pkl --mapping id-mapping.tsv --WRmapping reddit-wiki-mapping.tsv --num_topics 6311 --dir log/null/test-results-511/

# LLDA FULL - do inference on each document separately 
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx50G jgibblda.LDA -inf -myinfseparately -dir data/full/ -model full-model-may8 -twords 25 -dfile test-url-data-511.txt.gz -numtestdocs 9932
# LLDA NULL - do inference on each document separately 
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx50G jgibblda.LDA -inf -myinfseparately -dir data/null-april27/ -model null-model-apr27 -twords 25 -dfile test-url-data-511.txt.gz -numtestdocs 9932

#### NOTE: move everything into separate-inf/links/
# Parsing LLDA output (get top topics for each doc and accuracy distrib)
# in full/separate-inf and null/separate-inf
for f in *.theta.gz; do gunzip $f ; done
# full
touch ../../test-url-data-511.full-model-may8.theta
for f in *.theta; do cat $f >> test-url-data-511.full-model-may8.theta; done
python llda-inf-results.py full/separate-inf/test-url-data-511.full-model-may8.theta full 10 llda-full
	# outputs llda-full-top.txt and llda-full-accuracy_distrib.tsv

# null
touch test-url-data-511.null-model-apr27.theta
for f in *.theta; do cat $f >> test-url-data-511.null-model-apr27.theta; done
python llda-inf-results.py null/separate-inf/test-url-data-511.null-model-apr27.theta null 10 llda-null
	# outputs llda-null-top.txt and llda-null-accuracy_distrib.tsv


#### GETTING YAHOO ANSWERS DATA
# Crawl the data 
python answers.py 0 25 			# or distribute on different servers; indices indicate the section of categories to scrape
# Aggregate/format
python format.py 
	# Generates yahoo-test-docs.tsv and yahoo-test-docs.txt

# Create the test set/inferences 
wc -l yahoo-test-manual-docs.tsv # should be 20 
python MLmodels.py --data yahoo-test-manual-docs.tsv --model naive_bayes/april29/full/NBmodel.pkl --vectorizer naive_bayes/april29/full/vectorizer.pkl --mapping id-mapping.tsv --WRmapping reddit-wiki-mapping.tsv --num_topics 6311 --dir naive_bayes/april29/full/yahoo-manual-test-results/
python MLmodels.py --data yahoo-test-manual-docs.tsv --model naive_bayes/april29/null/NBmodel.pkl --vectorizer naive_bayes/april29/null/vectorizer.pkl --mapping id-mapping.tsv --WRmapping reddit-wiki-mapping.tsv --num_topics 6311 --dir naive_bayes/april29/null/yahoo-manual-test-results/
python MLmodels.py --data yahoo-test-manual-docs.tsv --model svm/full/SVMmodel.pkl --vectorizer svm/full/vectorizer.pkl --mapping id-mapping.tsv --WRmapping reddit-wiki-mapping.tsv --num_topics 6311 --dir svm/full/yahoo-manual-test-results/
python MLmodels.py --data yahoo-test-manual-docs.tsv --model svm/null/SVMmodel.pkl --vectorizer svm/null/vectorizer.pkl --mapping id-mapping.tsv --WRmapping reddit-wiki-mapping.tsv --num_topics 6311 --dir svm/null/yahoo-manual-test-results/
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx150G jgibblda.LDA -inf -myinfseparately -dir data/full/ -model full-model-may8 -twords 25 -dfile yahoo-test-manual-docs.txt.gz -numtestdocs 20
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx50G jgibblda.LDA -inf -myinfseparately -dir data/null-april27/ -model null-model-apr27 -twords 25 -dfile yahoo-test-manual-docs.txt.gz -numtestdocs 20

## Rerunning the yahoo answers inference stuff (with new dataset w/ links)
# 5893 yahoo docs ==> use this as -numtestdocs opt for LLDA myinfseparately 
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx150G jgibblda.LDA -inf -myinfseparately -dir data/full/ -model full-model-may8 -twords 25 -dfile yahoo-test-docs.txt.gz -numtestdocs 5893
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx50G jgibblda.LDA -inf -myinfseparately -dir data/null-april27/ -model null-model-apr27 -twords 25 -dfile yahoo-test-docs.txt.gz -numtestdocs 5893
python MLmodels.py --data yahoo-test-docs.tsv --model naive_bayes/april29/full/NBmodel.pkl --vectorizer naive_bayes/april29/full/vectorizer.pkl --mapping id-mapping.tsv --WRmapping reddit-wiki-mapping.tsv --num_topics 6311 --dir naive_bayes/april29/full/yahoo-test-results/
python MLmodels.py --data yahoo-test-docs.tsv --model naive_bayes/april29/null/NBmodel.pkl --vectorizer naive_bayes/april29/null/vectorizer.pkl --mapping id-mapping.tsv --WRmapping reddit-wiki-mapping.tsv --num_topics 6311 --dir naive_bayes/april29/null/yahoo-test-results/
python MLmodels.py --data yahoo-test-docs.tsv --model svm/full/SVMmodel.pkl --vectorizer svm/full/vectorizer.pkl --mapping id-mapping.tsv --WRmapping reddit-wiki-mapping.tsv --num_topics 6311 --dir svm/full/yahoo-test-results/
python MLmodels.py --data yahoo-test-docs.tsv --model svm/null/SVMmodel.pkl --vectorizer svm/null/vectorizer.pkl --mapping id-mapping.tsv --WRmapping reddit-wiki-mapping.tsv --num_topics 6311 --dir svm/null/yahoo-test-results/

#### GETTING STACK EXCHANGE DATA 
# Remove wiki/stackexchange links 
python filter.py 
# Split into 4 files , put these in separate dirs 
split -l 100000 se-tags-to-links_filtered.tsv
# Further split each of 4 into ones of size 1000 
split -l 1000 se-links.tsv
# Go into each dir and run:
for f in x*; do python ../scrape-SE-links.py $f & done ;
# aggregating them - in each dir:
touch se-link-data.tsv; for f in dat.*; do cat $f >> se-link-data.tsv; done;

#### Testing yahoo answers data 
# NB FULL
python MLmodels.py --data yahoo-test-docs.tsv --model naive_bayes/april29/full/NBmodel.pkl --vectorizer naive_bayes/april29/full/vectorizer.pkl --mapping id-mapping.tsv --WRmapping reddit-wiki-mapping.tsv --num_topics 6311 --dir naive_bayes/april29/full/yahoo-test-results/
# NB NULL
python MLmodels.py --data yahoo-test-docs.tsv --model naive_bayes/april29/null/NBmodel.pkl --vectorizer naive_bayes/april29/null/vectorizer.pkl --mapping id-mapping.tsv --WRmapping reddit-wiki-mapping.tsv --num_topics 6311 --dir naive_bayes/april29/null/yahoo-test-results/
# SVM FULL
python MLmodels.py --data yahoo-test-docs.tsv --model svm/full/SVMmodel.pkl --vectorizer svm/full/vectorizer.pkl --mapping id-mapping.tsv --WRmapping reddit-wiki-mapping.tsv --num_topics 6311 --dir svm/full/yahoo-test-results/
# SVM NULL
python MLmodels.py --data yahoo-test-docs.tsv --model svm/null/SVMmodel.pkl --vectorizer svm/null/vectorizer.pkl --mapping id-mapping.tsv --WRmapping reddit-wiki-mapping.tsv --num_topics 6311 --dir svm/null/yahoo-test-results/
# LR FULL
python MLmodels.py --data yahoo-test-docs.tsv --model log/full/SVMmodel.pkl --vectorizer log/full/vectorizer.pkl --mapping id-mapping.tsv --WRmapping reddit-wiki-mapping.tsv --num_topics 6311 --dir log/full/yahoo-test-results/
# LR NULL
python MLmodels.py --data yahoo-test-docs.tsv --model log/null/SVMmodel.pkl --vectorizer log/null/vectorizer.pkl --mapping id-mapping.tsv --WRmapping reddit-wiki-mapping.tsv --num_topics 6311 --dir log/null/yahoo-test-results/

# LLDA FULL
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx150G jgibblda.LDA -inf -myinfseparately -dir data/full/ -model full-model-may8 -twords 25 -dfile yahoo-test-docs.txt.gz -numtestdocs 5485
# LLDA NULL
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx50G jgibblda.LDA -inf -myinfseparately -dir data/null-april27/ -model null-model-apr27 -twords 25 -dfile yahoo-test-docs.txt.gz -numtestdocs 5485

# For parsing do the same thing as above  - in separate-inf/yahoo (full and null)
for f in *.theta.gz; do gunzip $f ; done

# full
python aggregate-thetas.py yahoo-test-docs full-model-may8 full/separate-inf/yahoo/ 5485
	# outputs yahoo-test-docs.full-model-may8.theta
# seems to be off by one so add a dummy line to the file 
mv yahoo-test-docs.full-model-may8.theta yahoo-test-docs.full-model-may8-temp.theta
echo 'DUMMY' > yahoo-test-docs.full-model-may8.theta
cat yahoo-test-docs.full-model-may8-temp.theta >> yahoo-test-docs.full-model-may8.theta
rm -f yahoo-test-docs.full-model-may8-temp.theta
python llda-inf-results.py yahoo-test-docs.full-model-may8.theta yahoo-test-docs.tsv full yahoo 10 6311 llda-full-yahoo
	# outputs llda-full-yahoo-top.txt

# null
python aggregate-thetas.py yahoo-test-docs null-model-apr27 null-april27/separate-inf/yahoo/ 5485
mv yahoo-test-docs.null-model-apr27.theta yahoo-test-docs.null-model-apr27-temp.theta; echo 'DUMMY' > yahoo-test-docs.null-model-apr27.theta; cat yahoo-test-docs.full-model-may8-temp.theta >> yahoo-test-docs.null-model-apr27.theta; rm -f yahoo-test-docs.full-model-may8-temp.theta
python llda-inf-results.py yahoo-test-docs.null-model-apr27.theta yahoo-test-docs.tsv null yahoo 10 6311 llda-null-yahoo
	# outputs llda-null-yahoo-top.txt

#### PIPELINE FOR TRAINING MODELS ONE DOCUMENT AT A TIME 

# in may-work/disaggregated 

## Regenerate the reddit data - but save one document at a time (post+comments)

# Go through all dumped data 
python src/reddit_content_per_doc.py data/collapsed-components/mapping.tsv data/may-work/disaggregated/reddit-content_all.tsv -1 -1 9999
# Only keep docs from subreddits we were using before
python keep-relevant.py subreddits.txt reddit-content_all.tsv > reddit-content.tsv 

# wikipedia-data-labeled_sorted.tsv has wiki-reddit and rest of wiki data by doc with labels, sorted 
# Only keep docs from subreddits/wikipages we were using before 
python keep-relevant.py labels.txt wikipedia-data-labeled_sorted.tsv > wiki-content_labeled.tsv 

# Label reddit docs with their ids 
python label.py id-mapping_subreddits.tsv reddit-content.tsv > reddit-content_labeled.tsv 

# Remove words from reddit data that occur in >70% of subreddits and occur < 50 times 
cat reddit-words_count_gt_50.txt > reddit-words-to-keep.txt
cat words-to-keep.txt >> reddit-words-to-keep.txt
sort -u reddit-words-to-keep.txt > reddit-words-to-keep_sorted.txt
python reduce_vocab.py reddit-words-to-keep_sorted.txt reddit-content_labeled.tsv  > reddit-content_reduced_labeled.tsv

# Remove words with count < 50 in wiki data
python reduce_vocab.py wiki-words_count_gt_50.txt wiki-content_labeled.tsv  > wiki-content_reduced_labeled.tsv

# Null data is just the wikipedia data 
cat wiki-content_reduced_labeled.tsv > null-data-DISAG.tsv 

# Create the full data 
cat wiki-content_reduced_labeled.tsv > full-data-DISAG.tsv
cat reddit-content_reduced_labeled.tsv >> full-data-DISAG.tsv

# Format for LLDA 
python format.py full-data-DISAG.tsv full-data_llda-DISAG.txt full-llda-mapping-DISAG.tsv 
python format.py null-data-DISAG.tsv null-data_llda-DISAG.txt null-llda-mapping-DISAG.tsv 

# Now we're ready to train! 

# LLDA 
# FULL
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx150G jgibblda.LDA -est -ntopics 6311 -dfile full-data_llda-DISAG.txt.gz -dir data/full -model full-model-may8
# NULL
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx80G jgibblda.LDA -est -ntopics 6311 -dfile null-data_llda-DISAG.txt.gz -dir data/null-april27 -model null-model-apr27

# NAIVE BAYES - in models/
# FULL
python MLmodels.py --train NB --data full-data-DISAG.tsv --dir naive_bayes/disaggregated/full
# NULL
python MLmodels.py --train NB --data null-data-DISAG.tsv --dir naive_bayes/disaggregated/null

# SVM 
# FULL
python MLmodels.py --train SVM --data full-data-DISAG.tsv --dir svm/disaggregated/full
# NULL
python MLmodels.py --train SVM --data null-data-DISAG.tsv --dir svm/disaggregated/null


# Figure out how many documents from yahoo LLDA inference don't have topics
# (i.e., labels whose probabilities are < threshold)
python non-topics.py yahoo/llda/llda-full-yahoo-top.txt 0.05

### MANUAL TESTS - LINKS
# LLDA null/full inference still not done on link so had to put 
# all the separate theta files currently completed in links-514 
mv test-url-data-511.txt_* links-514/
# Now unzip them 
for f in *.theta.gz ; do gunzip $f; done
# Check if 0 is dummy
wc -l test-url-data-511.txt_0.full-model-may8.theta
# Now aggregate in order 
python aggregate-thetas.py test-url-data-511 full-model-may8 full/separate-inf/links-514/ 868 
python aggregate-thetas.py test-url-data-511 null-model-apr27 null-april27/separate-inf/links-514/ 1012
# Add dummy variable to first line if necessary
mv test-url-data-511.null-model-apr27.theta temp.theta; echo 'DUMMY' > test-url-data-511.null-model-apr27.theta; cat temp.theta >> test-url-data-511.null-model-apr27.theta; rm -f temp.theta
mv test-url-data-511.full-model-may8.theta temp.theta; echo 'DUMMY' > test-url-data-511.full-model-may8.theta; cat temp.theta >> test-url-data-511.full-model-may8.theta; rm -f temp.theta
# Get results 
python llda-inf-results.py test-url-data-511_subset514.full-model-may8.theta test-url-data-511.tsv full links 10 6311 llda-full-subset514
python llda-inf-results.py test-url-data-511_subset514.null-model-apr27.theta test-url-data-511.tsv null links 10 6311 llda-null-subset514

# Find the set that passes our threshold test 
python non-topics.py links/llda/llda-full-subset514-top.txt 0.05
	# Number of documents with 0 topics: 7
	# Number of documents with < 3 topics: 112
	# Number of documents with >= 3 topics: 746
	# Total number of documents: 865 865 865
python non-topics.py links/llda/llda-null-subset514-top.txt 0.05
	# Number of documents with 0 topics: 12
	# Number of documents with < 3 topics: 350
	# Number of documents with >= 3 topics: 647
	# Total number of documents: 1009 1009 1009

# Now create tests (edit file)
python manual-tests.py 

### MANUAL TESTS - YAHOO Q&A
mv yahoo-test-docs* yahoo-515
for f in *.theta.gz ; do gunzip $f; done
ls *.theta | wc -l 
python aggregate-thetas.py yahoo-test-docs full-model-may8 full/separate-inf/yahoo-515/ 5893
python aggregate-thetas.py yahoo-test-docs null-model-apr27 null-april27/separate-inf/yahoo-515/ 5893
wc -l yahoo-test-docs.full-model-may8.theta ; wc -l yahoo-test-docs.null-model-apr27.theta
mv yahoo-test-docs.null-model-apr27.theta temp.theta; echo 'DUMMY' > yahoo-test-docs.null-model-apr27.theta; cat temp.theta >> yahoo-test-docs.null-model-apr27.theta; rm -f temp.theta
mv yahoo-test-docs.full-model-may8.theta temp.theta; echo 'DUMMY' > yahoo-test-docs.full-model-may8.theta; cat temp.theta >> yahoo-test-docs.full-model-may8.theta; rm -f temp.theta
python llda-inf-results.py yahoo-test-docs.full-model-may8.theta yahoo-test-docs.tsv full yahoo 10 6311 llda-full-yahoo
python llda-inf-results.py yahoo-test-docs.null-model-apr27.theta yahoo-test-docs.tsv null yahoo 10 6311 llda-null-yahoo


### WIKIPEDIA EXTERNAL REFERENCES 
python extract-wiki-urls.py 		# In wikidump/

# contains the intersection of wiki pages from the wiki content we have, wiki pages from WiBi taxonomy,
# and wiki pages from the link data we have -- 2,384,687 total 
wibi-wiki-links-pages-intersection.txt

wikipedia-external-links1.tsv	# First 3 random links - 5,081,876 total
wikipedia-external-links2.tsv	# Next 3 random links - 1,833,585 total 
wikipedia-external-links3.tsv	# Rest of links - 4,020,171 total 

# Crawl wikipedia external references 
# Start by crawling wikipedia-external-links1.tsv - split into files of 1mill each and put in separate dirs
# For each one, split into files of size 5000
mkdir epiphyte enterprise serenity mcbbigram dnode
# in each dir:
split -l 5000 ext-links.tsv
screen -S wiki-ext-data
for f in x*; do python ../scrape-wiki-ext-data.py $f & done ;

#### Hashtag inference
# First get the text from the hashtags in data/hashtags
python tweet_text.py *.json

# Now run inference:

## NB FULL
python MLmodels.py --data tweets-text.txt --model naive_bayes/april29/full/NBmodel.pkl --vectorizer naive_bayes/april29/full/vectorizer.pkl --mapping id-mapping.tsv --WRmapping reddit-wiki-mapping.tsv --dir naive_bayes/april29/full/hashtag-results
## NB NULL
python MLmodels.py --data tweets-text.txt --model naive_bayes/april29/null/NBmodel.pkl --vectorizer naive_bayes/april29/null/vectorizer.pkl --mapping id-mapping.tsv --WRmapping reddit-wiki-mapping.tsv --dir naive_bayes/april29/null/hashtag-results
## SVM FULL
python MLmodels.py --data tweets-text.txt --model svm/full/SVMmodel.pkl --vectorizer svm/full/vectorizer.pkl --mapping id-mapping.tsv --WRmapping reddit-wiki-mapping.tsv --dir svm/full/hashtag-results
## SVM NULL
python MLmodels.py --data tweets-text.txt --model svm/null/SVMmodel.pkl --vectorizer svm/null/vectorizer.pkl --mapping id-mapping.tsv --WRmapping reddit-wiki-mapping.tsv --dir svm/null/hashtag-results
## LLDA FULL
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx150G jgibblda.LDA -inf -dir data/full/ -model full-model-may8 -twords 25 -dfile tweets-text.txt.gz
## LLDA NULL
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx50G jgibblda.LDA -inf -dir data/null-april27/ -model null-model-apr27 -twords 25 -dfile tweets-text.txt.gz
gunzip tweets-text.txt.null-model-apr27.theta.gz
gunzip tweets-text.txt.full-model-may8.theta.gz
python llda-inf-results.py ../data/null-april27/tweets-text.txt.null-model-apr27.theta null 25 llda-null-hashtag-top-labels.txt
python llda-inf-results.py ../data/full/tweets-text.txt.full-model-may8.theta full 25 llda-full-hashtag-top-labels.txt

## DOUBLE CHECK THAT ???

### Formatting SE data

# Minimum of 300 words - 301 because include tag
cat cleaned-se-corpus-with-tags.tsv | awk '{if(NF >= 301) print $1}' > SE-data_truncated-300.tsv	# 30438 lines
# Minimum of 500 words 
cat cleaned-se-corpus-with-tags.tsv | awk '{if(NF >= 501) print $1}' > SE-data_truncated-500.tsv	# 11403 lines 

# Combine stack exchange categories and subreddits 
cut -f1 SE-data_truncated-500.tsv > SE-labels_500.txt; cut -f1 SE-data_truncated-300.tsv > SE-labels_300.txt
cp SE-labels_300.txt SE-reddit-labels_300.txt; cp SE-labels_500.txt SE-reddit-labels_500.txt
cat subreddits.txt >> SE-reddit-labels_300.txt; cat subreddits.txt >> SE-reddit-labels_500.txt
# Found those that are in mapping in python terminal
reddit-and-se-to-wiki.in-use_500.tsv ; reddit-and-se-to-wiki.in-use_300.tsv




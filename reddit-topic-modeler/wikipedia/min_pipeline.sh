### Build the most minimal topic model possible to see if this will finally run

## Collapse
# Collapsing params: max depth of 4, max subtree depth of 2
python wiki_graph2.py --roots collapsed-components/collapsible-topics4.txt --dir collapsed-components --thresh 4 --subtreedepth 2
	# 172311 potential collapsible topics
	# creates collapsed-components-4-d2.tsv - 170982 topics (some get ommitted because not in wibi taxonomy)
# Component params: min component size of 10 
python threshold_nodes.py collapsed-components-4-d2.tsv reddit-se-nodes_wikinames.txt 10 > collapsed-components-4-d2-thresholded@10.tsv
	# Left with 14894 topics...
cat collapsed-components/collapsed-components-4-d2-thresholded@10.tsv | awk '{split($0, a, "\t"); for(x in a) print a[x]}' > wikipages.txt
	# ...using 3184613 pages (before: 4248086)
	# indicating that most are at depth 2 anyway
sort -u wikipages.txt | wc -l; wc -l wikipages.txt	# Should be the same - sort of off ??? 

cat SE-topics.txt > reddit-SE-topics_post-thresh.txt; cat reddit-topics.txt >> reddit-SE-topics_post-thresh.txt
wc -l reddit-SE-topics_post-thresh.txt 
	# 11543 community topics 
# Get the associated wikipedia pages - python shell -- watch out for /r/
wc -l reddit-SE-topics_post-thresh_wiki.txt 	# should be same as above 

# Get the wikipedia data that we need to use
python get-wiki-content.py wikipages_unique.txt wikipedia-content.tsv > wikipedia-content-used.tsv

## Aggregate wikipedia topics and do a first pass at threshold
# Save aggregated content and reduced components (keep community topics)
#python aggregate.py wikipedia-content-used.tsv collapsed-components/collapsed-components-4-d2-thresholded@10.tsv reddit-SE-topics_post-thresh_wiki.txt 500 wikipedia-content_reduced500.tsv collapsed-components_reduced500.tsv
python aggregate.py wikipedia-content-used.tsv collapsed-components/collapsed-components-4-d2-thresholded@10.tsv reddit-SE-topics_post-thresh_wiki.txt 1000 wikipedia-content_reduced1000.tsv collapsed-components_reduced1000.tsv
	# thresholding at 1000: 14589 topics

## Clean wikipedia content -- distribute
split -l 2000 wikipedia-content_reduced1000.tsv wikicontent-split
mv wikicontent-split* split-wikicontent
python ../clean-content.py wikicontent-splitaa wikicontent-cleanaa 2000

## Threshold at 1000 again -- distribute
#cat wikicontent-cleanaa | awk '{if(NF>=1001) print $0}' > wikicontent-clean-reducedaa
# ^^ no! don't do this. want to keep community topics
python threshold-data.py wikicontent-cleanaa ../reddit-SE-topics_post-thresh_wiki.txt 1000 > wikicontent-clean-reducedaa

## Create the wikipedia vocabulary
cut -f2 wikicontent-clean-reducedaa | tr [:space:] '\n' | sort > wikiwords-aa

### (or use bash distrib-clean-thresh-words.sh a for these three distributed steps)
	## NOTE: first part is currently commented out 

# 14416 topics (removed ~100)

# Aggregate word counts
for f in wikiwords-*; do cat $f >> ../wikiwords-all.txt; done
python word-counts.py wikiwords-all.txt wikiwords-counts.txt
	# 7141584 unique tokens
	# 729890363 total words
wc -l wikiwords-counts.txt 		# initial vocab size of 7134886 words (728787865 words total)
# Remove words that don't appear at least 50 times 
cat wikiwords-counts.txt | awk '{if($2>=50) print $1}' > wiki-words-gt_50.txt	# vocab size now is 339978
# Reduce wiki content by this vocabulary  - distribute
touch wiki-content-clean-reduced.tsv 
for f in wikicontent-clean-reduceda*; do echo $f; cat $f >> wiki-content-clean-reduced.tsv; done
python reduce_vocab.py wiki-words-gt_50.txt wiki-content-clean-reduced.tsv > wiki-content_reduced_vocab.tsv
#python ../reduce_vocab.py ../wiki-words-gt_50.txt wikicontent-clean-reducedaa > wikicontent-clean-reduced2aa
#for f in wikicontent-clean-reduced2*; do cat $f >> ../wiki-content_reduced_vocab.tsv; done

## Compute TF-IDF stats 
# TF 
python calculate_tfidf.py --data wiki-content_reduced_vocab.tsv --tf wiki-TF.tsv
# IDF 
python calculate_tfidf.py --data wiki-content_reduced_vocab.tsv --idf wiki-IDF.tsv
# TF-IDF
python calculate_tfidf.py --tf wiki-TF.tsv --idf wiki-IDF.tsv --tfidf wiki-TFIDF.tsv
# Sort the IDF from most to least common words 
sort -g -k2 wiki-IDF.tsv > wiki-IDF_sorted.tsv
# Sort the TF-IDF from most to least important
sort -g -k1 -r wiki-TFIDF.tsv > wiki-TFIDF_sorted.tsv
# Take the top 250,000 words by TF-IDF and reduce
head -250000 wiki-TFIDF_sorted.tsv | cut -f2 > wiki-tfidf-vocab_250000.txt
python reduce_vocab.py wiki-tfidf-vocab_250000.txt wiki-content_reduced_vocab.tsv > wiki-content_reduced_vocab_reduced_tfidf.tsv

## REDO: top 100000 words 
head -100000 wiki-TFIDF_sorted.tsv | cut -f2 > wiki-tfidf-vocab_100000.txt 
python reduce_vocab.py wiki-tfidf-vocab_100000.txt wiki-content_reduced_vocab.tsv > wiki-content_reduced_vocab_reduced_tfidf_100000.tsv

## Create the 0-indexed mapping and relabel 
cut -f1 wiki-content_reduced_vocab_reduced_tfidf.tsv | awk '{print NR-1"\t"$0}' > null-index-mapping.tsv
cut -f2 wiki-content_reduced_vocab_reduced_tfidf.tsv | awk '{print NR-1"\t"$0}' > null-data.tsv

## Format for llda 
cut -f2 null-data.tsv > null-text.txt 
cut -f1 null-data.tsv | awk '{print "["$0"]"}' > null-llda-labels.txt
wc -l null-llda-labels.txt; wc -l null-text.txt 	# make sure have same number of lines 
paste -d" " null-llda-labels.txt null-text.txt > null-data-final.txt
cp null-data-final.txt ../../JGibbsLLDA/src/data
gzip null-data-final.txt

## REDO: format for llda with fewer words 
cut -f2 wiki-content_reduced_vocab_reduced_tfidf_100000.tsv | awk '{print NR-1"\t"$0}' > null-data_100000.tsv
cut -f2 null-data_100000.tsv > null-text_100000.txt 
cut -f1 null-data_100000.tsv | awk '{print "["$0"]"}' > null-llda-labels_100000.txt
wc -l null-llda-labels_100000.txt; wc -l null-text_100000.txt 	# make sure have same number of lines 
paste -d" " null-llda-labels_100000.txt null-text_100000.txt > null-data-final_100000.txt
cp null-data-final_100000.txt ../../JGibbsLLDA/src/data
gzip null-data-final_100000.txt

## Run LLDA null - enterprise
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx100G jgibblda.LDA -est -ntopics 14416 -dfile null-data-final.txt.gz -dir data/ -model null-model-final
	# top -p42244
## REDO 
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx100G jgibblda.LDA -est -ntopics 14416 -niters 500 -dfile null-data-final_100000.txt.gz -dir data/ -model null-model-final10

## Run Naive Bayes null - serenity 
python MLmodels.py --train NB --data ../data/final-round/null-data-final.txt --dir naive_bayes/null-final --max_features 75000

## Run SVM null - serenity 
python MLmodels.py --train SVM --data ../data/final-round/null-data-final.txt --dir svm/null-final --max_features 75000

### FULL data

## Get wikipedia external articles corresponding to the labels that we have - in wikidump/external-links
cut -f2 null-index-mapping.tsv > null-wiki-nodes.txt
wc -l wikipedia-external-links_needed.tsv		# 144,513 links - crawl these
python scrape-wiki-ext-data.py wikipedia-external-links_needed.tsv
python scrape-wiki-ext-data.py wikipedia-external-links_needed_tail.tsv
	# saved in dat.wikipedia-external-links_needed.tsv.txt

# test-links-needed-may27.txt >> contains test links to scrape
# train-links-needed-may27.txt >> contains train links to scrape

## Distribute external link collection - split according to nproc on each server, run in parallel
for f in xa*; do python ../../scrape-wiki-ext-data.py $f & done;
# Aggregate
touch link-data.tsv; for f in dat.*; do echo $f; cat $f >> link-data.tsv; done 
# cat all link-data.tsv files into one large file training-articles.tsv 
cat epiphyte/link-data.tsv >> training-articles.tsv		# etc
cat dat.wikipedia-external-links_needed_head.tsv.txt >> training-articles.tsv
cat dat.wikipedia-external-links_needed_tail.tsv.txt >> training-articles.tsv
cat dat.wikipedia-external-links_needed.tsv.txt >> training-articles.tsv
wc -l training-articles.tsv

## Aggregate and clean a max of 5 articles per topic
mv training-articles.tsv training-articles_all.tsv
python aggregate-wiki-articles.py training-articles_all.tsv training-articles.tsv 5 null-index-mapping.tsv
	# saves urls used and corresponding page-> index mapping in training-articles.tsv.urls
	# training-articles.tsv now contains the indexed labels and is llda-formatted and cleaned

## Replace SE labels with index label and aggregate
python relabel-and-aggregate-SE.py SE-content_cleaned_reduced.tsv null-index-mapping.tsv reddit-se-wiki-mapping.tsv SE-content-labeled_aggregated.txt
	# 331755 original docs, 19826 unique combinations of labels
	# After replacing (because some labels weren't in wikipedia data): 
		# 14931 unique combinations of labels, 23062 docs omitted

## Add in reddit content - 2561 docs
python relabel-reddit.py reddit-content_reduced_reduced.tsv null-index-mapping.tsv reddit-se-wiki-mapping.tsv reddit-content_labeled.txt

## Aggregate community content 
cat training-articles.tsv > community-data.txt
cat SE-content-labeled_aggregated.txt >> community-data.txt
cat reddit-content_labeled.txt >> community-data.txt 

## Get community vocabulary 
cut -f2 -d']' community-data.txt | tr [:space:] '\n' | sort > comm-words.txt
python word-counts.py comm-words.txt comm-words-counts.txt
	# 921826 unique tokens
	# 147666462 total words
# Remove words that don't appear at least 25 times 
cat comm-words-counts.txt | awk '{if($2>=25) print $1}' > comm-words-gt_25.txt	# vocab size now is 121296

# Reduce content by this vocabulary - distribute
python reduce_comm_vocab.py comm-words-gt_25.txt community-data.txt > community-data_reduced.txt

# Check overlap with wikipedia words
python comm-wiki-vocab-analysis.py
	# creates: 
	# comm-wiki-shared-words.txt 	69606
	# comm-words-not-in-wiki.txt 	51690

## Remove words appearing across 70% of docs
python calculate_tfidf.py --data community-data_reduced.txt --idf comm-IDF.tsv
sort -g -k2 comm-IDF.tsv > comm-IDF_sorted.tsv
cat comm-IDF_sorted.tsv | awk '{if($2>2.0) print $1}' > comm-vocab.txt 	# 140488

## Create the full vocabulary
head -170000 wiki-TFIDF_sorted.tsv | cut -f2 > wiki-tfidf-vocab_170000.txt
cp comm-vocab.txt full-vocab.txt; cat wiki-tfidf-vocab_170000.txt >> full-vocab.txt 
sort -u full-vocab.txt > temp; mv -f temp full-vocab.txt  	# 251742

## Get all the full data 
cat community-data_reduced.txt > full-data.txt
cat null-data-final.txt >> full-data.txt

## Reduce it by full-vocab
python reduce_comm_vocab.py full-vocab.txt full-data.txt > full-data_reduced.txt

## Run version1: disaggregated
cp full-data_reduced.txt ../../JGibbsLLDA/src/data/full-data-final.txt
gzip full-data-final.txt
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx200G jgibblda.LDA -est -ntopics 14416 -dfile full-data-final.txt.gz -dir data/ -model full-model-final

## Run version2: aggregated
python aggregate-topics.py full-data-final.txt full-data-final_agg.txt
cp full-data-final_agg.txt ../../JGibbsLLDA/src/data/
gzip full-data-final_agg.txt
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx200G jgibblda.LDA -est -ntopics 14416 -dfile full-data-final_agg.txt.gz -dir data/ -model full-model-final-agg

## Naive Bayes 
python MLmodels.py --train NB --data ../data/final-round/full-data-final_agg.txt --dir naive_bayes/full-final --max_features 200000

## SVM 
python MLmodels.py --train SVM --data ../data/final-round/full-data-final_agg.txt --dir svm/full-final --max_features 200000

### Community-only models 
# Relabel and create new mapping 
cut -f1 -d']' community-data_reduced.txt | cut -f2 -d'[' | tr [:space:] '\n' | sort -u -g | awk '{print NR-1"\t"$0}' > community-wiki-index-mapping.tsv
	# format: new \t old 
	# 11479 topics
python new_comm_labels.py community-data_reduced.txt community-wiki-index-mapping.tsv community-data_relabeled.txt 
	# double check - wc -l should be the same as above 11479
# Make sure corresponds to same vocab
python reduce_comm_vocab.py full-vocab.txt community-data_relabeled.txt > community-data_relabeled_reduced.txt
cp community-data_relabeled_reduced.txt ../../JGibbsLLDA/src/data/community-data.txt

# LLDA 
gzip community-data.txt 
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx50G jgibblda.LDA -est -ntopics 11479 -dfile community-data.txt.gz -dir data/ -model community-model
# NB 
python MLmodels.py --train NB --data ../data/final-round/community-data_relabeled_reduced.txt --dir naive_bayes/community
# SVM 
python MLmodels.py --train SVM --data ../data/final-round/community-data_relabeled_reduced.txt --dir svm/community

### Wikipedia LDA model 
# Remove labels 
#cut -f2 -d']' null-data-final.txt > null-data-final_unlabeled.txt
# Train 
#java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx80G jgibblda.LDA -est -ntopics 14416 -dfile null-data-final_unlabeled.txt.gz -dir data/ -model null-model-final-unlabeled
# >> wrong because are already aggregated 

## TRY C IMPLEMENTATION
#./lda est [alpha] [k] [settings] [data] [random/seeded/*] [directory]
# Convert to LDA format: [M] [term_1]:[count] [term_2]:[count] ...  [term_N]:[count]
#python LDA-format.py null-data-final_unlabeled.txt null-data-final_LDA.txt
# in lda-c/lda-c-dist/
#./lda est .0001 14416 setttings.txt ../../data/final-round/null-data-final_LDA.txt random ../ 
# >> wrong because are already aggregated 

## TRY PARALLELIZED LDA C++ IMPLEMENTATION
# format is the same as C implementation's (sparse representation), but without colons and M 
# cut -f2 wikipedia-content-used.tsv > wikipedia-content-used.txt
# # use same vocab as before 
# python LDA-format.py wikipedia-content-used.txt wiki-tfidf-vocab_170000.txt wikipedia-data_PLDA.txt
# # remove documents that barely have any words - must have at least 5 unique words (10 with count)
# cat wikipedia-data_PLDA.txt | awk '{if(NF>=10) print $0}' > wikipedia-data_filtered_PLDA.txt
# mv wikipedia-data_filtered_PLDA.txt ../../plda/data/wiki-data-plda.txt
# # in wikipedia/plda 
# # alpha = topic-document distribution - assume relative sparsity - 1/14416
# ./lda --num_topics 14416 --alpha .0001 --beta 0.01 --training_data_file data/wiki-data-plda.txt --model_file data/lda_wiki_model.txt --total_iterations 200 --burn_in_iterations 150 

## TRY JAVA IMPLEMENTATION AGAIN 
# used null-llda-labels_100000.txt and collapsed-components_reduced1000.tsv to obtain:
	# collapsed-components_reduced1000-final.tsv
		# These are the final collapsed components used #
# get individual wikipages
cat collapsed-components_reduced1000-final.tsv | awk '{split($0, a, "\t"); for(x in a) print a[x]}' > wiki-pages_all.txt
python LDA-format.py wikipedia-content-used.tsv wiki-tfidf-vocab_170000.txt wiki-pages_all.txt wikipedia-data_LDA_V2.txt
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx80G jgibblda.LDA -est -ntopics 14416 -dfile wikipedia-data_PLDA_V2.txt.gz -dir data/ -model null-model-final-unlabeled

####### TESTING #######

### Reddit articles 
# First get the subreddits that we're using 
wc -l reddit-topics.txt
# Now filter the articles by these topics
python filter-reddit-articles-needed.py test-url-data-511.tsv reddit-topics.txt > test-url-data-528.tsv
	# 8958 articles over 2057 topics 
# Label with wikipedia labels
python label-test-data.py test-url-data-528.tsv null-index-mapping.tsv reddit-se-wiki-mapping.tsv test-url-data-528_labeled.tsv
	# 179 not found - so now down to 8215 articles over 1878 topics
# Divide into 4 chunks (about 1 article per topic in each chunk)
python chunk-articles.py test-url-data-528_labeled.tsv
# For each chunk: 
cut -f4 test-url-data-528_labeled.1.tsv > test-url-data-528_labeled.1.txt
gzip test-url-data-528_labeled.1.txt
cp test-url-data-528_labeled.1.txt.gz ../../../JGibbsLLDA/src/data/

# Get the reddit to wiki mapping
grep '/r/' reddit-se-wiki-mapping.tsv > reddit-wiki-mapping.tsv

## LLDA - distribute 
# further segment first chunk into 5 sub-chunks, gzip, cp them over to jgibbs dir 
# full
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx100G jgibblda.LDA -inf -myinfseparately sep-full-reddit/batch1/ -dir ../../wikipedia/JGibbsLLDA/src/data/ -model full-model-final -twords 25 -dfile test-url-data-528.1.aa.txt.gz -numtestdocs 400
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx100G jgibblda.LDA -inf -myinfseparately sep-full-reddit/batch2/ -dir ../../wikipedia/JGibbsLLDA/src/data/ -model full-model-final -twords 25 -dfile test-url-data-528.1.ab.txt.gz -numtestdocs 400
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx100G jgibblda.LDA -inf -myinfseparately sep-full-reddit/batch3/ -dir ../../wikipedia/JGibbsLLDA/src/data/ -model full-model-final -twords 25 -dfile test-url-data-528.1.ac.txt.gz -numtestdocs 400
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx100G jgibblda.LDA -inf -myinfseparately sep-full-reddit/batch4/ -dir ../../wikipedia/JGibbsLLDA/src/data/ -model full-model-final -twords 25 -dfile test-url-data-528.1.ad.txt.gz -numtestdocs 400
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx100G jgibblda.LDA -inf -myinfseparately sep-full-reddit/batch5/ -dir ../../wikipedia/JGibbsLLDA/src/data/ -model full-model-final -twords 25 -dfile test-url-data-528.1.ae.txt.gz -numtestdocs 278
# null 
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx70G jgibblda.LDA -inf -myinfseparately sep-null-reddit/batch1/ -niters 500 -dir ../../wikipedia/JGibbsLLDA/src/data/ -model null-model-final10 -twords 25 -dfile test-url-data-528.1.aa.txt.gz -numtestdocs 400
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx70G jgibblda.LDA -inf -myinfseparately sep-null-reddit/batch2/ -niters 500 -dir ../../wikipedia/JGibbsLLDA/src/data/ -model null-model-final10 -twords 25 -dfile test-url-data-528.1.ab.txt.gz -numtestdocs 400
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx70G jgibblda.LDA -inf -myinfseparately sep-null-reddit/batch3/ -niters 500 -dir ../../wikipedia/JGibbsLLDA/src/data/ -model null-model-final10 -twords 25 -dfile test-url-data-528.1.ac.txt.gz -numtestdocs 400
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx70G jgibblda.LDA -inf -myinfseparately sep-null-reddit/batch4/ -niters 500 -dir ../../wikipedia/JGibbsLLDA/src/data/ -model null-model-final10 -twords 25 -dfile test-url-data-528.1.ad.txt.gz -numtestdocs 400
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx70G jgibblda.LDA -inf -myinfseparately sep-null-reddit/batch5/ -niters 500 -dir ../../wikipedia/JGibbsLLDA/src/data/ -model null-model-final10 -twords 25 -dfile test-url-data-528.1.ae.txt.gz -numtestdocs 278
# comm  - run w/ fewer iterations

# For full and null:
for f in batch1/*.theta.gz; do gunzip $f; done
# Aggregate theta files 
python aggregate-thetas2.py 400 batch1.theta batch1
python aggregate-thetas2.py 400 batch2.theta batch2
python aggregate-thetas2.py 400 batch3.theta batch3
python aggregate-thetas2.py 400 batch4.theta batch4
python aggregate-thetas2.py 278 batch5.theta batch5
# Get results for each 
python llda-results-final.py sep-full-reddit/batch1.theta ../../../data/final-round/test-sets/reddit-links-batch1/test-url-data-528.1.aa null-index-mapping.tsv reddit-wiki-mapping.tsv 14416 labeled > sep-full-reddit/batch1.top-labels.txt
python llda-results-final.py sep-full-reddit/batch2.theta ../../../data/final-round/test-sets/reddit-links-batch1/test-url-data-528.1.ab null-index-mapping.tsv reddit-wiki-mapping.tsv 14416 labeled > sep-full-reddit/batch2.top-labels.txt
python llda-results-final.py sep-full-reddit/batch3.theta ../../../data/final-round/test-sets/reddit-links-batch1/test-url-data-528.1.ac null-index-mapping.tsv reddit-wiki-mapping.tsv 14416 labeled > sep-full-reddit/batch3.top-labels.txt
python llda-results-final.py sep-full-reddit/batch4.theta ../../../data/final-round/test-sets/reddit-links-batch1/test-url-data-528.1.ad null-index-mapping.tsv reddit-wiki-mapping.tsv 14416 labeled > sep-full-reddit/batch4.top-labels.txt
python llda-results-final.py sep-full-reddit/batch5.theta ../../../data/final-round/test-sets/reddit-links-batch1/test-url-data-528.1.ae null-index-mapping.tsv reddit-wiki-mapping.tsv 14416 labeled > sep-full-reddit/batch5.top-labels.txt
# Combine distributions (weighted)
python combine-distribs.py LLDA-full.reddit-links.accuracy-distrib.tsv

# Parsing LLDA results 
for f in *.theta.gz; do gunzip $f ; done
python aggregate-thetas.py se-articles.aa full-model-final sep-full-se/batch1/ 125
	# outputs se-articles.aa.full-model-final.theta
# seems to be off by one so add a dummy line to the file 
mv se-articles.aa.full-model-final.theta temp
echo 'DUMMY' > se-articles.aa.full-model-final.theta 
cat temp >> se-articles.aa.full-model-final.theta 
rm -f temp
python llda-results-final.py se-articles.aa.full-model-final.theta ../../../data/final-round/test-sets/se-articles.aa null-index-mapping.tsv reddit-se-wiki-mapping.tsv 14416 labeled
	# outputs llda-full-yahoo-top.txt

## Naive Bayes
# null
python MLmodels.py --data ../data/final-round/test-sets/test-url-data-528_labeled.tsv --model naive_bayes/null-final/NBmodel.pkl --vectorizer naive_bayes/null-final/vectorizer.pkl --mapping ../data/final-round/test-sets/null-index-mapping.tsv --WRmapping ../data/final-round/test-sets/reddit-wiki-mapping.tsv --dir naive_bayes/null-final/reddit-link-results --num_topics 14416
# full 
python MLmodels.py --data ../data/final-round/test-sets/test-url-data-528_labeled.tsv --model naive_bayes/full-final/NBmodel.pkl --vectorizer naive_bayes/full-final/vectorizer.pkl --mapping ../data/final-round/test-sets/null-index-mapping.tsv --WRmapping ../data/final-round/test-sets/reddit-wiki-mapping.tsv --dir naive_bayes/full-final/reddit-link-results --num_topics 14416
# comm 
# TODO - need second mapping

## SVM 
# null
python MLmodels.py --data ../data/final-round/test-sets/test-url-data-528_labeled.tsv --model svm/null-final/SVMmodel.pkl --vectorizer svm/null-final/vectorizer.pkl --mapping ../data/final-round/test-sets/null-index-mapping.tsv --WRmapping ../data/final-round/test-sets/reddit-wiki-mapping.tsv --dir svm/null-final/reddit-link-results --num_topics 14416
# full
python MLmodels.py --data ../data/final-round/test-sets/test-url-data-528_labeled.tsv --model svm/full-final/SVMmodel.pkl --vectorizer svm/full-final/vectorizer.pkl --mapping ../data/final-round/test-sets/null-index-mapping.tsv --WRmapping ../data/final-round/test-sets/reddit-wiki-mapping.tsv --dir svm/full-final/reddit-link-results --num_topics 14416
# comm 
# TODO - need second mapping

# Get a sample of the reddit links to test on SVM 
	# filter bad urls and smaller word length
python get-sample-reddit-links.py 
	# Gets random/good urls from test-url-data-528_labeled.tsv 1000 
	# and saves them to test-url-data-528_sample1.tsv and _sample2.tsv
python MLmodels.py --data ../data/final-round/test-sets/test-url-data-528_sample1.tsv --model svm/full-final/SVMmodel.pkl --vectorizer svm/full-final/vectorizer.pkl --mapping ../data/final-round/test-sets/null-index-mapping.tsv --WRmapping ../data/final-round/test-sets/reddit-wiki-mapping.tsv --dir svm/full-final/reddit-link-results/sample1 --num_topics 14416
python MLmodels.py --data ../data/final-round/test-sets/test-url-data-528_sample2.tsv --model svm/full-final/SVMmodel.pkl --vectorizer svm/full-final/vectorizer.pkl --mapping ../data/final-round/test-sets/null-index-mapping.tsv --WRmapping ../data/final-round/test-sets/reddit-wiki-mapping.tsv --dir svm/full-final/reddit-link-results/sample2 --num_topics 14416

python MLmodels.py --data ../data/final-round/test-sets/test-url-data-528_sample1.tsv --model svm/null-final/SVMmodel.pkl --vectorizer svm/null-final/vectorizer.pkl --mapping ../data/final-round/test-sets/null-index-mapping.tsv --WRmapping ../data/final-round/test-sets/reddit-wiki-mapping.tsv --dir svm/null-final/reddit-link-results/sample1 --num_topics 14416
python MLmodels.py --data ../data/final-round/test-sets/test-url-data-528_sample2.tsv --model svm/null-final/SVMmodel.pkl --vectorizer svm/null-final/vectorizer.pkl --mapping ../data/final-round/test-sets/null-index-mapping.tsv --WRmapping ../data/final-round/test-sets/reddit-wiki-mapping.tsv --dir svm/null-final/reddit-link-results/sample2 --num_topics 14416


### SE articles 
# Aggregate and clean the urls - in data/stack-exchange
for f in dat.*; do cat $f >> se-link-data.tsv; done		# in each urls dir
# Get the SE tag to wiki mapping 
grep ':' reddit-se-wiki-mapping.tsv > se-wiki-mapping.tsv
# Get the labels that we are actually using - python shell 
wc -l se-labels-used.txt 	# 9131 of them 
# Get one article per label used - in data/stack-exchange
python filter-se-articles-needed.py se-labels-used.txt se-wiki-mapping.tsv null-index-mapping.tsv se-articles.tsv
wc -l se-articles.tsv
	# 10872 articles
	# 4644 topics 
	# NEED MORE!!! 
cut -f4 se-articles.tsv > se-articles.txt 
gzip se-articles.txt 
cp se-articles.txt.gz ../../../JGibbsLLDA/src/data/

# NB - full
python MLmodels.py --data ../data/final-round/test-sets/se-articles.tsv --model naive_bayes/full-final/NBmodel.pkl --vectorizer naive_bayes/full-final/vectorizer.pkl --mapping ../data/final-round/test-sets/null-index-mapping.tsv --WRmapping ../data/final-round/test-sets/se-wiki-mapping.tsv --dir naive_bayes/full-final/se-link-results --num_topics 14416
# NB - null 
python MLmodels.py --data ../data/final-round/test-sets/se-articles.tsv --model naive_bayes/null-final/NBmodel.pkl --vectorizer naive_bayes/null-final/vectorizer.pkl --mapping ../data/final-round/test-sets/null-index-mapping.tsv --WRmapping ../data/final-round/test-sets/se-wiki-mapping.tsv --dir naive_bayes/null-final/se-link-results --num_topics 14416

# Test NB on sample (with bad urls removed)
python MLmodels.py --data ../data/final-round/test-sets/se-articles_sample.tsv --model naive_bayes/full-final/NBmodel.pkl --vectorizer naive_bayes/full-final/vectorizer.pkl --mapping ../data/final-round/test-sets/null-index-mapping.tsv --WRmapping ../data/final-round/test-sets/reddit-wiki-mapping.tsv --dir naive_bayes/full-final/se-link-results/sample --num_topics 14416

# SVM - full
python MLmodels.py --data ../data/final-round/test-sets/se-articles.tsv --model svm/full-final/SVMmodel.pkl --vectorizer svm/full-final/vectorizer.pkl --mapping ../data/final-round/test-sets/null-index-mapping.tsv --WRmapping ../data/final-round/test-sets/se-wiki-mapping.tsv --dir svm/full-final/se-link-results --num_topics 14416
# SVM - null 
python MLmodels.py --data ../data/final-round/test-sets/se-articles.tsv --model svm/null-final/SVMmodel.pkl --vectorizer svm/null-final/vectorizer.pkl --mapping ../data/final-round/test-sets/null-index-mapping.tsv --WRmapping ../data/final-round/test-sets/se-wiki-mapping.tsv --dir svm/null-final/se-link-results --num_topics 14416

## Test a sample! 
python MLmodels.py --data ../data/final-round/test-sets/se-articles_sample.tsv --model svm/full-final/SVMmodel.pkl --vectorizer svm/full-final/vectorizer.pkl --mapping ../data/final-round/test-sets/null-index-mapping.tsv --WRmapping ../data/final-round/test-sets/reddit-wiki-mapping.tsv --dir svm/full-final/se-link-results/sample --num_topics 14416
python MLmodels.py --data ../data/final-round/test-sets/se-articles_sample.tsv --model svm/null-final/SVMmodel.pkl --vectorizer svm/null-final/vectorizer.pkl --mapping ../data/final-round/test-sets/null-index-mapping.tsv --WRmapping ../data/final-round/test-sets/reddit-wiki-mapping.tsv --dir svm/null-final/se-link-results/sample --num_topics 14416

# LLDA 
# Divide SE articles into 2 chunks , gzip, and cp 
# Full
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx100G jgibblda.LDA -inf -myinfseparately sep-full-se/batch1/ -dir ../../wikipedia/JGibbsLLDA/src/data/ -model full-model-final -twords 25 -dfile se-articles.aa.txt.gz -numtestdocs 5436
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx100G jgibblda.LDA -inf -myinfseparately sep-full-se/batch2/ -dir ../../wikipedia/JGibbsLLDA/src/data/ -model full-model-final -twords 25 -dfile se-articles.ab.txt.gz -numtestdocs 5436
# Null - run w/ fewer iterations
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx80G jgibblda.LDA -inf -myinfseparately sep-null-se/batch1/ -niters 500 -dir ../../wikipedia/JGibbsLLDA/src/data/ -model null-model-final10 -twords 25 -dfile se-articles.aa.txt.gz -numtestdocs 5436
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx80G jgibblda.LDA -inf -myinfseparately sep-null-se/batch2/ -niters 500 -dir ../../wikipedia/JGibbsLLDA/src/data/ -model null-model-final10 -twords 25 -dfile se-articles.ab.txt.gz -numtestdocs 5436

# Getting LLDA results - for full and null
for f in batch1/*.theta.gz; do gunzip $f; done
for f in batch2/*.theta.gz; do gunzip $f; done
# Aggregate theta files 
python aggregate-thetas2.py 2500 batch1.theta batch1
python aggregate-thetas2.py 2500 batch2.theta batch2
# Get results for each 
python llda-results-final.py sep-full-se/batch1.theta ../../../data/final-round/test-sets/se-articles.aa null-index-mapping.tsv reddit-se-wiki-mapping.tsv 14416 labeled > sep-full-se/batch1.top-labels.txt
python llda-results-final.py sep-full-se/batch2.theta ../../../data/final-round/test-sets/se-articles.ab null-index-mapping.tsv reddit-se-wiki-mapping.tsv 14416 labeled > sep-full-se/batch2.top-labels.txt
# Combine distributions (weighted)
python combine-distribs.py LLDA-full.reddit-links.accuracy-distrib.tsv


### IMPORTANT: tail -5150 se-articles.aa.txt > se-articles.aa.v2.txt
	# need to truncate the corresponding .tsv file similarly
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx100G jgibblda.LDA -inf -myinfseparately sep-full-se/batch1/ -dir ../../wikipedia/JGibbsLLDA/src/data/ -model full-model-final -twords 25 -dfile se-articles.aa.v2.txt.gz -numtestdocs 5150

### Yahoo answers 
# NB - full
python MLmodels.py --data ../data/final-round/test-sets/yahoo-test-docs.tsv --model naive_bayes/full-final/NBmodel.pkl --vectorizer naive_bayes/full-final/vectorizer.pkl --mapping ../data/final-round/test-sets/null-index-mapping.tsv --WRmapping ../data/final-round/test-sets/se-wiki-mapping.tsv --dir naive_bayes/full-final/yahoo-results --num_topics 14416
# NB - null 
python MLmodels.py --data ../data/final-round/test-sets/yahoo-test-docs.tsv --model naive_bayes/null-final/NBmodel.pkl --vectorizer naive_bayes/null-final/vectorizer.pkl --mapping ../data/final-round/test-sets/null-index-mapping.tsv --WRmapping ../data/final-round/test-sets/se-wiki-mapping.tsv --dir naive_bayes/null-final/yahoo-results --num_topics 14416
# SVM - full
python MLmodels.py --data ../data/final-round/test-sets/yahoo-test-docs.tsv --model svm/full-final/SVMmodel.pkl --vectorizer svm/full-final/vectorizer.pkl --mapping ../data/final-round/test-sets/null-index-mapping.tsv --WRmapping ../data/final-round/test-sets/se-wiki-mapping.tsv --dir svm/full-final/yahoo-results --num_topics 14416
# SVM - null 
python MLmodels.py --data ../data/final-round/test-sets/yahoo-test-docs.tsv --model svm/null-final/SVMmodel.pkl --vectorizer svm/null-final/vectorizer.pkl --mapping ../data/final-round/test-sets/null-index-mapping.tsv --WRmapping ../data/final-round/test-sets/se-wiki-mapping.tsv --dir svm/null-final/yahoo-results --num_topics 14416

# LLDA 
# Full
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx90G jgibblda.LDA -inf -myinfseparately sep-full-yahoo/ -niters 750 -dir ../../wikipedia/JGibbsLLDA/src/data/ -model full-model-final -twords 25 -dfile yahoo-test-docs.txt.gz -numtestdocs 5893
# Null - run w/ fewer iterations
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx80G jgibblda.LDA -inf -myinfseparately sep-null-yahoo/ -niters 450 -dir ../../wikipedia/JGibbsLLDA/src/data/ -model null-model-final10 -twords 25 -dfile yahoo-test-docs.txt.gz -numtestdocs 5893

# Get results
# For full and null:
for f in results/*.theta.gz; do gunzip $f; done
# Aggregate theta files 
python aggregate-thetas2.py 4781 results.theta results
# Get results for each 
python llda-results-final.py sep-full-yahoo/results.theta ../../../data/final-round/test-sets/yahoo-test-docs.tsv null-index-mapping.tsv reddit-wiki-mapping.tsv 14416 unlabeled

### Hashtags 

   #    9359 1DNews.json
   #     713 baristaproblems.json
   #   72846 deflategate.json
   #   20775 fml.json
   #    4100 fossilfriday.json
   #    1571 gohard.json
   #   76042 got.json
   #   15592 mlp.json
   #    1321 mothersdayclassic.json
   #   20829 nola.json
   # 1009662 nowplaying.json
   #    2000 p2.json
   #      39 passportready.json
   #     936 purplearmy.json
   #   10774 royalbaby.json
   #     379 sickburnahunk.json
   #    2642 veday70.json
   #    6311 virus.json
   #     832 wexmondays.json
   #   35885 yyc.json
   # 1292608 total

# Extract the text 
python tweet_text.py *.json
# Remove duplicates
for f in *.txt; do sort -u $f > $f.sorted & done;
# Clean and remove spanish tweets
for f in *.sorted; do python clean-rm-spanish.py $f & done
# Aggregate - each line gets all the hashtags
python aggregate-hashtags.py 	# Saved in tweets-text.tsv
cut -f2 tweets-text.tsv > tweets-text.txt
gzip tweets-text.txt
cp tweets-text.txt.gz ../../../JGibbsLLDA/src/data/

# Naive Bayes 
python MLmodels.py --data ../data/final-round/test-sets/tweets-text.tsv --model naive_bayes/full-final/NBmodel.pkl --vectorizer naive_bayes/full-final/vectorizer.pkl --mapping ../data/final-round/test-sets/null-index-mapping.tsv --WRmapping ../data/final-round/test-sets/se-wiki-mapping.tsv --dir naive_bayes/full-final/hashtag-results --num_topics 14416
python MLmodels.py --data ../data/final-round/test-sets/tweets-text.tsv --model naive_bayes/null-final/NBmodel.pkl --vectorizer naive_bayes/null-final/vectorizer.pkl --mapping ../data/final-round/test-sets/null-index-mapping.tsv --WRmapping ../data/final-round/test-sets/se-wiki-mapping.tsv --dir naive_bayes/null-final/hashtag-results --num_topics 14416

# SVM  
python MLmodels.py --data ../data/final-round/test-sets/tweets-text.tsv --model svm/full-final/SVMmodel.pkl --vectorizer svm/full-final/vectorizer.pkl --mapping ../data/final-round/test-sets/null-index-mapping.tsv --WRmapping ../data/final-round/test-sets/se-wiki-mapping.tsv --dir svm/full-final/hashtag-results --num_topics 14416
python MLmodels.py --data ../data/final-round/test-sets/tweets-text.tsv --model svm/null-final/SVMmodel.pkl --vectorizer svm/null-final/vectorizer.pkl --mapping ../data/final-round/test-sets/null-index-mapping.tsv --WRmapping ../data/final-round/test-sets/se-wiki-mapping.tsv --dir svm/null-final/hashtag-results --num_topics 14416

# LLDA 
# Full
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx90G jgibblda.LDA -inf -myinfseparately sep-hashtags-full -dir ../../wikipedia/JGibbsLLDA/src/data/ -model full-model-final -twords 25 -dfile tweets-text.txt.gz -numtestdocs 20
# Null
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx90G jgibblda.LDA -inf -myinfseparately sep-hashtags-null -dir ../../wikipedia/JGibbsLLDA/src/data/ -model null-model-final10 -twords 25 -dfile tweets-text.txt.gz -numtestdocs 20

### Wikipedia articles
# Pick the ones that aren't in the training set - 1000 of them (got max of 5, so pick the ones after 5)
python filter-wiki-articles-needed.py training-articles_all.tsv null-index-mapping.tsv
# Get random sample of 2000
sort -R testing-wiki-articles.tsv > testing-wiki-articles_randomized.tsv 
head -2000 testing-wiki-articles_randomized.tsv > testing-wiki-articles_sample.tsv

# NB full
python MLmodels.py --data ../data/final-round/test-sets/testing-wiki-articles_sample.tsv --model naive_bayes/full-final/NBmodel.pkl --vectorizer naive_bayes/full-final/vectorizer.pkl --mapping ../data/final-round/test-sets/null-index-mapping.tsv --WRmapping ../data/final-round/test-sets/reddit-wiki-mapping.tsv --dir naive_bayes/full-final/wiki-link-results --num_topics 14416
python MLmodels.py --data ../data/final-round/test-sets/testing-wiki-articles_randomized.tsv --model naive_bayes/full-final/NBmodel.pkl --vectorizer naive_bayes/full-final/vectorizer.pkl --mapping ../data/final-round/test-sets/null-index-mapping.tsv --WRmapping ../data/final-round/test-sets/reddit-wiki-mapping.tsv --dir naive_bayes/full-final/wiki-link-results --num_topics 14416
# NB null 
python MLmodels.py --data ../data/final-round/test-sets/testing-wiki-articles_sample.tsv --model naive_bayes/null-final/NBmodel.pkl --vectorizer naive_bayes/null-final/vectorizer.pkl --mapping ../data/final-round/test-sets/null-index-mapping.tsv --WRmapping ../data/final-round/test-sets/reddit-wiki-mapping.tsv --dir naive_bayes/null-final/wiki-link-results --num_topics 14416
python MLmodels.py --data ../data/final-round/test-sets/testing-wiki-articles_randomized.tsv --model naive_bayes/null-final/NBmodel.pkl --vectorizer naive_bayes/null-final/vectorizer.pkl --mapping ../data/final-round/test-sets/null-index-mapping.tsv --WRmapping ../data/final-round/test-sets/reddit-wiki-mapping.tsv --dir naive_bayes/null-final/wiki-link-results --num_topics 14416

# SVM full 
python MLmodels.py --data ../data/final-round/test-sets/testing-wiki-articles_sample.tsv --model svm/full-final/SVMmodel.pkl --vectorizer svm/full-final/vectorizer.pkl --mapping ../data/final-round/test-sets/null-index-mapping.tsv --WRmapping ../data/final-round/test-sets/reddit-wiki-mapping.tsv --dir svm/full-final/wiki-link-results --num_topics 14416
# SVM null 
python MLmodels.py --data ../data/final-round/test-sets/testing-wiki-articles_sample.tsv --model svm/null-final/SVMmodel.pkl --vectorizer svm/null-final/vectorizer.pkl --mapping ../data/final-round/test-sets/null-index-mapping.tsv --WRmapping ../data/final-round/test-sets/reddit-wiki-mapping.tsv --dir svm/null-final/wiki-link-results --num_topics 14416

# Divide random sample into 2 chunks

# LLDA full 
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx100G jgibblda.LDA -inf -myinfseparately sep-full-wiki/batch1/ -dir ../../wikipedia/JGibbsLLDA/src/data/ -model full-model-final -twords 25 -dfile testing-wiki-articles_sample.aa.txt.gz -numtestdocs 1000
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx100G jgibblda.LDA -inf -myinfseparately sep-full-wiki/batch2/ -dir ../../wikipedia/JGibbsLLDA/src/data/ -model full-model-final -twords 25 -dfile testing-wiki-articles_sample.ab.txt.gz -numtestdocs 1000
# LLDA null - run with fewer iterations!! 
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx80G jgibblda.LDA -inf -myinfseparately sep-null-wiki/batch1/ -niters 500 -dir ../../wikipedia/JGibbsLLDA/src/data/ -model null-model-final10 -twords 25 -dfile testing-wiki-articles_sample.aa.txt.gz -numtestdocs 1000
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx80G jgibblda.LDA -inf -myinfseparately sep-null-wiki/batch2/ -niters 500 -dir ../../wikipedia/JGibbsLLDA/src/data/ -model null-model-final10 -twords 25 -dfile testing-wiki-articles_sample.ab.txt.gz -numtestdocs 1000

# Getting LLDA results - for full and null
for f in batch1/*.theta.gz; do gunzip $f; done
# Aggregate theta files 
python aggregate-thetas2.py 1000 batch1.theta batch1
python aggregate-thetas2.py 1000 batch2.theta batch2
# Get results for each 
python llda-results-final.py sep-full-wiki/batch1.theta ../../../data/final-round/test-sets/testing-wiki-articles_sample.aa null-index-mapping.tsv reddit-wiki-mapping.tsv 14416 labeled > sep-full-wiki/batch1.top-labels.txt
python llda-results-final.py sep-full-wiki/batch2.theta ../../../data/final-round/test-sets/testing-wiki-articles_sample.ab null-index-mapping.tsv reddit-wiki-mapping.tsv 14416 labeled > sep-ull-wiki/batch2.top-labels.txt
# Combine distributions (weighted)
python combine-distribs.py LLDA-full.reddit-links.accuracy-distrib.tsv




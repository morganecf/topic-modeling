### FINAL PIPELINE

## Rename David's stuff
mv reddit-and-se-to-wiki.CORRECTED-AND-FINAL.FILTERED-BY-MIN-SIMILARITY.tsv reddit-se-wiki-mapping.tsv
mv node-collapse-classifications.collapsed-root-nodes.tsv collapsed-wiki-root-nodes.tsv

## Get the nodes we need to collapse (root nodes) - these include the ones we predict 
## should be collapsed, plus the reddit/SE nodes 
cut -f1 collapsed-wiki-root-nodes.tsv > root-nodes.txt
cut -f2 reddit-se-wiki-mapping.tsv >> root-nodes.txt
sort -u root-nodes.txt > root-nodes_u.txt 		# There are 329,033 root nodes, or topics

# Create the taxonomy graph and save it 
mkdir collapsed-components
python wiki_graph2.py --taxonomy WiBi.pagetaxonomy.txt --dir collapsed-components

# NOTE: 1329 root nodes not in WiBi taxonomy

## Find the collapsed components 
python wiki_graph2.py --roots root-nodes_u.txt --dir collapsed-components

# NOTE: 9545 remaining nodes in taxonomy after collapsing

## Generate the wikipedia data we want 
# First get all the wikipages we need 
cat collapsed-components/collapsed-components.tsv | awk '{split($0, a, "\t"); for(x in a) print a[x]}' > wikipages.txt
# Use David's data 
mv wiki-data.20150403.title-and-cleaned-content.wiki2html2txt.tsv wikipedia-content.tsv
# Get the content we actually want to use 
python get-wiki-content.py wikipages.txt wikipedia-content.tsv > wikipedia-content-used.tsv
wc -l wikipedia-content-used.tsv 	# 3198500 (out of 3404967)

# Only keep wikipedia components (not associated with reddit/SE) that have >= 500 words (in aggregate)
python threshold-components.py 500	
# components-enough-content-500.tsv has 252152

# Get the wikipedia page -> root node mapping (python shell)
wikipage-root-mapping.tsv	# This actually goes root \t page 

# Threshold wikipedia content itself based on above thresholding and relabel with the root node 
cat components-enough-content-500.tsv | awk '{split($0, a, "\t"); for(x in a) print a[x]}' > wikipages-500.txt
python get-wiki-content.py wikipages-500.txt wikipedia-content-used.tsv > wikipedia-content-500.tsv
wc -l wikipedia-content-500.tsv # 3120031 
# relabel with root node 
python relabel.py wikipage-root-mapping.tsv wikipedia-content-500.tsv > wikipedia-content-500_relabeled.tsv

# Clean wikipedia content
python clean-content.py wikipedia-content-500_relabeled.tsv > wikipedia-content-500_relabeled_cleaned.tsv
# NOTE: make sure this finished

# Get the unique word list with counts 
cut -f2 wikipedia-content-500_relabeled_cleaned.tsv | tr [:space:] '\n' | sort | uniq -c > wiki-word-counts.txt # 7819497 unique words
# Only allow words that appear at least 50 times in corpus
cat wiki-word-counts.txt | awk '{if($1>=50) print $2}' > wiki-word-counts_gt_50.txt 		# 378361 unique words

# Create the tf, idf, tf-idf word lists (distributed and tf and idf in parallel)
mkdir tfidf-stats 
split -l 350000 wikipedia-content-500_relabeled_cleaned.tsv wiki-content-split
mv wiki-content-split* tfidf-stats/
# in tfidf-stats/ - serenity (TF)
for f in wiki-content-split*; do python calculate_tfidf.py --data $f --allowed ../wiki-word-counts_gt_50.txt --tf $f.TF.tsv & done;
# in tfidf-stats/ - enterprise (IDF)
python calculate_tfidf.py --data ../wikipedia-content-500_relabeled_cleaned.tsv --allowed ../wiki-word-counts_gt_50.txt --idf wiki-IDF.tsv
# Merge TF files 
touch wiki-TF.tsv
for f in wiki-content-split*.TF.tsv; do cat $f >> wiki-TF.tsv; done
# in tfidf-stats/
python calculate_tfidf.py --tf wiki-TF.tsv --idf wiki-IDF.tsv --tfidf wiki-TFIDF.tsv
# Sort the IDF from most common to least common words 
sort -g -k2 wiki-IDF.tsv > wiki-IDF_sorted.tsv
# Sort the TF-IDF from least common to most common
sort -g -k1 -r wiki-TFIDF.tsv > wiki-TFIDF_sorted.tsv

## Reduce vocab

# Remove the most common words  (IDF threshold of >5)
cat wiki-IDF_sorted.tsv | awk '{split($0, a, "\t"); if(a[2] > 5) print $0}' | cut -f1 > ../wiki-words-to-keep.txt  # 374240 
# Reduce vocabulary based on top TF-IDF word list  
python reduce_vocab.py wiki-words-to-keep.txt wikipedia-content-500_relabeled_cleaned.tsv > wiki-content_reduced.tsv

## Get SE and Reddit data 
wc -l SE-content_all.tsv 		# 502216 documents to start with
# Aggregate SE data and filter out docs < 500 words total 
# (throw out tags that don't have enough aggregated content AND aren't in mapping)
cut -f1 reddit-se-wiki-mapping.tsv > reddit-se-nodes.txt
python reduce-SE.py SE-content_all.tsv 500 reddit-se-nodes.txt SE-content_reduced.tsv 	# 481214 documents now (-20,000)

# Reduce reddit data based on word count
wc -l reddit-content_all.tsv 	# 58894
cat reddit-content_all.tsv | awk '{if(NF>=500) print $0}' > reddit-content_reduced.tsv 		# 3436
# Only keep subreddits in mapping
python reduce-reddit-by-mapping.py reddit-content_reduced.tsv reddit-se-nodes.txt > reddit-content_reduced_reduced.tsv # 2561

# Combine stack exchange and reddit data 
cat SE-content_reduced.tsv > com-content.tsv
cat reddit-content_reduced_reduced.tsv >> com-content.tsv		# 334316 documents

# Get unique word list and counts for SE/reddit 
cut -f2 com-content.tsv | tr [:space:] '\n' | sort | uniq -c > com-word-counts.txt	# 103608 unique words
# Keep words that occur at least 25 times total
cat com-word-counts.txt | awk '{if($1>=25) print $2}' > com-words-gt_25.txt		# 114610 unique words
# Just compute IDF stats 
python calculate_tfidf.py --data ../com-content.tsv --allowed ../com-words-gt_25.txt --idf com-IDF.tsv
# Sort the IDF from most common to least common words 
sort -g -k2 com-IDF.tsv > com-IDF_sorted.tsv
# Remove the most common words
cat com-IDF_sorted.tsv | awk '{split($0, a, "\t"); if(a[2] > 5) print $0}' | cut -f1 > ../com-words-to-keep.txt  # 101777 
# Reduce the community content to only include these words 
python reduce_vocab.py com-words-to-keep.txt com-content.tsv > com-content_reduced.tsv

# Find intersection of community and wiki words 
cat com-words-to-keep.txt > all-words.txt; cat wiki-words-to-keep.txt >> all-words.txt 
sort all-words.txt | uniq -c | awk '{if($1 > 1) print $2}' > com-wiki-words-intersection.txt 		# 76043

# Just use community words since this is at ~100000 (only have 30000 extra unique community tokens)
sort -u com-words-to-keep.txt > vocabulary.txt
# Plus take top 101777 - 76043 = 25734 IDF wikipedia words 
tail -25734 wiki-IDF_sorted.tsv | cut -f1 > wiki-IDF-25734.tsv
cat wiki-IDF-25734.tsv >> ../vocabulary.txt 

# Reduce wikipedia data further (based on this reduced SE/Reddit vocab)
python reduce_vocab.py vocabulary.txt wiki-content_reduced.tsv > wiki-content_reduced_reduced.tsv

# Relabel community content with wikipedia pages (multiple pages for some)
# Remove labels (and potentially documents) that aren't in wikipedia data - some missing because aren't in wibi taxonomy
# use '~' delim since there are commas and spaces in the wikipedia names
cut -f1 wiki-content_reduced_reduced.tsv > wiki-labels.txt
python relabel-com.py reddit-se-wiki-mapping.tsv com-content_reduced.tsv wiki-labels.txt > com-content_reduced_relabeled.tsv 
# 7320 unique community labels

# Get the list of wikipedia nodes that have corresponding community label after doing all the comm thresholding
cut -f1 com-content_reduced_relabeled.tsv | tr '~' '\n' | sort -u > reddit-se-nodes_wiki_after_thresholding.txt

# Go through one more pass of wiki data - remove aggregate docs that have < 500 words (but keep subreddits/SE ones)
python reduce_docs.py wiki-content_reduced_reduced.tsv reddit-se-nodes_wiki_after_thresholding.txt 500 > wiki-content_final.tsv	
# 2873338 documents

# Make sure community topics are a subset of wikipedia topics - in python shell
# reddit-se-nodes_wiki_after_thresholding.txt
cut -f1 wiki-content_final.tsv | sort -u > topics.txt 		# 66206 final topics
# yes, it's a subset

# Save 0-indexed labeling 
cat topics.txt | awk '{print NR-1"\t"$0}' > topic-mapping.tsv

## Null data = wikipedia data 
# Relabel documents with 0-indexed labels and brackets around the labels - llda format
python relabel.py topic-mapping.tsv wiki-content_final.tsv > null-data.tsv	# 2873338 docs

## Full data = community + wikipedia data - llda format
cp null-data.tsv full-data.tsv
python relabel.py topic-mapping.tsv com-content_reduced_relabeled.tsv >> full-data.tsv	# 3187257 docs

## RUN LLDA 
cp null-data.tsv ../../JGibbsLLDA/src/data/null-data-final.txt & cp full-data.tsv ../../JGibbsLLDA/src/data/full-data-final.txt
# in JGibbsLLDA/src/data/
gzip full-data-final.txt & gzip null-data-final.txt
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx300G jgibblda.LDA -est -ntopics 66206 -dfile null-data-final.txt.gz -dir data/ -model null-model-final
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx350G jgibblda.LDA -est -ntopics 66206 -dfile full-data-final.txt.gz -dir data/ -model full-model-final

## RUN NAIVE BAYES - in models/
python MLmodels.py --train NB --data ../data/final-round/full-data.tsv --dir models/naive_bayes/full-final
python MLmodels.py --train NB --data ../data/final-round/null-data.tsv --dir models/naive_bayes/null-final

## MEMORY ERROR! :(

## RUN SVM 
python MLmodels.py --train SVM --data ../data/final-round/full-data.tsv --dir models/svm/full-final
python MLmodels.py --train SVM --data ../data/final-round/null-data.tsv --dir models/svm/null-final

# TODO:
# FIX depth thing - missing 48000 nodes?? 
# Get collapsed components - run in parallel? 
# Get wikipedia pages 

# Truncate wikipedia content - take sample? or take top words in each document? 
# Add wikipedia external links 
# Aggregating by topic might be easier? 
# Create the pure reddit-SE model (just those topics, without structure)

## Figure out number of topics for each depth limit - saves in collapsed-components/depth-stats.tsv
python wiki_graph2.py --roots root-nodes_u.txt --dir collapsed-components --stats 1 --taxonomy WiBi.pagetaxonomy.txt

# Get the number of topics after filtering at each depth-filter (with min node requirement of 3)
for x in [0,1,2,3,4,5,6]; do 
	python wiki_graph2.py --depths collapsed-components/topics-at-each-depth.tsv --dir collapsed-components --thresh $x;
done

## Note: first two columns are the same in collapsed components
cut -f1 --complement collapsed-components-0.tsv | awk '{n=split($0, a, "\t"); if(n>=3) print $0}' | wc -l

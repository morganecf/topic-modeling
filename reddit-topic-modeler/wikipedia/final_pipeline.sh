#### FINAL PIPELINE!! FOR REAL

## Create the wikipedia taxonomy graph 
python wiki_graph2.py --taxonomy WiBi.pagetaxonomy.txt --dir collapsed-components

## Find the topics (our wiki roots) at each depth 
cut -f1 collapsed-wiki-root-nodes.tsv > wiki-root-nodes.txt
python wiki_graph2.py --roots wiki-root-nodes.txt --wikiroots collapsed-components/all-roots.txt --taxonomy WiBi.pagetaxonomy.txt --stats 1 --dir collapsed-components

## Collapse the components at depth threshold = 3 
python depth-thresholding-stats.py > depths-at-thresholds.tsv
cat topics-at-each-depth.tsv | awk '{if($1<=3) print $0}' > topics-at-depth-3.tsv	# 136369 depth-3 wiki topics
# Add the reddit/SE topics 
cut -f2 collapsed-components/topics-at-depth-3.tsv > topics-to-collapse-3.tsv
cut -f2 reddit-se-wiki-mapping.tsv >> topics-to-collapse-3.tsv						# 13620 reddit/se topics
wc -l topics-to-collapse-3.tsv														# 149989 total 
sort -u topics-to-collapse-3.tsv > topics-to-collapse-3_unique.tsv					# 145977 total unique
cp topics-to-collapse-3_unique.tsv collapsed-components/collapsible-topics3.txt
# Collapse with depth threshold
python wiki_graph2.py --roots collapsed-components/collapsible-topics3.txt --dir collapsed-components --thresh 3
	# creates collapsed-components-3.tsv

## Remove components that have fewer than 3 nodes total 
mv collapsed-components-3.tsv collapsed-components-3_final.tsv # to avoid interference from other stuff running
# Parent node is duplicated so cut it out
#cut -f1 --complement collapsed-components-3_final.tsv | awk '{n=split($0, a, "\t"); if(n>=3) print $0}' > collapsed-components3_nodes-gt-3.tsv
#wc -l collapsed-components3_nodes-gt-3.tsv 		# 22648
	# note: parent will be mixed up in ordering here 
# But we only want to omit those that don't have a reddit/SE mapping 
cut -f2 reddit-se-wiki-mapping.tsv > collapsed-components/reddit-se-nodes_wikinames.txt
python threshold_nodes.py collapsed-components-3_final.tsv reddit-se-nodes_wikinames.txt 3 > collapsed-components-3_thresholded.tsv
	# 27213 collapsed-components-3_thresholded.tsv - not bad 

## Get the wikipedia pages we need content from 
cat collapsed-components/collapsed-components-3_thresholded.tsv | awk '{split($0, a, "\t"); for(x in a) print a[x]}' > wikipages.txt
sort -u wikipages.txt > wikipages_unique.txt
wc -l wikipages.txt ; wc -l wikipages_unique.txt		# 3277669 wikipedia pages used total (so we still have very good coverage of wikipedia)
python get-wiki-content.py wikipages_unique.txt wikipedia-content.tsv > wikipedia-content-used.tsv

## Get and clean the stack exchange data 
python clean-content.py SE-content_all.tsv SE-content_cleaned.tsv 500000

## Get rid of stack exchange topics that, in aggregate, have fewer than 500 words and are in mapping
cut -f1 reddit-se-wiki-mapping.tsv > reddit-se-nodes.txt
python reduce-SE.py SE-content_cleaned.tsv 500 reddit-se-nodes.txt SE-content_cleaned_reduced.tsv	
	# went from 502216 to 331755 documents
cut -f1 SE-content_cleaned_reduced.tsv | awk '{for(i=1; i<=NF; ++i) print $i}' | sort -u > SE-topics.txt	# 8982 SE topics

## Get rid of reddit topics that have fewer than 500 words and are in mapping
python reduce-reddit.py reddit-content_all.tsv 500 reddit-se-nodes.txt reddit-content_cleaned_reduced.tsv	# 2561 reddit topics
cut -f1 reddit-content_cleaned_reduced.tsv > reddit-topics.txt

## Update the list of reddit/SE topics we want to keep
cat SE-topics.txt > reddit-SE-topics_post-thresh.txt; cat reddit-topics.txt >> reddit-SE-topics_post-thresh.txt
	# 11543 total community topics 

## First pass at thresholding, because cleaning is expensive - remove components that, in aggregate, have fewer than 500 words 
	# but keep those that have a corresponding community topic (if have <500 words before clean, will have <500 after)
python threshold-components.py collapsed-components/collapsed-components-3_thresholded.tsv reddit-SE-topics_post-thresh.txt wikipedia-content-used.tsv 500 collapsed-components_thresh1.tsv
wc -l collapsed-components_thresh1.tsv
	# 26727 (got rid of ~1000 topics) 
# Filter the wikipedia content based on this new set of components/wikipedia pages
cat collapsed-components_thresh1.tsv | awk '{split($0, a, "\t"); for(x in a) print a[x]}' | sort -u > wikipages_after_thresh1.txt
python get-wiki-content.py wikipages_after_thresh1.txt wikipedia-content-used.tsv > wikipedia-content-thresh1.tsv

## Second pass at thresholding - clean and then threshold again
# Clean - distribute
split -l 300000 wikipedia-content-thresh1.tsv wikicontent-split
python clean-content.py wikicontent-splitaa wikicontent-cleanaa 300000
mkdir split-wikicontent; mv wikicontent-* split-wikicontent/
for f in wikicontent-clean*; do cat $f >> ../wikipedia-content-thresh1-clean.tsv; done
# Threshold - use 1000 words. The more words, the more likely it is to be a topic (500 is just two paragraphs)
python threshold-components.py collapsed-components_thresh1.tsv reddit-SE-topics_post-thresh.txt wikipedia-content-thresh1-clean.tsv 1000 collapsed-components_thresh2-1000.tsv
cat collapsed-components_thresh2-1000.tsv | awk '{split($0, a, "\t"); for(x in a) print a[x]}' | sort -u > wikipages_after_thresh2.txt
python get-wiki-content.py wikipages_after_thresh2.txt wikipedia-content-thresh1-clean.tsv > wikipedia-content-thresh2-clean.tsv

## Create the wikipedia vocabulary
# Get unique words and their counts - distribute 
cut -f2 wikicontent-cleanaa | tr [:space:] '\n' | sort > wikiwords-aa
for f in wikiwords-*; do cat $f >> wikiwords-all; done
sort wikiwords-all | uniq -c > ../wikiwords-counts.txt
	# NOTE: did this part in python shell - sort and uniq -c taking way too long
wc -l wikiwords-counts.txt 		# initial vocab size of 7,417,473 words (700,000,000+ words total)
# Remove words that don't appear at least 50 times 
cat wikiwords-counts.txt | awk '{if($2>=50) print $2}' > wiki-words-gt_50.txt	# vocab size now is 355,272
# Reduce wiki content by this vocabulary  - distribute
python ../reduce_vocab.py wiki-words-gt_50.txt wikicontent-cleanaa > wikicontent-reducedaa
for f in wikicontent-reduced*; do cat $f >> ../wiki-content_reduced_vocab.tsv; done
# Compute TF-IDF stats 
# tf - distribute
python calculate_tfidf.py --data split-wikicontent/wikicontent-reducedaa --allowed wiki-words-gt_50.txt --tf split-wikicontent/wiki-TF-aa
for f in wiki-TF-*; do cat $f >> ../wiki-TF.tsv; done
# IDF 
python calculate_tfidf.py --data wiki-content_reduced_vocab.tsv --allowed wiki-words-gt_50.txt --idf wiki-IDF.tsv
# TF-iDF
python calculate_tfidf.py --tf wiki-TF.tsv --idf wiki-IDF.tsv --tfidf wiki-TFIDF.tsv
# Sort the IDF from most to least common words 
sort -g -k2 wiki-IDF.tsv > wiki-IDF_sorted.tsv
# Sort the TF-IDF from most to least important
sort -g -k1 -r wiki-TFIDF.tsv > wiki-TFIDF_sorted.tsv
# Take the top 300,000 words by TF-IDF and reduce (distribute)
#head -300000 wiki-TFIDF_sorted.tsv | cut -f2 > wiki-tfidf-vocab_300000.txt
# Take the top 250,000 words by TF-IDF and reduce (distribute)
head -250000 wiki-TFIDF_sorted.tsv | cut -f2 > wiki-tfidf-vocab_250000.txt
python ../reduce_vocab.py ../wiki-tfidf-vocab_250000.txt wikicontent-reducedaa > wikicontent-reducedreducedaa
for f in wikicontent-reducedreduced*; do cat $f >> ../wiki-content_reduced_reduced_vocab.tsv; done
# Take the top 150,000 words by TF-IDF and reduce (distribute)
#head -150000 wiki-TFIDF_sorted.tsv | cut -f2 > wiki-tfidf-vocab_150000.txt

## Create null data file 
# Get parent -> child mapping 
python parent-child-mapping.py collapsed-components_thresh2-1000.tsv wiki-parent-child-mapping.tsv
# Relabel content file with parent topics 
python relabel-wiki.py wiki-parent-child-mapping.tsv wiki-content_reduced_reduced_vocab.tsv wikipages-missing-from-final-mapping.txt > wiki-content_relabeled.tsv
	# NOTE: some are missing? 5686 to be exact 
# Create 0-indexed labeling 
cut -f1 wiki-content_relabeled.tsv | sort -u | awk '{print NR-1"\t"$0}' > wiki-topic-index-mapping.tsv
	# Num topics: 24333
# Label docs with indices
python label-with-index.py wiki-topic-index-mapping.tsv wiki-content_relabeled.tsv > wiki-content_index_relabeled.tsv
# Format for llda 
python format-llda.py wiki-content_index_relabeled.tsv > null-data.txt
	# null data has 24333 topics
	# 3066012 documents
	# vocabulary of size 250,000 

## Run null data models
cp null-data.txt ../../JGibbsLLDA/src/data/null-data-final.txt
gzip null-data-final.txt
java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx400G jgibblda.LDA -est -ntopics 24333 -dfile null-data-final.txt.gz -dir data/ -model null-model-final

### FULL data

## Add wikipedia articles 

### NOTE: IMPORTANT --- might be counting parent node data twice when thresholding???? ?
#### DOUBLE CHECK THIS!!!!!!!!!!!

### NOTE: IMPORTANT ---- taking broader topics doesn't seem to make that much sense, actually
	# ex: Transformation (function) subsumes a lot of nodes that don't really make sense
	# we should also cut off the depth and just ignore some nodes? 
	# although in general looks good

## NOTE: missing-root.txt - overwritten? 



### depth = 2
wc -l collapsed-components-2_thresholded.tsv
	# 22376 thresholded at 3 


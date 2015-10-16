# Wikipedia/subreddit topic modeling pipeline 
# Usage: ./pipeline.sh <part-to-execute>

part=$1

echo 'Hello! Executing' $part

### Create the wikipage taxonomy with annotated subreddits (~2 minutes)

# WiBi's page taxonomy edge list 
taxonomy="wibi/taxonomies/WiBi.pagetaxonomy.txt"
# David's subreddit to wikipage mapping 
raw_mapping="data/reddit-wiki-mapping/subreddit-to-wiki.tsv"
# List of subreddits by % of posts that are pics
subreddits_by_pic="data/subreddits_by_perc_img_links.txt"
# The threshold of % pics for banned subreddits
pic_threshold=0.7
# The output directory
out_dir="data/collapsed-components/"

# The pickled wikipage network annotated with subreddits 
nx_taxonomy="data/collapsed-components/page_taxonomy.gpickle"
# The subreddits that belong in the network and their affiliated wikipage
# (those that have a mapping and were found in the page taxonomy)
mapping="data/collapsed-components/mapping.tsv"

# Where to save information on runs 
info="data/info.txt"

if [ $part = "build-taxonomy" ]; then
	python src/wiki_graph.py --taxonomy $taxonomy --mapping $raw_mapping --pics $subreddits_by_pic --threshold $pic_threshold --dir $out_dir

	# Save some stats on the output 
	echo 'Number of subreddits that have a mapping to a wikipedia page:' > $info
	wc -l data/reddit-wiki-mapping/subreddit-to-wiki.tsv >> $info
	echo 'Number of these subreddits that are in the page taxonomy AND below pic threshold:' >> $info
	wc -l data/collapsed-components/mapping.tsv >> $info
	echo 'Number of edges in the WiBi page taxonomy:' >> $info
	wc -l wibi/taxonomies/WiBi.pagetaxonomy.txt >> $info 
	echo '' >> $info
fi

### Collapse the taxonomy to its subreddit nodes (~3 minutes)

if [ $part = "collapse" ]; then
	python src/wiki_graph.py --dir $out_dir

	# Save some output stats 
	echo 'Number of cycle pairs in taxonomy:' >> $info
	wc -l data/collapsed-components/cycles.tsv >> $info
	echo 'Number of banned subreddits:' >> $info
	wc -l data/collapsed-components/banned.txt >> $info
	echo '' >> $info

	echo 'Number of subreddit components:' >> $info 
	wc -l data/collapsed-components/collapsed-subreddit-components.tsv >> $info
	echo 'Number of wikipedia components:' >> $info
	wc -l data/collapsed-components/collapsed-wikipedia-components.tsv >> $info 
	echo 'Component stats:' >> $info
	cat data/collapsed-components/component-stats.txt >> $info
	echo '' >> $info
fi

### Get text data for the components and clean it, omitting subreddits or wikipages
### that have fewer than 1000 words. Outputs the files with the data and a new file
### with the components that were kept. 

# The subreddit components (and all the wikipages underneath each subreddit)
subreddit_components="data/collapsed-components/collapsed-subreddit-components.tsv"
# The wikipedia components (what remains after removing subreddit trees)
wikipedia_components="data/collapsed-components/collapsed-wikipedia-components.tsv"
# Output wikipedia content file
wikipedia_content="data/wikipedia-content.tsv"
# All wikipedia pages to get parsed content from
wikipedia_pages="data/wikipages-needed.txt"

# Get wikipedia data (~1/2 an hour)
if [ $part = "wiki-data" ]; then 
	# First get all the wikipages we need from subreddit components (everything except for first part of each line)
	cat $subreddit_components | awk '{if (NF>1) print $0}' | cut --complement -f1 | tr "\t" "\n" > $wikipedia_pages
	# Now get the wikipages corresponding to the subreddit pages 
	cut -f2 $mapping >> $wikipedia_pages
	# Now get the wikipages from the wikipedia collapsed components 
	cat $wikipedia_components | tr '\t' '\n' >> $wikipedia_pages
	
	# # Same thing, but in title=""> format (for grepping)
	# wikipedia_pages_grep="wikidump/wikipages-needed-grep.txt"
	# # Construct a grep regex for finding the wikipages in the parsed directory
	# cat $wikipedia_ages | awk '{print "title=\""$0"\">"}' > $wikipedia_pages_grep
	# # Go through each page and find the directory and line number in parsed-wiki containing the wikipage
	# # >> data/wiki-table-contents.tsv 

	python src/wiki_content.py $wikipedia_pages $wikipedia_content

	# Print size and line/word counts of wiki and reddit content files 
	echo 'Wiki content file:' >> $info
	wc data/wikipedia-content.tsv >> $info
	du -BM data/wikipedia-content.tsv >> $info
	echo '' >> $info
fi

# Output subreddit content file 
subreddit_content="data/reddit-content.tsv"
# The max number of submissions to get per subreddit -- will get all of them with -1
submission_threshold=-1
# The max number of comments to get per subreddit -- will get all of them with -1
comment_threshold=-1
# Only get comments below or equal to this level 
comment_level=3

# Get reddit content (~45 minutes)
if [ $part = "reddit-data" ]; then 
	python src/reddit_content.py $mapping $subreddit_content $submission_threshold $comment_threshold $comment_level

	echo 'Reddit content file:' >> $info
	wc data/reddit-content.tsv >> $info
	du -BM data/reddit-content.tsv >> $info
	echo 'Max number of submissions:' $submission_threshold >> $info
	echo 'Max number of comments:' $comment_threshold >> $info
	echo 'Max comment level:' $comment_level >> $info
	echo '' >> $info

	# New round of reddit data (with better clean function):
	python src/reddit_content.py data/collapsed-components/mapping.tsv data/reddit-data-better-clean/reddit-content.tsv -1 -1 5
fi

### Reduce the content by removing subreddits that are below a certain 
### word count and wikipages below a certain character count

# Ignore subreddit documents with less than this number of words
word_threshold=1000
# Ignore wikipedia documenst with less than this number of chars (stub docs)
char_threshold=2000

subreddit_content_reduced="data/reddit-content_reduced.tsv"
#wikipedia_content_reduced="data/wikipedia-content_reduced.tsv"

if [ $part = "filter" ]; then
	# Remove subreddits that don't have at least word_threshold number of words 
	cat $subreddit_content | awk 'NF>='$word_threshold > $subreddit_content_reduced

	# Remove wikipages that don't have at least char_threshold number of characters
	# actually don't do this - don't want to remove wikipages that belong to a component
	#cat $wikipedia_content | awk 'length>='$char_threshold > $wikipedia_content_reduced
fi

### Aggregate all the wiki/subreddit content by collapsed component 

# All of the components 
components="data/collapsed-components/collapsed-components.tsv"
# The group id to page mapping 
id_mapping="data/id-mapping.tsv"

if [ $part = "aggregate" ]; then 
	# Concat the wikipedia and subreddit components
	cat $subreddit_components > $components
	cat $wikipedia_components >> $components  

	# Assign a group id number to each component and save the id to page mapping
	cat $components | awk '{split($0, a, "\t"); for (i in a) print NR"\t"a[i]}' > data/id-mapping.tsv

	# Then label each line in the wikipedia and subreddit content pages with this id 
	wiki_labels="data/aggregated-data/wikipedia-content-labels.txt"
	reddit_labels="data/aggregated-data/reddit-content-labels.txt"
	cut -f1 $wikipedia_content > data/aggregated-data/wikipedia-content-pages.txt
	cut -f1 $subreddit_content_reduced > data/aggregated-data/reddit-content-pages.txt
	python data/aggregated-data/label.py data/aggregated-data/wikipedia-content-pages.txt > $wiki_labels
	python data/aggregated-data/label.py data/aggregated-data/reddit-content-pages.txt > $reddit_labels

	# Make sure that there are the same amount of labels as lines in content files
	echo 'Number of wikipedia lines/labels:'
	wc -l $wikipedia_content
	wc -l $wiki_labels
	echo 'Number of reddit lines/labels:'
	wc -l $subreddit_content_reduced
	wc -l $reddit_labels

	# Label the actual content 
	labeled_wiki="data/aggregated-data/labeled-wiki-content.tsv"
	labeled_reddit="data/aggregated-data/labeled-reddit-content.tsv"
	paste -d"\t" $wiki_labels $wikipedia_content > $labeled_wiki
	paste -d"\t" $reddit_labels $subreddit_content_reduced > $labeled_reddit

	# Aggregate wikipedia data by id -- this will also be the null data 
	# wiki_agg="data/aggregated-data/wiki-aggregated.tsv"
	# cat $labeled_wiki | sort | awk -F "\t" 's != $1 || NR ==1{s=$1;if(p){print p};p=$0;next}{sub($1,"",$0);p=p""$0;}END{print p}' > $wiki_agg

	# Aggregate reddit data by id 
	reddit_agg="data/aggregated-data/reddit-aggregated.tsv"
	cat $labeled_reddit | sort -nk1 | awk -F "\t" 's != $1 || NR ==1{s=$1;if(p){print p};p=$0;next}{sub($1,"",$0);p=p""$0;}END{print p}' > $reddit_agg

	# Aggregate wikipedia data by id 
	sort labeled-wiki-content.tsv > labeled-wiki-content_sorted.tsv 
	python aggregate_data.py labeled-wiki-content_sorted.tsv > wiki-aggregated_final.tsv 

	# Separate wikipedia topics that are also subreddit topics
	python separate_reddit_from_wiki.py reddit-labels.txt wiki-aggregated_final.tsv wiki-aggregated_reddit.tsv wiki-aggregated_wiki.tsv

	# Still not completely aggregated ... not sure why, so do again with diff version
	python aggregate_data2.py wiki-aggregated_wiki.tsv wiki-aggregated_wiki_final.tsv
	python aggregate_data2.py wiki-aggregated_reddit.tsv wiki-aggregated_reddit_final.tsv

	# Remove any pure-wikipedia topics that have fewer than 2000 words
	cat wiki-aggregated_wiki_final.tsv | awk '{if(NF>=2000) print $0}' > wiki-aggregated_wiki_final_reduced.tsv

	# Remove any reddit topics not in wikipedia data 
	cut -f1 wiki-aggregated_reddit_final.tsv > wiki-reddit-labels.txt
	python reddit_topics_with_wikipage.py wiki-reddit-labels.txt reddit-aggregated_fixed.tsv > reddit-aggregated_reduced.tsv
	# Do the same for wiki data 
	cut -f1 reddit-aggregated_reduced.tsv > reddit-wiki-labels.txt
	python reddit_topics_with_wikipage.py reddit-wiki-labels.txt wiki-aggregated_reddit_final.tsv > wiki-aggregated_reddit_reduced.tsv

	# Now aggregate pure reddit data with wiki-reddit data 
	cut -f1 reddit-aggregated_reduced.tsv | sort -g > reddit-aggregated_reduced_labels.txt 
	cut -f1 wiki-aggregated_reddit_reduced.tsv | sort -g > wiki-aggregated_reddit_reduced_labels.txt
	# both should have the same line count -- 2523
	comm -12 reddit-aggregated_reduced_labels.txt wiki-aggregated_reddit_reduced_labels.txt | wc -l

	# NULL data: combine wiki-aggregated_wiki_final_reduced.tsv and wiki-aggregated_reddit_reduced.tsv 
	cat wiki-aggregated_wiki_final_reduced.tsv > WIKI-DATA.tsv
	cat wiki-aggregated_reddit_reduced.tsv >> WIKI-DATA.tsv
	# make sure they're all unique topics
	wc -l WIKI-DATA.tsv
	cut -f1 WIKI-DATA.tsv | sort -u | wc -l 

	# FULL data: aggregate everything
	# first aggregate wiki-reddit data to reddit data 
	cut -f1 --complement wiki-aggregated_reddit_reduced.tsv > wiki-aggregated_reddit_reduced_no_labels.tsv
	paste -d" " reddit-aggregated_reduced.tsv wiki-aggregated_reddit_reduced_no_labels.tsv > reddit-aggregated_wiki.tsv
	cat reddit-aggregated_wiki.tsv > REDDIT-WIKI-DATA.tsv
	cat wiki-aggregated_wiki_final_reduced.tsv >> REDDIT-WIKI-DATA.tsv
	# make sure they're all unique topics
	wc -l REDDIT-WIKI-DATA.tsv
	cut -f1 REDDIT-WIKI-DATA.tsv | sort -u | wc -l 


	# Yay! We have our two datasets 

	# Now fix the stupid extra tabs/whitespace AND extra label 
	# cat $reddit_agg | cut -f1 > data/aggregated-data/temp-labels.txt
	# cat $reddit_agg | cut --complement -f1 | tr -s ' ' > data/aggregated-data/temp-data.txt
	# paste -d"\t" data/aggregated-data/temp-labels.txt data/aggregated-data/temp-data.txt > $reddit_agg
	# cat $wiki_agg_reduced | cut -f1 > data/aggregated-data/temp-labels.txt
	# cat $wiki_agg_reduced | cut --complement -f1 | tr ',' ' ' | tr '\t' ' ' | tr -s ' ' > data/aggregated-data/temp-data.txt
	# paste -d"\t" data/aggregated-data/temp-labels.txt data/aggregated-data/temp-data.txt > $wiki_agg_reduced

	# Now merge wiki and reddit groups
	# labeled_full="data/aggregated-data/labeled-full-data.tsv"
	# final_data="data/labeled-data-final.tsv"
	# cat $reddit_agg > $labeled_full
	# cat $wiki_agg_reduced >> $labeled_full
	# cat $labeled_full | sort | awk -F "\t" 's != $1 || NR ==1{s=$1;if(p){print p};p=$0;next}{sub($1,"",$0);p=p""$0;}END{print p}' > $final_data

	# cat $final_data | cut -f1 > data/aggregated-data/temp-labels.txt
	# cat $final_data | cut --complement -f1 | tr -s ' ' > data/aggregated-data/temp-data.txt
	# paste -d"\t" data/aggregated-data/temp-labels.txt data/aggregated-data/temp-data.txt > $final_data 
	# rm -f data/aggregated-data/temp-labels.txt
	# rm -f data/aggregated-data/temp-data.txt

	# final_data contains the final full model data !!
	# wiki_agg_reduced contains the final null model data !!

	# TODO: Save stats 

fi

if [ $part = "tfidf" ]; then
	# In data/tfidf-stats/

	# Get the word count lists 
	cut -f1 --complement reddit-aggregated_reduced.tsv | tr  [:space:] '\n' | sort | uniq -c > reddit-words.txt
	cut -f1 --complement WIKI-DATA.tsv | tr  [:space:] '\n' | sort | uniq -c > wiki-words.txt

	# Calculate TF, IDF, TF-IDF lists -- ignore words that don't at least appear 50 times in entire corpus
	python calculate_tfidf.py reddit-aggregated_reduced.tsv reddit-words.txt reddit-TF.tsv reddit-IDF.tsv reddit-TFIDF.tsv 50
	python calculate_tfidf.py WIKI-DATA.tsv wiki-words.txt wiki-TF.tsv wiki-IDF.tsv wiki-TFIDF.tsv 50

	# Sort by tf-idf
	sort -g -k1 -r reddit-TFIDF.tsv > reddit-TFIDF_sorted.tsv
	sort -g -k1 -r wiki-TFIDF.tsv > wiki-TFIDF_sorted.tsv

fi

### Create feature files (vocab) and save stats on reddit vs. wiki vocabularies 
### output vocabularies and formatted data in [doc_id] text format, and save the page->id mapping

# The aggregated data
data="data/data-by-topic.tsv"
# Maximum number of features (words) for training models
max_features=500000
# Where to output the formatted data
feature_output_dir="data/formatted-data/"

# Create the features (~5 hours)
if [ $part = "vocab" ]; then

	# Get lists of words 
	cut --complement -f1 reddit-topics.tsv | tr ' ' '\n' > reddit-words.txt
	cut --complement -f1 wiki-topics.tsv | tr ' ' '\n' > wiki-words.txt
	cat reddit-words.txt > words.txt 
	cat wiki-words.txt >> words.txt

	# Sort and get word counts 
	cat reddit-words.txt | sort | uniq -c > reddit-words-count.txt
	cat wiki-words.txt | sort | uniq -c > wiki-words-count.txt
	cat words.txt | sort | uniq -c > words-count.txt 

	# Remove words with count of 1 
	cat reddit-words-count.txt | awk '{if($1>1) print $0}' > reddit-words-count_above1.txt
	cat wiki-words-count.txt | awk '{if($1>1) print $0}' > wiki-words-count_above1.txt
	cat words-count.txt | awk '{if($1>1) print $0}' > words-count_above1.txt

	# Gives the new word total
	# cat reddit-words-count_above1.txt | awk '{count+=$1} END {print count}'
	# cat wiki-words-count_above1.txt | awk '{count+=$1} END {print count}'
	# cat words-count_above1.txt | awk '{count+=$1} END {print count}'

	# Remove numbers and alphanumeric characters 
	python rm_alphnum.py reddit-words-count_above1.txt > reddit-words-count_above1_no-num.txt
	python rm_alphnum.py wiki-words-count_above1.txt > wiki-words-count_above1_no-num.txt
	python rm_alphnum.py words-count_above1.txt > words-count_above1_no-num.txt

	# Gives the new word total
	cat reddit-words-count_above1_no-num.txt | awk '{count+=$1} END {print count}'
	cat wiki-words-count_above1_no-num.txt | awk '{count+=$1} END {print count}'
	cat words-count_above1_no-num.txt | awk '{count+=$1} END {print count}'

	# Get term frequencies 
	cat reddit-words-count_above1_no-num.txt | awk '{print $1/101727282.0" "$2}' > reddit-words-tf.txt
	cat wiki-words-count_above1_no-num.txt | awk '{print $1/368190970.0" "$2}' > wiki-words-tf.txt
	cat words-count_above1_no-num.txt | awk '{print $1/470205825.0" "$2}' > words-tf.txt

	### TODO: something is wrong here...some of them are not aligned 
	# Get tf-idf values 
	# Get word list 
	# cat reddit-words-count_above1_no-num.txt | awk '{print $2}' > reddit-word-list.txt
	# cat wiki-words-count_above1_no-num.txt | awk '{print $2}' > wiki-word-list.txt
	# # Get the number of documents each word appears in 
	# awk 'NR == FNR {count[$1]=0; next} { for (i=0; i<=NF; i++) if ($i in count) count[$i]++ } END { for (word in count) print word, count[word] }' reddit-word-list.txt reddit-topics.tsv > reddit-word-doc-counts.txt
	# awk 'NR == FNR {count[$1]=0; next} { for (i=0; i<=NF; i++) if ($i in count) count[$i]++ } END { for (word in count) print word, count[word] }' wiki-word-list.txt wiki-topics.tsv > wiki-word-doc-counts.txt
	# sort reddit-word-doc-counts.txt > reddit-word-doc-counts_sorted.txt
	# sort wiki-word-doc-counts.txt > wiki-word-doc-counts_sorted.txt
	# # Merge these two to get the tf and idf components 
	# paste -d" " reddit-word-doc-counts_sorted.txt reddit-words-count_above1_no-num.txt > reddit-doc-word-counts.txt
	# paste -d" " wiki-word-doc-counts_sorted.txt wiki-words-count_above1_no-num.txt > wiki-doc-word-counts.txt
	# # Now compute the full score - $2 is the 
	# cat reddit-doc-word-counts.txt | awk '{}'

	# Sort by count and get top 100000
	sort -g -r reddit-words-count_above1_no-num.txt > reddit-words-count_sorted.txt
	sort -g -r wiki-words-count_above1_no-num.txt > wiki-words-count_sorted.txt
	sort -g -r words-count_above1_no-num.txt > words-count_sorted.txt

	head -100000 reddit-words-count_sorted.txt | awk '{print $2}' > reddit-words-count_100000.txt
	head -100000 wiki-words-count_sorted.txt | awk '{print $2}' > wiki-words-count_100000.txt
	head -100000 words-count_sorted.txt | awk '{print $2}' > words-count_100000.txt

	# Sort by TF and get top 100000
	sort -g -r reddit-words-tf.txt > reddit-words-tf_sorted.txt
	sort -g -r wiki-words-tf.txt > wiki-words-tf_sorted.txt
	sort -g -r words-tf.txt > words-tf_sorted.txt

	head -100000 reddit-words-tf_sorted.txt | awk '{print $2}' > reddit-words-tf_100000.txt
	head -100000 wiki-words-tf_sorted.txt | awk '{print $2}' > wiki-words-tf_100000.txt
	head -100000 words-tf_sorted.txt | awk '{print $2}' > words-tf_100000.txt

	# Sort by tf-idf and get top 100000
	## TODO 

	# Trim/format the topic files according to top words by word count, tf, tf-idf
	python filter_words.py topics.tsv words-count_100000.txt gid_to_id_mapping.tsv > topics-100000.txt
	python filter_words.py topics.tsv words-count_50000.txt gid_to_id_mapping.tsv > topics-50000.txt
	#python filter_words.py topics.tsv words-tf_100000.txt > topics-tf-100000.tsv
	# TODO: tf-idf

	#paste -d" " words-count_100000.txt words-tf_100000.txt | awk '{if($1 != $2) count++} END {print count}'
	## NOTE: differ by only 2 words. 

	# Trim/format the topic files according to top WIKI words by word count, tf, tf-idf
	python filter_words.py wiki-topics.tsv wiki-words-count_100000.txt gid_to_id_mapping-null.tsv > topics-null-100000.txt
	python filter_words.py wiki-topics.tsv wiki-words-count_50000.txt gid_to_id_mapping-null.tsv > topics-null-50000.txt

	# Trim/format the topic files according to top REDDIT words by word count, tf, tf-idf

	# Trim/format the NULL (wiki) topic files by word count 

	
	# Get reddit's unique contribution 
	comm -23 reddit-word-list.txt wiki-word-list.txt > reddit-unique-contrib_above1_no-num.txt
	# Get reddit's unique contribution by volume


	# echo 'creating features'
	# python src/features.py $subreddit_content_reduced $wikipedia_content_reduced $mapping $subreddit_components $wikipedia_components $word_threshold $max_features $feature_output_dir
fi

### Create models 

if [ $part = "run-llda" ]

	# to get number of topics
	wc -l topics-100000.txt 

	gzip topics-100000.txt

	# 15121 total topics
	# 13286 null topics

	java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx200G jgibblda.LDA -est -ntopics 15121 -dfile topics-100000.txt.gz -dir data/ -model model100000
	java -cp '.:../lib/args4j-2.0.6.jar:../lib/trove-3.0.3.jar' -Xmx200G jgibblda.LDA -est -ntopics 13286 -dfile topics-null-100000.txt.gz -dir data/ -model null-model100000

fi


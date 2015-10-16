
matrix="/matrix.txt"
labels="/labels.txt"
words="/words.txt"
root="../data/formatted_data/monthly/"
ast="*"
ext125="top125/"
ext500="top500/"
dir125="$root$ext125"
dir500="$root$ext500"

dir125all="$dir125$ast"
dir500all="$dir500$ast"

for path in $dir125all
	do
		IFS='/' read -a parts <<< "$path"
		date="${parts[5]}"
		echo $date
		resultsdir="../data/naivebayes/monthly/top125/$date"
		inputdir="$dir125$date"
		inputfile="$inputdir$matrix"
		labelsfile="$inputdir$labels"
		wordsfile="$inputdir$words"
		mkdir $resultsdir
		python naiveBayes.py --data $inputfile --labels $labelsfile --words $wordsfile --dir $resultsdir
	done

for path in $dir500all
	do
		IFS='/' read -a parts <<< "$path"
		date="${parts[5]}"
		echo $date
		resultsdir="../data/naivebayes/monthly/top500/$date"
		inputdir="$dir500$date"
		inputfile="$inputdir$matrix"
		labelsfile="$inputdir$labels"
		wordsfile="$inputdir$words"
		mkdir $resultsdir
		python naiveBayes.py --data $inputfile --labels $labelsfile --words $wordsfile --dir $resultsdir
	done




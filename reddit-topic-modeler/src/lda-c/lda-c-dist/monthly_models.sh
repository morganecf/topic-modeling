
matrix="/matrix.txt"
alpha="/alpha.txt"
info="/info.txt"
root="../../../data/formatted_data/monthly/"
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
		date="${parts[7]}"
		echo $date
		resultsdir="../../../data/unsupervised-LDA/monthly/top125/$date"
		inputdir="$dir125$date"
		inputfile="$inputdir$matrix"
		approx=$(cat $inputdir$alpha)
		infofile="$inputdir$info"
		k=$(grep 'label-key.txt' $infofile | cut -d ' ' -f 1)
		mkdir $resultsdir
		./lda est $approx $k settings.txt $inputfile random $resultsdir
	done

for path in $dir500all
	do
		IFS='/' read -a parts <<< "$path"
		date="${parts[7]}"
		echo $date
		resultsdir="../../../data/unsupervised-LDA/monthly/top500/$date"
		inputdir="$dir500$date"
		inputfile="$inputdir$matrix"
		approx=$(cat $inputdir$alpha)
		infofile="$inputdir$info"
		k=$(grep 'label-key.txt' $infofile | cut -d ' ' -f 1)
		mkdir $resultsdir
		./lda est $approx $k settings.txt $inputfile random $resultsdir
	done


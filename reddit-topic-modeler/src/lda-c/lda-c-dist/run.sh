# LDA-C pipeline

# Usage: bash run.sh <username> <password> <layernum> <links> <freq_thresh> <k> <seed> <alpha>
	# Username and password are used to access the mongo database
	# Use links=links to use links 
	# Use links=none to just use submissions/comments
	# Use layernum=-1 to use all comments. 
	# Use freq_thresh=5 to remove words occurring <= 5 times 
	# Use k=100 to specify that you want to end up with 100 topics
	# Use seed=random to randomly initialize the topics in LDA
	# Use seed=seeded to initialize the topics in LDA with a seed (?)
	# Alpha is optional and represents the prior belief in the per document topic distribution
		# this is computed for you heuristically, but will be overrided if you specify it 

# Get parameters
user=$1
passwd=$2
layer=$3
freq=$5
k=$6
seed=$7

# If user specified links, use link content
get_links="false"
if [ $4 = "links" ]; then
	get_links="true"
fi


#this is run in: /users/mciot/reddit-topic-modeler/src/lda-c/lda-c-dist
#data is in: /users/mciot/reddit-topic-modeler/data/supervised-lda/

path="../../../data/unsupervised-LDA/"
dir="lda-c-"
info="/info.txt"
dump="/dump.txt"
unique="/unique.txt"
matrix="/matrix.txt"
alpha="alpha.txt"

echo "WARNING: dump stuff is commented out"

# Each run will have its own directory
#identifier=$(date +"%m-%d-%y-%H_%M")
identifier="10-07-14-01_19"
newdir="$path$dir$identifier"
results="/results/"

infof="$newdir$info"
dumpf="$newdir$dump"
uniquef="$newdir$unique"
matrixf="$newdir$matrix"
resultsd="$newdir$results"
alphaf="$path$alpha"

# Make a new directory where everything will go 
#mkdir $newdir

echo "storing everything in " $newdir

# Store information about this iteration 
echo "Date ran: $(date)" > $infof
echo "Layer number: $3" >> $infof
echo "Links used: $get_links" >> $infof
echo "Number of topics to infer: $k" >> $infof
echo "Seeded or random: $seed" >> $infof

#echo "dumping data to text file"

## Dump data to text file
#python ../../dump.py --host blacksun.cs.mcgill.ca --port 31050 --username $user --password $passwd --db reddit_topics --layer $layer --links $get_links > $dumpf

# Update user/info file 
echo "Number of documents:"
wc -l $dumpf

echo "" >> $infof
echo "Number of documents:" >> $infof
wc -l $dumpf >> $infof

echo "creating sorted unique word list"

## Get unique words 
cat $dumpf | tr " " "\n" | sort | uniq -c > $uniquef

# Update user/info file
echo "Number of unique words:"
wc -l $uniquef

echo "" >> $infof
echo "Number of unique words:" >> $infof
wc -l $uniquef >> $infof

echo "formatting data for LDA"

## Create frequency matrix 
python ../../format-lda-c.py $dumpf $uniquef $freq > $matrixf

# Frequency will have saved approximation of alpha to a file 
# called "alpha.txt" in /data/unsupervised-lda. However, user-
# specified alpha takes precedence. So first check if user 
# specified alpha (arg position $8)
if [ -z $8 ]; then
	# Didn't specify it, fetch in file 
	alpha=$(cat $alphaf)
else
	alpha=$8
fi

echo "using alpha: $alpha"

echo "" >> $infof
echo "Alpha: $alpha" >> $infof

# Move alpha file to current folder 
mv $alphaf $newdir

echo "running LDA"

# First recompile (sometimes run into error from scp'ing)
make clean
make

# Run LDA-C
./lda est $alpha $k settings.txt $matrixf $seed $resultsd

echo "Date finished: $(date)" >> $infof

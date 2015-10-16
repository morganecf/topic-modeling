### FORMAT GENDER TWEETS FOR HDP 
python format-tweets.py --tweets ../data/twitter/crowdflower/tweets_gender_temporal.csv --ids ../data/twitter/crowdflower/ids_gender_temporal.csv --words ../data/formatted_data/monthly/top125/2014-03/words.txt --dir ../data/formatted_data/twitter/temporal/2014-03
echo 'done 03'
python format-tweets.py --tweets ../data/twitter/crowdflower/tweets_gender_temporal.csv --ids ../data/twitter/crowdflower/ids_gender_temporal.csv --words ../data/formatted_data/monthly/top125/2014-06/words.txt --dir ../data/formatted_data/twitter/temporal/2014-06
echo 'done 06'
python format-tweets.py --tweets ../data/twitter/crowdflower/tweets_gender_temporal.csv --ids ../data/twitter/crowdflower/ids_gender_temporal.csv --words ../data/formatted_data/monthly/top125/2014-08/words.txt --dir ../data/formatted_data/twitter/temporal/2014-08
echo 'done 09'
python format-tweets.py --tweets ../data/twitter/crowdflower/tweets_gender_temporal.csv --ids ../data/twitter/crowdflower/ids_gender_temporal.csv --words ../data/formatted_data/monthly/top125/2014-09/words.txt --dir ../data/formatted_data/twitter/temporal/2014-09
echo 'done 08'
python format-tweets.py --tweets ../data/twitter/crowdflower/tweets_gender_temporal.csv --ids ../data/twitter/crowdflower/ids_gender_temporal.csv --words ../data/formatted_data/monthly/top125/2014-11/words.txt --dir ../data/formatted_data/twitter/temporal/2014-11
echo 'done 11'

# Bash script to iterate through months from 2010-2014 
# and create data dumps for each of these months. 

for i in `seq 0 4`;
	do
		year=201$i

		# January to September 
		for j in `seq 1 9`;
			do
				month=0$j
				date="$year-$month"

				echo $date

				# top 125 subreddits 
				ext125="_top125.txt"
				fname125="dump_$date$ext125"
				dirname125="../data/data_dumps/$fname125"
				python dump.py --username mciot --password r3dd1tmorgane --subreddits ../data/topics/top125.txt --date $date > $dirname125
				echo $dirname125

				# top 500 subreddits 
				ext500="_top500.txt"
				fname500="dump_$date$ext500"
				dirname500="../data/data_dumps/$fname500"
				python dump.py --username mciot --password r3dd1tmorgane --subreddits ../data/topics/top500.txt --date $date > $dirname500
				echo $dirname500

			done

		# October to December 
		for j in `seq 10 12`;
		    do
		        month=$j
		        date="$year-$month"

		        echo $date
		       
		       	# top 125 subreddits 
				ext125="_top125.txt"
				fname125="dump_$date$ext125"
				dirname125="../data/data_dumps/$fname125"
				python dump.py --username mciot --password r3dd1tmorgane --subreddits ../data/topics/top125.txt --date $date > $dirname125
				echo $dirname125
				
				# top 500 subreddits 
				ext500="_top500.txt"
				fname500="dump_$date$ext500"
				dirname500="../data/data_dumps/$fname500"
				python dump.py --username mciot --password r3dd1tmorgane --subreddits ../data/topics/top500.txt --date $date > $dirname500
				echo $dirname500
		    done    
	done

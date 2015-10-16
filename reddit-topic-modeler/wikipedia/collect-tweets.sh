if [ $1 = "1" ]; then
	echo '#1DNews'
	twittersearch -k \#1DNews -o morgane-tweets -f 1DNews.json
	python notify.py morganeciot@gmail.com 1dnews carpathia

	echo '#baristaproblems'
	twittersearch -k \#baristaproblems -o morgane-tweets -f baristaproblems.json
	python notify.py morganeciot@gmail.com baristaproblems carpathia

	echo '#deflategate'
	twittersearch -k \#deflategate -o morgane-tweets -f deflategate.json
	python notify.py morganeciot@gmail.com deflategate carpathia

	echo '#fml'
	twittersearch -k \#fml -o morgane-tweets -f fml.json
	python notify.py morganeciot@gmail.com fml carpathia

	echo '#fossilfriday'
	twittersearch -k \#fossilfriday -o morgane-tweets -f fossilfriday.json
	python notify.py morganeciot@gmail.com fossilfriday carpathia

	echo '#gohard'
	twittersearch -k \#gohard -o morgane-tweets -f gohard.json
	python notify.py morganeciot@gmail.com gohard carpathia
fi

if [ $1 = "2" ]; then
	echo '#got'
	twittersearch -k \#got -o morgane-tweets -f got.json
	python notify.py morganeciot@gmail.com got carpathia

	echo '#mlp'
	twittersearch -k \#mlp -o morgane-tweets -f mlp.json
	python notify.py morganeciot@gmail.com mlp carpathia

	echo '#mothersdayclassic'
	twittersearch -k \#mothersdayclassic -o morgane-tweets -f mothersdayclassic.json
	python notify.py morganeciot@gmail.com mothersdayclassic carpathia

	echo '#nola'
	twittersearch -k \#nola -o morgane-tweets -f nola.json
	python notify.py morganeciot@gmail.com nola carpathia

	echo '#nowplaying'
	twittersearch -k \#nowplaying -o morgane-tweets -f nowplaying.json
	python notify.py morganeciot@gmail.com nowplaying carpathia

	echo '#p2'
	twittersearch -k \#p2 -o morgane-tweets -f p2.json
	python notify.py morganeciot@gmail.com p2 carpathia

	echo '#passportready'
	twittersearch -k \#passportready -o morgane-tweets -f passportready.json
	python notify.py morganeciot@gmail.com passportready carpathia
fi

if [ $1 = "3" ]; then
	echo '#purplearmy'
	twittersearch -k \#purplearmy -o morgane-tweets -f purplearmy.json
	python notify.py morganeciot@gmail.com purplearmy carpathia

	echo '#royalbaby'
	twittersearch -k \#royalbaby -o morgane-tweets -f royalbaby.json
	python notify.py morganeciot@gmail.com royalbaby carpathia

	echo '#sickburnahunk'
	twittersearch -k \#sickburnahunk -o morgane-tweets -f sickburnahunk.json
	python notify.py morganeciot@gmail.com sickburnahunk carpathia

	echo '#VEDay70'
	twittersearch -k \#VEDay70 -o morgane-tweets -f veday70.json
	python notify.py morganeciot@gmail.com veday70 carpathia

	echo '#virus'
	twittersearch -k \#virus -o morgane-tweets -f virus.json
	python notify.py morganeciot@gmail.com virus carpathia

	echo '#wexmondays'
	twittersearch -k \#wexmondays -o morgane-tweets -f wexmondays.json
	python notify.py morganeciot@gmail.com wexmondays carpathia

	echo '#yyc'
	twittersearch -k \#yyc -o morgane-tweets -f yyc.json
	python notify.py morganeciot@gmail.com yyc carpathia
fi
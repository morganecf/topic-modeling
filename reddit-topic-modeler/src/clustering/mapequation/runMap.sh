#./Infomap -z --input-format link-list --map ../../../data/clustering/dec5_full/integer/component0.wpairs ../../../data/clustering/map/dec5_full/regular
./Infomap -z --input-format link-list --map ../../../data/clustering/dec5_full/integer/component1.wpairs ../../../data/clustering/map/dec5_full/regular
./Infomap -z --input-format link-list --map ../../../data/clustering/dec5_full/integer/component2.wpairs ../../../data/clustering/map/dec5_full/regular

./Infomap -z --input-format link-list --map ../../../data/clustering/dec5_full/decimal-norm/component0.wpairs ../../../data/clustering/map/dec5_full/normalized
./Infomap -z --input-format link-list --map ../../../data/clustering/dec5_full/decimal-norm/component1.wpairs ../../../data/clustering/map/dec5_full/normalized
./Infomap -z --input-format link-list --map ../../../data/clustering/dec5_full/decimal-norm/component2.wpairs ../../../data/clustering/map/dec5_full/normalized

./Infomap -z --input-format link-list --map ../../../data/clustering/dec5_full/decimal-log/component0.wpairs ../../../data/clustering/map/dec5_full/lognormalized
./Infomap -z --input-format link-list --map ../../../data/clustering/dec5_full/decimal-log/component1.wpairs ../../../data/clustering/map/dec5_full/lognormalized
./Infomap -z --input-format link-list --map ../../../data/clustering/dec5_full/decimal-log/component2.wpairs ../../../data/clustering/map/dec5_full/lognormalized

python ../../notify.py morganeciot@gmail.com 'done running info map on all versions' enterprise


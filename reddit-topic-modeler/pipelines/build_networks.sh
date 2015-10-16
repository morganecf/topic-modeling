python networks.py --password r3dd1tmorgane --topics ../data/topics/top125.txt --networks xpost --limit 100 --name top125_100

### top1000 -- epiphyte

# Build content, subdomain, and xpost networks - 1000 limit 100
python networks.py --password r3dd1tmorgane --topics ../data/topics/top1000.txt --networks content --limit 100 --name top1000_100
python notify.py morganeciot@gmail.com 'building content network with top1000 limit 100' epiphyte
python networks.py --password r3dd1tmorgane --topics ../data/topics/top1000.txt --networks subdomain --limit 100 --name top1000_100
python notify.py morganeciot@gmail.com 'building subdomain network with top1000 limit 100' epiphyte
python networks.py --password r3dd1tmorgane --topics ../data/topics/top1000.txt --networks xpost --limit 100 --name top1000_100
python notify.py morganeciot@gmail.com 'building xpost network with top1000 limit 100' epiphyte

# Build content, subdomain, and xpost networks - 1000 limit 1000
python networks.py --password r3dd1tmorgane --topics ../data/topics/top1000.txt --networks content --limit 1000 --name top1000_1000
python notify.py morganeciot@gmail.com 'building content network with top1000 limit 1000' epiphyte
python networks.py --password r3dd1tmorgane --topics ../data/topics/top1000.txt --networks subdomain --limit 1000 --name top1000_1000
python notify.py morganeciot@gmail.com 'building subdomain network with top1000 limit 1000' epiphyte
python networks.py --password r3dd1tmorgane --topics ../data/topics/top1000.txt --networks xpost --limit 1000 --name top1000_1000
python notify.py morganeciot@gmail.com 'building xpost network with top1000 limit 1000' epiphyte

### top5000 -- epiphyte

# Build content, subdomain, and xpost networks - 5000 limit 100
python networks.py --password r3dd1tmorgane --topics ../data/topics/top5000.txt --networks content --limit 100 --name top5000_100
python notify.py morganeciot@gmail.com 'building content network with top5000 limit 100' epiphyte
python networks.py --password r3dd1tmorgane --topics ../data/topics/top5000.txt --networks subdomain --limit 100 --name top5000_100
python notify.py morganeciot@gmail.com 'building subdomain network with top5000 limit 100' epiphyte
python networks.py --password r3dd1tmorgane --topics ../data/topics/top5000.txt --networks xpost --limit 100 --name top5000_100
python notify.py morganeciot@gmail.com 'building xpost network with top5000 limit 100' epiphyte

# Build content, subdomain, and xpost networks - 5000 limit 1000
python networks.py --password r3dd1tmorgane --topics ../data/topics/top5000.txt --networks content --limit 1000 --name top5000_1000
python notify.py morganeciot@gmail.com 'building content network with top5000 limit 1000' epiphyte
python networks.py --password r3dd1tmorgane --topics ../data/topics/top5000.txt --networks subdomain --limit 1000 --name top5000_1000
python notify.py morganeciot@gmail.com 'building subdomain network with top5000 limit 1000' epiphyte
python networks.py --password r3dd1tmorgane --topics ../data/topics/top5000.txt --networks xpost --limit 1000 --name top5000_1000
python notify.py morganeciot@gmail.com 'building xpost network with top5000 limit 1000' epiphyte

# Build content, subdomain, and xpost networks - 5000 limit None
python networks.py --password r3dd1tmorgane --topics ../data/topics/top5000.txt --networks content --name top5000_None
python notify.py morganeciot@gmail.com 'building content network with top5000 limit None' epiphyte
python networks.py --password r3dd1tmorgane --topics ../data/topics/top5000.txt --networks subdomain --name top5000_None
python notify.py morganeciot@gmail.com 'building subdomain network with top5000 limit None' epiphyte
python networks.py --password r3dd1tmorgane --topics ../data/topics/top5000.txt --networks xpost --name top5000_None
python notify.py morganeciot@gmail.com 'building xpost network with top5000 limit None' epiphyte

### ALL - enterprise
python networks.py --password r3dd1tmorgane --networks content --name all
python notify.py morganeciot@gmail.com 'building content network with all subreddits' enterprise
python networks.py --password r3dd1tmorgane --networks subdomain --name all
python notify.py morganeciot@gmail.com 'building subdomain network with all subreddits' enterprise
python networks.py --password r3dd1tmorgane --networks xpost --name all
python notify.py morganeciot@gmail.com 'building xpost network with all subreddits' enterprise

## USER NETWORKS

python networks.py --password r3dd1tmorgane --networks user --limit 1000 --name top1000
python notify.py morganeciot@gmail.com 'building user network with limit 1000' enterprise
python networks.py --password r3dd1tmorgane --networks user --limit 5000 --name top5000
python notify.py morganeciot@gmail.com 'building user network with limit 5000' enterprise
python networks.py --password r3dd1tmorgane --networks user --name all
python notify.py morganeciot@gmail.com 'building user network with limit None' enterprise




#python merge_user_networks.py top1000_submissions.txt local-run/submission_weighted.tsv submission_weighted.tsv
#python merge_user_networks.py top1000_submissions.txt local-run/submission_unweighted.tsv submission_unweighted.tsv
#python ../../../src/notify.py morganeciot@gmail.com 'done merging user submission networks' vps 

#python merge_user_networks.py top1000_comments.txt local-run/comment_weighted.tsv comment_weighted.tsv 
#python merge_user_networks.py top1000_comments.txt local-run/comment_unweighted.tsv comment_unweighted.tsv
#python ../../../src/notify.py morganeciot@gmail.com 'done merging user comment networks' vps 

#python merge_user_networks.py top1000_all.txt local-run/user_weighted.tsv user_weighted.tsv 
python merge_user_networks.py top1000_all.txt local-run/user_unweighted.tsv user_unweighted.tsv
python ../../../src/notify.py morganeciot@gmail.com 'done merging user full netowrks' vps 


cat a ../dict.v0/$1 |LC_ALL=C sort |LC_ALL=C uniq >$1
wc -l ../dict.v0/$1 $1

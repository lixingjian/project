
i=1
for url in `cat url.pic`
do
    wget $url -O /data/image/img_src/pages/$i
    echo $i" "$url >>/data/image/img_src/urllist
    i=`expr $i + 1`
done    

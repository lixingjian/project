#!/bin/sh

dir="/home/work/tools"
mkdir -p $dir

#install vim
if [ ! -f $dir/vim-8.0.tar.bz2 ]; then
	wget ftp://ftp.vim.org/pub/vim/unix/vim-8.0.tar.bz2 -P $dir
fi
cd $dir
tar -jxvf vim-8.0.tar.bz2
cd vim80
./configure --enable-multibyte
make; make install

#安装python3.5
if [ "$1" == "python3" ]; then
yum groupinstall -y Development tools
yum install -y zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel
wget https://www.python.org/ftp/python/3.5.2/Python-3.5.2.tar.xz -P $dir
cd $dir
xz -d Python-3.5.2.tar.xz
tar xvf Python-3.5.2.tar
cd Python-3.5.2
./configure --prefix=/usr/local
make && make install && echo OK
cd /usr/local/bin; ln -s python3.5 python

#安装setuptools和pip3
wget https://bootstrap.pypa.io/ez_setup.py -P $dir
cd $dir
python3.5 ez_setup.py
easy_install-3.5 pip
pip3.5 install --upgrade pip

#install gcc4.9
if [ "$1" == "gcc4.9" ]; then
wget http://ftp.tsukuba.wide.ad.jp/software/gcc/releases/gcc-4.9.3/gcc-4.9.3.tar.bz2 -P $dir
cd $dir
tar xjvf gcc-4.9.3.tar.bz2
cd gcc-4.9.3
./contrib/download_prerequisites
cd ..
mkdir gcc-4.9.3-build-temp
cd gcc-4.9.3-build-temp
../gcc-4.9.3/configure --enable-checking=release --enable-languages=c,c++ --disable-multilib
make -j4
make install

#架构算法库
pip3 install leveldb
#策略算法库
pip3 install ahocorasick, pybloom -i https://pypi.tuna.tsinghua.edu.cn/simple
#网页解析库
pip3 install request, beautifulsoup4, lxml -i https://pypi.tuna.tsinghua.edu.cn/simple
#机器学习库
pip3 install numpy, matplotlib, scikit-learn -i https://pypi.tuna.tsinghua.edu.cn/simple
#自然语言处理库
pip3 install pyltp -i https://pypi.tuna.tsinghua.edu.cn/simple

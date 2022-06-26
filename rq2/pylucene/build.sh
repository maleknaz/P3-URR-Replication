#/bin/bash -eu
export JAVA_HOME=$(readlink -f $PREFIX/bin/java | sed "s:/bin/java::")
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$PREFIX/lib:$PREFIX/jre/lib:$PREFIX/jre/lib/amd64:$PREFIX/jre/lib/amd64/server
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$SP_DIR

echo 'Making'
make
#make test
echo 'Make install'
make install

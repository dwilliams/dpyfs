set file=chunk8k.bin
set md5=420c9ca705ba296c940c95bdc892a58c
set sha1=da58380049143013cd6a8508c8c028c4b11545ab

python putchunk.py --host localhost --port 8081 %file%
python getchunk.py --host localhost --port 8081 %md5% %sha1%
python deletechunk.py --host localhost --port 8081 %md5% %sha1%

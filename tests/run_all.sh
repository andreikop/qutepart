#bin/sh

for test in `ls *.py`; do
    echo Running $test
    ./$test;
done
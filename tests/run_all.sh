#bin/sh

for test in `find -name '*.py'`; do
    echo Running $test
    ./$test;
done

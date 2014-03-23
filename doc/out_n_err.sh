#!/bin/bash

for i in 1 2 3 4 5; do
    echo ok > /dev/stdout
    echo nok > /dev/stderr
    sleep .2
done

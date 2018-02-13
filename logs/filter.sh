#!/bin/bash

grep -i 'error' testset_ucla.log | egrep -o '[0-9a-z]{15}|test-[0-9]+.jpg' > test_fails.txt
grep -i 'error' trainset_ucla.log | egrep -o '[0-9a-z]{15}|train-[0-9]+.jpg' > train_fails.txt

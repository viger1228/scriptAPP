#!/bin/bash
# auth: walker
# date: 2019-02-20

if [ $1'x' != 'x' ]; then
  tag=$1
else
  tag=origin
fi

echo -e "\033[1;31m-----------------------$n----------------------------\033[0m"
git pull $tag master
git log -n 3
echo

echo -e "\033[1;31m-----------------------$n----------------------------\033[0m"
git log -n 3 --oneline
echo

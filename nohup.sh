#!/bin/bash

now=`pwd`
dir=`dirname $0`

cd $dir
path=`echo \`pwd\` | awk -F '/' '{print $NF}'`

usage(){
  echo -e '\033[31m'
  echo -e 'Usage:'
  echo -e ' nohup.sh [start|stop|restart]'
  echo -e '\033[0m'
}

start(){
  nohup python3 -u run.py $path >> logs/nohup.out 2>&1 &
  sleep 1
  tail logs/nohup.out
  state
}

stop(){
  kill -9 `ps aux | grep python | grep $path | grep -v grep | awk '{print $2}'`
}

state(){
  ps aux | grep python | grep $path | grep -v grep
}

if [ $# != 1 ]; then
  usage
elif [ $1 == 'start' ]; then
  start
elif [ $1 == 'stop' ]; then
  stop
elif [ $1 == 'state' ]; then
  state
elif [ $1 == 'restart' ]; then
  stop
  sleep 1
  start
else
  usage
fi

cd $now

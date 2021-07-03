#!/bin/bash

if [[ -n ${1} ]]; then
  result=$(screen -p 0 -S minecraft -L -X eval "stuff \"${1}\"\015")
  if [[ -z $result ]]; then
    sleep 5
    output=$(tail /home/alex/mineserv/screenlog.0)
    echo "$output"  
  else
    echo "Майнкрафт не запущен"
  fi
fi
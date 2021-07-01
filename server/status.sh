#!/bin/bash

# screen -L -dmS minecraft java -Xmx2G -Xms1024M -jar minecraft_server.1.16.5.jar nogui

ip=$(curl -s ifconfig.me/ip)
result=$(screen -p 0 -S minecraft -L -X eval 'stuff "list"\015')
sleep 5
output=$(tail /home/alex/mineserv/screenlog.0)
echo "$result"
echo "$ip"
echo "$output"
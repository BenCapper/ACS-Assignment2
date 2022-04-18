#!/bin/bash
INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
USEDMEMORY=$(free -m | awk 'NR==2{printf "%.2f\t", $3*100/$2 }')
TCP_CONN=$(netstat -an | wc -l)
TCP_CONN_PORT_80=$(netstat -an | grep 80 | wc -l)
TCP_CONN_PORT_3000=$(netstat -an | grep 3000 | wc -l)
IO_WAIT=$(iostat | awk 'NR==4 {print $4}')
CPU_USAGE=$(top -bn1 | grep load | awk '{printf "CPU Usage: %.2f\n", $(NF-2)}')
PROCCESSCOUNT=$(ps -e | wc -l)
overload=0
if [[ $IO_WAIT > 70 && $USEDMEMORY > 80 ]]
then
 overload=1
fi

aws cloudwatch put-metric-data --metric-name danger --dimensions Instance=$INSTANCE_ID --namespace "Custom" --value $overload
aws cloudwatch put-metric-data --metric-name memory-usage --dimensions Instance=$INSTANCE_ID --namespace "Custom" --value $USEDMEMORY
aws cloudwatch put-metric-data --metric-name Tcp_connections --dimensions Instance=$INSTANCE_ID --namespace "Custom" --value $TCP_CONN
aws cloudwatch put-metric-data --metric-name TCP_connection_on_port_80 --dimensions Instance=$INSTANCE_ID --namespace "Custom" --value $TCP_CONN_PORT_80
aws cloudwatch put-metric-data --metric-name TCP_connection_on_port_3000 --dimensions Instance=$INSTANCE_ID --namespace "Custom" --value $TCP_CONN_PORT_3000
aws cloudwatch put-metric-data --metric-name IO_WAIT --dimensions Instance=$INSTANCE_ID --namespace "Custom" --value $IO_WAIT
aws cloudwatch put-metric-data --metric-name CPU_USAGE --dimensions Instance=$INSTANCE_ID --namespace "Custom" --value $CPU_USAGE
aws cloudwatch put-metric-data --metric-name PROCCESSCOUNT --dimensions Instance=$INSTANCE_ID --namespace "Custom" --value $PROCCESSCOUNT


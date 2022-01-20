#!/bin/bash

# Script to close a given number of TCP ports, starting at the given port number

start_port = $1
range = $2

port = $start_port

while [$port -lt ($start_port + $range)]
do
    echo 'Closing port ${port}'
    fuser -k ${port}/tcp 
    
    $port++

echo 'Completed killing of ports'


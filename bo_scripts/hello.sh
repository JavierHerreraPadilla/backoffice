#!/bin/bash

echo "El script está a punto de pausarse durante 5 segundos..."
sleep 5
echo "El escript es $0"
for arg in "$@"
do
    echo "argumento: $arg"
done
echo "¡La pausa ha terminado!"
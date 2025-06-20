#!/bin/bash

# Affiche les arguments s'ils existent (jusqu'à 3)

if [ $# -ge 1 ]; then
  echo "Argument 1 : $1"
fi

if [ $# -ge 2 ]; then
  echo "Argument 2 : $2"
fi

if [ $# -ge 3 ]; then
  echo "Argument 3 : $3"
fi

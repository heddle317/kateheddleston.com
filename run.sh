#!/bin/bash

# find our way to the "app" dir where run.sh lives so we can set up paths
pushd `dirname "$0"` &> /dev/null

export ENVIRONMENT='dev'

source keys.sh

# get ourselves back to the beginning so that the script path isn't relative to app, but relative to where we ran the command
popd &> /dev/null

command=$1
shift # rather than trying to predict the total # of arguments, lop off the command argument and invoke the rest of the arguments
python $command "$@"

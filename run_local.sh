#!/bin/bash

source ./keys.sh
supervisord -c ./files/supervisor_local.conf

#!/bin/bash
set -ev

# Synthesis build
if [ "${SYNTHESIS}" = "true" ]; then
    wget https://www.dropbox.com/s/xvum1md2deppgre/quartus_14.0.tar.gz?dl=0
    mv quartus* quartus_14.0.tar.gz
    tar -zxf quartus_14.0.tar.gz
    cd syn && PATH=$PWD/../altera/14.0/quartus/bin:$PATH make &
    pid=$!

    # Often no output so have to force output
    while kill -0 $pid >/dev/null 2>&1; do sleep 5m; echo Build still running, honest; done
fi


# Simulation build
if [ "${SIMULATION}" = "true" ]; then
    git clone https://github.com/potentialventures/cocotb.git
    export COCOTB=$PWD/cocotb
    cd tb && make
fi
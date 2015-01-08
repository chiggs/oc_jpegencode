oc_jpegencode
=============

![Build Status](https://api.travis-ci.org/chiggs/oc_jpegencode.png?branch=master)

Fork of OpenCores jpegencode with Cocotb testbench. Uses the Python image library to send files through the encoder.

Original project page on Opencores: http://opencores.org/project,jpegencode

To run the testbench:

    # Pre-requisites
    sudo yum install -y python-imaging
    sudo yum install -y iverilog
    
    # Checkout git repositories
    git clone https://github.com/potentialventures/cocotb.git
    git clone https://github.com/chiggs/oc_jpegencode.git
    
    # Environment
    export COCOTB=`pwd`/cocotb
    
    # Run the tests...
    cd oc_jpegencode/tb
    make


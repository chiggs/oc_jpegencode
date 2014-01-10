oc_jpegencode
=============

Fork of OpenCores jpegencode with Cocotb testbench. Uses the Python image library to send files through the encoder.

Original project page on Opencores: http://opencores.org/project,jpegencode

To run the testbench:

    # Pre-requisites
    sudo yum install -y python-imaging
    git clone https://github.com/potentialventures/cocotb.git
    git clone https://github.com/chiggs/oc_jpegencode.git
    
    export COCOTB=`pwd`/cocotb

    cd oc_jpegencode/tb
    make


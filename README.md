oc_jpegencode
=============

[![Build Status](https://api.travis-ci.org/chiggs/oc_jpegencode.png?branch=master)](https://travis-ci.org/chiggs/oc_jpegencode)
[![Coverage Status](https://img.shields.io/coveralls/chiggs/oc_jpegencode.svg)](https://coveralls.io/r/chiggs/oc_jpegencode)
[![Documentation Status](https://readthedocs.org/projects/opencores-jpegencoder/badge/?version=latest)](https://readthedocs.org/projects/opencores-jpegencoder/?badge=latest)

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

[Documentation](https://readthedocs.org/projects/opencores-jpegencoder/badge/?version=latest) hosted on [ReadTheDocs](https://readthedocs.org/).

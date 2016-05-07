bca-redtools: BitCurator Access Redaction Tools
-----------------------------------------------

Disk image and bitstream redaction tools for the BitCurator Access project.

This repository currently includes the following libraries:

 * libredact: A standalone rewrite of the iredact.py tool

# Building and installing libredact

Clone out this repository:

 * git clone https://github.com/bitcurator/bca-webtools

Navigate to the libredact directory:

 * cd bca-webtools/libredact

Build and install with Python 3 setuptools:

 * python3 setup.py build
 * sudo python3 setup.py install

# Running

The redaction tool can be run from the command line as follows:

 * python3 iredact.py /path/to/iredact-config.txt

A sample iredact-config.txt file is included. You should modify it as needed.


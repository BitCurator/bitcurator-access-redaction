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

(Future: Should be updated for virtualenv)

# Running

The redaction tool can be run from the command line as follows:

 * iredact.py /path/to/iredact-config.txt

A sample iredact-config.txt file is included. You should modify it as needed.

(Future: improve config procedure)

# Dependencies

The redaction tool requires fiwalk, which is distributed with The Sleuth Kit (https://github.com/sleuthkit/sleuthkit).

# Licenses

Project documentation and other non-software products of the BitCurator Access team and contracted partners are subject to the the Creative Commons Attribution 4.0 Unported license (CC BY 4.0).

Unless otherwise indicated, software objects in this repository are distributed under the terms of the GNU General Public License, Version 3. See the text file "LICENSE" for further details about the terms of this license.

bca-redtools: BitCurator Access Redaction Tools
-----------------------------------------------

Disk image and bitstream redaction tools for the BitCurator Access project.

This repository currently includes the following libraries:

 * libredact: A Python redaction library and standalone raw disk image redaction tool. Loosely based on the iredact.py tool.

# Building and installing libredact

Clone out this repository:

 * git clone https://github.com/bitcurator/bca-redtools

Navigate to the libredact directory:

 * cd bca-webtools/libredact

Build and install with Python 3 setuptools:

 * python3 setup.py build
 * sudo python3 setup.py install

Note: Python 3 is required. Do not attempt to build or install with Python 2.x.

(Future: Should be updated for virtualenv and pip package creation)

# Running

The redaction tool can be run from the command line as follows:

 * sredact.py /path/to/iredact-config.txt

A sample sredact-config.txt file is included. You should modify it as needed.

(Future: improve config procedure)

# Dependencies

The redaction tool requires fiwalk, which is distributed with The Sleuth Kit (https://github.com/sleuthkit/sleuthkit).

# Licenses

Project documentation and other non-software products of the BitCurator Access team and contracted partners are subject to the the Creative Commons Attribution 4.0 Unported license (CC BY 4.0).

Unless otherwise indicated, software objects in this repository are distributed under the terms of the GNU General Public License, Version 3. See the text file "LICENSE" for further details about the terms of this license.

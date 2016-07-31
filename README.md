bca-redtools: BitCurator Access Redaction Tools
-----------------------------------------------

Disk image and bitstream redaction tools for the BitCurator Access project.

This repository currently includes the following libraries:

* libredact: A Python redaction library and standalone raw disk image redaction tool. Loosely based on the iredact.py tool.

# Prerequisites
* Install PIP:
```shell
$ sudo apt-get install python-pip
```

# Building and installing libredact
* Clone this repository:
```shell
$ git clone https://github.com/bitcurator/bca-redtools
```
* Enter the repository directory:
```shell
$ cd bca-redtools
```
* Navigate to the libredact directory:
```shell
$ cd libredact
```
* Build and install with PIP:
```shell
$ pip install -e .
```
* PIP will create a executable script here: /home/youruser/.local/bin/sredact

* If sredact is not on your PATH, you can add it temporarily:
```shell
$ PATH=$PATH:/home/`whoami`/.local/bin
```

# Running

The redaction tool can be run from the command line as follows:
```shell
    $ sredact -h
```
Instructions for creating a configuration file are also available on the command line:
```shell
    $ sredact -H
```
(Future: improve config instructions)

# Using the Python module

All of the same functions as the command line are also available in the
libredact module. Below is a short example Python script that uses the
Redactor API to process a disk image.



# Dependencies

The redaction tool requires fiwalk, which is distributed with The Sleuth Kit (https://github.com/sleuthkit/sleuthkit).

# Licenses

Project documentation and other non-software products of the BitCurator Access team and contracted partners are subject to the the Creative Commons Attribution 4.0 Unported license (CC BY 4.0).

Unless otherwise indicated, software objects in this repository are distributed under the terms of the GNU General Public License, Version 3. See the text file "LICENSE" for further details about the terms of this license.

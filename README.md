bca-redtools: BitCurator Access Redaction Tools
-----------------------------------------------

Disk image redaction tools developed for the BitCurator Access project.

This repository currently includes the following libraries:

* libredact: A Python redaction library and standalone raw disk image redaction tool. Loosely based on the iredact.py tool.

# Prerequisites

Note! If you're using the BitCurator environment version 1.7.28 or newer, these dependencies and environmental modifications are already installed. You can skip ahead to "Building and installing libredact".

  * Install pip:
```shell
$ sudo apt-get install python-pip
```
  * The redaction tool reads file system metadata from DFXML files produced by fiwalk. Fiwalk can be installed by downloading and building the latest release of The Sleuth Kit from https://github.com/sleuthkit/sleuthkit.

  * For redaction of sequences based on regular expressions, you need the Lightgrep library, see instructions here:
https://github.com/strozfriedberg/liblightgrep/blob/master/BUILD.md
Note: Lightgrep builds from source and has further dependencies in turn, including GNU Bison and Boost. You must follow the instructions above.
  * With some more recent operating systems you will need to tell the lightgrep configure script where to find Boost, like this:
```shell
$ ./configure --with-boost-libdir=/usr/lib/x86_64-linux-gnu
```
  * The lightgrep library install into /usr/local/lib, so this directory will need to be on the system's LD_LIBRARY_PATH in order for redact-cli to find it. Your bca-redtools environment must include the LD_LIBRARY_PATH setting:
```shell
$ export LD_LIBRARY_PATH=/usr/local/lib
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
* Build and install with pip. Note! In the BitCurator Environment, both Python 2.7 and Python 3.5 are installed, and the "pip" command links to Python 3.5 version of pip. You must use "pip2" to install with Python 2.7 (currently required due to a dependency on pylightgrep).
```shell
$ pip2 install -e .
```
* Pip will create a executable script here: /home/youruser/.local/bin/redact-cli

* If redact-cli is not on your PATH, you can add it temporarily:
```shell
$ PATH=$PATH:/home/`whoami`/.local/bin
```

# Running (command line interface)

The redaction tool can be run from the command line as follows:
```shell
    $ redact-cli -h
```
Instructions for creating a configuration file are also available on the command line:
```shell
    $ redact-cli -H
```
# Running (command line interface, redacting using annotated bulk_extractor reports)

# Running (graphical interface)

The redation tool includes a GUI that can be used to create and edit configuration files, and execute redaction actions. When using the GUI, all options (including input and output files) must be specified within the configuration file.

The GUI can be started by running the following command in a terminal:
```shell
    $ redact-gui
```

# Using the Python module

All of the same functions as the command line are also available in the
libredact module. Below is a short example Python script that uses the
Redactor API to process a disk image. (Coming soon...)

# Dependencies

  * The lightgrep.py Python API file is included with this repository. Should you need to update it to match future iterations of liblightgrep, the file can be downloaded and placed into the bca-redtools/libredact folder (alongside fiwalk.py and dfxml.py) using these commands:
```shell
$ cd bca-redtools/libredact; wget https://raw.githubusercontent.com/strozfriedberg/liblightgrep/master/pylightgrep/lightgrep.py
```

# Licenses

Project documentation and other non-software products of the BitCurator Access team and contracted partners are subject to the the Creative Commons Attribution 4.0 Unported license (CC BY 4.0).

Unless otherwise indicated, software objects in this repository are distributed under the terms of the GNU General Public License, Version 3. See the text file "LICENSE" for further details about the terms of this license.

The lightgrep.py Python interface to liblightgrep is included under the terms of the license for liblightgrep, namely the GNU General Public License, Version 3. 

(See https://github.com/strozfriedberg/liblightgrep/blob/master/COPYING for original liblightgrep license terms).

![Logo](https://github.com/BitCurator/bitcurator.github.io/blob/master/logos/BitCurator-Basic-400px.png)

# BitCurator Access Redaction Tools (bitcurator-access-redaction)

[![GitHub issues](https://img.shields.io/github/issues/bitcurator/bitcurator-access-redaction.svg)](https://github.com/bitcurator/bitcurator-access-redaction/issues)
[![GitHub forks](https://img.shields.io/github/forks/bitcurator/bitcurator-access-redaction.svg)](https://github.com/bitcurator/bitcurator-access-redaction/network)
[![Travis](https://img.shields.io/travis/BitCurator/bitcurator-access-redaction.svg)](https://travis-ci.org/BitCurator/bitcurator-access-redaction)

This repository includes a set of redaction tools developed for the BitCurator Access project. These tools are primarily intended to support scrubbing/overwriting patterns identified in raw disk image files, but may be applied to any source presented as a file. Redacting patterns from raw disk images (or files) may render the disk image (or file) unmountable or unrenderable. Use at your own risk!

This repository currently includes the following libraries:

* **libredact**: A Python redaction library and standalone raw disk image redaction tool. Loosely based on the iredact.py tool.

* **redact-cli**: A command-line interface to the redaction library
* **redact-bulk**: A command-line interface to the redaction library that redacts items identified in annotated bulk_extractor reports
* **redact-gui**: A GUI interface that mirrors the functionality of redact-cli

## Prerequisites

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
  * The lightgrep library install into /usr/local/lib, so this directory will need to be on the system's LD_LIBRARY_PATH in order for redact-cli to find it. Your __bitcurator-access-redaction__ environment must include the LD_LIBRARY_PATH setting:
```shell
$ export LD_LIBRARY_PATH=/usr/local/lib
```

## Building and installing libredact

* Clone this repository:
```shell
$ git clone https://github.com/bitcurator/bitcurator-access-redaction
```
* Enter the repository directory:
```shell
$ cd bitcurator-access-redaction
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

## Running (command line interface)

The redaction tool can be run from the command line as follows:
```shell
    $ redact-cli -h
```
Instructions for creating a configuration file are also available on the command line:
```shell
    $ redact-cli -H
```
## Running (command line interface, redacting using annotated bulk_extractor reports)

If you have previously generated bulk_extractor feature reports (and annotated them with identify_filenames.py), the final annotated text reports can be used as redaction lists (redacting each entry in the report).  The bulk_extractor report-ready redaction tool can be run from the command line as follows:
```shell
    $ redact-bulk -h
```
Instructions for creating a configuration file are also available on the command line:
```shell
    $ redact-bulk -H
```

## Running (graphical interface)

The redation tool includes a GUI that can be used to create and edit configuration files, and execute redaction actions equivalent to those performed using redact-cli. When using the GUI, all options (including input and output files) must be specified within the configuration file.

The GUI can be started by running the following command in a terminal:
```shell
    $ redact-gui
```

## Using the Python module

All of the same functions as the command line are also available in the
libredact module. Below is a short example Python script that uses the
Redactor API to process a disk image. (Coming soon...)

## Dependencies

  * The lightgrep.py Python API file is included with this repository (in the libredact folder). It should not be modified. If you need to update it or submit patches, the original source can be found at:
```shell
$ https://raw.githubusercontent.com/strozfriedberg/liblightgrep/master/pylightgrep/lightgrep.py
```

  * The dfxml.py and fiwalk.py files are included with this repository (in the libredact folder). They should not be modified. If you need to update them or submit patches, the original sources can be found in the following master repository:
```shell
$ https://github.com/simsong/dfxml/tree/master/python
```

## Acknowledgements

Greg Jansen developed the BitCurator Access Redaction Tools under contract for the BitCurator Access project.

## Licenses

Project documentation and other non-software products of the BitCurator Access team and contracted partners are subject to the the Creative Commons Attribution 4.0 Unported license (CC BY 4.0).

Unless otherwise indicated, software objects in this repository are distributed under the terms of the GNU General Public License, Version 3. See the text file "LICENSE" for further details about the terms of this license.

The lightgrep.py Python interface to liblightgrep is included under the terms of the license for liblightgrep, namely the GNU General Public License, Version 3. 

(See https://github.com/strozfriedberg/liblightgrep/blob/master/COPYING for original liblightgrep license terms).

# Testing bitcurator-access-redaction in the BitCurator Environment

## Downloading and Installing

Download a bca-redtools source code release from GitHub. (For this example, we’ll
use the v0.4.2 release. You should use the latest release, which you can find 
at https://github.com/BitCurator/bitcurator-access-redaction/releases). You will 
see options to download either the .tar.gz or .zip versions of the release. 
Use the .zip link.

Open a terminal window. Use the following commands to move the zip file to the BitCurator home directory and unzip it:

```shell
$ mv ~/Downloads/v0.4.2.zip .
$ unzip v0.4.2
```

In the same terminal, navigate to the libredact sub-folder, and then run the pip (Python 2.7 version) install command:

```shell
$ cd bca-redtools-0.4.0/libredact
$ pip2 install -e .
```

The bca-redtools source contains a small FAT32 test image with text files from Project Gutenburg, text dumps of email from the M57 forensic corpus, and several Windows executables. In the same terminal, copy this test image to your home directory (this is a convenience step to simplify the commands described here):

```shell
$ cp ~/bca-redtools-0.4.0/libredact/test/test_image.raw ~/
$ cd /home/bcadmin
```

If you would like to examine the contents of this disk image, you can do so by double-clicking on the “home” folder on the Desktop. Right-click on the test_image.raw file and select “Scripts->Mount Disk Image”. The disk image will mount read-only. After examining the contents, right-click on the image file (not the mounted disk icon) and select “Scripts->Unmount Disk Image”.

In the following steps, we will run the redaction tool. For the purposes of this tutorial, we will separate the various redaction actions out into discrete configuration files for clarity. In normal usage, these could be grouped together in a single configuration file (see the Quickstart Guide for additional detail and examples). Note: This testing document covers only a small selection of the possible redaction options.

## Generating DFXML (Optional)

You can optionally generate a Digital Forensics XML file for the disk image using fiwalk, in order to redact sequences that match specific types of file system metadata (for example, filenames, or files matching particular MD5 hashes). Note: If you do not generate the fiwalk DFXML file, the DFXML will be generated automatically (and you must omit the --dfxml flag and  associated filename in the subsequent steps). However, we will generate one ahead of time here to demonstrate the capabilities of the tool when working with preexisting DFXML files.
Open a terminal (or return to your existing terminal) and type the following command:

```shell
$ fiwalk -f -X ~/test_image_fw.xml ~/test_image.raw
```

## Scrubbing a file associated with an MD5 hash

The rule in this example targets a file associated with a specific MD5 hash for redaction. The action - SCRUB - indicates that every byte associated with the file will be overwritten with zeroes.


Run the redaction


Create a text file called “scrub-config.txt” in /home/bcadmin. We will be scrubbing the “Metamorphosis.txt” file using its MD5. Save the following plain text content into your file:

```shell
FILE_MD5 df19e9a0b370d47aba5c89c810b05ad3 SCRUB
COMMIT
```

Open the terminal. At the command prompt ($), type the following commands:

```shell
$ cd /home/bcadmin
$ redact-cli --input=test_image.raw --dfxml=test_image_fw.xml --output=scrub-output.raw --report=scrub-report.json --config=scrub-config.txt
```

You should see the following confirmation message appear:
	
```shell
$ INFO:root:Commit is ON. Will perform redactions..
$ INFO:root:Finished. 1 file was redacted.
```

Verify the redaction


On the desktop, double-click on the home icon and locate the file scrub-output.raw. Right-click on scrub-output.raw, and select Scripts > Mount Disk Image. The mounted disk image should appear on the desktop. Double-click on this icon and navigate to the Metamorphosis.txt file. Right-click on Metamorphosis, then select Scripts > File Analysis > View in Hex Editor. Confirm that the contents of the file have been zeroed out. After examining the contents, right-click on the image file (not the mounted disk icon) and select “Scripts->Unmount Disk Image”.



## Overwriting a string sequence with a repeating character

The rule in this example overwrites any matching sequences with the byte 0x44 (the hex code for capital ‘D’ in ASCII). For the example, we’ll overwrite all instances of the email address “pat@m57.biz”, an email address that appears frequently in the test data.
 
Run the redaction


Create a text file called “fill-config.txt” in /home/bcadmin. Save the following plain text content into your file:

```shell
SEQ_EQUAL pat@m57.biz FILL 0x44
COMMIT
```

Open the terminal. At the command prompt ($), type the following commands, hitting enter after each:

Note: You can tap the ‘up arrow’ key at the command prompt to show the previous command (cycling through all previous commands as you tap it additional times).  You can edit the command as needed (altering file names for output, report and config) and then tap enter.

```shell
$ cd /home/bcadmin
$ redact-cli --input=test_image.raw --dfxml=test_image_fw.xml --output=fill-output.raw --report=fill-report.json --config=fill-config.txt
```

You should see the following confirmation message appear:

```shell
$ INFO:root:Commit is ON. Will perform redactions..
$ INFO:root:Finished. 16 files were redacted.
```

## Fuzzing a binary (preventing execution)

The rule in this example “fuzzes” a binary, altering the bytes (but not the length of the byte sequence) so that the binary can no longer be executed (in the case of .exe files) or accessed by other programs (in the case of .dll files).

Run the redaction


Create a text file called “fuzz-config.txt” in /home/bcadmin. Save the following plain text content into your file:

```shell
FILE_NAME_EQUAL PUTTY.EXE FUZZ
COMMIT
```

Open the terminal. At the command prompt ($), type the following commands, hitting enter after each:

Note: You can tap the ‘up arrow’ key at the command prompt to see the previous command (cycling through all previous commands as you tap it additional times).  You can edit the command as needed (altering file names for output, report and config) and then tap enter.

```shell
$ cd /home/bcadmin
$ redact-cli --input=test_image.raw --dfxml=test_image_fw.xml --output=fuzz-output.raw --report=fuzz-report.json --config=fuzz-config.txt
```

You should see the following confirmation message appear:

```shell
$ INFO:root:Commit is ON. Will perform redactions..
$ INFO:root:Finished. 1 file was redacted.
```

Verify the redaction (Optional: The binary fuzz test requires access to a Windows machine)


On the desktop, double-click on the home icon and locate the file fuzz-output.raw. Right-click on fuzz-output.raw, then select Scripts > Mount Disk Image. Within the mounted disk image, navigate to executables/PUTTY.EXE. Copy PUTTY.EXE to a directory on a Windows computer.  If you’re running the BitCurator environment as a Virtual Machine on top of Windows, you can do this by copying PUTTY.EXE to a shared folder.


On the Windows host, double-click on PUTTY.EXE to confirm that it does not execute.


## Using the graphical interface

The bca-redtools source code includes a GUI front-end to the functionality described in the previous section. 


Start the GUI from the terminal by typing the following commands in a terminal:

```shell
$ cd /home/bcadmin
$ redact-gui
```

In this test, we will perform the “SCRUB” action. We’ll create a new scrub configuration file and a new output file to demonstrate the process, even though we’ll be scrubbing the same file from the raw disk image.

In the Disk Image Redaction window, click “Open Editor” (top right section, shown below).

A gedit text editing window will appear. Add the following lines:

```shell
INPUT_FILE /home/bcadmin/test_image.raw
OUTPUT_FILE /home/bcadmin/scrub_output2.raw
FILE_MD5 df19e9a0b370d47aba5c89c810b05ad3 SCRUB
COMMIT
```

Do not click “Save” - this will simply save the file with the default name, “None”. Instead, move your cursor to the gedit menu bar, select “File -> Save As”, and save the file as “scrub_config2.txt” in the /home/bcadmin directory. Click “Save” in the file dialog, then close the gedit window. Click “OK” to dismiss the final reminder dialog.


Now click “Select File..”, and in the file dialog select the “scrub-config2.txt” file you just created in /home/bcadmin. Click “Run”, and the application should apply the redaction, generating feedback on the process in the “Console Output” window:

Verify the redaction

On the desktop, double-click on the home icon and locate the file scrub-output2.raw. Right-click on scrub-output2.raw, and select Scripts > Mount Disk Image. The mounted disk image should appear on the desktop. Double-click on this icon and navigate to the Metamorphosis.txt file. Right-click on Metamorphosis, then select Scripts > File Analysis > View in Hex Editor. Confirm that the contents of the file have been zeroed out. After examining the contents, right-click on the image file (not the mounted disk icon) and select “Scripts->Unmount Disk Image”.

## Redacting matches from an annotated bulk_extractor report

Another interface to the redaction library - redact-bulk - operates similarly to redact-cli, but redacts item directly from a bulk_extractor report (which can be generated using bulk_extractor or BEVeiwer - both of which are built in to BitCurator).

We will use a previously prepared bulk_extractor report to perform the redaction in this example.

In a terminal, copy this sample report to your home directory (this is a convenience step to simplify the commands described here):

```shell
$ cp ~/bca-redtools-0.4.0/libredact/bulk_redact/email.txt ~/
$ cd /home/bcadmin
```

By default, redact-bulk will perform a “SCRUB” operation, filling the identified sequences with zeros. You can view other options by running “redact-bulk -h” on the command line. In this example, we will run it against the complete contents of email.txt with default settings. Note that we do not require a configuration file for this test.

IMPORTANT: redact-bulk will use the input file (disk image) path from the comment at the top of a given annotated bulk_extractor report. If the disk image is no longer at that path, you must edit the comment to match the current location. The sample report here expects the disk image to exist in /home/bcadmin/test_image.raw.

In the terminal, type the following commands, hitting enter after each:

```shell
$ cd /home/bcadmin
$ redact-bulk --output=email-output.raw email.txt
```

You should see the following confirmation message appear:
	
```shell
$ INFO:root:Commit is ON. Will perform redactions..
$ INFO:root:Finished. 1 file was redacted.
```

Verify the redaction

On the desktop, double-click on the home icon and locate the file email-output.raw. Right-click on email-output.raw, and select Scripts > File Analysis > View in Hex Editor. Confirm that the email addresses at the associated offsets have been zeroed out.


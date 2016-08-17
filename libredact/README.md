Development Notes: BitCurator Access Redaction Tools
-----------------------------------------------


## Warning

Do not modify dfxml.py or fiwalk.py. These files have been included here for convenience, as no appropriate installer is provided by the DFXML repository.

# Unit Tests
There are unit tests in the test module. These are written against redaction
configurations that are inline, in the test/main.py program. You can run the tests as follows:

1. Source the virtual environment:
```shell
    $ source bca-redtools/env/bin/activate
```

1. Change to code directory:
```shell
    $ cd bca-redtools/libredact
```

1. Run the test class:
```shell
    $ python test/main.py
```

Results are printed to the console, including the report. This will show all of the redactions performed for the test functions.

# Modifying the Test Disk Image
The test disk image is 2MB in size and contains the full text of several books
from Project Gutenberg. It also contains some specially composed files that
support certain rules in the test configuration file.

To modify the test image, you will need to mount it as a filesystem. Follow these steps:

1. Create a mount point (directory):
```shell
    $ mkdir ~/Desktop/redact_test_image
```

1. Mount the disk image as a loopback device:
```shell
    $ sudo mount -o uid=1000,gid=1000,loop ~/git/bca-redtools/libredact/test/test_image.raw ~/Desktop/redact_test_image/
```

1. Add files. If you run out of room on the disk, consider truncating one of the books. You can do this by opening a book file in a text editor, deleting the second half of the text. You will have to save the result outside of the disk image, then delete the original file in the image, then replace it with the new file you created.

1. When done modifying the test image, umount it:
```shell
    $ sudo umount ~/Desktop/sredact_test_image/
```

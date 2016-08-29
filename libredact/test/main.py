import unittest
from libredact import config, cli
from libredact.redact import Redactor
from io import StringIO
import hashlib
from contextlib import closing
import logging

config_string = u"""
INPUT_FILE /home/bcadmin/Desktop/jowork.raw
DFXML_FILE /home/bcadmin/Desktop/jofiwalk.xml
OUTPUT_FILE /tmp/jowork.raw

# Targets The Whale.txt
FILE_NAME_MATCH *Whale.txt FUZZ

# Targets Dorian Gray.txt
FILE_MD5 114583cd8355334071e9343a929f6f7c FILL 0x44

# Targets DRINKME.TXT
FILE_SHA1 7f9f0286e16e9c74c992e682e27487a9eb691e86 FILL 0x44

# Fill Kafka sequences in Metamorphsis.txt with K
SEQ_EQUAL Kafka FILL 0x4B

# FILE_SEQ_MATCH \d{3}-?\d{2}-?\d{4} FILL 0x44
SEQ_MATCH \d{3}-?\d{2}-?\d{4} FILL 0x44

# Scrub EATME.TXT
FILE_SEQ_EQUAL pineapple-upside-down-cake SCRUB

# Scrub Alice in Wonderland
FILE_DIRNAME_EQUAL looking-glass SCRUB

# Ignore EATME.TXT.BACKUP
IGNORE *.BACKUP
IGNORE *.DOCX
"""


class RedactTest(unittest.TestCase):
    def test_config_parse(self):
        config_in = StringIO(config_string)
        result = config.parsehandle(config_in)
        self.assertEqual(len(result['rules']), 7)
        self.assertEqual(len(result['ignore_patterns']), 2)
        self.assertEqual(result['input_file'], "/home/bcadmin/Desktop/jowork.raw")
        self.assertEqual(result['dfxml_file'], "/home/bcadmin/Desktop/jofiwalk.xml")
        self.assertEqual(result['output_file'], "/tmp/jowork.raw")

    def test_lib(self):

        """ Tests that redaction based on file content is achieved on first pass. """

        content_rules = u"""
# Targets Dorian Gray.txt
FILE_MD5 114583cd8355334071e9343a929f6f7c FILL 0x44

# Targets DRINKME.TXT
FILE_SHA1 7f9f0286e16e9c74c992e682e27487a9eb691e86 FILL 0x44

# Fill Kafka sequences in Metamorphsis.txt with K
SEQ_EQUAL Kafka FILL 0x4B

SEQ_MATCH \d{3}-?\d{2}-?\d{4} FILL 0x44

# Scrub EATME.TXT
FILE_SEQ_EQUAL pineapple-upside-down-cake SCRUB

# Ignore EATME.TXT.BACKUP
IGNORE *.BACKUP
"""
        config_in = StringIO(content_rules)
        cfg = config.parsehandle(config_in)
        cfg['commit'] = True
        import os
        dirname = os.path.dirname(os.path.abspath(__file__))
        input_file = os.path.join(dirname, "test_image.raw")
        cfg['input_file'] = input_file
        cfg['dfxml_file'] = None
        output_file = '/tmp/output_image.raw'
        cfg['output_file'] = output_file
        redactor = Redactor(**cfg)
        # First redaction verifies an output file
        redactor.execute()
        self.assertEqual(os.path.isfile(output_file), True)

        # Second redaction processes the output file again, to verify no further changes.
        config_in2 = StringIO(content_rules)
        cfg2 = config.parsehandle(config_in2)
        cfg2['commit'] = True
        md5sum1 = md5sum(output_file)
        cfg2['input_file'] = output_file
        output_file2 = '/tmp/output_image2.raw'
        cfg2['output_file'] = output_file2
        # dfxml_file = os.path.join(dirname, "test_image.xml")
        cfg2['dfxml_file'] = None
        report = "/tmp/report.json"
        cfg2['report_file'] = report

        redactor2 = Redactor(**cfg2)
        redactor2.execute()
        md5sum2 = md5sum(output_file2)
        self.assertEqual(md5sum1, md5sum2)
        # Verify the report only has the first config line
        self.assertEqual(file_lines(report), 1)


def md5sum(filename):
    md5 = hashlib.md5()
    with closing(open(filename, 'rb')) as f:
        for chunk in iter(lambda: f.read(8192), b''):
            md5.update(chunk)
    return md5.digest()


def file_lines(fname):
    r = 0
    with open(fname) as f:
        for i, l in enumerate(f):
            ++r
    return r + 1


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()

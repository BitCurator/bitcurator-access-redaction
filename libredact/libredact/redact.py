'''Disk Image Redaction Library

Redacts disk images according to the given configuration.
'''

import logging
import fiwalk
import re
import json
import shutil
from .rule import redact_rule, rule_file_md5, rule_file_sha1, convert_fileglob_to_re
from .action import redact_action, _


class Redactor:
    conf = None
    image = None
    report = None
    commit = False
    kwargs = {}

    def __init__(self, input_file=None, output_file=None, dfxml_file=None, report_file=None,
                 commit=False, ignore_patterns=[], rules=[]):
        #  Validate configuration
        from schema import Schema, Optional, Or, Use, And, SchemaError
        schema = Schema({
            'input_file': Use(lambda f: open(f, 'r'), error='Cannot read the input file'),
            Optional('output_file'):
            Or(None,
               Use(lambda f: open(f, 'w'), error='Cannot write to the output file')),
            Optional('dfxml_file'):
            Or(None,
               Use(lambda f: open(f, 'r'), error='Cannot read DFXML file')),
            Optional('report_file'):
            Or(None,
               lambda f: open(f, 'w'), error='Cannot write to the report file'),
            'commit': Or(True, False),
            'ignore_patterns':
                Use(lambda f: re.compile(convert_fileglob_to_re('|'.join(f))),
                    error='Cannot compile unified ignore regex'),
            'rules': And([(redact_rule, redact_action)], lambda f: len(f) > 0)})

        self.kwargs = {
            'input_file': input_file,
            'output_file': output_file,
            'dfxml_file': dfxml_file,
            'report_file': report_file,
            'commit': commit,
            'ignore_patterns': ignore_patterns,
            'rules': rules
        }
        try:
            self.conf = schema.validate(self.kwargs)
        except SchemaError as e:
            logging.warning('The redact configuration did not validate:')
            exit(e)
        if self.conf['commit'] and 'output_file' not in self.conf.keys():
            logging.error('An output file is required when COMMIT is on.')
            exit(1)
        # TODO Check input and output are not same file

        self.input_file = self.conf['input_file']
        from os import path
        self.image_size = path.getsize(self.input_file.name)
        self.output_file = self.conf['output_file']
        self.report_file = self.conf['report_file']
        self.dfxml_file = self.conf['dfxml_file']
        self.commit = self.conf['commit']
        self.configure_report_logger()

    def need_md5(self):
        for (rule, action) in self.conf['rules']:
            if rule.__class__ == rule_file_md5:
                return True
        return False

    def need_sha1(self):
        for (rule, action) in self.conf['rules']:
            if rule.__class__ == rule_file_sha1:
                return True
        return False

    def fiwalk_opts(self):
        "Returns the options that fiwalk needs given the redaction requested."
        opts = "-x"
        if self.need_sha1():
            opts = opts + "1"
        if self.need_md5():
            opts = opts + "m"
        return opts

    def should_ignore(self, fi):
        return self.conf['ignore_patterns'].search(fi.filename())

    def process_file(self, fileinfo):
        # logging.debug("Processing file: %s" % fileinfo.filename())
        if fileinfo.is_dir() or fileinfo.filename().startswith('$') or self.should_ignore(fileinfo):
            logging.info("Ignoring %s" % fileinfo.filename())
            return

        if fileinfo.filename().startswith('.goutputstream'):
            logging.debug('got a .goutputstream file in meta_type: '+str(fileinfo.meta_type()))
            logging.debug('.goutputstream file length: '+str(fileinfo.filesize()))
            logging.debug('contents: '+fileinfo.contents())

        # logging.debug("Stage 2 processing file: "+fileinfo.filename())
        for (rule, action) in self.conf['rules']:
            # logging.debug("processing rule: " + rule.line)
            if rule.should_redact(fileinfo):
                # logging.debug("should redact file: "+fileinfo.filename())
                action.redact(rule, fileinfo, self.output_file, self.commit)
                # logging.debug("redacted file: "+fileinfo.filename())
                if rule.complete:
                    return  # only need to redact once!

    def close_files(self):
        for f in [self.input_file, self.output_file, self.dfxml_file]:
            if f and f.closed is False:
                logging.debug("Closing file: %s" % f.name)
                f.close()
        logging.debug("files closed")

    def execute(self):
        if self.conf.get('commit'):
            logging.warning("Commit is ON. Will perform redactions..")
        else:
            logging.warning("Commit is OFF. Performing dry-run only..")
        if self.report_logger is not None:
            self.report_logger.info('{')
            self.report_logger.info('"configuration": ')
            self.report_logger.info(_(self.kwargs))
            self.report_logger.info(',')
            self.report_logger.info('"redactions": [')
        logging.debug('DEBUG OUTPUT IS ON')
        # Copy input_file to output_file
        if not self.output_file.closed:
            self.output_file.close()
        if not self.input_file.closed:
            self.input_file.close()
        import time
        t0 = time.time()  # start a timer
        shutil.copy(self.input_file.name, self.output_file.name)
        self.output_file = open(self.output_file.name, 'r+')
        self.input_file = open(self.input_file.name, 'r')

        fiwalk.fiwalk_using_sax(
            imagefile=self.output_file,
            xmlfile=self.dfxml_file,
            callback=self.process_file)
        self.close_files()

        elapsed = time.time() - t0
        logging.debug("Time to run: %d seconds" % elapsed)
        if self.report_logger is not None:
            self.report_logger.info('],')
            self.report_logger.info('"runtime": %d' % elapsed)
            self.report_logger.info('}')

    def configure_report_logger(self):
        logger = logging.getLogger('audit_report')
        logger.setLevel(logging.INFO)
        logger.propagate = False

        # create file handler which logs even debug messages
        if self.report_file is None:
            fh = logging.NullHandler()
        else:
            fh = logging.FileHandler(self.report_file)
            fh.setLevel(logging.DEBUG)

        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(message)s')
        fh.setFormatter(formatter)
        # add the handlers to the logger
        for h in list(logger.handlers):
            logger.removeHandler(h)
        logger.addHandler(fh)
        self.report_logger = logger

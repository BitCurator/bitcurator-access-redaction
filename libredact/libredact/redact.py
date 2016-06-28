'''Disk Image Redaction Library

Redacts disk images according to the given configuration.
'''

import logging
import fiwalk
import re
from rule import redact_rule, rule_md5, rule_sha1, convert_fileglob_to_re
from action import redact_action, _


class Redactor:
    conf = None
    image = None
    report = None
    commit = False

    def __init__(self, **kwargs):
        #  Validate configuration
        from schema import Schema, Optional, Or, Use, SchemaError
        schema = Schema({
            'image_file': Use(lambda f: open(f, 'r+b'), error='Image file is not writable'),
            Optional('dfxml_file'):
            Or(None,
               Use(lambda f: open(f, 'r'), error='Cannot read DFXML file')),
            Optional('report_file'):
            Or(None,
               lambda f: open(f, 'w'), error='Cannot write to the report file'),
            'commit': Or(True, False),
            Optional('detail'): Or(True, False),
            'ignore_patterns':
                Use(lambda f: re.compile(convert_fileglob_to_re('|'.join(f))),
                    error='Cannot compile unified ignore regex'),
            'key': Or(None, str),
            'rules': [(redact_rule, redact_action)]})
        try:
            self.conf = schema.validate(kwargs)
        except SchemaError as e:
            logging.warning('The sredact configuration did not validate:')
            exit(e)

        logging.debug('Configuration:\n%s' % self.conf)

        self.image_file = self.conf['image_file']
        self.report_file = self.conf['report_file']
        self.dfxml_file = self.conf['dfxml_file']
        self.detail = self.conf['detail']
        self.commit = self.conf['commit']
        self.configure_report_logger()
        if self.commit:
            logging.warning("COMMIT is True, performing redaction")
        else:
            logging.warning("COMMIT is False, dry-run only")

    def need_md5(self):
        for (rule, action) in self.conf['rules']:
            if rule.__class__ == rule_md5:
                return True
        return False

    def need_sha1(self):
        for (rule, action) in self.conf['rules']:
            if rule.__class__ == rule_sha1:
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
        if self.should_ignore(fileinfo):
            logging.info("Ignoring %s" % fileinfo.filename())
            return
        for (rule, action) in self.conf['rules']:
            if rule.should_redact(fileinfo):
                action.redact(rule, fileinfo, self.image_file, self.commit)
                if rule.complete:
                    return  # only need to redact once!

    def close_files(self):
        for f in [self.image_file, self.dfxml_file]:
            if f and f.closed is False:
                logging.debug("Closing file: %s" % f.name)
                f.close()

    def execute(self):
        if self.conf.get('COMMIT'):
            logging.warning("Performing redactions..")
        else:
            logging.warning("Performing dry-run only..")
        if self.report_logger is not None:
            self.report_logger.info(_(self.conf))
        fiwalk.fiwalk_using_sax(
            imagefile=self.image_file,
            xmlfile=self.dfxml_file,
            callback=self.process_file)
        self.close_files()

    def configure_report_logger(self):
        logger = logging.getLogger('audit_report')

        # Using DEBUG as 'detailed' logging level
        if self.detail:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

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
        logger.addHandler(fh)
        self.report_logger = logger

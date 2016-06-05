'''Disk Image Redaction Library

Redacts disk images according to the given configuration.
'''

import logging
import fiwalk
import re
from rule import redact_rule, rule_md5, rule_sha1, convert_fileglob_to_re
from action import redact_action


class Redactor:
    conf = None

    def __init__(self, cfg):
        #  Validate configuration
        from schema import Schema, Optional, Or, Use, SchemaError
        schema = Schema({
            'IMAGE_FILE': Use(lambda f: open(f, 'r+b'), error='IMAGE_FILE is not writable'),
            Optional('DFXML_FILE'):
            Or(None,
               Use(lambda f: open(f, 'r'), error='Cannot read DFXML_FILE')),
            Optional('REPORT_FILE'):
            Or(None,
               Use(lambda f: open(f, 'w'), error='Cannot write REPORT_FILE')),
            'COMMIT': Or(True, False),
            'IGNORE_PATTERNS':
                Use(lambda f: re.compile(convert_fileglob_to_re('|'.join(f))),
                    error='Cannot compile unified ignore regex'),
            'KEY': Or(None, str),
            'rules': [(redact_rule, redact_action)]})
        try:
            self.conf = schema.validate(cfg)
        except SchemaError as e:
            logging.warning('The sredact configuration did not validate:')
            exit(e)

        logging.debug('Configuration:\n%s' % self.conf)

        if self.conf.get('COMMIT'):
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
        return self.conf['IGNORE_PATTERNS'].search(fi.filename())

    def process_file(self, fileinfo):
        # logging.debug("Processing file: %s" % fileinfo.filename())
        if self.should_ignore(fileinfo):
            logging.info("Ignoring %s" % fileinfo.filename())
            return
        for (rule, action) in self.conf['rules']:
            if rule.should_redact(fileinfo):
                print("")
                print("Redacting ", fileinfo.filename())
                print("Reason:", str(rule))
                print("Action:", action)
                action.redact(rule, fileinfo, self)
                if rule.complete:
                    return  # only need to redact once!

    def close_files(self):
        for f in [self.conf['IMAGE_FILE'], self.conf['DFXML_FILE']]:
            if f and f.closed is False:
                logging.debug("Closing file: %s" % f.name)
                f.close()

    def execute(self):
        if self.conf.get('COMMIT'):
            logging.warning("Performing redactions..")
        else:
            logging.warning("Performing dry-run only..")
        fiwalk.fiwalk_using_sax(
            imagefile=self.conf['IMAGE_FILE'],
            xmlfile=self.conf['DFXML_FILE'],
            callback=self.process_file)
        self.close_files()

"""Usage:
  sredact [-nqd] CONFIG_FILE
  sredact [-nqd] [--image=FILE] [--dfxml=FILE] [--report=FILE] CONFIG_FILE
  sredact -h | --help
  sredact -H
  sredact -v | --version

This program redacts a disk image file using a set of rules that describe what to redact and
how to redact it. Prints a summary of actions taken to standard output.

Arguments:
  CONFIG_FILE     configuration file that specifies rules and other items (for details, see -H)

Options:
  --image=FILE     disk image file to redact (or use file specified in CONFIG_FILE)
  --dfxml=FILE     previously generated dfxml file (or use file specified in CONFIG_FILE)
  --report=FILE    create an audit report of redactions performed
  -n, --dry-run    runs analysis and creates the report without redact actions, overrides COMMIT
  -q, --quiet      quiet mode (no console output unless errors occur)
  -d, --debug      debug mode, prints individual actions taken (or planned in dry runs)
  -h, --help       show this usage information
  -H, --chelp      show configuration help
  -v, --version    print sredact version and exit
"""

import os.path
import fiwalk


config_help = """
sredact Configuration File Help
===============================

The configuration file can specify complete instructions for how sredact runs. Arguments given on
the command-line or in calls to the sredact API method will override settings in the configuration
file. The readaction configuration file consists of commands, one per line. Order of the commands
does not matter.

Simple Commands:
  IMAGE_FILE        path to disk image file to redact
  DFXML_FILE        optional path to previously generated DFXML
  REPORT_FILE       optional path to write audit report file
  IGNORE <regex>    ignore files whose names match regex (repeatable)
  KEY <key>         encrytion key used by ENCRYPT action, see below
  COMMIT            perform rule actions
                    (w/o COMMIT we have a dry run and report will indicate planned actions)

Rule Command Format:
  [condition] [action]

Each rule consists of an "condition" and an "action".

Conditions:
  FILENAME <afilename> - a file with the given name
  FILEPAT  <a file pattern> - any file with a given pattern
  DIRNAME  <a directory> - any file in the directory
  MD5 <a md5> - any file with the given md5
  SHA1 <a sha1> - any file with the given sha1
  CONTAINS <a string> - any file that contains <a string>

Actions:
  SCRUB MATCH     Scrubs the pattern where it occurs
  SCRUB SECTOR    Scrubs the block where the patern occurs
  SCRUB FILE      Scrubs the file in which the pattern occurs
  FILL 0x44       overwrite by filling with character 0x44 ('D')
  ENCRYPT         encrypts the data, using KEY
  FUZZ            fuzz the binary, but not the strings

Example file:
===============
MD5 3482347345345 SCRUB FILE
MATCH simsong@acm.org SCRUB FILE
MATCH foobar SCRUB BLOCK
KEY 12342343
================================================================
"""


def need_md5(self):
    for (rule, action) in self.cmds:
        if rule.__class__ == redact_rule_md5:
            return True
    return False


def need_sha1(self):
    for (rule, action) in self.cmds:
        if rule.__class__ == redact_rule_sha1:
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


def process_file(self, fileinfo):
    for (rule, action) in self.cmds:
        if rule.should_redact(fileinfo):
            print("Processing file: %s" % fileinfo.filename())

            if self.ignore_rule.should_ignore(fileinfo):
                print("(Ignoring %s)" % fileinfo.filename())
                return

            print("")
            print("Redacting ", fileinfo.filename())
            print("Reason:", str(rule))
            print("Action:", action)
            action.redact(rule, fileinfo, self)
            if rule.complete:
                return  # only need to redact once!

    def close_files(self):
        if self.imagefile and self.imagefile.closed is False:
            print("Closing file: %s" % self.imagefile.name)
            self.imagefile.close()
        if self.xmlfile and self.xmlfile.closed is False:
            print("Closing file: %s" % self.xmlfile.name)
            self.xmlfile.close()


if __name__ == "__main__":
    from docopt import docopt
    from libredact import __version__
    args = docopt(__doc__, version=__version__)
    # print(args)

    # Command-line interface
    if args.get('--chelp'):
        print(config_help)
        exit()

    # Set up console log levels (default=warn, quiet=error, debug=debug)
    log_level = 'warn'
    if args.get('--quiet'):
        log_level = 'error'
    if args.get('--debug'):  # debug overrides quiet
        log_level = 'debug'

    # Read the redaction configuration file
    from libredact.config import RedactConfigParser
    cfg = RedactConfigParser.parse(args.get('CONFIG_FILE'))

    # Override any CLI arguments
    if args.get('--image'):
        cfg.set('IMAGE_FILE', args.get('--image'))
    if args.get('--dfxml'):
        cfg.set('DFXML_FILE', args.get('--dfxml'))
    if args.get('--report'):
        cfg.set('REPORT_FILE', args.get('--report'))
    if args.get('--dry-run'):  # if True then override COMMIT
        cfg.set('COMMIT', False)
    # print(cfg)

    # Validate configuration
    from schema import Schema, Optional, Or, Use, SchemaError
    schema = Schema({
        'IMAGE_FILE': Use(lambda f: open(f, 'r+b'), error='IMAGE_FILE is not writable'),
        Optional('DFXML_FILE'): Or(None,
                                   Use(lambda f: open(f, 'r'), error='Cannot read DFXML_FILE')),
        Optional('REPORT_FILE'): Or(None,
                                    Use(lambda f: open(f, 'w'), error='Cannot write REPORT_FILE')),
        'COMMIT': Or(True, False)})
    try:
        args = schema.validate(cfg)
    except SchemaError as e:
        exit(e)

    if cfg.get('COMMIT'):
        logger.warn("COMMIT is True, performing redaction")
    else:
        logger.warn("COMMIT is False, dry-run only")

    import time
    t0 = time.time()
    # fiwalk.fiwalk_using_sax(
    #    imagefile=rc.imagefile, xmlfile=rc.xmlfile, callback=rc.process_file)
    t1 = time.time()

    close_files()

    print("Time to run: %d seconds" % (t1 - t0))

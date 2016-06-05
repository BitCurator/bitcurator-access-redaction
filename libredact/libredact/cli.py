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

from redact import Redactor
import logging


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


def main():
    from docopt import docopt
    from libredact import __version__
    args = docopt(__doc__, version=__version__)
    # print(args)

    # Command-line interface
    if args.get('--chelp'):
        print(config_help)
        exit()

    # Set up console log levels (default=warn, quiet=error, debug=debug)
    log_level = logging.WARN
    if args.get('--quiet'):
        log_level = logging.ERROR
    if args.get('--debug'):  # debug overrides quiet
        log_level = logging.DEBUG
    logging.basicConfig(level=log_level)

    # Read the redaction configuration file
    from libredact.config import parse
    cfg = parse(args.get('CONFIG_FILE'))

    # Override any CLI arguments
    if args.get('--image'):
        cfg['IMAGE_FILE'] = args.get('--image')
    if args.get('--dfxml'):
        cfg['DFXML_FILE'] = args.get('--dfxml')
    if args.get('--report'):
        cfg['REPORT_FILE'] = args.get('--report')
    if args.get('--dry-run'):  # if True then override COMMIT
        cfg['COMMIT'] = False

    logging.debug('Combined config & arguments:\n%s' % cfg)

    redactor = Redactor(cfg)

    import time
    t0 = time.time()
    redactor.execute()
    t1 = time.time()
    print("Time to run: %d seconds" % (t1 - t0))

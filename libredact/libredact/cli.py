"""Usage:
  redact-cli [-nqd] -c FILE
  redact-cli [-nqd] [--input=FILE] [--output=FILE] [--dfxml=FILE] [--report=FILE] [--abe-config=FILE] --config=FILE
  redact-cli -h | --help
  redact-cli -H
  redact-cli -v | --version

This program redacts a disk image file using a set of rules that describe what to redact and
how to redact it. Prints a summary of actions taken to standard output.

Options:
  -c, --config=FILE      configuration file specifies redaction settings (see -H for details)
  -abe-config=FILE       also scrub files indicated in an annotated bulk extrator feature file
  -i, --input=FILE       disk image file to redact (or use file specified by --config)
  -o, --output=FILE      file location for output redacted image file (required for COMMIT)
  --dfxml=FILE           previously generated dfxml file (or use file specified by --config)
  --report=FILE          create an audit report of redactions performed
  -n, --dry-run          creates report without taking action ( overrides COMMIT in --config)
  -q, --quiet            quiet mode (no console output unless errors occur)
  -d, --detail           detail mode, prints individual actions taken (or planned in dry runs)
  -p, --progress=FILE    writes progress to the stdout or a file, if specified
  -h, --help             show this usage information
  -H, --chelp            show configuration help
  -v, --version          print version and exit
"""

from .redact import Redactor
import logging


config_help = """
redact-cli Configuration File Help
===============================

The configuration file can specify complete instructions for how redact-cli runs. Arguments given on
the command-line or in calls to the redact-cli API method will override settings in the configuration
file. The readaction configuration file consists of commands, one per line. Order of the commands
does not matter.

Simple Commands:
  INPUT_FILE <file path>     path to disk image file to redact
  OUTPUT_FILE <file path>    path to write the redacted disk image
  DFXML_FILE <file path>     optional path to previously generated DFXML
  REPORT_FILE <file path>    optional path to write audit report file
  IGNORE <pattern>           ignore files whose names match regex (repeatable)
  COMMIT            perform rule actions
                    (w/o COMMIT we have a dry run and report will indicate planned actions)

Rule Command Format:
  [target condition] [action]

Each rule consists of an "condition" and an "action".

Target Conditions:
  FILE_NAME_EQUAL <filename> - target a file with the given filename
  FILE_NAME_MATCH <pattern> - target any file with a given filename pattern
  FILE_DIRNAME_EQUAL <directory> - target all files in the directory
  FILE_MD5 <md5> - target any file with the given md5
  FILE_SHA1 <sha1> - target any file with the given sha1
  FILE_SEQ_EQUAL <string> - target any file that contains <a string>
  FILE_SEQ_MATCH <pattern> - target any file that contains a sequence matching <a pattern>
  SEQ_EQUAL <string> - target any sequences equal to <a string>
  SEQ_MATCH <pattern> - target any sequences matching <a pattern>

Actions:
  SCRUB        overwrite the bytes in the target with zeroes
  FILL 0x44    overwrite by filling with character 0x44 ('D')
  FUZZ         fuzz the binary, but not the strings

Patterns:
  Patterns can be a wildcard expression of the form '*.txt', for example. They can also be a regular
  expression. For example, this regular expression will target social security numbers
  '\d{3}-?\d{2}-?\d{4}'. Be cautious with patterns and the SEQ_MATCH condition. It is easy to write
  a pattern that will match the whole file.

Example file:
===============
FILE_MD5 3482347345345 SCRUB
FILE_SEQ_EQUAL greg@example.com FILL 0x47
FILE_DIRNAME_EQUAL C:/Windows FUZZ
================================================================
"""


def main():
    from docopt import docopt
    from libredact import __version__
    args = docopt(__doc__, version=__version__)

    if args.get('--chelp'):
        print(config_help)
        exit()

    # Set up console log levels (default=warn, quiet=error, debug=debug)
    log_level = logging.WARN
    if args.get('--quiet'):
        log_level = logging.ERROR
    if args.get('--detail'):  # debug overrides quiet
        log_level = logging.DEBUG
    logging.basicConfig(level=log_level)

    # Read the redaction configuration file
    from libredact.config import parse, parse_abe
    cfg = parse(args.get('--config'))

    # Override any CLI arguments
    if args.get('--input'):
        cfg['image_file'] = args.get('--input')
    if args.get('--output'):
        cfg['output_file'] = args.get('--output')
    if args.get('--dfxml'):
        cfg['dfxml_file'] = args.get('--dfxml')
    if args.get('--report'):
        cfg['report_file'] = args.get('--report')
    if args.get('--dry-run'):  # if True then override COMMIT
        cfg['commit'] = False
    if args.get('--abe-config'):
        abe_rules = parse_abe(args.get('--abe-config'))
        cfg['rules'].extend(abe_rules)

    # TODO cfg['detail'] = args.get('--detail')

    logging.debug('Combined config & arguments:\n%s' % cfg)

    redactor = Redactor(**cfg)

    import time
    t0 = time.time()
    redactor.execute()
    t1 = time.time()
    print("Time to run: %d seconds" % (t1 - t0))

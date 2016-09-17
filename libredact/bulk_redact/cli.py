"""Usage:
  redact-bulk [-nqd] PATH
  redact-bulk [-nqd] [--dry-run] [--output=FILE] [--fill-with=BYTE] PATH
  redact-bulk -h | --help
  redact-bulk -v | --version

This program redacts features from a disk image, based on annotated Bulk Extractor reports
produced by BitCurator. Can redact based on a single feature file, or a whole directory of feature
files, making one pass over the data. By default it redacts features with SCRUB, filling sequences
with a byte value of zero.

Arguments
  PATH  The path to an *annotated* bulk extrator feature directory, or a single feature file.

Options:
  -o, --output=FILE      path to write output redacted image file (defaults to "<input>.redacted")
  -f, --fill-with=BYTE   hex value with which to fill redacted sequences (instead of 0x00)
  -n, --dry-run          creates report without taking action ( overrides COMMIT in --config)
  -q, --quiet            quiet mode (no console output unless Exceptions occur)
  -d, --detail           detail mode, prints individual actions taken (or planned in dry runs)
  -h, --help             show this usage information
  -v, --version          print version and exit
"""
#  -p, --progress=FILE    writes progress to the stdout or a file, if specified


from libredact.redact import Redactor
import logging


def main():
    from docopt import docopt
    from libredact import __version__
    args = docopt(__doc__, version=__version__)

    # Set up console log levels (default=warn, quiet=Exception, debug=debug)
    log_level = logging.INFO
    if args.get('--quiet'):
        log_level = logging.Exception
    if args.get('--detail'):  # debug overrides quiet
        log_level = logging.DEBUG
    logging.basicConfig(level=log_level)

    # Read the redaction configuration file
    from bulk_redact.config import parse
    fillbyte = args.get('--fill-with')
    if fillbyte is None:
        fillbyte = 0x00
    else:
        import re
        if re.search('^0x[0-9A-Fa-f]{2}$', fillbyte) is not None:
            fillbyte = eval(fillbyte)
        else:
            raise Exception('Fill value must be a hex value of the form \'0x44\'')

    cfg = parse(args.get('PATH'), fillbyte)

    # Override any CLI arguments
    if args.get('--output'):
        cfg['output_file'] = args.get('--output')
    if args.get('--dry-run'):  # if True then override COMMIT
        cfg['commit'] = False

    logging.debug('Combined config & arguments:\n%s' % cfg)
    redactor = Redactor(**cfg)
    redactor.execute()

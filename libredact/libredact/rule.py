import re
import mmap
import os
import logging
from ctypes import *
from dfxml import byte_run
from contextlib import closing
try:
    from lightgrep import Lightgrep, HitAccumulator, KeyOpts
except ImportError:
    logging.warn('Lightgrep library not found. If you have installed it, make sure it is included'
                 ' in LD_LIBRARY_PATH. Without lightgrep SEQ_MATCH rules will fail.')


def convert_fileglob_to_re(fileglob):
    regex = fileglob.replace(".", "[.]").replace("*", ".*").replace("?", ".?")
    return re.compile(regex)


class redact_rule:

    """ Instances of this class are objects that can decide what bytes to redact."""

    def __init__(self, line):
        self.line = line
        self.complete = True  # by default, redacts everything

    def should_redact(self, fileobject):
        """Returns True if this fileobject should be redacted"""
        raise ValueError(
            "redact method of redact_rule super class should not be called")

    def __str__(self):
        return self.line

    def runs_to_redact(self, fi):
        """Returns the byte_runs of the source which match the rule.
        By default this is the entire object."""
        return fi.byte_runs()


class rule_file_md5(redact_rule):

    """Redact file if the MD5 matches"""

    def __init__(self, line, val):
        redact_rule.__init__(self, line)
        self.md5val = val.lower()

    def should_redact(self, fi):
        return self.md5val == fi.tag('md5')


class rule_file_sha1(redact_rule):

    """Redact file if the SHA1 matches"""

    def __init__(self, line, val):
        redact_rule.__init__(self, line)
        self.sha1val = val.lower()

    def should_redact(self, fi):
        return self.sha1val == fi.tag('sha1')


class rule_file_name_match(redact_rule):

    """Redact the file if the name matches the pattern"""

    def __init__(self, line, filepat):
        redact_rule.__init__(self, line)
        # convert fileglobbing to regular expression
        self.filepat_re = convert_fileglob_to_re(filepat)

    def should_redact(self, fileobject):
        return self.filepat_re.search(fileobject.filename())


class rule_file_name_equal(redact_rule):

    """Redact the file if the name equals the given string"""

    def __init__(self, line, filename):
        redact_rule.__init__(self, line)
        self.filename = filename

    def should_redact(self, fileobject):
        was = os.path.sep
        os.path.sep = '/'                       # Force Unix filename conventions
        ret = self.filename == os.path.basename(fileobject.filename())
        os.path.sep = was
        return ret


class rule_file_dirname_equal(redact_rule):

    """Redact the file if the directory equals the given string"""

    def __init__(self, line, dirname):
        redact_rule.__init__(self, line)
        self.dirname = dirname

    def should_redact(self, fileobject):
        was = os.path.sep
        os.path.sep = '/'                      # Force Unix filename conventions
        ret = self.dirname == os.path.dirname(fileobject.filename())
        os.path.sep = was
        return ret


class rule_file_seq_match(redact_rule):

    """Redact the file if it contains a sequences matching the given pattern."""

    def __init__(self, line, seq_pattern):
        redact_rule.__init__(self, line)
        self.seq_pattern = seq_pattern
        self.seq_pattern_re = re.compile(seq_pattern)

    def should_redact(self, fileobject):
        # Use memory-mapped tempfile for more than 128MB
        if fileobject.has_contents() is False:
            return False
        if 0 < fileobject.filesize > 1024 * 1024 * 128:
            import tempfile
            tf = tempfile.NamedTemporaryFile(delete=False)
            tf.close()
            fileobject.savefile(tf.name)
            tf.close()
            with closing(open(tf.name, 'r+')) as tempfile:
                mf = mmap.mmap(tempfile.fileno(), 0, access=mmap.ACCESS_READ)
                return self.seq_pattern_re.search(mf)
        else:
            byte_array = fileobject.contents()
            return self.seq_pattern_re.search(byte_array)


class rule_seq_match(redact_rule):

    """Redacts any sequence that matches the given pattern"""

    lg = Lightgrep()
    accum = HitAccumulator()

    def __init__(self, line, lgpattern):
        redact_rule.__init__(self, line)
        logging.debug("Creating lightgrep-based rule for pattern: "+lgpattern)
        self.lgpattern = lgpattern
        self.complete = False
        pats = [(lgpattern, ['US-ASCII', 'UTF-8', 'UTF-16LE', 'ISO-8859-1'],
                KeyOpts(fixedString=False, caseInsensitive=True))]
        prog, pmap = Lightgrep.createProgram(pats)
        self.lg.createContext(prog, pmap, self.accum.lgCallback)

    def should_redact(self, fileobject):
        hitcount = self.lg.searchBuffer(fileobject.contents(), self.accum)
        return hitcount > 0

    def runs_to_redact(self, fi):
        """Overridden to return the byte runs of just the given text"""
        red_seqs = []
        for h in self.accum.Hits:
            print("hit at (%s, %s) on keyindex %s, pattern is '%s' with encoding chain '%s'" %
                  (str(h.get("start")),
                   str(h.get("end")),
                   str(h.get("keywordIndex")),
                   h.get("pattern"),
                   h.get("encChain")))
            new = True
            for seq in red_seqs:
                if seq[0] == h['start'] and seq[1] == h['end']:
                    new = False
                    break
            if new:
                red_seqs.append((h['start'], h['end']))
        self.lg.reset()
        self.accum.reset()
        return get_runs_for_file_sequences(fi, red_seqs)


class rule_file_seq_equal(rule_seq_match):

    """Redacts any file containing a sequence the equals the given string"""

    def __init__(self, line, text):
        rule_seq_match.__init__(self, line, re.escape(text))

    def runs_to_redact(self, fi):
        """Returns the byte_runs of the source which match the rule.
        By default this is the entire object."""
        return fi.byte_runs()


class rule_seq_equal(rule_seq_match):

    """Redacts a given sequence (string) anywhere it appears in the image"""

    def __init__(self, line, text):
        rule_seq_match.__init__(self, line, re.escape(text))


def get_runs_for_file_sequences(fi, file_sequences):

    '''Converts a list of file offsets into a list of image byte runs. Takes a list of tuples
    containing start, end file offsets'''

    ret = []
    for start, end in file_sequences:
        for run in fi.byte_runs():
            # handle starting point of a sequence
            if start > (run.file_offset + run.len):
                continue  # not starting yet, go to next run
            elif start < run.file_offset:  # started in prior run and not finished
                file_offset = run.file_offset
                img_offset = run.img_offset
            else:  # starting within this run
                file_offset = start
                img_offset = run.img_offset + (start - run.file_offset)

            # handle end of sequence
            if end <= (run.file_offset + run.len):  # sequence ends within run
                len = end - file_offset
                ret.append(
                    byte_run(img_offset=img_offset,
                             len=len,
                             file_offset=file_offset))
            else:  # sequence ends after this run
                len = run.len - (file_offset - run.file_offset)
                ret.append(
                    byte_run(img_offset=img_offset,
                             len=len,
                             file_offset=file_offset))
    return ret

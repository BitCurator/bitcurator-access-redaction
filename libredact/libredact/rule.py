import re
import mmap
import os
from dfxml import byte_run
from contextlib import closing


def convert_fileglob_to_re(fileglob):
    regex = fileglob.replace(".", "[.]").replace("*", ".*").replace("?", ".?")
    return re.compile(regex)


class redact_rule:

    """ Instances of this class are objects that can decide whether or not to redact."""

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

    """ redact if the MD5 matches"""

    def __init__(self, line, val):
        redact_rule.__init__(self, line)
        self.md5val = val.lower()

    def should_redact(self, fi):
        return self.md5val == fi.tag('md5')


class rule_file_sha1(redact_rule):

    """ redact if the SHA1 matches"""

    def __init__(self, line, val):
        redact_rule.__init__(self, line)
        self.sha1val = val.lower()

    def should_redact(self, fi):
        return self.sha1val == fi.tag('sha1')


class rule_file_name_match(redact_rule):

    def __init__(self, line, filepat):
        redact_rule.__init__(self, line)
        # convert fileglobbing to regular expression
        self.filepat_re = convert_fileglob_to_re(filepat)

    def should_redact(self, fileobject):
        return self.filepat_re.search(fileobject.filename())


class rule_file_name_equal(redact_rule):

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

    def __init__(self, line, text):
        redact_rule.__init__(self, line)
        self.text = text
        self.complete = False

    def should_redact(self, fileobject):
        raise ValueError(
            "redaction rule not implemented")

    def runs_to_redact(self, fi):
        """Overridden to return the byte runs of just the given text"""
        # TODO sequences need to account for utf-8 double characters


class rule_file_seq_equal(redact_rule):

    def __init__(self, line, text):
        redact_rule.__init__(self, line)
        self.text = text

    def should_redact(self, fileobject):
        return self.text in fileobject.contents()


class rule_seq_equal(redact_rule):

    def __init__(self, line, text):
        redact_rule.__init__(self, line)
        self.text = text
        self.complete = False           # doesn't redact the entire file

    def should_redact(self, fileobject):
        return self.text in fileobject.contents()

    def runs_to_redact(self, fi):
        """Overridden to return the byte runs of just the given text"""
        ret = []
        tlen = len(self.text)
        for run in fi.byte_runs():
            print(run)
            file_offset = run.file_offset
            run_len = run.len
            img_offset = run.img_offset
            # (file_offset, run_len, img_offset) = run
            run_content = fi.content_for_run(run)
            offset = 0
            # Now find all the places inside "run"
            # where the text "self.text" appears
            # print(("looking for '{}' in '{}'".format(self.text, run)))
            while offset >= 0:
                offset = run_content.find(self.text, offset)
                if offset >= 0:
                    ret.append(
                        byte_run(img_offset=img_offset + offset,
                                 len=tlen,
                                 file_offset=file_offset + offset))
                    offset += 1
        return ret


def get_runs_for_file_sequences(fi, file_sequences):
    ret = []
    tlen = len(self.text)
    for run in fi.byte_runs():
        print(run)
        file_offset = run.file_offset
        run_len = run.len
        img_offset = run.img_offset
        # (file_offset, run_len, img_offset) = run
        run_content = fi.content_for_run(run)
        offset = 0
        # Now find all the places inside "run"
        # where the text "self.text" appears
        # print(("looking for '{}' in '{}'".format(self.text, run)))
        while offset >= 0:
            offset = run_content.find(self.text, offset)
            if offset >= 0:
                ret.append(
                    byte_run(img_offset=img_offset + offset,
                             len=tlen,
                             file_offset=file_offset + offset))
                offset += 1
    return ret

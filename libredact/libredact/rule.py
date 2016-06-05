import re


def convert_fileglob_to_re(fileglob):
    regex = fileglob.replace(".", "[.]").replace("*", ".*").replace("?", ".?")
    return re.compile(regex)


class redact_rule:

    """ Instances of this class are objects that can decide whether or not to redact."""

    def __init__(self, line):
        self.line = line
        self.complete = True               # by default, redacts everything

    def should_redact(self, fileobject):
        """Returns True if this fileobject should be redacted"""
        raise ValueError(
            "redact method of redact_rule super class should not be called")

    def __str__(self):
        return "action<" + self.line + ">"

    def runs_to_redact(self, fi):
        """Returns the byte_runs of the source which match the rule.
        By default this is the entire object."""
        return fi.byte_runs()


class rule_md5(redact_rule):

    """ redact if the MD5 matches"""

    def __init__(self, line, val):
        redact_rule.__init__(self, line)
        self.md5val = val.lower()

    def should_redact(self, fi):
        return self.md5val == fi.tag('md5')


class rule_sha1(redact_rule):

    """ redact if the SHA1 matches"""

    def __init__(self, line, val):
        redact_rule.__init__(self, line)
        self.sha1val = val.lower()

    def should_redact(self, fi):
        return self.sha1val == fi.tag('sha1')


class rule_filepat(redact_rule):

    def __init__(self, line, filepat):
        import re
        redact_rule.__init__(self, line)
        # convert fileglobbing to regular expression
        self.filepat_re = convert_fileglob_to_re(filepat)
        print(("adding rule to redact path " + self.filepat_re.pattern))

    def should_redact(self, fileobject):
        return self.filepat_re.search(fileobject.filename())


class rule_filename(redact_rule):

    def __init__(self, line, filename):
        redact_rule.__init__(self, line)
        self.filename = filename
        print(("adding rule to redact filename " + self.filename))

    def should_redact(self, fileobject):
        was = os.path.sep
        os.path.sep = '/'                       # Force Unix filename conventions
        ret = self.filename == os.path.basename(fileobject.filename())
        os.path.sep = was
        return ret


class rule_dirname(redact_rule):

    def __init__(self, line, dirname):
        redact_rule.__init__(self, line)
        self.dirname = dirname

    def should_redact(self, fileobject):
        was = os.path.sep
        os.path.sep = '/'                      # Force Unix filename conventions
        ret = self.dirname == os.path.dirname(fileobject.filename())
        os.path.sep = was
        return ret


class rule_contains(redact_rule):

    def __init__(self, line, text):
        redact_rule.__init__(self, line)
        self.text = text

    def should_redact(self, fileobject):
        return self.text in fileobject.contents()


class rule_string(redact_rule):

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
            (file_offset, run_len, img_offset) = run

            run_content = fi.content_for_run(run)
            offset = 0
            # Now find all the places inside "run"
            # where the text "self.text" appears
            print(("looking for '{}' in '{}'".format(self.text, run)))
            while offset >= 0:
                offset = run.find(self.text, offset)
                if offset >= 0:
                    ret.append(
                        (file_offset + offset, tlen, img_offset + offset))
                    offset += 1         #
        return ret

# import hashlib
import json
import logging

first = True


class StructuredMessage(object):
    def __init__(self, data):
        self.data = data

    def __str__(self):
        msg = json.dumps(self.data, indent=4)
        global first
        if first:
            first = False
            return '[\n%s,' % msg
        else:
            return '%s,' % msg


_ = StructuredMessage   # to improve readability
audit_logger = logging.getLogger('audit_report')


def endAuditLog():
    audit_logger.info("]")


class redact_action():
    def log(self, fileinfo, rule, commit, rundata):
        data = {}
        data['filename'] = fileinfo.filename()
        data['reason'] = str(rule)
        data['action'] = str(self)
        data['runs'] = rundata
        audit_logger.info(_(data))

    """Instances of this class are objects that specify how a redaction should be done."""

    def redact(self, rule, fi, imagefile, commit):
        """Performs the redaction"""
        raise ValueError(
            "redact method of redact_action super class should not be called")


class action_scrub(redact_action):

    """ Perform redaction by scrub, meaning fill with null character (hex 0x00)"""

    def redact(self, rule, fi, imagefile, commit):
        runlist = []
        val = chr(0)
        for run in rule.runs_to_redact(fi):
            if commit:
                imagefile.seek(run.img_offset)
                imagefile.write(val * run.len)
            runlist.append({'file_offset': run.file_offset,
                            'image_offset': run.img_offset,
                            'length': run.len})
        self.log(fi, rule, commit, runlist)

    def __str__(self):
        return 'Scrub (fill with null char, %s)' % '0x00'


class action_fill(redact_action):

    """ Perform redaction by filling"""

    def __init__(self, val):
        self.fillvalue = val

    def redact(self, rule, fi, imagefile, commit):
        runlist = []
        for run in rule.runs_to_redact(fi):
            if commit:
                imagefile.seek(run.img_offset)
                imagefile.write(chr(self.fillvalue) * run.len)
            runlist.append({'file_offset': run.file_offset,
                            'image_offset': run.img_offset,
                            'length': run.len})
        self.log(fi, rule, commit, runlist)

    def __str__(self):
        return 'Fill with %s' % hex(self.fillvalue)


class action_fuzz(redact_action):

    """ Perform redaction by fuzzing x86 instructions """

    def redact(self, rule, fi, imagefile, commit):
        '''
        The net effect of this function is that bytes 127-255 are "fuzzed" over
        the range of 159-191, with each series of four bytes
        (e.g. 128-131) to one byte value (e.g. 160).
        '''
        runlist = []

        def fuzz(ch):
            o = ord(ch)
            if(o < 127):
                r = ch
            else:
                r = chr(((o >> 2) + 128) % 256)
            return r
        for run in rule.runs_to_redact(fi):
            try:
                imagefile.seek(run.img_offset)

                # Previously redacted only first 10 bytes, now redacts entire sequence
                # first_ten_bytes = rc.imagefile.read(10)
                run_bytes = imagefile.read(run.len)
                newbytes = "".join([fuzz(x) for x in run_bytes])
                assert(len(newbytes) == run.len)
                if commit:
                    imagefile.seek(run.img_offset)
                    imagefile.write(newbytes)
                runlist.append({'file_offset': run.file_offset,
                                'image_offset': run.img_offset,
                                'length': run.len})
            except AttributeError:
                logging.warn("!AttributeError: no byte run?")
        self.log(fi, rule, commit, runlist)

    def __str__(self):
        return 'Fuzz'

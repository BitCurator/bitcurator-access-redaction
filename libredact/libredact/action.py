# import hashlib
import json
import logging


class StructuredMessage(object):
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return '%s' % json.dumps(self.data)

_ = StructuredMessage   # to improve readability
audit_logger = logging.getLogger('audit_report')


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


class action_fill(redact_action):

    """ Perform redaction by filling"""

    def __init__(self, val):
        self.fillvalue = val

    def redact(self, rule, fi, imagefile, commit):
        runlist = []
        for run in rule.runs_to_redact(fi):
            imagefile.seek(run.img_offset)
            # print("\tFile info - \n\t\tname: %s\n\t\tclosed: %s \n\t\tposition: %d \n\t\tmode: %s"
            #      % (imagefile.name, imagefile.closed, imagefile.tell(), imagefile.mode))
            # print(
            #    ("   Filling at offset {}, {} bytes with pattern {}"
            #     .format(run.img_offset, runlen, hex(self.fillvalue))))
            if commit:
                imagefile.seek(run.img_offset)
                imagefile.write(chr(self.fillvalue) * run.len)
            runlist.append({'file_offset': run.file_offset,
                            'image_offset': run.img_offset,
                            'length': run.len})
        self.log(fi, rule, commit, runlist)

    def __str__(self):
        return 'Fill with %s' % hex(self.fillvalue)


class action_encrypt(redact_action):

    """ Perform redaction by encrypting"""

    def redact(self, rule, fi, imagefile, commit):
        runlist = []
        for run in rule.runs_to_redact(fi):
            print(
                ("   encrypting at offset {}, {} bytes with cipher"
                 .format(run.img_offset, run.bytes)))
            raise ValueError("Whoops; Didn't write this yet")
            runlist.append({'file_offset': run.file_offset,
                            'image_offset': run.img_offset,
                            'length': run.len})
        self.log(fi, rule, commit, runlist)


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
        print("Redacting with FUZZ: ", fi)
        for run in rule.runs_to_redact(fi):
            try:
                print("   Fuzzing at offset: %d, can fuzz up to %d bytes " %
                      (run.img_offset, run.len))
                imagefile.seek(run.img_offset)

                # Previously redacted only first 10 bytes, now redacts entire sequence
                # first_ten_bytes = rc.imagefile.read(10)
                run_bytes = imagefile.read(run.len)

                print(("\tFile info - \n\t\tname: %s  \n\t\tclosed: %s \n"
                      "\t\tposition: %d \n\t\tmode: %s") %
                      (imagefile.name, imagefile.closed, imagefile.tell(), imagefile.mode))
                print("    Fuzzing %d bytes - should be %d" %
                      (len(run_bytes), run.len))
                newbytes = "".join([fuzz(x) for x in run_bytes])
                # debug
                print("new: %i old: %i" % (len(newbytes), run.len))
                assert(len(newbytes) == run.len)
                if commit:
                    imagefile.seek(run.img_offset)
                    imagefile.write(newbytes)
                    print("\n   >>COMMIT")
                runlist.append({'file_offset': run.file_offset,
                                'image_offset': run.img_offset,
                                'length': run.len})
            except AttributeError:
                print("!AttributeError: no byte run?")
        self.log(fi, rule, commit, runlist)

    def __str__(self):
        return 'Fuzz'

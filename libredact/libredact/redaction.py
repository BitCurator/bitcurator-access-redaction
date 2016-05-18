# import hashlib


class redact_action():

    """Instances of this class are objects that specify how a redaction should be done."""

    def redact(self, rule, fileobject, rc):
        """Performs the redaction"""
        raise ValueError(
            "redact method of redact_action super class should not be called")


class action_fill(redact_action):

    """ Perform redaction by filling"""

    def __init__(self, val):
        self.fillvalue = val

    def redact(self, rule, fi, rc):
        for run in rule.runs_to_redact(fi):
            print(("   Current run %s " % run))
            rc.imagefile.seek(run.img_offset)
            runlen = run.len
            print("\tFile info - \n\t\tname: %s  \n\t\tclosed: %s \n\t\tposition: %d \n\t\tmode: %s" %
                  (rc.imagefile.name, rc.imagefile.closed, rc.imagefile.tell(), rc.imagefile.mode))
            print(
                ("   Filling at offset {}, {} bytes with pattern {}".format(run.img_offset, runlen, hex(self.fillvalue))))
            if rc.commit:
                rc.imagefile.seek(run.img_offset)
                rc.imagefile.write(chr(self.fillvalue) * run.len)
                print("   >>COMMIT\n")


class action_encrypt(redact_action):

    """ Perform redaction by encrypting"""

    def redact(self, rule, fileobject, rc):
        for run in rule.runs_to_redact(fileobject):
            print(
                ("   encrypting at offset {}, {} bytes with cipher".format(run.img_offset, run.bytes)))
            raise ValueError("Whoops; Didn't write this yet")


class action_fuzz(redact_action):

    """ Perform redaction by fuzzing x86 instructions """

    def redact(self, rule, fileobject, rc):
        '''
        The net effect of this function is that bytes 127-255 are "fuzzed" over
        the range of 159-191, with each series of four bytes
        (e.g. 128-131) to one byte value (e.g. 160).
        '''
        def fuzz(ch):
            o = ord(ch)
            if(o < 127):
                r = ch
            else:
                r = chr(((o >> 2) + 128) % 256)
            return r
        print("Redacting with FUZZ: ", fileobject)
        for run in rule.runs_to_redact(fileobject):
            try:
                print("   Fuzzing at offset: %d, can fuzz up to %d bytes " %
                      (run.img_offset, run.len))
                rc.imagefile.seek(run.img_offset)

                # Previously redacted only first 10 bytes, now redacts entire sequence
                # first_ten_bytes = rc.imagefile.read(10)
                run_bytes = rc.imagefile.read(run.len)

                print("\tFile info - \n\t\tname: %s  \n\t\tclosed: %s \n\t\tposition: %d \n\t\tmode: %s" %
                      (rc.imagefile.name, rc.imagefile.closed, rc.imagefile.tell(), rc.imagefile.mode))
                print("    Fuzzing %d bytes - should be %d" %
                      (len(run_bytes), run.len))
                newbytes = "".join([fuzz(x) for x in run_bytes])
                # debug
                print("new: %i old: %i" % (len(newbytes), run.len))
                assert(len(newbytes) == run.len)
                if rc.commit:
                    rc.imagefile.seek(run.img_offset)
                    rc.imagefile.write(newbytes)
                    print("\n   >>COMMIT")
            except AttributeError:
                print("!AttributeError: no byte run?")

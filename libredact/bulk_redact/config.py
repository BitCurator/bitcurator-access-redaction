from os import path, listdir
import logging
from contextlib import closing
from libredact.action import action_fill
from libredact.rule import redact_rule
import sqlite3
from tempfile import NamedTemporaryFile
from dfxml import byte_run


supported_feature_file_versions = ['1.1']
included_reports = [
    "email.txt",
    "telephone.txt",
    "ip.txt",
    "domain.txt",
    "ccn.txt",
    "elf.txt",
    "aes_keys.txt",
    "gps.txt",
    "hex.txt",
    "httplogs.txt",
    "pii.txt",
    "url.txt",
    "vcard.txt"
]


def parse(mypath, fillbyte):
    """Builds a Redaction configuration dictionary, based on annotated bulk extractor reports. If
    passed a folder it will parse a file (email.txt) within for configuration details."""
    conf = {}
    feature_files = None
    if not path.exists(mypath):
        raise Exception("The path %s is reachable." % mypath)

    if path.isdir(mypath):
        feature_files = [path.join(mypath, p) for p in listdir(mypath)
                         if path.isfile(path.join(mypath, p)) and p in included_reports]
        mypath = path.join(mypath, listdir(mypath)[0])
    else:
        feature_files = [mypath]

    # Gather input image file from one of the file headers
    with closing(open(mypath, "r")) as handle:
        for line in handle:
            if not line.startswith('#'):
                break
            line = line[2:]  # strip off comment marker

            if line.startswith('Filename:'):
                input_file = line[10:].strip()
                conf['input_file'] = input_file
                conf['output_file'] = input_file + ".redacted"
                logging.debug('Found image file path: %s' % input_file)

            elif line.startswith('Feature-File-Version:'):
                feature_file_ver = line[21:].strip()
                if feature_file_ver not in supported_feature_file_versions:
                    logging.warn('Feature file version %s is not recognized. '
                                 'This can have unpredictable results. '
                                 'Please update your install of bca-redtools.')

    # create custom redaction rule per feature file
    rules = []
    for feature_file in feature_files:
        target = rule_feature_file_match(feature_file)
        if target is not None:
            rules.append((target, action_fill(fillbyte)))
    conf['rules'] = rules
    conf['commit'] = True
    return conf


class rule_feature_file_match(redact_rule):

    """Redacts any sequence that is mentioned in the feature file"""

    def __init__(self, file):
        redact_rule.__init__(self, "Feature File: %s" % str(file))
        self.feature_file = file
        logging.debug("Creating feature file matching rule: %s" % str(file))
        self.complete = False
        self.create_db()
        self.handle = open(file)
        # i = [l.split('\t')[0, 1] for l in self.handle if not l.startswith('#')]
        with closing(self.db.cursor()) as cursor:
            def myiter(itr):
                for x in itr:
                    if x.startswith('#') or len(x.strip()) == 0:
                        continue
                    else:
                        atoms = x.split('\t')
                        yield (atoms[0], atoms[1], len(atoms[1]))
            cursor.executemany("INSERT INTO feature (_offset, literal, length) values (?, ?, ?);",
                               myiter(self.handle))
        self.handle.close()

    def create_db(self):
        tmp = NamedTemporaryFile(delete=False)
        dbpath = tmp.name
        tmp.close()
        self.db = sqlite3.connect(dbpath)
        with closing(self.db.cursor()) as cursor:
            cursor.execute("DROP TABLE IF EXISTS feature")
            sql = '''CREATE TABLE feature (
                    literal TEXT,
                    _offset INT,
                    length INT
                    );'''
            cursor.execute(sql)
            cursor.execute("CREATE INDEX offset_index ON feature (_offset);")

    def should_redact(self, fi):
        with closing(self.db.cursor()) as cursor:
            self.file_features = []
            for run in fi.byte_runs():
                cursor.execute(
                    "SELECT _offset, length FROM feature WHERE _offset BETWEEN ? AND ?;",
                    (run.img_offset, run.img_offset + run.len))
                self.file_features.extend(cursor.fetchall())
        return len(self.file_features) > 0

    def runs_to_redact(self, fi):
        """Overridden to return the byte runs of just the given text"""
        ret = []
        for (offset, length) in self.file_features:
            ret.append(
                byte_run(img_offset=int(offset),
                         len=int(length),
                         file_offset="n/a"))
        return ret

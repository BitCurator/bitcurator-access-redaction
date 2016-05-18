'''Parser(s) for sredact configuration files
'''

from libredact.rule import rule_md5, rule_sha1, rule_string, rule_filepat, rule_filename, \
    rule_contains
from libredact.redaction import action_fill, action_fuzz, action_encrypt


class RedactConfigParser:

    """Class to read and parse a redaction config file"""

    def parse(filepath):
        result = {
          'rules': [],
          'COMMIT': False,
          'IMAGE_FILE': None,
          'DFXML_FILE': None,
          'REPORT_FILE': None,
          'KEY': None,
          'IGNORE_PATTERNS': []
        }

        for line in open(filepath, "r"):
            if line[0] in '#;':
                continue       # comment line
            line = line.strip()
            if line == "":
                continue
            atoms = line.split(" ")
            while "" in atoms:
                atoms.remove("")  # take care of extra spaces
            cmd = atoms[0].upper()
            rule = None
            action = None

            # First look for simple commands
            if cmd == 'KEY':
                result['KEY'] = atoms[1]
                continue

            if cmd == "COMMIT":
                result['COMMIT'] = True
                continue

            if cmd == "IMAGE_FILE":
                result['IMAGE_FILE'] = atoms[1]
                continue

            if cmd == "DFXML_FILE":
                result['DFXML_FILE'] = atoms[1]
                continue

            if cmd == 'IGNORE':
                result['IGNORE_PATTERNS'].append(atoms[1])
                continue

            # Now look for commands that are rules

            if cmd == 'MD5':
                rule = rule_md5(line, atoms[1])
            if cmd == 'SHA1':
                rule = rule_sha1(line, atoms[1])
            if cmd == 'FILENAME':
                rule = rule_filename(line, atoms[1])
            if cmd == 'FILEPAT':
                rule = rule_filepat(line, atoms[1])
            if cmd == 'CONTAINS':
                rule = rule_contains(line, atoms[1])
            if cmd == 'STRING':
                rule = rule_string(line, atoms[1])

            if rule:
                if atoms[2].upper() == 'FILL':
                    action = action_fill(eval(atoms[3]))
                if atoms[2].upper() == 'ENCRYPT':
                    action = action_encrypt()
                if atoms[2].upper() == 'FUZZ':
                    action = action_fuzz()

            if not rule or not action:
                print("atoms:", atoms)
                print("rule:", rule)
                print("action:", action)
                raise ValueError("Cannot parse: '%s'" % line)

            result.get('rules').append((rule, action))
        return result

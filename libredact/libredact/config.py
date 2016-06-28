'''Parser(s) for sredact configuration files
'''

from libredact.rule import rule_md5, rule_sha1, rule_string, rule_filepat, rule_filename, \
    rule_contains
from libredact.action import action_fill, action_fuzz, action_encrypt


def parse(filepath):
    result = {
      'rules': [],
      'commit': False,
      'image_file': None,
      'dfxml_file': None,
      'report_file': None,
      'key': None,
      'ignore_patterns': []
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
            result['key'] = atoms[1]
            continue

        if cmd == "COMMIT":
            result['commit'] = True
            continue

        if cmd == "IMAGE_FILE":
            result['image_file'] = atoms[1]
            continue

        if cmd == "REPORT_FILE":
            result['report_file'] = atoms[1]
            continue

        if cmd == "DFXML_FILE":
            result['dfxml_file'] = atoms[1]
            continue

        if cmd == 'IGNORE':
            result['ignore_patterns'].append(atoms[1])
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

'''Parser(s) for redact-cli configuration files
'''

from libredact.rule import rule_file_md5, rule_file_sha1, rule_file_name_match, \
    rule_file_name_equal, rule_file_dirname_equal, rule_file_seq_match, rule_file_seq_equal, \
    rule_seq_equal, rule_seq_match
from libredact.action import action_fill, action_fuzz, action_scrub


def parse(filepath):
    handle = open(filepath, "r")
    return parsehandle(handle)


def parsehandle(handle):
    result = {
      'rules': [],
      'commit': False,
      'input_file': None,
      'dfxml_file': None,
      'report_file': None,
      'key': None,
      'ignore_patterns': []
    }

    for line in handle:
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

        if cmd == "INPUT_FILE":
            result['input_file'] = atoms[1]
            continue

        if cmd == "OUTPUT_FILE":
            result['output_file'] = atoms[1]
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

        if cmd in ['FILE_MD5', 'MD5']:
            rule = rule_file_md5(line, atoms[1])
        if cmd in ['FILE_SHA1', 'SHA1']:
            rule = rule_file_sha1(line, atoms[1])
        if cmd in ['FILE_NAME_EQUAL', 'FILENAME']:
            rule = rule_file_name_equal(line, atoms[1])
        if cmd in ['FILE_NAME_MATCH', 'FILEPAT']:
            rule = rule_file_name_match(line, atoms[1])
        if cmd in ['FILE_DIRNAME_EQUAL', 'DIRNAME']:
            rule = rule_file_dirname_equal(line, atoms[1])
        if cmd in ['FILE_SEQ_EQUAL', 'CONTAINS']:
            rule = rule_file_seq_equal(line, atoms[1])
        if cmd in ['FILE_SEQ_MATCH', 'MATCH']:
            rule = rule_file_seq_match(line, atoms[1])
        if cmd == 'SEQ_MATCH':
            rule = rule_seq_match(line, atoms[1])
        if cmd in ['SEQ_EQUAL', 'STRING']:
            rule = rule_seq_equal(line, atoms[1])

        if rule:
            if atoms[2].upper() == 'FILL':
                action = action_fill(eval(atoms[3]))
            # if atoms[2].upper() == 'ENCRYPT':
            #    action = action_encrypt()
            if atoms[2].upper() == 'FUZZ':
                action = action_fuzz()
            if atoms[2].upper() == 'SCRUB':
                action = action_scrub()

        if not rule or not action:
            print("atoms:", atoms)
            print("rule:", rule)
            print("action:", action)
            raise ValueError("Cannot parse: '%s'" % line)

        result.get('rules').append((rule, action))
    return result


def parse_abe(filepath):
    handle = open(filepath, "r")
    result = []
    for line in handle:
        if line[0] in '#;':
            continue       # comment line
        line = line.strip()
        if line == "":
            continue
        atoms = line.split("\t")
        if len(atoms) < 5:
            import logging
            logging.debug(line)
        rule = rule_file_md5(line, atoms[4])
        result.append((rule, action_scrub()))
    return result

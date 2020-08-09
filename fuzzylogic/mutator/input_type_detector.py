import sys
import json
import xml.etree.ElementTree as ET
import csv


RET_FAIL = 0
RET_JSON = 1
RET_XML = 2
RET_CSV = 3
RET_MULTILINE_TEXT = 4


def detect(s):
    if is_json(s) != RET_FAIL:
        return RET_JSON
    elif is_xml(s) != RET_FAIL:
        return RET_XML
    elif is_csv(s) != RET_FAIL:
        return RET_CSV
    elif is_multiline_text(s) != RET_FAIL:
        return RET_MULTILINE_TEXT
    else:
        return RET_MULTILINE_TEXT


def is_json(s):
    try:
        json.loads(s)
    except json.JSONDecodeError:
        return RET_FAIL

    return RET_JSON


def is_xml(s):
    try:
        ET.fromstring(s)
    except ET.ParseError:
        return RET_FAIL

    return RET_XML


def is_csv(s):
    try:
        csv.Sniffer().sniff(s, ',')
        # print(f"Does this csv have a header: {csv.Sniffer().has_header(s)}")
        # Perform various checks on the dialect (e.g., lineseparator,
        # delimiter) to make sure it's sane
    except csv.Error:
        return RET_FAIL

    return RET_CSV


def is_multiline_text(s):
    arr = s.split('\n')
    if len(arr) < 2:
        return RET_FAIL
    elif len(arr) == 2 and arr[1] == "":
        return RET_FAIL
    return RET_MULTILINE_TEXT


if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise ValueError('Please provide an input file')

    file_name = sys.argv[1]

    print(f'input name: {file_name}')

    with open(file_name, 'r') as f:
        input_string = f.read()

    print(f'File contents: {input_string}')

    print('Json: T') if is_json(input_string) != RET_FAIL else print('Json: F')
    print('Xml: T') if is_xml(input_string) != RET_FAIL else print('Xml: F')
    print('Csv: T') if is_csv(input_string) != RET_FAIL else print('Csv: F')
    print('Multiline text: T\nSingleline text: F') if is_multiline_text(input_string) != RET_FAIL else print('Multiline text: F\nSingleline text: T')
    
    if is_json(input_string) != RET_FAIL:
        print(f"{file_name} is of type JSON")

    elif is_xml(input_string) != RET_FAIL:
        print(f"{file_name} is of type XML")
    
    elif is_csv(input_string) != RET_FAIL:
        print(f"{file_name} is of type CSV")

    elif is_multiline_text(input_string) != RET_FAIL:
        print(f"{file_name} is of type multiline text")
    
    else:
        print(f"{file_name} is of type singleline text")

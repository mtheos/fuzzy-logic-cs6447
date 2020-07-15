
import sys
import json
import xml.etree.ElementTree as ET
import csv


RET_FAIL = 0
RET_JSON = 1
RET_XML = 2
RET_CSV = 3
RET_MULTILINE_TEXT = 4


def isJson(s):
    try:
        json_input = json.loads(s)
    except json.JSONDecodeError as err:
        # print(f"Json ERR: {err}") 
        return RET_FAIL
    
    return RET_JSON

def isXml(s):
    try:
        root = ET.fromstring(s)
    except ET.ParseError as err:
        # print(f"Xml ERR: {err}") 
        return RET_FAIL
    
    return RET_XML

def isCsv(s):
    # IO_string = StringIO(string)
    # df = pd.read_csv(IO_string, sep=",")
    # print(df)
    try:
        dialect = csv.Sniffer().sniff(s,',')
        # print(f"Does this csv have a header: {csv.Sniffer().has_header(s)}")
        # Perform various checks on the dialect (e.g., lineseparator,
        # delimiter) to make sure it's sane
    except csv.Error as err:
        print(f"Csv ERR: {err}")
        return RET_FAIL
    
    return RET_CSV

def isMultilineText(s):
    arr = s.split('\n')
    # print(arr)
    if len(arr) < 2:
        return RET_FAIL
    elif len(arr) == 2 and arr[1] == "":
        return RET_FAIL
    
    return RET_MULTILINE_TEXT
    

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise ValueError('Please provide an input file')

    file_name = sys.argv[1]

    print(f"input name: {file_name}")

    input_string = ''

    with open(file_name, 'r') as f:
        input_string = f.read()

    print(f"File contents: {input_string}")

    print('Json: T') if isJson(input_string) != RET_FAIL else print('Json: F')
    print('Xml: T') if isXml(input_string) != RET_FAIL else print('Xml: F')
    print('Csv: T') if isCsv(input_string) != RET_FAIL else print('Csv: F')
    print('Multiline text: T') if isMultilineText(input_string) != RET_FAIL else print('Multiline text: F')
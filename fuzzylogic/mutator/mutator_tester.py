import sys
import json
import random
sys.path.append('../../')
__name__ = 'fuzzylogic.mutator.mutator_tester'
__package__ = 'fuzzylogic.mutator'
print(__name__)
print(__package__)

import re
from .xml_mutator import XmlMutator
import xml.etree.ElementTree as ET
import xmltodict
from collections import OrderedDict


def _get_type_(v):
    if _is_int_(v):
        return int
    elif _is_float_(v):
        return float
    raise TypeError(f'*** {v} is an unhandled type ***')


def _is_float_(v):
    try:
        float(v)
        return True
    except ValueError:
        return False


def _is_int_(v):
    try:
        int(v)
        return True
    except ValueError:
        return False


mut = XmlMutator()

string = '''<html>
    <head>
        <link href="http://somewebsite.com" />
    </head>
    <body>
        <h1>I'm not a web developer.</h1>
    </body>

    <div id="#lol">
        <a href="http://google.com">Here is some link...</a>
    </div>


    <tail>
        <a href="http://bing.com">Footer link</a>
    </tail>
</html>
'''

# print(xmltodict.unparse(xmltodict.parse("""
#     <mydocument has="an attribute">
#       <and>
#         <many new="wow">elements</many>
#         <many>more elements
#         </many>
#       </and>
#       <plus a="complex">
#         element as well
#       </plus>
#       <lol></lol>
#     </mydocument>
#     """)))

original = """
    <mydocument has="an attribute">
      <and>
        <many new="wow">elements</many>
        <many>55.55</many>
        <many>69</many>
        <many></many>
      </and>
      <plus a="complex">
        element as well
      </plus>
      <lol id="lol"></lol>
      <yay>False</yay>
      <empty>helloo</empty>
    </mydocument>
    """


# test = """
#     <and>
#         <many new="wow">elements</many>
#         <many>55.55</many>
#         <many>69</many>
#     </and>
#     """

# xml_dict = xmltodict.parse(original)

for i in range(200):
    mut.mutate(original)

# rand_index = random.choice(range(5))
# print(rand_index)
# mut.mutate(original)

# dictyy = OrderedDict()
# dictyy["lol"] = 1
# dictyy["@atty"] = 2 
# dictyy["#text"] = 3 

# print(dictyy.items())

# dictyy2 = OrderedDict()
# dictyy2["wow"] = 15
# dictyy2["@onettty"] = 22 
# dictyy2["#text"] = 33 

# listy = [dictyy, dictyy2]
# print("\n".join(mut._mutate_ordered_dict(dictyy)))
# print(mut._mutate_ordered_dict(xml_dict))
# print(mut._mutate_list(listy))

# dicty = {
#     "lol": { 
#         "atty": 3,
#         "atty2": 4,
#         "lol2": 2,
#         "text": 2,
#     },
# }

def recurse(item):
    if type(item) is dict:
        for k,v in item.items():
            print('k = ', k, ' v = ', v)
            # og_v = dict(v)
            item[k] = 'whack'
            print(dicty)
            item[k] = v
            recurse(v)
    else:
        print('item = ', item)

# recurse(dicty)
        


string ='hell1123 wow 32yes, how is lif3 so do32.22'

def split_string_by_types(string):
    print(f"\n{string}")

    nums = re.findall(r'-?\d+\.?\d*',string)
    nums = [_get_type_(x)(x) for x in nums]

    str_broken = []
    for num in nums:
        str_broken.append(string[:string.index(str(num))])
        str_broken.append(num)
        minimum = string.index(str(num)) + len(str(num))
        string = string[minimum:]
        # print(num)
        # str_broken.append()
        # print(str_broken)

    # print(str_broken)
    return str_broken
# print("\n".join(ints))

# print(split_string_by_types(string))

# listy = [1,2,3,4,5]

# print("\n".join([x for x in dicty.keys() if x[0] == '@']))
# print("\n".join([x for x in dicty.keys() if x[0] != '@' and x[0] != '#']))

# v = '65.32323'
# v_type = _get_type_(v)
# typed_v = v_type(v)
# print(type(typed_v))

# # del original["mydocument"]["plus"]["#text"]
# original["mydocument"]["and"]["many"][1] = {"#text": "new one baby"}

# print(original)

# back = xmltodict.unparse(original)
# print(back)

# original = ET.fromstring(string)
# print("******")
# print(ET.tostring(original))
# print("******")
# head = original.iter()
# next_node = head
# for i, node in enumerate(head):
#     tmp_text = str(node.text)
#     tmp_attrib = dict(node.attrib)
    
#     node.text = "lol"
#     node.set('new','changed')
#     print(f"{i}: {ET.tostring(original).decode()}")
    
#     node.text = tmp_text
#     node.attrib = tmp_attrib

# print(ET.tostring(original))
# next_node

# mut.mutate(string)

# mut = StringMutator()
# print(mut.meme_mutation(5.0))
# string = "hello"
# for i in range(16):
#     string = mut.mutate(string)
#     print(string)

# mut = StringMutator()
# csv = [[1,2,3],['lol','yay',4]]
# print(mut._meme_mutation_(string))

# print("---- Turn right")
# print("---- Another comment")

# print(1+1)
# print("What's your name?")

# name = input()

# print("Hi "+ name)
# print("how was your day")
# day = input()

# print(string)

# infinity = float('Infinity')
# print(type(infinity))
# # infinity -= 100000
# print(infinity)

# lol = {"wow":infinity}

# lol2 = json.dumps(lol)

# print(lol2)

# string = "asdfghjkl"

# mut = StringMutator()
# final = string
# for i in range(0,15):
#     final = mut.mutate(final)
#     print(f"{i}: {final}")

# num = 246
# mut = FloatMutator()
# final = num
# for i in range(0,15):
#     final = mut.mutate(final)
#     print(f"{i}: {final}")

# result =  False
# mut = BooleanMutator()
# print(mut.mutate(result))

# dictionary = {"Arushi" : 'lolz', "Anuradha" : 21, "Mani" : 21, "Haritha" : 21} 

# lol = ObjectMutator()

# print(f"== {dictionary} == ")
# mutation = dictionary
# for i in range(2):
#     mutation = lol.mutate(dictionary)
#     print(mutation)

# lis = [1, 2, 3]
# l_mutator = ListMutator()
# mutation = lis
# for i in range(10):
#     mutation = l_mutator.mutate(mutation)
#     print(mutation)
import random
import xml
# import json
# import xml.etree.ElementTree as ET
import xmltodict
from collections import OrderedDict
from .int_mutator import IntMutator
from .float_mutator import FloatMutator
from .string_mutator import StringMutator
from .boolean_mutator import BooleanMutator
from .complex_mutators import ListMutator, ObjectMutator
from ..strategy import Strategy

class XmlMutator:
    def __init__(self):
        self._seed = 0
        self._original = None   # xml tree
        self._yields = []       # yileds to yield
        self._strategy = None   # strat
        self._mutators = {str:StringMutator(),int:IntMutator(),float:FloatMutator(),bool:BooleanMutator()}

    """
    Go through each node and mutate it...

    Original mutate logic: mutate a leaf node
    Current mutate logic: mutate a node by:
     - mutate attribute value
     - mutate text
     - add attr (new)
     - add text (when there wasn't previously one)
     - remove att
     - remove text

    Return to string format using ET.tostring(root_node)
    """

    def mutate(self, xml_input, strategy='none'):
        self._yields = []
        try:
            self._analyse_(xml_input)
        except xml.parsers.expat.ExpatError: # parser cannot parse input, ignore this input
            return []
        self._preprocessing_recurse_(self._original)
        # print(self._original)
        self._strategy = strategy
        self.recurse(self._original)
        for y in self._yields:
            # print(y)
            yield y
        # return self._yields

    """
    Parses string input
    """
    def _analyse_(self, _input):
        self._original = xmltodict.parse(_input,process_namespaces=True)
    
    """
    Some preprocessing to make adding/removing attributes/text easier
    """
    def _preprocessing_recurse_(self, original):
        if type(original) is OrderedDict:
            for k,v in original.items():
                if type(v) is str and (k[0] != '@' and k[0] != '#'):
                    original[k] = OrderedDict()
                    original[k]["#text"] = v
                self._preprocessing_recurse_(v)
                
        elif type(original) is list:
            for k in range(len(original)):
                v = original[k]
                if type(v) is str:
                    original[k] = OrderedDict()
                    original[k]["#text"] = v
                elif type(v) is OrderedDict:
                    self._preprocessing_recurse_(v)
                elif type(v) is list:
                    self._preprocessing_recurse_(v)
        
    """
    Recurse through the xml and mutate the following:
     * individual types:
        - finding the type
        - calling the right mutator
     * A None mutator
        - creates a filled element
     * OrderedDict mutator
     * List mutator
     * stategies:
        - Add/remove elements functionality
    """
    def recurse(self, original):
        if type(original) is OrderedDict:
            # if (self._strategy == Strategy.ADD_DICTS): #badly named. adds members to dict.
            #     for i in range(Strategy.members_to_add_to_dict): #who cares if we overwrite existing shit
            #         original["tag"+str(i)] ={"#text":"some nice cool sample meme"}
            #     self._yields.append(xmltodict.unparse(self._original, full_document=False))
            #     for i in range(Strategy.members_to_add_to_dict):
            #         del original["tag"+str(i)]
            
            for k,v in original.items():
                if type(v) is OrderedDict:
                    for mutation in self._mutate_ordered_dict(OrderedDict(v)):
                        original[k] = OrderedDict(mutation)
                        # print(f"*********Dict mutation on {k}:\n++++++"+xmltodict.unparse(self._original, full_document=False))
                        # print(mutation,'\n')
                        self._yields.append(xmltodict.unparse(self._original, full_document=False))
                        original[k] = v
                    self.recurse(v)
                elif type(v) is list:
                    for mutation in self._mutate_list(list(v)):
                        original[k] = list(mutation)
                        # print(f"List mutation on {v}:\n++"+xmltodict.unparse(self._original, full_document=False))
                        # print(mutation)
                        self._yields.append(xmltodict.unparse(self._original, full_document=False))
                        original[k] = v
                    self.recurse(v)
                elif v is None:
                    original[k] = self._get_sample_element_()
                    # print("new Elem: "+xmltodict.unparse(self._original, full_document=False))
                    self._yields.append(xmltodict.unparse(self._original, full_document=False))
                    original[k] = None
                else: # mutate a type (int, string, float)
                    v_type = self._get_type_(v)
                    typed_v = v_type(v)
                    original[k] = str(self._fat_type_mutation_(self._mutators[v_type],typed_v))
                    # print(f"type {v_type} mutation on '{v}': "+ xmltodict.unparse(self._original, full_document=False))
                    # print(mutation)
                    self._yields.append(xmltodict.unparse(self._original, full_document=False))
                    original[k] = v

        elif type(original) is list:
            for k in range(len(original)):
                v = original[k]
                if type(v) is OrderedDict:
                    for mutation in self._mutate_ordered_dict(OrderedDict(v)):
                        original[k] = OrderedDict(mutation)
                        # print(f"*********Dict mutation on {k}:\n++++++"+xmltodict.unparse(self._original, full_document=False))
                        # print(mutation)
                        self._yields.append(xmltodict.unparse(self._original, full_document=False))
                        original[k] = v
                    self.recurse(v)
                elif type(v) is list:
                    for mutation in self._mutate_list(list(v)):
                        original[k] = list(mutation)
                        # print(f"List mutation on {v}:\n++"+xmltodict.unparse(self._original, full_document=False))
                        # print(mutation)
                        self._yields.append(xmltodict.unparse(self._original, full_document=False))
                        original[k] = v
                    self.recurse(v)
                elif v is None:
                    original[k] = self._get_sample_element_()
                    # print("new Elem: "+xmltodict.unparse(self._original, full_document=False))
                    self._yields.append(xmltodict.unparse(self._original, full_document=False))
                    original[k] = None
                    
            
    
    """
    Performs each of these mutations on the ordred dict
    and returns an array of these mutations:
        1. Add attribute
        2. Remove attribute
        3. Add text (if doesn't exist)
        4. Remove text
        5. Add element
        6. Remove Element
    """
    def _mutate_ordered_dict(self, v):
        mutations = []
        original = OrderedDict(v)
        
        # add attribute
        for i in range(random.randint(1,15)):
            v["@new_att_"+str(self._seed)] = "new_att_value_"+str(self._seed)
            self._seed += 1
        mutations.append(OrderedDict(v))
        v = OrderedDict(original)
        
        # remove random attribute
        elem_att = [key for key in v.keys() if key[0] == '@']
        if len(elem_att) > 0:
            random_key = random.choice(elem_att)
            del v[random_key]
            mutations.append(OrderedDict(v))
            v = OrderedDict(original)

        # Enumerate removal of attributes
        # for key in [key for key in v.keys() if key[0] == '@']:
        #     del v[key]
        #     mutations.append(OrderedDict(v))
        #     v = OrderedDict(original)
        
        # add text
        if '#text' not in v.keys():
            string = "sample_attr"
            v['#text'] = self._fat_type_mutation_(self._mutators[str],string)
            
            mutations.append(OrderedDict(v))
            v = OrderedDict(original)
        
        # remove text
        if '#text' in v.keys():
            del v['#text']
            mutations.append(OrderedDict(v))
            v = OrderedDict(original)
        
        # add element FOR THE MEMES
        for i in range(random.randint(1,200)):
            v["new_element_"+str(self._seed)] = self._get_sample_element_()
            self._seed += 1
        mutations.append(OrderedDict(v))
        v = OrderedDict(original)
        
        # remove random element
        elem_list = [key for key in v.keys() if key[0] != '@' and key[0] != '#']
        # for i in range(random.randint(0,int(len(elem_list)/2))):
        if len(elem_list) > 0:
            random_key = random.choice(elem_list)
            del v[random_key]
            mutations.append(OrderedDict(v))
            v = OrderedDict(original)

        # remove element
        # for key in [key for key in v.keys() if key[0] != '@' and key[0] != '#']:
        #     del v[key]
        #     mutations.append(OrderedDict(v))
        #     v = OrderedDict(original)

        self._seed += 1
        return mutations

    """
    Performs each of these mutations on the list of OrderedDicts
    and returns an array of these mutations:
        1. Add new sample element (OrderedDict)
        2. Remove Element
    """
    def _mutate_list(self, v):
        mutations = []
        original = list(v)

        # added fat amount of sample element
        for i in range(random.randint(1,200)):
            v.append(self._get_sample_element_())
        mutations.append(list(v))
        v = list(original)

        # remove random element
        # for i in range(random.randint(0,int(len(v)/2))):
        rand_index = random.choice(range(len(v)))
        del v[rand_index]
        mutations.append(list(v))
        v = list(original)

        # Remove element enumerations
        # for i in range(len(v)):
        #     del v[i]
        #     mutations.append(list(v))
        #     v = list(original)
        
        return mutations

    @staticmethod
    def _fat_type_mutation_(mutator, elem):
        for i in range(random.randint(1,5)):
            elem = mutator.mutate(elem)
        return elem

    def _get_sample_element_(self):
        new = OrderedDict()
        string = "sample_attr"
        
        new["@sample_attr_"+str(self._seed)] = string
        new["#text"] = self._fat_type_mutation_(self._mutators[str],string)
        self._seed += 1
        return new
    
    def _get_type_(self, v):
        if self._is_int_(v):
            return int
        elif self._is_float_(v):
            return float
        elif self._is_str_(v):
            return str
        elif self._is_None_(v):
            return None
        raise TypeError(f'*** {v} is an unhandled type ***')

    @staticmethod
    def _is_float_(v):
        try:
            float(v)
            return True
        except ValueError:
            return False

    @staticmethod
    def _is_int_(v):
        try:
            int(v)
            return True
        except ValueError:
            return False

    @staticmethod
    def _is_str_(v):
        try:
            str(v)
            return True
        except ValueError:
            raise Exception('Can you imagine something that will fail this?')

    @staticmethod
    def _is_None_(v):
        if v is None:
            return True
        return False
    
    @staticmethod
    def empty():
        return "<html></html>"


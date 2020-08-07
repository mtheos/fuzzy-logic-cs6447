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
        
        # normal mutation
        self.recurse(self._original)
        # print("\n".join(self._yields))
        return self._yields

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
    individual types:
        - finding the type
        - calling the right mutator
    A None mutator
        - creates a filled element
    Add/Remove attributes
    Add/Remove text
    stategies
        - Add/remove elements functionality
    """
    def recurse(self, original):
        if type(original) is OrderedDict:
            for k,v in original.items():
                # print ("k = ", k, " v = ", v)
                if type(v) is OrderedDict:
                    v_original = OrderedDict(v)
                    for mutation in self._mutate_ordered_dict(OrderedDict(v)):
                        original[k] = OrderedDict(mutation)
                        self._yields.append(xmltodict.unparse(self._original, full_document=False))
                        original[k] = OrderedDict(v_original)
                    self.recurse(v)
                elif type(v) is list:
                    """
                    TODO:
                        1. Add new fucky element
                        2. Remove Element
                    """
                    self.recurse(v)
                elif v is None:
                    """
                    TODO: Create new fucky element
                    """
                    continue
                else:
                    v_type = self._get_type_(v)
                    typed_v = v_type(v)
                    mutation = self._mutators[v_type].mutate(typed_v)
                    tmp = typed_v
                    # print(self._mutators[v_type], mutation)
                    original[k] = str(mutation)
                    self._yields.append(xmltodict.unparse(self._original, full_document=False))
                    original[k] = str(tmp)
                # else:
                #     if self._strategy != None:
                #         for mutation in self._static_mutators[type(v)].deterministic_mutator(v, self._strategy):
                #             tmp = v
                #             original[k] = mutation
                #             self._yields.append(json.dumps(self._original))
                #             original[k] = tmp

        elif type(original) is list:
            for k in range(len( original)):
                v = original[k]
                if type(v) is OrderedDict:
                    v_original = OrderedDict(v)
                    for mutation in self._mutate_ordered_dict(OrderedDict(v)):
                        original[k] = OrderedDict(mutation)
                        self._yields.append(xmltodict.unparse(self._original, full_document=False))
                        original[k] = OrderedDict(v_original)
                    self.recurse(v)
                elif type(v) is list:
                    """
                    TODO:
                        1. Add new fucky element
                        2. Remove Element
                    """
                    self.recurse(v)
                elif type(v) is None:
                    #TODO
                    pass
    
    """
    TODO:
        1. Add attribute
        2. Add text (if doesn't exist)
        3. Remove attribute
        4. Remove text
        5. Add element
        6. Remove Element
    """
    def _mutate_ordered_dict(self, v):
        mutations = []
        original = OrderedDict(v)
        
        # add attribute
        v["@_new_att_"+str(self._seed)] = "new_att_value_"+str(self._seed)
        mutations.append(OrderedDict(v))
        v = OrderedDict(original)
        
        # remove attribute
        for key in [key for key in v.keys() if key[0] == '@']:
            del v[key]
            mutations.append(OrderedDict(v))
            v = OrderedDict(original)
        
        # add text
        if '#text' not in v.keys():
            v['#text'] = 'new_text_'+str(self._seed)
            mutations.append(OrderedDict(v))
            v = OrderedDict(original)
        
        # remove text
        if '#text' in v.keys():
            del v['#text']
            mutations.append(OrderedDict(v))
            v = OrderedDict(original)
        
        # add element TODO add random shit to element?
        v["_new_element_"+str(self._seed)] = OrderedDict()
        mutations.append(OrderedDict(v))
        v = OrderedDict(original)
        
        # remove element
        for key in [key for key in v.keys() if key[0] != '@' and key[0] != '#']:
            del v[key]
            mutations.append(OrderedDict(v))
            v = OrderedDict(original)

        self._seed += 1
        return mutations

    """
    TODO:
        1. Add new fucky element
        2. Remove Element
    """
    def _mutate_list(self, v):
        pass
    
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
    
    def empty(self):
        return "<html></html>"


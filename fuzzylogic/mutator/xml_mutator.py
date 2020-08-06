import random
import json
# import xml.etree.ElementTree as ET
import xmltodict
import pprint
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

    def mutate(self, xml_input):
        self._analyse_(xml_input)
        # print(xmltodict.unparse(self._original))
        # print(json.dumps(self._original))
        self._preprocessing_recurse_(self._original)
        # print(xmltodict.unparse(self._original))
        self.recurse(self._original)
        print('\n'.join(self._yields))
        print(len(self._yields))
        

    """
    Prases string input
    """
    def _analyse_(self, _input):
        self._original = xmltodict.parse(_input,process_namespaces=True)
    
    """
    TODO
    """
    def _preprocessing_recurse_(self, original):
        # print("recursing into ", json.dumps(original))
        # print(type(original))
        if type(original) is OrderedDict:
            for k,v in original.items():
                # print ("k = ", k, " v= ", v)
                self._preprocessing_recurse_(v)
                
        elif type(original) is list:
            for k in range(len(original)):
                v = original[k]
                if type(v) is str:
                    original[k] = {"#text":v}
                elif type(v) is OrderedDict:
                    self._preprocessing_recurse_(v)
                elif type(v) is list:
                    self._preprocessing_recurse_(v)
    """
    TODO
    """
    def recurse(self, original):
        print("recursing into ", json.dumps(original))
        if type(original) is OrderedDict:
            for k,v in original.items():
                print ("k = ", k, " v= ", v)
                if type(v) is OrderedDict:
                    self.recurse(v)
                elif type(v) is list:
                    self.recurse(v)
                elif type(v) is str:
                    for mutation in ['%n%n%n%n']:
                        tmp = v
                        original[k] = mutation
                        self._yields.append(xmltodict.unparse(self._original, full_document=False))
                        original[k] = tmp
                elif type(v) is None:
                    #TODO
                    pass
        elif type(original) is list:
            for k in range(len( original)):
                v = original[k]
                if type(v) is OrderedDict:
                    self.recurse(v)
                elif type(v) is list:
                    self.recurse(v)
                elif type(v) is None:
                    #TODO
                    pass

    
    """
    Original mutate logic: mutate a leaf node
    Current mutate logic: mutate a node by:
     - mutate attribute value
     - mutate text
     - add attr (new)
     - add text (when there wasn't previously one)
     - remove att
     - remove text
    """
    #### IGNORE
    def _mutate_(self, head):
        # finaly find a 
        if len(list(head)) == 0: # leaf
            if len(head.keys()) == 0:
                self._found_bad = True
                return head      # indiciate that a node wasn't mutated and needs to find another to mutate.
            
            rand_att = random.choice(list(head.keys()).append('text'))
            print(rand_att)
            return head
        
        # get nodes that contain attributes
        nodes_list = [node for node in list(head) if (len(node.keys()) != 0 or node.text != None)]
        print(f"Nodes with an attribute or text: {nodes_list}")
        if len(nodes_list) == 0:
            return head
        
        rand_node = random.choice(nodes_list)
        
        print(rand_node.tag)
        while True:
            new = self._mutate_(rand_node)
            if self._found_bad == False:
                break


            
        # print(new.tag)
        return head


    
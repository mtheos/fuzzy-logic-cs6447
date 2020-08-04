import random
import xml.etree.ElementTree as ET
from .int_mutator import IntMutator
from .float_mutator import FloatMutator
from .string_mutator import StringMutator
from .boolean_mutator import BooleanMutator
from .complex_mutators import ListMutator, ObjectMutator

class XmlMutator:
    def __init__(self):
        self._seed = 0
        self._original = None   # xml tree
        self._nodes = []        # xml nodes

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
        # print(xml_input)
        self._analyse_(xml_input)

        for node in self._original.iter():
            self._seed += 1
            print(f"{node.tag} = {node.text}")

    """
    Prases string input and adds all nodes to a list
    """
    ### IGNORE
    def _analyse_(self, _input):
        self._original = ET.fromstring(_input)
        # iterate through all the nodes and add each to nodes lost
        # xml_iter = self._original.iter()
        # for i, node in enumerate(xml_iter):
        #     print(f"{i}: {node.tag}")
        #     self._nodes.append(node)
    
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


    
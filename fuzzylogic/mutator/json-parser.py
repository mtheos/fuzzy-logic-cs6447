import json

with open('../test_binaries/json1.txt') as file:
    data = json.load(file)
    print(data)
    for (k, v) in data.items():
        print(f'{k}: {v}  {type(v)}')

# 1. figure out type of input (json mutator, XML, CSV, text)
# 2. mutator for each type (json mutator, XML, CSV, text)
#   rule base mutation w/ random
# 	text:
# 		- fewer/more new lines
# 		- longer/shorter text
# 		- empty
# 		- test if any specific strings of text has to be the way they are
# 		  (e.g. such as a password like in image-viewer)
# 		- change 'type' of characters (e.g. replace a 'A' with a 5)
# 		-
# 	json:
# 		- for each of the fields mutate based on type and rules
# 		- e.g. int (negative, 0, positive, int overflow)
# 		- mutate multiple fields vs mutate single field at a time
# 		-
# 	csv :
# 		- add/remove rows
# 		- add/remove columns
# 		- mutating based on type
# 	xml :
# 		- adding/removing tags
# 		- mutating each type
# 		- giving input of invalid type (e.g. plain text into a link header)
# 		-
# 		-
# 3. mutate based on known vulns:
# 		- buffer overflow
# 		- integer overflow
# 		- integer underflow
# 		- format strings
# 		- implicit type conversion?
# 		- injection (include/interchange single and double quote)
# 		-
# 4. keep track of mutations
# 		- in memory
# 		-
# 		-
# 		-

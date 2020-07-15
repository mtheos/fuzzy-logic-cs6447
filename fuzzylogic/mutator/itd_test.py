import os

test_files = ['json1.txt', 'json2.txt', 'xml1.txt', 'xml2.txt', 'xml3.txt', 'csv1.txt', 'csv2.txt', 'plaintext1.txt', 'plaintext2.txt', 'plaintext3.txt','multiline-plaintext1.txt', 'multiline-plaintext2.txt', 'multiline-plaintext3.txt', 'invalid-csv1.txt', 'invalid-csv2.txt']

if os.path.exists("test_out.txt"):
    os.remove("test_out.txt")

for f in test_files:
    with open('test_out.txt','a') as out_file:
        out_file.write(f'\n========= {f} =========\n')
    
    myCmd = f'python3 input_type_detector.py {f} >> test_out.txt'
    os.system(myCmd)
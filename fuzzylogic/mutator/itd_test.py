import os

test_path = '../../test_binaries/'
test_files = ['json1.txt', 'json2.txt', 'json3.txt', 'xml1.txt', 'xml2.txt',
              'xml3.txt', 'csv1.txt', 'csv2.txt', 'plaintext1.txt', 'plaintext2.txt',
              'plaintext3.txt', 'plaintext4.txt', 'invalid-csv1.txt', 'invalid-csv2.txt']

test_files = [test_path + x for x in test_files]

if os.path.exists("test_out.txt"):
    os.remove("test_out.txt")

for f in test_files:
    print(f'running {f[f.rindex("/") + 1:]}')
    with open('test_out.txt', 'a') as out_file:
        out_file.write(f'\n========= {f} =========\n')
    myCmd = f'python3 input_type_detector.py {f} >> test_out.txt'
    os.system(myCmd)

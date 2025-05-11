import os

def write_file(file_name, data):
    directory = os.path.dirname(file_name)  
    if not os.path.exists(directory):
        os.makedirs(directory)
    print(f"Writing file: {file_name}")
    f = open(file_name, "w")
    f.write(data)
    f.close()

def read_file(file_name):
    try:
        #try utf-8 encoding
        f = open(file_name, 'r')
        file_content = f.read()
    except:
        #try unicode_escape encoding
        f = open(file_name, 'r', encoding='unicode_escape')
        file_content = f.read()
    f.close()
    return file_content

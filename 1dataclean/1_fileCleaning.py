import os
from tqdm import tqdm
def get_size(file_path, unit='bytes'):
    file_size = os.path.getsize(file_path)
    exponents_map = {'bytes': 0, 'kb': 1, 'mb': 2, 'gb': 3}
    if unit not in exponents_map:
        raise ValueError("Must select from \
        ['bytes', 'kb', 'mb', 'gb']")
    else:
        size = file_size / 1024 ** exponents_map[unit]
        return round(size, 3)


def file_detect_cleaning(file_path, dir_path, clean_path):
    # case 1: delete empty files
    try:
        is_empty = get_size(file_path, unit='kb') <= 3
        if is_empty:
            return 'empty'
        # case 2: delete 'PS' files
        with open(file_path, 'r', encoding='ISO-8859-1') as file:
            first_line = file.readline()
            is_ps = first_line[0:4] == '%!PS'
            is_html = (first_line[0:5] == '<HTML' or first_line[0:5] == '<html' or first_line[0:9] == '<!doctype')
            if is_ps:
                return 'ps'
            if is_html:
                return 'html'
            # write to utftex
            context = file.read()
            with open(clean_path +  file_path.replace(dir_path,"").replace("/","_"), 'w', encoding='utf-8') as writef:
                writef.write(context)
        return 'normal'
    

    except:
        return 'exception'
import os
from tqdm import tqdm
def find_tex_files(root_directory):
    tex_files = []

    for entry in tqdm(os.scandir(root_directory)):
        if entry.is_file() and entry.name.endswith('.tex'):
            tex_files.append(entry.path)
        elif entry.is_dir():
            for sub_entry in os.scandir(entry.path):
                if sub_entry.name.endswith('.tex'):
                    tex_files.append(sub_entry.path)

    return tex_files




for ssss in range(1990,2021):
    root_directory = "/media/sdb/arxiv_bert/COUNTFORFIG/{}/".format(ssss)
    clean_path = "/media/sdb/arxiv_bert/HPC_texClean/{}/".format(ssss)

    tex_files = find_tex_files(root_directory)


    normal, empty, ps, exception, html = 0, 0, 0, 0, 0

    for file in tqdm(tex_files):
        res = file_detect_cleaning(file, root_directory, clean_path)
        if res == 'normal':
            normal += 1
        elif res == 'empty':
            empty += 1
        elif res == 'ps':
            ps += 1
        elif res == 'exception':
            exception += 1
        elif res == 'html':
            html += 1

    print("normal: ", normal)
    print("empty: ", empty)
    print("ps: ", ps)
    print("exception: ", exception)
    print("html: ", html) 
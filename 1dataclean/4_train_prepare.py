import os
import io
import random
import re
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

def remove_bracket(all):
    # The regular expression pattern looks for brackets and their contents
    # It matches a pair of brackets containing anything except alphabets (a-zA-Z)
    pattern = r'\([^a-zA-Z]*\)'

    # re.sub replaces all occurrences of the pattern with an empty string
    return re.sub(pattern, '', all)


def remove_egn(all):
    pattern = 'e.g.\n'
    return re.sub(pattern, 'e.g. ', all)

def replace_multiple_commas(all):
    # 正则表达式匹配一个或多个连续的逗号
    pattern = r',+'

    # 将匹配到的连续逗号替换为单个逗号
    return re.sub(pattern, ',', all)


def read_file(file_path):
    with io.open(file_path, 'r', encoding='utf-8') as f:
        data = f.read()
        data = remove_bracket(data)
        data = remove_egn(data)
        data = replace_multiple_commas(data)
        return data

def process_year(year):
    dir_path1 = '/media/sdb/arxiv_bert/HPC_txt/{}/'.format(year)
    file_paths1 = [os.path.join(dir_path1, file_name) for file_name in os.listdir(dir_path1)]

    dir_path2 = '/media/sdb/arxiv_bert/HPC_pdf2txt/{}/'.format(year)
    file_paths2 = [os.path.join(dir_path2, file_name) for file_name in os.listdir(dir_path2)]

    # Combine the two lists of file paths
    file_paths = file_paths1 + file_paths2

    # Shuffle the file_paths list
    random.shuffle(file_paths)

    # 使用线程池并行读取文件
    with ThreadPoolExecutor() as executor:
        file_contents = list(executor.map(read_file, file_paths))

    # 将所有文件内容合并，并写入一个文件
    with io.open('/media/sdb/arxiv_bert/HPC_txt/txt_year/{}.txt'.format(year), 'w', encoding='utf-8') as f:
        for content in tqdm(file_contents):
            f.write(content)
            f.write("\n")

for year in range(1990, 2021):
    process_year(year)

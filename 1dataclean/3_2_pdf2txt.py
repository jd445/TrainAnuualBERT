import re
import fitz
from neattext.functions import clean_text
from neattext import TextMetrics
import nltk
from nltk.tokenize import sent_tokenize
import os
import multiprocessing
from tqdm import tqdm
import subprocess
def extract_pdf_text(file_path):
    # 使用 PyMuPDF 打开 PDF 文件
    doc = fitz.open(file_path)

    # 提取 PDF 文本
    text = ""
    for page in doc:
        text += page.get_text()

    return text

def cleantext(text):
    # if line < 5, delete
    lines = text.split("\n")

    lines = [line for line in lines if (len(line) > 20 and TextMetrics(line).noise_scan()['text_noise'] < 40)]

    return " ".join(lines)


def clean_pdfs(file_path, txt_folder, tokenizer):
    # 提取 PDF 文本
    # print(file_path)
    pdf_text = extract_pdf_text(file_path)
    
    # 清洗文本
    pdf_text = cleantext(pdf_text)
    # re for remove "- "
    import re
    pdf_text = re.sub(r'- ', '', pdf_text)
    # remove all in []
    pdf_text = re.sub(r'\[.*?\]', '', pdf_text)
    # remove • 
    pdf_text = re.sub(r'•', '.', pdf_text)
    context = re.sub(r'eq\.', ' EQU ', pdf_text, flags=re.IGNORECASE)
    context = re.sub(r'equ\.', ' EQU ', context, flags=re.IGNORECASE)
    context = re.sub(r'eqs\.', ' EQU ', context, flags=re.IGNORECASE)
    context = re.sub(r'fig\.', ' FIG ', context, flags=re.IGNORECASE)
    context = re.sub(r'Figs\.', ' FIG ', context, flags=re.IGNORECASE)
    context = re.sub(r'Ref\.', ' REF ', context, flags=re.IGNORECASE)
    context = re.sub(r'Refs\.', ' REF ', context, flags=re.IGNORECASE)
    pdf_text = re.sub(r'sec\.', ' SEC,', context, flags=re.IGNORECASE)
    context = clean_text(pdf_text)
    sentences = tokenizer.tokenize(pdf_text)
    #   5.3 remove sentences with less than 3 words
    sentences = [sentence.replace("  "," ") for sentence in sentences if len(sentence.split(" ")) >= 2]

    with open(os.path.join(txt_folder, file_path.split("/")[-1][:-4] + '.txt'), 'wt', encoding='utf-8') as output_file:
        output_file.write('\n'.join(sentences))



def tokeizer2sentences(tokenizer, file_name):
        # print(file_name)
    result = True
    try:
        clean_pdfs(file_name, clean_path, tokenizer)
    except Exception as e:
        # save e to log file
        with open('error.log', 'at', encoding='utf-8') as log_file:
            log_file.write(file_name + '\n')
            log_file.write(str(e) + '\n')
            log_file.write('\n')
        result = False
    return result


def process_chunk(chunk):
    count_file = {}
    count_file['success'] = 0
    count_file['fail'] = 0
    for file_name in tqdm(chunk):
        res = tokeizer2sentences(tokenizer, file_name)
        if res:
            count_file['success'] += 1
        else:
            count_file['fail'] += 1
    return count_file



from tqdm import tqdm
import os

def find_pdf_files(root_directory):
    tex_files = []

    for entry in tqdm(os.scandir(root_directory)):
        if entry.is_file() and entry.name.endswith('.pdf'):
            tex_files.append(entry.path)

    return tex_files


for ssss in range(1990,2021):
    root_directory = "/media/sdb/arxiv_bert/COUNTFORFIG/{}/".format(ssss)
    clean_path = "/media/sdb/arxiv_bert/HPC_pdf2txt/{}/".format(ssss)

    pdf_files = find_pdf_files(root_directory)
    if len(pdf_files) == 0:
        continue



    # Define the number of processes to use (8 in this case)
    num_processes = 1
    from tqdm import tqdm

    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    # get all the file name in the folder


    chunks = [pdf_files[i:i + len(pdf_files) // num_processes] for i in range(0, len(pdf_files), len(pdf_files) // num_processes)]

    pool = multiprocessing.Pool(processes=num_processes)
    merged_count_file = {'success': 0, 'fail': 0}
    for count_file in pool.imap_unordered(process_chunk, chunks):
        merged_count_file['success'] += count_file['success']
        merged_count_file['fail'] += count_file['fail']
    print('success: ', merged_count_file['success'])
    print('fail: ', merged_count_file['fail'])
    pool.close()
    pool.join()
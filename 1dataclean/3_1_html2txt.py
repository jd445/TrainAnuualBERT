# read all the file neams from /html folder
import os
import re
import nltk
from html2text import html2text
from multiprocessing import Pool
import tqdm
from neattext import TextMetrics
def clean_html(years, file_name, tokenizer):
    with open('/media/sdb/arxiv_bert/HPC_html/{}/'.format(years) + file_name, 'r') as f:
        html = f.read()
        # 1. remove <?xml version="1.0" encoding="UTF-8"?>
        html = re.sub(r'<\?xml.*\?>', '', html)
        # 2. remove lines start with <?latexml
        html = re.sub(r'<\?latexml.*\?>', '', html)
        # 3. remove title: <title>Dynamical Objects for Cohomologically Expanding Maps.</title>
        html = re.sub(r'<title>.*</title>', '', html)
        # 4. remove <resource src="LaTeXML.css" type="text/css"/>
        html = re.sub(r'<resource.*>', '', html)
        # 5. remove <creator role="author">
        html = re.sub(r'<creator.*>', '', html)
        # 6. remove <document xmlns="http://dlmf.nist.gov/LaTeXML" labels="LABEL:holEndSection LABEL:postproductionCurrent.jpg" xml:id="id1">
        html = re.sub(r'<document.*>', '', html)
        # </document>
        html = re.sub(r'</document>', '', html)
        # 7. remove <personname>John W. Robertson</personname>
        html = re.sub(r'<personname>.*</personname>', '', html)
        #   <classification scheme="pacs">PACS numbers: 61.44.+p, 64.70.Dv, 61.25.Mv</classification>
        html = re.sub(r'<classification.*>', '', html)
        #     <contact role="address">Institut für Theoretische Physik, Technische Universität Wien<break/>Wiedner Hauptstraße 8-10, A-1040 Wien, Austria</contact>
        html = re.sub(r'<contact.*>', '', html)
        #   <date role="creation">November 7, 2023</date>
        html = re.sub(r'<date.*>', '', html)
        # 8. remove   </creator>
        html = re.sub(r'</creator>', '', html)
        # <abstract name="Abstract">
        html = re.sub(r'<abstract.*>', '', html)
        #   </abstract>
        html = re.sub(r'</abstract>', '', html)
        # 9. <ERROR class="undefined">\pacs</ERROR>
        html = re.sub(r'<ERROR.*>', '', html)
        # 10. <Math mode="inline" tex="\sim" xml:id="m1">
    #     <XMath>
    #       <XMTok meaning="similar-to" name="sim" role="RELOP">∼</XMTok>
    #     </XMath>
    #   </Math>
        html = re.sub(r'<Math[^>]*>[\s\S]*?</Math>', ' EQU ', html)
        # 11. <bibliography> ... </bibliography>
        html = re.sub(r'<bibliography [\s\S]*?</bibliography>', '', html)
        # 12. XMath
        html = re.sub(r'<XMath[^>]*>[\s\S]*?</XMath>', '', html)
        # <equationgroup
        html = re.sub(r'<equationgroup\b[^>]*>[\s\S]*?</equationgroup>', '', html)
        html = re.sub(r'<equation\b[^>]*>[\s\S]*?</equation>', '', html)
        # <itemize
        html = re.sub(r'<itemize\b[^>]*>[\s\S]*?</itemize>', '', html)
        # enumerate
        # <theorem
        html = re.sub(r'<theorem\b[^>]*>[\s\S]*?</theorem>', '', html)
        html = re.sub(r'<enumerate\b[^>]*>[\s\S]*?</enumerate>', '', html)
        # lemma
        html = re.sub(r'<lemma\b[^>]*>[\s\S]*?</lemma>', '', html)
        # table
        html = re.sub(r'<table\b[^>]*>[\s\S]*?</table>', '', html)
        html = re.sub(r'<tabular\b[^>]*>[\s\S]*?</tabular>', '', html)
        html = re.sub(r'<tags\b[^>]*>[\s\S]*?</tags>', '', html)
        # proof
        html = re.sub(r'<proof\b[^>]*>[\s\S]*?</proof>', '', html)
        # <acknowledgements
        html = re.sub(r'<acknowledgements\b[^>]*>[\s\S]*?</acknowledgements>', '', html)
        # pagination
        html = re.sub(r'<pagination\b[^>]*>[\s\S]*?</pagination>', '', html)
        # 14 figure
        html = re.sub(r'<figure\b[^>]*>[\s\S]*?</figure>', '', html)
        # 15 ref <ref labelref="LABEL:fig:scanJ"/> 
        html = re.sub(r'<ref [^>]*>', '', html)
        # 16 <cite class="ltx_citemacro_cite">[<bibref bibrefs="strack" separator="," yyseparator=","/>]</cite>
        html = re.sub(r'<cite.*?</cite>',"CITE", html)


        html = re.sub(r'</Math>', '', html)

        markdown_file = ".md"
        # with open('ss/' + file_name, 'w') as f:
        #     f.write(html)
        # 使用subprocess调用pandoc进行转换
        markdown_content = html2text(html)
        markdown_content = re.sub(r'§', '', markdown_content)
        output = re.sub(r'eq\.', ' EQU ', markdown_content, flags=re.IGNORECASE)
        output = re.sub(r'eqs\.', 'EQU', output, flags=re.IGNORECASE)
        output = re.sub(r'fig\.', ' FIG ', output, flags=re.IGNORECASE)
        output = re.sub(r'Figs\.', ' FIG ', output, flags=re.IGNORECASE)
        output = re.sub(r'Ref\.', ' REF ', output, flags=re.IGNORECASE)
        output = re.sub(r'Refs\.', ' REF ', output, flags=re.IGNORECASE)
        output = re.sub(r'sec\.', ' SEC,', output, flags=re.IGNORECASE)
        output = re.sub(r'\\<equation\\>', ' EQU ', output)
        output = re.sub(r'\\<point\\>', ' POINT ', output)
        # 4. generate sentences
        # with open('temp_txt.md' , 'wt', encoding='utf-8') as temp_file:
        #     temp_file.write(output)
        # 5. clean sentences
        #   5.1 markdown title start with #, so add "." to the end of title,("\n# xxxx " to " \n# xxxx. ")
        output = re.sub(r'(#+\s[^\n]+)(?=\n|$)', r'\1.', output)
        #   5.2 "{#xxxxxx} "这种remove
        output = re.sub(r'(#+\s[^\n]+)\s*\{#[^}]+\}', r'\1', output)
        output = re.sub(r'^\s*#.*$', '', output, flags=re.MULTILINE)

        #   5.3 "[^x]: "这种remove
        output = re.sub(r'\[[^\]]*\]: ', '', output)
        #   5.4 "[^x]"这种remove
        output = re.sub(r'\[[^\]]*\]', '', output)
        #   5.5 去掉"-   "
        output = re.sub(r'-   ', '', output)
        #   5.6 去掉:::
        pattern = r':::(.*?):::'

        # 匹配 ::: 结构并处理每个匹配项
        def process_match(match):
            content = match.group(1)
            lines = content.split('\n')
            modified_lines = [line.strip() + '.' if line.strip() else line for line in lines]
            return ':::' + '\n'.join(modified_lines) + ':::'

        # 使用 re.sub 函数匹配 ::: 结构并处理每个匹配项
        output = re.sub(pattern, process_match, output, flags=re.DOTALL)
        output = re.sub(r':::.*', '', output)
        #   去掉 连续重复的标点
        output = re.sub(r'([-,.!?]+)\1+', r'\1', output)
        #   去掉 换行
        output = re.sub(r'\n', ' ', output)
        #   去掉 连续空格
        output = re.sub(r'\s+', ' ', output)
        #   去掉标点前的空格
        output = re.sub(r'\s+([.,!?])', r'\1', output)
        #   去掉0◻
        output = re.sub(r'0◻', '', output)
        output = re.sub(r'', '', output)
        output = re.sub(r'\(\s*\)|\[\s*\]|\{\s*\}', '', output)

        # with open('temp_txt_clean.txt' , 'wt', encoding='utf-8') as temp_file:
        #     temp_file.write(output)
        sentences = tokenizer.tokenize(output)
        #   5.3 remove sentences with less than 3 words
        sentences = [sentence.replace("  "," ") for sentence in sentences if (len(sentence.split()) >= 2 and TextMetrics(sentence).noise_scan()['text_noise'] < 30)]
        
        # 6. save sentences to  tex_folder
        # requirmenets: filename end with .tex, replace .tex with .txt
    with open('/media/sdb/arxiv_bert/HPC_txt/{}/'.format(years) + file_name[:-4] + 'txt', 'wt', encoding='utf-8') as output_file:
        output_file.write('\n'.join(sentences))


import nltk
from multiprocessing import Pool
def process_file(args):
    year, file_name, tokenizer = args
    clean_html(year, file_name, tokenizer)

if __name__ == "__main__":
    for year in range(2020, 2021):
        file_names = os.listdir('/media/sdb/arxiv_bert/HPC_html/{}/'.format(year))
        tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

        # 创建参数列表
        args_list = [(year, file_name, tokenizer) for file_name in file_names]

        # 创建进程池并分配任务
        with Pool(64) as pool:
            list(tqdm.tqdm(pool.imap(process_file, args_list), total=len(args_list)))
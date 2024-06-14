import os
import shutil
import tarfile
import tempfile
from tqdm import tqdm
import gzip
import time
import multiprocessing as mp

def Process_member(tar, member):
    if member.isfile() and member.name.endswith('.tar.gz'):
        # Create a temporary directory
        gz_time = member.mtime
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract nested tar.gz file to the temporary directory
            tar.extract(member, path=temp_dir)
            # print(f"Extracted {member.name} to temporary directory {temp_dir}")
            
            # Call extract_tex_file_from_tar for the nested tar.gz file
            file_id = os.path.join(temp_dir, member.name).split('/')[-1].replace(".tar.gz","")
            year_df = get_time_df(time_line_df, file_id, gz_time)
            year_id = get_time_id(file_id)
            final_path = folder_selection_for_tex_file(file_id, year_df, year_id, file_id)
            # print(final_path)
            try:
                # 抽取文件1：抽取所有的tex文件
                extract_tex_file_from_tar(os.path.join(temp_dir, member.name), final_path)
                return "multi"
            except:
                # print("Error: ",os.path.join(temp_dir, member.name))
                try:
                    # 抽取文件2：这里是所有的单文件
                    res = only_one_file_in_tar(os.path.join(temp_dir, member.name), final_path)
                    if res == 'tex':
                        return "tex"
                    elif res == 'pdf':
                        return "pdf"
                except:
                    return "error"



def process_member_chunk(tar_path, member_chunk):
    error_number = 0
    multi_folder = 0
    single_tex = 0
    single_pdf = 0
    with tarfile.open(tar_path, 'r:gz') as tar:
        for member in tqdm(member_chunk):
            res = Process_member(tar, member)
            if res == "multi":
                multi_folder += 1
            elif res == "tex":
                single_tex += 1
            elif res == "pdf":
                single_pdf += 1
            elif res == "error":
                error_number += 1

    return (error_number, multi_folder, single_tex, single_pdf)

def extract_tar_file_from_tar_parallel(source_tar_gz, num_workers=24):
    bigtar = tarfile.open("/mnt/data/arxiv/source/" + source_tar_gz, 'r:gz')
    big_path = "/mnt/data/arxiv/source/" + source_tar_gz
    # 获取所有成员并分成num_workers份
    members = bigtar.getmembers()
    member_chunks = [members[i::num_workers] for i in range(num_workers)]
    bigtar.close()
    # 创建进程池
    with mp.Pool(processes=num_workers) as pool:
        # 使用进程池并发执行新的函数
        results = list(pool.starmap(process_member_chunk, [(big_path, chunk) for chunk in member_chunks]))


    # 汇总结果
    total_error_number = sum([r[0] for r in results])
    total_multi_folder = sum([r[1] for r in results])
    total_single_tex = sum([r[2] for r in results])
    total_single_pdf = sum([r[3] for r in results])

    return (total_error_number, total_multi_folder, total_single_tex, total_single_pdf)






def only_one_file_in_tar(source_tar_gz, final_path):

    try:
        # save the file to the bigger year.
        
        with gzip.open(source_tar_gz, 'r') as f_in:
            with open(final_path.replace(".tar.gz","") + '.tex', 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        return 'tex'
    except:
        os.remove(final_path.replace(".tar.gz","") + '.tex')
        save_MayPDF_to_file(source_tar_gz, final_path + ".pdf")
        return 'pdf'



def folder_selection_for_tex_file(file_id, year_df, year_id, member_name):
    path = "/media/sdb/COUNTFORFIG"
    year_id = 0
    # if year_df > year_id, we take the year_df, else we take the year_id
    year = int(year_df) if int(year_df) > int(year_id) else int(year_id)
    if year < 30:
        if year < 10:
            year = '200' + str(year)
        else:
            year = '20' + str(year)
    else:
        year = '19'+ str(year)
    file_id = file_id.strip('._/')
    return os.path.join(path, year, file_id)


def extract_tex_file_from_tar(file_path,  final_path):
    with tarfile.open(file_path, 'r:gz') as tar2:
        for member in tar2.getmembers():
            if member.isfile() and member.name.endswith('.tex'):
                tar2.extract(member, path=os.path.join(final_path))

def save_MayPDF_to_file(file_path, dest_dir):
    shutil.copyfile(file_path, dest_dir)


def get_time_id(id):
    is_number = id[0:4].isdigit()
    if is_number == False:
        return 10
    else:
        return id[0:2]

def download_date(gz_time):
    # convert the time to the format year-month-day
    gz_time = time.localtime(gz_time)

    # get year
    year = time.strftime("%Y", gz_time)
    # print(year)
    return int(year[-2:])


def find_largest_less_equal_number(year_list, modify_year):
    try:
        return max(year for year in year_list if year <= modify_year)
    except:
        return year_list[-1]

def get_time_df(df, id, gz_time):

    id = id.replace('_','/').strip('._/')
    modify_year = download_date(gz_time)

    selected_data = df.loc[df['id'] == id]
    try:
        versions_list = selected_data['versions'].values[0]
        years = [int(item['created'].split(' ')[3][-2:]) for item in versions_list]

        final_df_year = find_largest_less_equal_number(years, modify_year)
        # if final_df_year > 30 or final_df_year < 10:
        #     final_df_year = 10
    except:
        print(id , 'bad, I lost you')
        return 0
    return final_df_year





# Call the recursive extraction function

# 获取当前目录下的所有文件和子目录
files_and_dirs = os.listdir("/mnt/data/arxiv/source/")

# 使用列表推导式筛选以.tar.gz结尾的文件名
tar_gz_files = [filename for filename in files_and_dirs if filename.endswith('.tar.gz')]
# tar_gz_files = [filename for filename in tar_gz_files if (int(filename[0:2]) <= 16 ) or (int(filename[0:2]) >= 30 )]
# tar_gz_files = [filename for filename in tar_gz_files if (int(filename[0:2]) > 16 ) and (int(filename[0:2]) < 30 )]
# print(tar_gz_files)
# tar_gz_files = tar_gz_files[4:]
# 打印或进一步处理 tar.gz 文件列表
print(tar_gz_files)

destination_dir = '/media/sdb/arxiv_text/tex'

# using df to record the result of each tar.gz file
import pandas as pd

df = pd.DataFrame(columns=['tar_gz_files', 'error_number', 'multi_folder', 'single_tex', 'single_pdf'])

time_line_df = pd.read_json(r'/mnt/data/arxiv/arxiv-metadata-oai-snapshot.json', lines=True)
print("finish read")

for gzfilepath in tar_gz_files:
    # os.makedirs(os.path.join(destination_dir, gzfilepath.replace(".tar.gz","")))
    states = extract_tar_file_from_tar_parallel(gzfilepath)
    # add states to df using pd.concat
    new_row = {'tar_gz_files': gzfilepath, 'error_number': states[0], 'multi_folder': states[1],
               'single_tex': states[2], 'single_pdf': states[3]}
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    print(df)
    df.to_csv("/media/sdb/COUNTFORFIG/situation.csv",index=False)
    




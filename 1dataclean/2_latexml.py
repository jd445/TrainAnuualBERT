import subprocess
from tqdm import tqdm
import os



for sss in range(2015,2021):
    path = '/media/sdb/arxiv_bert/HPC_texClean/{}/'.format(sss)
    path2 = '/media/sdb/arxiv_bert/HPC_html/{}/'.format(sss)

    files = os.listdir(path)
    num_cpus = 62
    # split files into num_cpus parts
    file_packs = [files[i::num_cpus] for i in range(num_cpus)]
 
    import multiprocessing as mp
    from multiprocessing import Pool

    def convert(file_pack):
        for file in tqdm(file_pack):
            if not os.path.isdir(file):
                # print(file)
                name = file.replace('.tex','')
                # print(name)
                # convert to html
                try:

                    cmd = f'latexml {path}{name}.tex --nocomments --noparse --quiet --destination={path2}{name}.html'
                    subprocess.run(cmd, shell=True)
                    # print('rm ' + name + '.latexml.log')
                    # delete output log file
                    current_names = os.listdir()
                    for current_name in current_names:
                        if current_name.endswith('.latexml.log'):
                            os.system('rm ' + current_name)
                except:
                    print('failed on ' + name)



    pool = Pool(num_cpus)

    for _ in tqdm(pool.imap_unordered(convert, file_packs), total=len(file_packs)):

        pass

    pool.close()

    pool.join()


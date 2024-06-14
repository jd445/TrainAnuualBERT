# %%
# from pathlib import Path

# from tokenizers import ByteLevelBPETokenizer

# paths = [str(x) for x in Path("/mnt/data/arxiv/source/tex2txt").glob("**/*.txt")]

# # # Initialize a tokenizer
# tokenizer = ByteLevelBPETokenizer()

# # Customize training
# tokenizer.train(files=paths, vocab_size=52_000, min_frequency=2, special_tokens=[
#     "<s>",
#     "<pad>",
#     "</s>",
#     "<unk>",
#     "<mask>",
# ], show_progress=True)
# # !mkdir arxivbert
# tokenizer.save_model("arxivbert")

# %%
# read the all the file names in the folder
# folder name: /mnt/data/arxiv/source/tex2txt
# import os
# import pandas as pd
# from tqdm import tqdm
# file_names = os.listdir('/mnt/data/arxiv/source/tex2txt')
# file_names = file_names[:1000]
# # merge all file into a txt
# with open('/mnt/data/arxiv/source/all_file_bert1000.txt', 'w') as f:
#     for file_name in tqdm(file_names):
#         # read the file
#         with open('/mnt/data/arxiv/source/tex2txt/' + file_name, 'r') as f1:
#             text = f1.read()
#             f.write(text)

# %%
# from tokenizers.implementations import ByteLevelBPETokenizer
# from tokenizers.processors import BertProcessing


# tokenizer = ByteLevelBPETokenizer(
#     "./arxivbert/vocab.json",
#     "./arxivbert/merges.txt",
# )

# # %%
# tokenizer._tokenizer.post_processor = BertProcessing(
#     ("</s>", tokenizer.token_to_id("</s>")),
#     ("<s>", tokenizer.token_to_id("<s>")),
# )
# tokenizer.enable_truncation(max_length=128)

# # %%
# tokenizer.encode("This is America")

# # %%
# tokenizer.encode("This is bioinformatics").tokens


# %%
# !nvidia-smi

# %%
from transformers import RobertaConfig

config = RobertaConfig(
    vocab_size=53_100,
    max_position_embeddings=258,
    num_attention_heads=12,
    num_hidden_layers=6,
    type_vocab_size=1,
)

from transformers import RobertaTokenizerFast

tokenizer = RobertaTokenizerFast.from_pretrained("./arxivbert", truncation=True, max_len=256)
from transformers import RobertaForMaskedLM

model = RobertaForMaskedLM(config=config)
model.num_parameters()

# %%
from datasets import load_dataset

# dataset = load_dataset('text', data_files='/mnt/data/arxiv/source/all_file_bert.txt')

# # Tokenize the dataset
# def tokenize_function(examples):
#     return tokenizer(examples["text"], truncation=True, max_length=256)

# tokenized_dataset = dataset.map(tokenize_function, batched=True)

# %%
# tokenized_dataset.save_to_disk('/mnt/data/arxiv/source/tokenized_dataset1000')

# %%
from datasets import  load_from_disk
# Load the saved dataset from disk
tokenized_dataset = load_from_disk('/media/sdb/token_bert')

# %%
from transformers import Trainer, TrainingArguments, DataCollatorForLanguageModeling

data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer, mlm=True, mlm_probability=0.15
)

training_args = TrainingArguments(
    output_dir="./arxivbert",
    overwrite_output_dir=True,
    num_train_epochs=1,
    per_device_train_batch_size=32,
    save_steps=100,
    save_total_limit=2,
)

trainer = Trainer(
    model=model,
    args=training_args,
    data_collator=data_collator,
    train_dataset=tokenized_dataset['train'],  # use the entire tokenized dataset
)

# %%

import warnings

# Ignore all warnings
warnings.filterwarnings('ignore')

trainer.train()

# %%
from transformers import pipeline

fill_mask = pipeline(
    "fill-mask",
    model="./arxivbert/",
    tokenizer="./arxivbert"
)
fill_mask("Firstly, our <mask> can achieve the highest classification accuracy on nearly half of the data sets.")



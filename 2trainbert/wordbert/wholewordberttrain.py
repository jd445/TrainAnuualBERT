

# %%
from transformers import RobertaConfig

config = RobertaConfig(
    vocab_size=53_100,
    max_position_embeddings=258,
    num_attention_heads=12,
    num_hidden_layers=12,
    type_vocab_size=1,
)
from transformers import BertTokenizerFast

from datasets import load_dataset
# Load the pretrained tokenizer
tokenizer = BertTokenizerFast.from_pretrained("/media/sdb/arxiv_bert/WholeWordToken", truncation=True, max_len=256)

from transformers import RobertaForMaskedLM

model = RobertaForMaskedLM(config=config)
dataset = load_dataset('text', data_files='/mnt/data/arxiv/source/before2010.txt', cache_dir='/media/sdb/datasetcache')

# # Tokenize the dataset
def tokenize_function(examples):
    return tokenizer(examples["text"], truncation=True, max_length=256)

tokenized_dataset = dataset.map(tokenize_function, batched=True)

tokenized_dataset.save_to_disk('/media/sdb/datasetcache')
from transformers import RobertaForMaskedLM

model = RobertaForMaskedLM(config=config)


from datasets import  load_from_disk
# # Load the saved dataset from disk
tokenized_dataset = load_from_disk('/media/sdb/datasetcache')

# %%
from transformers import Trainer, TrainingArguments, DataCollatorForLanguageModeling



data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer, mlm=True, mlm_probability=0.15
)

training_args = TrainingArguments(
    output_dir="/home/jjdong/wholewordbert",
    overwrite_output_dir=True,
    num_train_epochs=1,
    per_device_train_batch_size=64,
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

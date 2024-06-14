from transformers import RobertaConfig, BertTokenizerFast
from datasets import load_dataset, load_from_disk
from transformers import RobertaForMaskedLM
from transformers import Trainer, TrainingArguments, DataCollatorForLanguageModeling
import torch
from accelerate import Accelerator

# Checking if CUDA is available
cuda_available = torch.cuda.is_available()
print(cuda_available, flush=True)

config = RobertaConfig(
    vocab_size=53100,
    max_position_embeddings=520,
    num_attention_heads=12,
    num_hidden_layers=12,
    type_vocab_size=1,
)

# Load the pretrained tokenizer
tokenizer = BertTokenizerFast.from_pretrained(
    "/home/jjdong/arxiv_bert_project/arxiv_bert", truncation=True, max_len=512, return_tensors="pt")

model = RobertaForMaskedLM(config=config)

dataset = load_dataset('text', data_files='/media/sdb/arxiv_bert/HPC_txt/txt_year/1990_2008.txt',
                       cache_dir='/media/sdb/arxiv_bert/datacache/1990_2008')

# Tokenize the dataset


def tokenize_function(examples):
    return tokenizer(examples["text"], truncation=True, max_length=512)


tokenized_dataset = dataset.map(tokenize_function, batched=True)

data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer, mlm=True, mlm_probability=0.15
)

training_args = TrainingArguments(
    output_dir="/home/jjdong/trainArxivBERT/bb",
    overwrite_output_dir=True,
    num_train_epochs=2,
    per_device_train_batch_size=32,
    save_steps=10000,
    save_total_limit=2,
)

# Initialize the accelerator
# accelerator = Accelerator()

# Train with the accelerator
trainer = Trainer(
    model=model,
    args=training_args,
    data_collator=data_collator,
    # use the entire tokenized dataset
    train_dataset=tokenized_dataset['train'],
)

# Enable accelerator
# trainer = accelerator.prepare(trainer)

print('training start', flush=True)
trainer.train(
    resume_from_checkpoint='/home/jjdong/trainArxivBERT/bb/checkpoint-2570000')

model.save_pretrained("/home/jjdong/arxiv_year_model/base")

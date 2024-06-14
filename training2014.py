from transformers import RobertaConfig, BertTokenizer
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

accelerator = Accelerator()
year = 2014
# Load the pretrained tokenizer
tokenizer = BertTokenizer.from_pretrained(
    "/home/junjdong/trainArxivBert/wholewordtoken", truncation=True, max_len=512, return_tensors="pt")
pathM = "/home/junjdong/arxiv_year_model/{}".format(int(year-1))
model = RobertaForMaskedLM.from_pretrained(pathM)


from datasets import  load_from_disk
# # Load the saved dataset from disk
tokenized_dataset = load_from_disk('/home/junjdong/token_cache/{}'.format(year))



data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer, mlm=True, mlm_probability=0.15
)
print("training start")
training_args = TrainingArguments(
    output_dir="/home/junjdong/trainArxivBert/{}".format(year),
    overwrite_output_dir=True,
    num_train_epochs=1,
    per_device_train_batch_size=24,
    save_steps=10000,
    save_total_limit=2,
)


# Train with the accelerator
trainer = accelerator.prepare(Trainer(
    model=model,
    args=training_args,
    data_collator=data_collator,
    # use the entire tokenized dataset
    train_dataset=tokenized_dataset['train'],
))

# Enable accelerator
# trainer = accelerator.prepare(trainer)

print('training start', flush=True)
trainer.train()

unwrapped_model = accelerator.unwrap_model(trainer.model)
unwrapped_model.save_pretrained(
    "/home/junjdong/arxiv_year_model/{}".format(year),
    is_main_process=accelerator.is_main_process,
    save_function=accelerator.save,
)


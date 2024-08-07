# from huggingface_hub import notebook_login

# notebook_login()

from datasets import load_dataset, DatasetDict, Dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments
from trl import SFTTrainer
from peft import LoraConfig

dataset = load_dataset("b-mc2/sql-create-context")

dataset

# dataset['train'][0]

model_checkpoint = "stabilityai/StableBeluga-7B"
# Initialize the tokenizer and model
model = AutoModelForCausalLM.from_pretrained(model_checkpoint)


tokenizer = AutoTokenizer.from_pretrained(model_checkpoint, max_length=512)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"

model.config.use_cache = False

model.config.quantization_config.to_dict()

lora_target_modules = [
    "query_key_value",
    "dense",
    "dense_h_to_4h",
    "dense_4h_to_h",
]
config = LoraConfig(
    r=16,  # attention heads
    lora_alpha=12,  # alpha scaling
    target_modules=lora_target_modules,
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)

import random

split_ratio = 0.8
eval_ratio = 0.2

# the 30% subset
total_examples = len(dataset["train"])
subset_size = int(total_examples * 0.2)
train_size = int(subset_size * split_ratio)
eval_size = subset_size - train_size
shuffled_indices = list(range(total_examples))
random.shuffle(shuffled_indices)
training_set = dataset["train"].select(shuffled_indices[:train_size])
evaluation_set = dataset["train"].select(
    shuffled_indices[train_size : train_size + eval_size]
)
split_dataset = DatasetDict({"train": training_set, "eval": evaluation_set})
split_dataset

evaluation_set

# hyperparameters
lr = 1e-4
batch_size = 4
num_epochs = 1
training_args = TrainingArguments(
    per_device_train_batch_size=batch_size,
    per_device_eval_batch_size=batch_size,
    optim="paged_adamw_32bit",
    logging_steps=1,
    learning_rate=lr,
    fp16=True,
    max_grad_norm=0.3,
    num_train_epochs=num_epochs,
    evaluation_strategy="steps",
    eval_steps=0.2,
    warmup_ratio=0.05,
    save_strategy="epoch",
    group_by_length=True,
    output_dir="outputs",
    report_to="tensorboard",
    save_safetensors=True,
    lr_scheduler_type="cosine",
    seed=12,
)

trainer = SFTTrainer(
    model=model,
    train_dataset=split_dataset["train"],
    eval_dataset=split_dataset["eval"],
    peft_config=config,
    dataset_text_field="question",
    max_seq_length=4096,
    tokenizer=tokenizer,
    args=training_args,
)

# train model
trainer.train()

model.push_to_hub("samadpls/querypls-prompt2sql")
tokenizer.push_to_hub("samadpls/querypls-prompt2sql")

# DEVICE = 'cuda:0' if torch.cuda.is_available() else 'cpu'

import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset
from sklearn.metrics import accuracy_score, f1_score
import numpy as np
import json

print("Загрузка данных для тем...")
df = pd.read_csv("training_data_topics.csv")

topics = sorted(df['topic'].unique())
topic_to_id = {topic: i for i, topic in enumerate(topics)}
id_to_topic = {i: topic for topic, i in topic_to_id.items()}
num_topics = len(topics)

print(f"Тем: {num_topics}")
print(f"Диалогов: {len(df)}")

df['label'] = df['topic'].map(topic_to_id)

train_texts, val_texts, train_labels, val_labels = train_test_split(
    df['dialog'].tolist(), df['label'].tolist(), test_size=0.2, random_state=42, stratify=df['label'].tolist()
)

model_name = "DeepPavlov/rubert-base-cased"
tokenizer = AutoTokenizer.from_pretrained(model_name)

class TopicDataset(Dataset):
    def __init__(self, texts, labels):
        self.encodings = tokenizer(texts, truncation=True, padding=True, max_length=512, return_tensors="pt")
        self.labels = torch.tensor(labels)
    def __getitem__(self, idx):
        return {"input_ids": self.encodings["input_ids"][idx], "attention_mask": self.encodings["attention_mask"][idx], "labels": self.labels[idx]}
    def __len__(self):
        return len(self.labels)

train_dataset = TopicDataset(train_texts, train_labels)
val_dataset = TopicDataset(val_texts, val_labels)

model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=num_topics, ignore_mismatched_sizes=True)

def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=1)
    return {"accuracy": accuracy_score(labels, predictions), "f1": f1_score(labels, predictions, average="weighted")}

training_args = TrainingArguments(
    output_dir="./topic_model_results",
    num_train_epochs=5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="accuracy",
    logging_steps=50,
    learning_rate=2e-5,
    warmup_steps=100,
    weight_decay=0.01,
    report_to="none"
)

trainer = Trainer(model=model, args=training_args, train_dataset=train_dataset, eval_dataset=val_dataset, compute_metrics=compute_metrics)

print("Обучение модели тем...")
trainer.train()

model.save_pretrained("./topic_model")
tokenizer.save_pretrained("./topic_model")

with open("./topic_model/topics_mapping.json", "w", encoding="utf-8") as f:
    json.dump({"topic_to_id": topic_to_id, "id_to_topic": id_to_topic}, f, ensure_ascii=False, indent=2)

print("Модель тем сохранена!")
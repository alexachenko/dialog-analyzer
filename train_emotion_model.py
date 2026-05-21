import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset
from sklearn.metrics import accuracy_score, f1_score
import numpy as np
import json

print("Загрузка данных для эмоций...")
df = pd.read_csv("training_data_emotions.csv")

emotions = sorted(df['emotion'].unique())
emotion_to_id = {e: i for i, e in enumerate(emotions)}
id_to_emotion = {i: e for e, i in emotion_to_id.items()}
num_emotions = len(emotions)

print(f"Эмоции: {emotions}")
print(f"Диалогов: {len(df)}")

df['label'] = df['emotion'].map(emotion_to_id)

train_texts, val_texts, train_labels, val_labels = train_test_split(
    df['dialog'].tolist(), df['label'].tolist(), test_size=0.2, random_state=42, stratify=df['label'].tolist()
)

model_name = "DeepPavlov/rubert-base-cased"
tokenizer = AutoTokenizer.from_pretrained(model_name)

class EmotionDataset(Dataset):
    def __init__(self, texts, labels):
        self.encodings = tokenizer(texts, truncation=True, padding=True, max_length=512, return_tensors="pt")
        self.labels = torch.tensor(labels)
    def __getitem__(self, idx):
        return {"input_ids": self.encodings["input_ids"][idx], "attention_mask": self.encodings["attention_mask"][idx], "labels": self.labels[idx]}
    def __len__(self):
        return len(self.labels)

train_dataset = EmotionDataset(train_texts, train_labels)
val_dataset = EmotionDataset(val_texts, val_labels)

model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=num_emotions, ignore_mismatched_sizes=True)

def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=1)
    return {"accuracy": accuracy_score(labels, predictions), "f1": f1_score(labels, predictions, average="weighted")}

training_args = TrainingArguments(
    output_dir="./emotion_model_results",
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

print("Обучение модели эмоций...")
trainer.train()

model.save_pretrained("./emotion_model")
tokenizer.save_pretrained("./emotion_model")

with open("./emotion_model/emotion_mapping.json", "w", encoding="utf-8") as f:
    json.dump({"emotion_to_id": emotion_to_id, "id_to_emotion": id_to_emotion}, f, ensure_ascii=False, indent=2)

print("Модель эмоций сохранена!")
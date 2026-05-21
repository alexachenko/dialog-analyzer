import re
import json
import os
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class DialogAnalyzer:
    def __init__(self):
        self.use_topic_model = False
        self.use_emotion_model = False

        if os.path.exists("./topic_model"):
            self.topic_model = AutoModelForSequenceClassification.from_pretrained("./topic_model")
            self.topic_tokenizer = AutoTokenizer.from_pretrained("./topic_model")
            self.topic_model.eval()
            with open("./topic_model/topics_mapping.json", "r", encoding="utf-8") as f:
                mapping = json.load(f)
                self.id_to_topic = {int(k): v for k, v in mapping["id_to_topic"].items()}
            self.use_topic_model = True
            print("Модель тем загружена")

        if os.path.exists("./emotion_model"):
            self.emotion_model = AutoModelForSequenceClassification.from_pretrained("./emotion_model")
            self.emotion_tokenizer = AutoTokenizer.from_pretrained("./emotion_model")
            self.emotion_model.eval()
            with open("./emotion_model/emotion_mapping.json", "r", encoding="utf-8") as f:
                mapping = json.load(f)
                self.id_to_emotion = {int(k): v for k, v in mapping["id_to_emotion"].items()}
            self.use_emotion_model = True
            print("Модель эмоций загружена")

    def get_client_text(self, dialog):
        match = re.search(r'Клиент:\s*(.*?)(?=Оператор:|$)', dialog, re.DOTALL)
        return (match.group(1).strip() if match else dialog)[:500]

    def classify_topic(self, text):
        client_text = self.get_client_text(text)
        if not self.use_topic_model or not client_text:
            return "другое"
        inputs = self.topic_tokenizer(client_text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.topic_model(**inputs)
            pred = torch.argmax(outputs.logits, dim=1).item()
        return self.id_to_topic.get(pred, "другое")

    def analyze_sentiment(self, dialog):
        client_text = self.get_client_text(dialog)
        if not self.use_emotion_model or not client_text:
            return "нейтральный"
        inputs = self.emotion_tokenizer(client_text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.emotion_model(**inputs)
            pred = torch.argmax(outputs.logits, dim=1).item()
        return self.id_to_emotion.get(pred, "нейтральный")

    def analyze_dialog(self, dialog):
        return {
            'topic': self.classify_topic(dialog),
            'emotion': self.analyze_sentiment(dialog),
            'is_problem': self.analyze_sentiment(dialog) == 'негативный'
        }
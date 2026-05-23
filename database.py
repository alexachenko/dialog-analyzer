import pandas as pd
import re
import uuid
import chromadb
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class DialogDatabase:

    def __init__(self):

        self.texts = []

        self.full_texts = []

        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2)
        )

        self.matrix = None

    # -----------------------------
    # Извлекаем только текст клиента
    # -----------------------------

    def extract_client_text(self, dialog):

        matches = re.findall(
            r"Клиент:\s*(.*?)(?=Оператор:|$)",
            dialog,
            re.DOTALL
        )

        if matches:
            return " ".join(matches).strip().lower()

        return str(dialog).strip().lower()

    # -----------------------------
    # Загружаем диалоги
    # -----------------------------

    def load_dialogs(self, csv_file):

        df = pd.read_csv(csv_file)

        if "dialog" not in df.columns:
            raise Exception("CSV должен содержать колонку 'dialog'")

        # Убираем полные дубликаты диалогов
        df = df.drop_duplicates(subset=["dialog"])

        # Полный текст для вывода
        self.full_texts = df["dialog"].astype(str).tolist()

        # Клиентский текст для поиска
        self.texts = (
            df["dialog"]
            .apply(self.extract_client_text)
            .tolist()
        )

        self.matrix = self.vectorizer.fit_transform(self.texts)

        print(f"Уникальных диалогов загружено: {len(self.texts)}")

        return len(self.texts)

    # -----------------------------
    # Поиск похожих обращений
    # -----------------------------

    def find_similar(self, query_text, top_k=5):

        if not self.texts or self.matrix is None:
            return []

        query_text = str(query_text).lower().strip()

        query_vector = self.vectorizer.transform(
            [query_text]
        )

        similarities = cosine_similarity(
            query_vector,
            self.matrix
        )[0]

        indexes = similarities.argsort()[::-1]

        results = []
        used_texts = set()

        for idx in indexes:
            search_text = self.texts[idx].strip().lower()
            full_text = self.full_texts[idx].strip()
            score = round(similarities[idx] * 100, 2)

            if score <= 0:
                continue

            if full_text in used_texts:
                continue

            used_texts.add(full_text)

            results.append((
                full_text,
                score
            ))

            if len(results) >= top_k:
                break

        return results
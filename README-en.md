# Text Dialogue Analysis System

**Text Dialogue Analysis System** — a web application for automated processing 
of support dialogues from marketplaces. Based on uploaded CSV files with 
dialogues, the neural network can determine the topic of an inquiry, analyze 
its emotional tone, and find similar inquiries.

## Key Features

- uploading dialogues from a CSV file;
- classification of inquiries by topic:
  - delivery;
  - product quality;
  - payment;
  - account;
  - return;
- sentiment analysis of messages:
  - positive;
  - neutral;
  - negative.
- finding similar inquiries;
- displaying statistics as bar charts, pie charts, and radar charts;
- exporting analysis results to CSV and Excel.

## Input CSV File Format

The file must contain a `dialog` column.

Example:

```csv
dialog
"Клиент: Заказ не пришёл. Оператор: Проверим. Клиент: Спасибо."
"Клиент: Товар сломался. Оператор: Вернём деньги. Клиент: Хорошо."
"Клиент: Курьер опоздал. Оператор: Извините. Клиент: Недопустимо."
```

## Installing Dependencies

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the virtual environment (choose one):

```bash
.venv\Scripts\activate # on Windows
```
```bash
source .venv/bin/activate # on macOS/Linux
```

Install libraries:

```bash
pip install streamlit pandas sentence-transformers chromadb transformers torch scikit-learn accelerate openpyxl plotly pytest
```

## Running the Application

To launch the Streamlit application at http://localhost:8501/, run:

```bash
streamlit run app.py
```

After launching, a web interface will open where you can upload a CSV file and analyze dialogues.

## Using the Application

1. Open the application in your browser.
2. In the sidebar, upload a CSV file with a `dialog` column.
3. Click the **Analyze** button.
4. After processing, the following metrics will appear:
   - total dialogues;
   - number of negative inquiries;
   - number of positive inquiries.
5. In the **Dialogues** tab, you can view all processed records.
6. In the **Statistics** tab, charts showing the distribution by topic and sentiment are displayed.
7. In the **Search** tab, you can find similar inquiries by entering a text query.
8. Analysis results can be downloaded in CSV or Excel format.

## How to Contribute

Create a branch of the repository, make your changes, and then send us 
a [pull request](). We will review your changes and apply them to 
the main branch soon, provided they do not conflict with our project vision. 
Before submitting a [pull request](), make sure all tests pass:

```bash
pytest
```

We also welcome new [issues]() that you suggest for the development of the project!

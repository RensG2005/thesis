import pandas as pd
import os
import glob
import time
import torch
import tensorflow
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from transformers import BertForSequenceClassification, BertConfig

config = BertConfig.from_pretrained('./multilingualBERTmodel/config.json')

model = BertForSequenceClassification.from_pretrained(
    './multilingualBERTmodel/bert_model.ckpt',
    from_tf=True,
    config=config
)

# Load multilingual FinBERT model and tokenizer
# model_name = "./multilingualBERTmodel"
# tokenizer = AutoTokenizer.from_pretrained(model_name)
# model = AutoModelForSequenceClassification.from_pretrained(model_name)
model.eval()

# Load CSV file
csv_file = glob.glob(os.path.join('/home/rens/scriptie/iex/postslist/', 'EXOR-NV.csv'))[0]
df = pd.read_csv(csv_file)

# Ensure sentiment_score column exists
if 'sentiment_score' not in df.columns:
    df['sentiment_score'] = None

# Sentiment scoring function
def get_sentiment_score(text):
    try:
        if pd.isna(text) or not isinstance(text, str) or text.strip() == "":
            return None

        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = model(**inputs)
        scores = torch.nn.functional.softmax(outputs.logits, dim=1)[0]

        # 0: negative, 1: neutral, 2: positive
        sentiment = scores.argmax().item()
        if sentiment == 0:
            return -10 * scores[0].item()
        elif sentiment == 1:
            return 0.0
        else:
            return 10 * scores[2].item()

    except Exception as e:
        print(f"Error processing text: {e}")
        return None

# Process rows with progress logging
start_time = time.time()
total_rows = len(df)

for idx, row in df.iterrows():
    if pd.isna(row['sentiment_score']):
        score = get_sentiment_score(row.get('content', ''))
        df.at[idx, 'sentiment_score'] = score

        if idx % 10 == 0 or idx == total_rows - 1:
            df.to_csv(csv_file, index=False)

        if idx % 10 == 0:
            elapsed = time.time() - start_time
            percent = ((idx + 1) / total_rows) * 100
            print(f"[{idx+1}/{total_rows}] {percent:.2f}% done")

print("✅ Done scoring all rows.")

import os
import json
import matplotlib.pyplot as plt
import numpy as np
import datetime
from collections import defaultdict
import re

# Path to your folder
FOLDER_PATH = "/Users/leila/Desktop/UNI/BT/kompas_articles"

# Initialize lists to hold metrics
char_counts = []
word_counts = []
sentence_counts = []
daily_counts = defaultdict(int)

# Count sentences using regex
def count_sentences(text):
    return len(re.findall(r'[.!?]+', text))

# Loop through JSON files
for filename in os.listdir(FOLDER_PATH):
    if filename.endswith(".json"):
        filepath = os.path.join(FOLDER_PATH, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                articles = json.load(f)
            except json.JSONDecodeError:
                continue  # skip invalid files

            # Get date from filename
            date_str = filename.replace("kompas_", "").replace(".json", "")
            for article in articles:
                content = article.get("content")
                if content:
                    content = content.strip()
                    char_counts.append(len(content))
                    word_counts.append(len(content.split()))
                    sentence_counts.append(count_sentences(content))
                    daily_counts[date_str] += 1

# Sort daily counts by date
dates_sorted = sorted(daily_counts.keys())
daily_article_counts = [daily_counts[date] for date in dates_sorted]
average_daily_articles = np.mean(daily_article_counts)

# === Print statistics ===
def print_stats(name, data):
    print(f"{name}:")
    print(f"  - Average: {np.mean(data):.2f}")
    print(f"  - Minimum: {np.min(data)}")
    print(f"  - Maximum: {np.max(data)}\n")

print_stats("Characters per article", char_counts)
print_stats("Words per article", word_counts)
print_stats("Sentences per article", sentence_counts)
print(f"Average articles posted per day: {average_daily_articles:.2f}\n")

# === Plot histogram for characters with custom bins ===
char_bins = np.arange(0, 7000, 1000)  # 0–1000, 1000–2000, ..., 6000–7000

plt.figure()
plt.hist(char_counts, bins=char_bins, edgecolor='black')
plt.title("Histogram of Characters per Article")
plt.xlabel("Number of Characters")
plt.ylabel("Number of Articles")
plt.grid(True)
plt.show()

# === Plot histograms for words and sentences (10 regular bins) ===
def plot_histogram(data, label):
    plt.figure()
    plt.hist(data, bins=10, edgecolor='black')  # 10 equal-width bins
    plt.title(f"Histogram of {label}")
    plt.xlabel(label)
    plt.ylabel("Number of articles")
    plt.grid(True)
    plt.show()

plot_histogram(word_counts, "Words per article")
plot_histogram(sentence_counts, "Sentences per article")

# === Line graph: articles per day ===
plt.figure(figsize=(10, 5))
plt.plot([datetime.datetime.strptime(d, "%Y-%m-%d") for d in dates_sorted], daily_article_counts, marker="o")
plt.title("Number of Articles Posted per Day")
plt.xlabel("Date")
plt.ylabel("Number of Articles")
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

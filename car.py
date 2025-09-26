import json
import requests
from bs4 import BeautifulSoup
from openai import OpenAI

# --- Config ---
ENDPOINT = "https://cdong1--azure-proxy-web-app.modal.run"
API_KEY = "supersecretkey"
MODEL = "gpt-4o"

RAW_FILE = "raw_blob.txt"
STRUCTURED_FILE = "structured.json"

# 1) Collector: scrape Books to Scrape homepage
def collect():
    url = "http://books.toscrape.com/"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    records = []
    for item in soup.select(".product_pod"):
        title = item.h3.a["title"]
        price = item.select_one(".price_color").get_text(strip=True)
        link = "http://books.toscrape.com/" + item.h3.a["href"]
        records.append({
            "title": title,
            "price": price,
            "source_url": link
        })
    return records

# 2) Structurer: call LLM to return JSON
def structure(records):
    client = OpenAI(base_url=ENDPOINT, api_key=API_KEY)
    prompt = (
        "Return ONLY a JSON array. For each input record, output an object with: "
        "id, title, price, summary, source_url, extracted_at (UTC)."
    )
    msgs = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": json.dumps(records)}
    ]
    resp = client.chat.completions.create(model=MODEL, messages=msgs)
    return json.loads(resp.choices[0].message.content)

def main():
    # Collect
    raw = collect()
    with open(RAW_FILE, "w", encoding="utf-8") as f:
        for r in raw:
            f.write(json.dumps(r) + "\n")
    print(f"Saved raw data to {RAW_FILE} ({len(raw)} records)")

    # Structure
    structured = structure(raw)
    with open(STRUCTURED_FILE, "w", encoding="utf-8") as f:
        json.dump(structured, f, indent=2)
    print(f"Saved structured JSON to {STRUCTURED_FILE}")

if __name__ == "__main__":
    main()

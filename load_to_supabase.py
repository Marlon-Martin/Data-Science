import os
import json
import pandas as pd
from supabase import create_client, Client

# 1. Load environment variables (set these in your shell or Modal secrets)
url: str = os.environ["SUPABASE_URL"]
key: str = os.environ["SUPABASE_KEY"]

supabase_client: Client = create_client(url, key)
print("load_to_supabase: created supabase_client ->", supabase_client)
print(
    "load_to_supabase: supabase module file:",
    (lambda m: getattr(m, "__file__", None))(__import__("supabase")),
)

# 2. Read the structured JSON (output from car.py)
with open("structured.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# 3. Convert JSON → pandas DataFrame
df = pd.DataFrame(data)

# 4. Ensure timestamp column exists
if "extracted_at" not in df.columns:
    df["extracted_at"] = pd.Timestamp.utcnow()

# 5. Upsert/insert rows into Supabase
#    Make sure you have created a table with matching columns:
#    id (text), title (text), summary (text),
#    source_url (text), extracted_at (timestamptz)
rows = df.to_dict(orient="records")
try:
    response = supabase_client.table("books").upsert(rows).execute()
    print("Upserted:", len(rows), "rows")
    print("upsert response:", getattr(response, "data", None))
except Exception as e:
    print("ERROR during upsert:", repr(e))
    raise

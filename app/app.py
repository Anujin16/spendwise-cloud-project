import os
import psycopg2
from flask import Flask

app = Flask(__name__)


def get_conn():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "db"),
        dbname=os.environ.get("DB_NAME", "spendwise"),
        user=os.environ.get("DB_USER", "spendwise"),
        password=os.environ.get("DB_PASSWORD", "spendwise_pass"),
    )


@app.route("/")
def home():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT title, amount, category, spent_on FROM expenses ORDER BY spent_on DESC, id DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    items = "".join(f"<li>{t}: {a} ({c}) {d}</li>" for t, a, c, d in rows)
    return f"<h1>SpendWise</h1><ul>{items}</ul>"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
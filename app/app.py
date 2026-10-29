import os
from datetime import date
import psycopg2
from flask import Flask, redirect, render_template_string, request

app = Flask(__name__)

CATEGORIES = ["Food", "Transport", "Study", "Shopping", "Other"]

PAGE = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>SpendWise</title>
  <style>
    body { font-family: sans-serif; max-width: 700px; margin: 30px auto; }
    form { display: flex; gap: 8px; margin-bottom: 20px; flex-wrap: wrap; }
    table { width: 100%; border-collapse: collapse; }
    th, td { text-align: left; padding: 6px; border-bottom: 1px solid #ddd; }
    .total { font-size: 1.2em; margin: 15px 0; }
  </style>
</head>
<body>
  <h1>SpendWise</h1>
  <form method="post" action="/add">
    <input name="title" placeholder="What?" required>
    <input name="amount" type="number" step="0.01" min="0.01" placeholder="Amount" required>
    <select name="category">
      {% for c in categories %}<option>{{ c }}</option>{% endfor %}
    </select>
    <input name="spent_on" type="date" value="{{ today }}" required>
    <button type="submit">Add</button>
  </form>
  <div class="total">This month total: <b>{{ total }}</b></div>
  <table>
    <tr><th>Title</th><th>Amount</th><th>Category</th><th>Date</th><th></th></tr>
    {% for id, title, amount, category, spent_on in rows %}
    <tr>
      <td>{{ title }}</td><td>{{ amount }}</td><td>{{ category }}</td><td>{{ spent_on }}</td>
      <td>
        <form method="post" action="/delete/{{ id }}" style="margin:0">
          <button type="submit">Delete</button>
        </form>
      </td>
    </tr>
    {% endfor %}
  </table>
</body>
</html>
"""


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
    cur.execute(
        "SELECT id, title, amount, category, spent_on FROM expenses "
        "ORDER BY spent_on DESC, id DESC"
    )
    rows = cur.fetchall()
    cur.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM expenses "
        "WHERE date_trunc('month', spent_on) = date_trunc('month', CURRENT_DATE)"
    )
    total = cur.fetchone()[0]
    cur.close()
    conn.close()
    return render_template_string(
        PAGE, rows=rows, total=total, categories=CATEGORIES, today=date.today().isoformat()
    )


@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title", "").strip()
    category = request.form.get("category", "Other")
    spent_on = request.form.get("spent_on") or date.today().isoformat()
    try:
        amount = float(request.form.get("amount", "0"))
    except ValueError:
        amount = 0
    if category not in CATEGORIES:
        category = "Other"
    if title and amount > 0:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO expenses (title, amount, category, spent_on) VALUES (%s, %s, %s, %s)",
            (title, amount, category, spent_on),
        )
        conn.commit()
        cur.close()
        conn.close()
    return redirect("/")


@app.route("/delete/<int:expense_id>", methods=["POST"])
def delete(expense_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM expenses WHERE id = %s", (expense_id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
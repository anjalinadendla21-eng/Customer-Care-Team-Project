from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

def connect():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    search = request.args.get('search', '')

    conn = connect()

    if search:
        customers = conn.execute("""
        SELECT * FROM customers
        WHERE name LIKE ? OR phone LIKE ?
        """, ('%' + search + '%', '%' + search + '%')).fetchall()
    else:
        customers = conn.execute("SELECT * FROM customers").fetchall()

    total = conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
    open_c = conn.execute("SELECT COUNT(*) FROM customers WHERE status='Open'").fetchone()[0]
    progress = conn.execute("SELECT COUNT(*) FROM customers WHERE status='In Progress'").fetchone()[0]
    resolved = conn.execute("SELECT COUNT(*) FROM customers WHERE status='Resolved'").fetchone()[0]

    conn.close()

    return render_template(
        "index.html",
        customers=customers,
        total=total,
        open_c=open_c,
        progress=progress,
        resolved=resolved,
        search=search
    )

@app.route('/add', methods=['GET','POST'])
def add():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        category = request.form['category']
        description = request.form['description']
        priority = request.form['priority']
        status = request.form['status']
        date = datetime.now().strftime("%d-%m-%Y")

        conn = connect()
        conn.execute("""
        INSERT INTO customers(name,phone,email,category,description,priority,status,date)
        VALUES(?,?,?,?,?,?,?,?)
        """,(name,phone,email,category,description,priority,status,date))
        conn.commit()
        conn.close()

        return redirect('/')

    return render_template("add_customer.html")

@app.route('/delete/<int:id>')
def delete(id):
    conn = connect()
    conn.execute("DELETE FROM customers WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = connect()

    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        category = request.form['category']
        description = request.form['description']
        priority = request.form['priority']
        status = request.form['status']

        conn.execute("""
        UPDATE customers
        SET name=?, phone=?, email=?, category=?, description=?, priority=?, status=?
        WHERE id=?
        """, (name, phone, email, category, description, priority, status, id))

        conn.commit()
        conn.close()

        return redirect('/')

    customer = conn.execute("SELECT * FROM customers WHERE id=?", (id,)).fetchone()
    conn.close()

    return render_template("edit_customer.html", customer=customer)

if __name__ == '__main__':
    app.run(debug=True)
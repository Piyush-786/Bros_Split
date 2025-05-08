from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)

# In-memory storage
people = []
expenses = []
bill_name = ""

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", names=people)

@app.route("/add_names", methods=["POST"])
def add_names():
    global bill_name
    action = request.form["action"]
    if "new_name" in request.form and request.form["new_name"]:
        people.append(request.form["new_name"])
    if "bill_name" in request.form:
        bill_name = request.form["bill_name"]
    if action == "continue":
        return redirect("/add_expense")
    return render_template("index.html", names=people)

@app.route("/delete_name/<name>")
def delete_name(name):
    if name in people:
        people.remove(name)
    return redirect("/")

@app.route("/add_expense", methods=["GET", "POST"])
def add_expense():
    if request.method == "POST":
        payer = request.form["paid_by"]
        amount = float(request.form["amount"])
        shared_by = request.form.getlist("shared_by")
        if not payer or not amount or not shared_by:
            return "<script>alert('Please fill all fields.'); window.history.back();</script>"
        expenses.append({"paid_by": payer, "amount": amount, "shared_by": shared_by})
        if "finish" in request.form:
            return redirect("/summary")
    return render_template("add_expense.html", people=people, expenses=expenses)

@app.route("/edit_expenses", methods=["GET", "POST"])
def edit_expenses():
    if request.method == "POST":
        for i, exp in enumerate(expenses):
            exp["paid_by"] = request.form.get(f"paid_by_{i}")
            exp["amount"] = float(request.form.get(f"amount_{i}"))
            exp["shared_by"] = request.form.getlist(f"shared_by_{i}")
        return redirect("/summary")
    return render_template("edit_expenses.html", people=people, expenses=expenses)

@app.route("/summary")
def summary():
    balances = {p: 0 for p in people}
    total = 0
    for exp in expenses:
        payer = exp["paid_by"]
        amt = exp["amount"]
        shared = exp["shared_by"]
        share = amt / len(shared)
        total += amt
        for person in shared:
            balances[person] -= share
        balances[payer] += amt
    report = []
    for person, balance in balances.items():
        if balance < 0:
            report.append(f"{person} owes ₹{abs(balance):.2f}")
        elif balance > 0:
            report.append(f"{person} gets back ₹{balance:.2f}")
        else:
            report.append(f"{person} is settled up.")
    return render_template("summary.html", report=report, bill_name=bill_name, total=total)

@app.route("/new_split")
def new_split():
    global people, expenses, bill_name
    people = []
    expenses = []
    bill_name = ""
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)

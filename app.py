from flask import Flask, render_template, request, redirect, url_for, session
from collections import defaultdict

app = Flask(__name__)
app.secret_key = 'bros_split_secret_key'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        members = request.form['members'].split(',')
        session['members'] = [m.strip() for m in members]
        session['expenses'] = []
        return redirect(url_for('expenses'))
    return render_template('index.html')

@app.route('/expenses', methods=['GET', 'POST'])
def expenses():
    if request.method == 'POST':
        desc = request.form['desc']
        amount = float(request.form['amount'])
        payer = request.form['payer']
        shared_by = request.form.getlist('shared_by')

        expense = {'desc': desc, 'amount': amount, 'payer': payer, 'shared_by': shared_by}
        session['expenses'].append(expense)
        session.modified = True

        if 'done' in request.form:
            return redirect(url_for('results'))
    return render_template('expenses.html', members=session['members'])

@app.route('/results')
def results():
    balances = defaultdict(float)
    for exp in session['expenses']:
        share = exp['amount'] / len(exp['shared_by'])
        for member in exp['shared_by']:
            balances[member] -= share
        balances[exp['payer']] += exp['amount']

    settlements = []
    owed = sorted([(k, v) for k, v in balances.items() if v < 0], key=lambda x: x[1])
    owing = sorted([(k, v) for k, v in balances.items() if v > 0], key=lambda x: x[1], reverse=True)

    i, j = 0, 0
    while i < len(owed) and j < len(owing):
        ower, owe_amt = owed[i]
        owner, own_amt = owing[j]
        settle_amt = min(-owe_amt, own_amt)
        settlements.append(f"{ower} owes {owner} ₹{settle_amt:.2f}")
        owed[i] = (ower, owe_amt + settle_amt)
        owing[j] = (owner, own_amt - settle_amt)
        if owed[i][1] == 0: i += 1
        if owing[j][1] == 0: j += 1

    return render_template('results.html', balances=balances, settlements=settlements)
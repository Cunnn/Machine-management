from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import csv
import os
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///machines.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Machine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50), nullable=False)
    product_name = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    cost = db.Column(db.Integer, nullable=False)

# 初始化資料庫
def create_tables():
    with app.app_context():
        db.create_all()

@app.route('/')
def index():
    machines = Machine.query.all()
    total_quantity = sum(machine.quantity for machine in machines)
    return render_template('index.html', machines=machines, total_quantity=total_quantity)

@app.route('/add', methods=['GET', 'POST'])
def add_machine():
    if request.method == 'POST':
        name = request.form['name']
        quantity = request.form['quantity']
        new_machine = Machine(name=name, quantity=int(quantity))
        db.session.add(new_machine)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/edit/<int:machine_id>', methods=['GET', 'POST'])
def edit_machine(machine_id):
    machine = Machine.query.get_or_404(machine_id)
    if request.method == 'POST':
        machine.name = request.form['name']
        machine.quantity = int(request.form['quantity'])
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit.html', machine=machine)

@app.route('/delete/<int:machine_id>')
def delete_machine(machine_id):
    machine = Machine.query.get_or_404(machine_id)
    db.session.delete(machine)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/export')
def export_data():
    machines = Machine.query.all()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'machines_{timestamp}.csv'
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['id', 'name', 'quantity']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for machine in machines:
            writer.writerow({'id': machine.id, 'name': machine.name, 'quantity': machine.quantity})
    return redirect(url_for('index'))

@app.route('/import', methods=['GET', 'POST'])
def import_data():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.csv'):
            upload_folder = 'uploads'
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            filepath = os.path.join(upload_folder, file.filename)
            file.save(filepath)
            with open(filepath, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    new_machine = Machine(name=row['name'], quantity=int(row['quantity']))
                    db.session.add(new_machine)
                db.session.commit()
            os.remove(filepath)
        return redirect(url_for('index'))
    return render_template('import.html')

@app.route('/purchase_cost', methods=['GET', 'POST'])
def purchase_cost():
    if request.method == 'POST':
        date = request.form['date']
        product_name = request.form['product_name']
        quantity = request.form['quantity']
        cost = request.form['cost']
        new_purchase = Purchase(date=date, product_name=product_name, quantity=int(quantity), cost=int(cost))
        db.session.add(new_purchase)
        db.session.commit()
        return redirect(url_for('purchase_cost'))
    purchases = Purchase.query.all()
    return render_template('purchase_cost.html', purchases=purchases)

@app.route('/edit_purchase/<int:purchase_id>', methods=['GET', 'POST'])
def edit_purchase(purchase_id):
    purchase = Purchase.query.get_or_404(purchase_id)
    if request.method == 'POST':
        purchase.date = request.form['date']
        purchase.product_name = request.form['product_name']
        purchase.quantity = int(request.form['quantity'])
        purchase.cost = int(request.form['cost'])
        db.session.commit()
        return redirect(url_for('purchase_cost'))
    return render_template('edit_purchase.html', purchase=purchase)

@app.route('/delete_purchase/<int:purchase_id>')
def delete_purchase(purchase_id):
    purchase = Purchase.query.get_or_404(purchase_id)
    db.session.delete(purchase)
    db.session.commit()
    return redirect(url_for('purchase_cost'))

@app.route('/revenue')
def revenue():
    return render_template('revenue.html')

@app.route('/member_management')
def member_management():
    return render_template('member_management.html')

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)

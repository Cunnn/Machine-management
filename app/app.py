import threading
import pystray
from pystray import MenuItem as item
from PIL import Image
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///machines.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Machine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

@app.route('/')
def index():
    machines = Machine.query.all()
    total_quantity = sum(machine.quantity for machine in machines)
    return render_template('index.html', machines=machines, total_quantity=total_quantity)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form['name']
        quantity = int(request.form['quantity'])
        new_machine = Machine(name=name, quantity=quantity)
        db.session.add(new_machine)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/edit/<int:machine_id>', methods=['GET', 'POST'])
def edit(machine_id):
    machine = Machine.query.get_or_404(machine_id)
    if request.method == 'POST':
        machine.name = request.form['name']
        machine.quantity = int(request.form['quantity'])
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit.html', machine=machine)

@app.route('/delete/<int:machine_id>')
def delete(machine_id):
    machine = Machine.query.get_or_404(machine_id)
    db.session.delete(machine)
    db.session.commit()
    return redirect(url_for('index'))

def create_image(image_path):
    # Open the image file
    image = Image.open(image_path)
    return image

def setup(tray):
    tray.icon = create_image("doll.png")  # 替換成你的 JPG 圖片路徑
    tray.visible = True

def quit_app(tray):
    tray.visible = False
    tray.stop()
    os._exit(0)

if __name__ == '__main__':
    # Create the system tray icon
    icon = pystray.Icon("test")
    icon.menu = pystray.Menu(item('Quit', quit_app))
    icon.icon = create_image("doll.png")  # 替換成你的 JPG 圖片路徑
    icon.run(setup)

    # Run Flask app in a separate thread
    threading.Thread(target=app.run).start()

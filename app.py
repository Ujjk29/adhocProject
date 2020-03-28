import os
from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
db = SQLAlchemy(app)




#database for guest details
class Guest(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.Unicode(50), nullable = False)
    
    
    def __repr__ (self):
        return '<Task %r >' % self.id

#database for host details
class Host(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.Unicode(50), nullable = False)
    

    def __repr__ (self):
        return '<Task %r >' % self.id

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/host/', methods=['POST','GET'])
def host():
    if request.method == 'POST':
        h_name = request.form['host_name']
        
        new_task = Host(name=h_name)

        db.session.add(new_task)
        db.session.commit()
        return redirect('/host')

    else:
        hosts = Host.query.order_by(Host.id).all()
        return render_template('host.html', hosts = hosts)


              

if __name__ == "__main__":
    app.run(debug=True)   


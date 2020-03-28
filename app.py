from flask import Flask, render_template, url_for, request, redirect, flash
from urllib import request as rs
from flask_sqlalchemy import SQLAlchemy
from bs4 import BeautifulSoup
from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


#### web-scrapping
url = 'https://en.wikipedia.org/wiki/Machine_learning'
htmldata=rs.urlopen(url)
soup = BeautifulSoup(htmldata,'html.parser')
###end of scrapping

@app.route('/')
def index():    
    return render_template('index.html')


@app.route('/main/', methods=['POST','GET'])
def main():
    if request.method == 'POST':
        name = request.form['g_name']
        location = request.form['g_loc']
        
        head = soup.find('h3').text
        return render_template('result.html',**locals() )

    else:        
        return render_template('main.html')


              

if __name__ == "__main__":
    app.run(debug=True)   


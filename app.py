from flask import Flask, render_template, url_for, redirect, request

app = Flask(__name__)

productos = []

@app.route('/')
def root():
    return render_template('index.html')
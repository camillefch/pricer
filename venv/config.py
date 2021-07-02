import os
from flask import Flask
from datetime import timedelta
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, UniqueConstraint
from flask_sqlalchemy import SQLAlchemy

app=Flask(__name__)
app.config['SECRET_KEY']='123'
app.permanent_session_lifetime = timedelta(minutes=5)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///db.sqlite3"
db = SQLAlchemy(app)
db.init_app(app)
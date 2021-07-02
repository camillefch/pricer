from flask import Flask, redirect, url_for, render_template, request, session, flash, make_response
from flask_sqlalchemy import SQLAlchemy
from config import app, db

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100))
    prenom = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    mdp = db.Column(db.String(100))
    adresse = db.Column(db.String(200))
    ville = db.Column(db.String(100))
    pays = db.Column(db.String(100))
    tel = db.Column(db.String(100))
    code_postal = db.Column(db.String(100))
    reduction = db.Column(db.Float)
    admin = db.Column(db.Integer)


    commandes = db.relationship('Commande', backref='client')


class Sous_categorie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)

    produits_ = db.relationship('Produit', backref='sous_categorie')


class Categorie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)

    produits = db.relationship('Produit', backref='categorie')


class Commande_produit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    commande_id = db.Column(db.Integer, db.ForeignKey('commande.id'))
    produit_id = db.Column(db.Integer, db.ForeignKey('produit.id'))
    quantite = db.Column(db.Integer)

    commandesproduits = db.relationship('Produit', backref='produit')
    commandesproduits_ = db.relationship('Commande', backref='commande')


class Commande(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    numero = db.Column(db.String)


class Produit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prix = db.Column(db.Float, nullable=False)
    categorie_id = db.Column(db.Integer, db.ForeignKey('categorie.id'))
    sous_categorie_id = db.Column(db.Integer, db.ForeignKey('sous_categorie.id'))
    remise= db.Column(db.Float)
    recurrence=db.Column(db.Integer)
    description = db.Column(db.String(300))
    ordre = db.Column(db.Integer)
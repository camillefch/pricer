
#-*- coding : utf-8 -*-

from flask import Flask, redirect, url_for, render_template, request, session, flash, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, UniqueConstraint
from sqlalchemy.orm import mapper, sessionmaker, Session
import datetime
from datetime import timedelta
import pdfkit
import os
import ast
from classes import Categorie, Produit, Sous_categorie, Commande, Commande_produit, Client
from config import app, db
import admin
from admin import admin_login_required, login_required
from functools  import wraps
import hashlib


#-*- coding : utf-8 -*-


@app.route('/')
def main():
    return render_template("accueil.html", **locals())

@app.route('/inscription', methods = ["GET", "POST"])
def inscription():
    if request.method == "GET":
        return render_template("inscription.html")
    else :
        nom = request.form["nom"]
        prenom = request.form["prenom"]
        email = request.form["email"]
        adresse = request.form["adresse"]
        ville = request.form["ville"]
        code_postal = request.form["code postal"]
        pays = request.form["pays"]
        tel = request.form["tel"]
        password = request.form["password"]
        password_ = request.form["password_confirmation"]
        if password != password_ :
            flash("Les mots de passe ne sont pas identiques")
            return redirect(url_for('inscription'))
        client = Client.query.filter_by(email = email).first()
        if client != None :
            flash ("Erreur : Un compte est déjà associé à cet email")
            return render_template("inscription.html")
        password = hashlib.sha224(password.encode('utf-8')).hexdigest()
        new_client=Client(nom =nom, prenom= prenom, mdp = password, email = email, adresse = adresse, ville = ville, code_postal=code_postal, pays=pays, tel=tel, admin=0, reduction=0)
        db.session.add(new_client)
        db.session.commit()
        flash("Inscription réussie")
        return redirect(url_for("main"))


@app.route('/connexion', methods=["POST", "GET"])
def connexion():
    if request.method == "POST":
        session.permanent = True
        email = request.form['email']
        mdp = request.form['password']
        mdp = hashlib.sha224(mdp.encode('utf-8')).hexdigest()
        client_ = Client.query.filter_by(email = email).first()
        if client_ == None :
           flash("vous n'etes pas inscrit")
           return redirect(url_for('connexion'))
        if client_.mdp != mdp :
           flash ("mot de passe éronné")
           return redirect(url_for('connexion'))
        session['client']={}
        session['client']['email']= request.form['email']
        session ['client']['prenom_']= client_.prenom
        if client_.admin == 1 :
            return redirect(url_for("admin"))
        return redirect(url_for("main"))
    else:
        if "client" in session :
            email = session['client']['email']
            client_ = Client.query.filter_by(email=email).first()
            prenom_ = client_.prenom
            flash (f'{prenom_}, vous êtes déjà connecté')
            return redirect(url_for('main'))
        return render_template("connexion.html", **locals())


@app.route('/deconnexion')
@login_required
def deconnexion():
    session.clear()
    flash ("Deconnexion réussie")
    return redirect(url_for('main'))


@app.route('/modifierprofil', methods = ["POST", "GET"])
@login_required
def modifierprofil():
    if request.method == "GET":
        email = session['client']['email']
        client = Client.query.filter_by(email=email).first()
        return render_template("modifierprofil.html", **locals())
    if request.method == "POST":
        email = session['client']['email']
        client = Client.query.filter_by(email=email).first()
        L={}
        L['nom'] = f"{client.nom}"
        L['prenom'] = f"{client.prenom}"
        L['ville']=client.ville
        L['adresse']= client.adresse
        L['code_postal']= client.code_postal
        L['pays']= client.pays
        L['tel']= client.tel
        for i in request.form :
            if request.form[i] != "":
                L[f"{i}"]=request.form[i]
        client.nom = L["nom"]
        client.prenom = L["prenom"]
        client.ville = L['ville']
        client.adresse = L['adresse']
        client.code_postal = L['code_postal']
        client.pays= L['pays']
        client.tel = L['tel']
        db.session.commit()
        flash("les informations ont bien été modifiées")
        return redirect(url_for("modifierprofil"))


@app.route('/modifierlemdp', methods =["GET", "POST"])
@login_required
def modifierlemdp():
    email = session["client"]["email"]
    client = Client.query.filter_by(email=email).first()
    if request.method == "GET":
        return render_template("modifierlemdp.html")
    if request.method == "POST":
        mdp = request.form["mdp"]
        mdp = hashlib.sha224(mdp.encode('utf-8')).hexdigest()
        if client.mdp == mdp:
            newmdp =request.form["newmdp"]
            newmdp_ = request.form["newmdp_"]
            if newmdp == newmdp_ :
                newmdp = hashlib.sha224(newmdp.encode('utf-8')).hexdigest()
                client.mdp = newmdp
                db.session.commit()
                flash("Le mot de passe a bien été modifié")
                return redirect(url_for("modifierprofil"))
            else:
                flash("Erreur : les deux mots de passe ne correspondent pas")
                return redirect(url_for("modifierlemdp"))
        else:
            flash('Erreur :le mot de passe est incorrect')
            return redirect(url_for("modifierlemdp"))




@app.route("/categories", methods=["GET", "POST"])
def categories():
    if request.method == "GET":
        categories = Categorie.query.all()
        L = []
        for cat in categories:
            print(cat)
            cat_ = []
            products = Produit.query.filter_by(categorie_id=cat.id).all()
            for x in products:
                cat_.append(
                    [x.id, x.nom, x.description,x.prix, x.categorie.nom, x.categorie.remarques])
            L.append(cat_)
        print(len(L))
        return render_template("categories.html", **locals())

@app.route("/prixdisques")
def prixdisques ():
    SAN = Produit.query.filter_by(id=3).first()
    Local = Produit.query.filter_by(id=4).first()
    Distance = Produit.query.filter_by(id=5).first()
    PrixGOSAN =[]
    LOCAL =[]
    DISTANCE=[]
    Volume = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 2000, 3000, 4000, 5000]
    prix=0
    for i in range(14):
        prix = float(SAN.prix)*((float(1)-(float(SAN.remise)))**i)
        prix_mois = float(Volume[i])*float(prix)
        prix = round(prix, 3)
        prix_mois = round(prix_mois, 2)
        PrixGOSAN.append([prix,prix_mois])

        prix = float(Local.prix)*((float(1)-(float(Local.remise)))**i)
        prix_mois = float(Volume[i]) * float(prix)
        prix = round(prix, 3)
        prix_mois = round(prix_mois, 2)
        LOCAL.append([prix, prix_mois])

        prix = float(Distance.prix)*((float(1)-(float(Distance.remise)))**i)
        prix_mois = float(Volume[i]) * float(prix)
        prix = round(prix, 3)
        prix_mois = round(prix_mois, 2)
        DISTANCE.append([prix, prix_mois])



    return render_template('prixdisques.html', **locals())



@app.route("/devis", methods=["POST","GET"])
def devis():
    ##rec=liste des produits avec prix mensuel
    ##pasrec = liste produits à payer une seule fois
    rec= [] ; pasrec=[] ; TOTAL_REC = 0 ; TOTAL_PASREC=0
    if request.method == "POST":
        for i in request.form:
            quantite = request.form[i]
            if quantite!= "":
                quantite = int(ast.literal_eval(quantite))
                if quantite != 0 :
                    p = Produit.query.filter_by(id=i).first()
                    if p.recurrence == 1:
                        if p.remise == None :
                            total = round((float(quantite)*float(p.prix)),2)
                            TOTAL_REC += total
                            rec.append([i, quantite, p.id, p.nom, p.prix, total])
                        else:
                            remise = p.remise
                            quantite=int(quantite)
                            if quantite in range(0,200):
                                prix = float(p.prix)*((float(1)-float(remise))**0)
                            if quantite in range(200,300):
                                prix = float(p.prix)*((float(1)-float(remise))**1)
                            if quantite in range(300,400):
                                prix = float(p.prix)*((float(1)-float(remise))**2)
                            if quantite in range(400,500):
                                prix = float(p.prix)*((float(1)-float(remise))**3)
                            if quantite in range(600,700):
                                prix = float(p.prix)*((float(1)-float(remise))**4)
                            if quantite in range(700,800):
                                prix = float(p.prix)*((float(1)-float(remise))**5)
                            if quantite in range(800,900):
                                prix = float(p.prix)*((float(1)-float(remise))**6)
                            if quantite in range(900,1000):
                                prix = float(p.prix)*((float(1)-float(remise))**7)
                            if quantite in range(1000,2000):
                                prix = float(p.prix)*((float(1)-float(remise))**8)
                            if quantite in range(1000,2000):
                                prix = float(p.prix)*((float(1)-float(remise))**9)
                            if quantite in range(3000,4000):
                                prix = float(p.prix)*((float(1)-float(remise))**10)
                            if quantite in range(4000,5000):
                                prix = float(p.prix)*((float(1)-float(remise))**11)
                            if quantite >= 5000 :
                                prix = float(p.prix)*((float(1)-float(remise))**12)
                            prix = round(prix, 3)
                            total = round((float(quantite) * float(prix)), 2)
                            TOTAL_REC+= total
                            rec.append([i, quantite, p.id, p.nom, prix, total])
                else :
                    total = round((float(quantite) * float(p.prix)), 2)
                    TOTAL_PASREC += total
                    pasrec.append([i, quantite, p.id, p.nom, p.prix, total])
        return render_template("devis.html", **locals())
        
        
        
@app.route("/genererpdf2", methods=["POST"])
@login_required
def genererpdf2():
    if request.method == "POST":
        ##recup infos clients
        email = session['client']['email']
        client_ = Client.query.filter_by(email=email).first()
        ##infos pour le tableau
        ##Produits paiement reccurrent
        prixrec_=request.form["liste"]
        print(prixrec_)
        prixrec_=eval(prixrec_)##transformer rec en liste
        prixrec=[]
        TOTAL_PRIXREC = 0
        for x in prixrec_:
            x = eval('x')
            prixrec.append(x)
            TOTAL_PRIXREC += x[5]
        reduction = client_.reduction
        TOTAL_REDUC_PRIXREC = float(TOTAL_PRIXREC)*(1-float(reduction))
        TOTAL_REDUC_PRIXREC = round(TOTAL_REDUC_PRIXREC, 2)
        ##Produits payer une seule fois
        prixpasrec_ = request.form["liste_"]
        prixpasrec_ = eval(prixpasrec_)
        prixpasrec = [];
        TOTAL_PRIXPASREC = 0
        for x in prixpasrec_ :
            x = eval('x')
            prixpasrec_.append(x)
            TOTAL_PRIXPASREC += x[5]
        reduction = client_.reduction
        TOTAL_REDUC_PRIXPASREC = float(TOTAL_PRIXPASREC) * (1 - float(reduction))
        TOTAL_REDUC_PRIXPASREC = round(TOTAL_REDUC_PRIXPASREC, 2)
        ## création commande
        date = datetime.datetime.now()
        jour = (date.strftime('%d'))
        mois = (date.strftime('%m'))
        annee = (date.strftime('%Y'))
        new_commande = Commande(client_id = client_.id)
        db.session.add(new_commande)
        db.session.commit()
        numero = annee + mois + jour + '-bcd' +f'{new_commande.id}'
        new_commande.numero = numero
        db.session.commit()
        ##creation produits_commandes
        for x in prixrec :
            quantite = x[1]
            id_produit = x[2]
            id_commande = new_commande.id
            new_commande_produit = Commande_produit(commande_id = id_commande, produit_id = id_produit, quantite = quantite)
            db.session.add(new_commande_produit)
        for x in prixpasrec :
            quantite = x[1]
            id_produit = x[2]
            id_commande = new_commande.id
            new_commande_produit = Commande_produit(commande_id = id_commande, produit_id = id_produit, quantite = quantite)
            db.session.add(new_commande_produit)
        db.session.commit()
        ##creationpdf
        rendered = render_template("genererpdf2.html", **locals())
        pdf = pdfkit.from_string(rendered, False)
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline ; filename = devis{numero}.pdf'
        return response
    else:
        response = session['pdf']
        return response
    





if __name__ == "__main__":
    app.run(debug=True)

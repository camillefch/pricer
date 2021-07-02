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
from functools  import wraps
import hashlib


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "client" in session :
            return f(*args, **kwargs)
        else:
            flash("Vous devez d'abord vous connecter")
            return redirect(url_for('main'))
    return wrap


def admin_login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        email = session ['client']['email']
        client = Client.query.filter_by(email = email).first()
        if client.admin == 1 :
            return f(*args, **kwargs)
        else:
            flash("Vous devez être administateur")
            return redirect(url_for('main'))
    return wrap



@app.route("/admin", methods=["POST", "GET"])
@login_required
@admin_login_required
def admin():
    return render_template('admin.html')



@app.route("/admin/clients", methods=["GET"])
@login_required
@admin_login_required
def adminclients():
    clients = Client.query.all()
    L = []
    admin = 'non'
    for x in clients:
        if x.admin == 1:
            admin = 'oui'
        else:
            admin = 'non'
        L.append([x.id, x.nom, x.prenom, x.email, x.reduction, admin])
    if request.method == "GET":
        return render_template("adminclients.html", **locals())


@app.route("/admin/ajouterclient", methods=["POST"])
@login_required
@admin_login_required
def ajouterclient():
    if request.method == "POST":
        nom = request.form["prenom_client"];
        prenom = request.form["prenom_client"];
        email = request.form["email_client"];
        reduction = request.form["reduction_client"]
        mdp = request.form["mdp"]
        mdp_ = request.form["mdp_"]
        if mdp_ != mdp:
            flash("Erreur : les deux mots de passe ne correspondent pas ")
            return redirect(url_for("adminclients"))
        mdp = hashlib.sha224(mdp.encode('utf-8')).hexdigest()
        new_client = Client(nom=nom, prenom=prenom, email=email, reduction=reduction, mdp=mdp)
        db.session.add(new_client)
        db.session.commit()
        flash("Client ajouté")
        return redirect(url_for("adminclients"))


@app.route("/admin/supprimerclient/<int:id>", methods=["GET"])
@login_required
@admin_login_required
def supprimerclient(id):
    if request.method == "GET":
        client = Client.query.filter_by(id=id).first()
        nom = client.nom
        prenom = client.prenom
        id = client.id
        db.session.delete(client)
        db.session.commit()
        flash(f"Le client  (id = {id} ; nom ={nom} ; prenom = {prenom}), a bien été supprimé de la base de données")
        return redirect(url_for("adminclients"))


@app.route("/admin/modifierreduction/<int:id>", methods=["POST"])
@login_required
@admin_login_required
def modifierreduction(id):
    client_ = Client.query.filter_by(id=id).first()
    new_red = request.form["reduction"]
    print(client_)
    new_red = ast.literal_eval(new_red)
    new_red = float(new_red)
    ancienne_red = client_.reduction
    client_.reduction = new_red
    db.session.commit()
    flash(f"la reduction du client {client_.nom} {client_.prenom} est passé de {ancienne_red} à {new_red} ")
    return redirect(url_for("adminclients"))


@app.route("/admin/modifieradmin/<int:id>", methods=["GET"])
@login_required
@admin_login_required
def modifieradmin(id):
    client_ = Client.query.filter_by(id=id).first()
    if client_.admin == 1:
        client_.admin = 0
    else:
        client_.admin = 1
    db.session.commit()
    return redirect(url_for("adminclients"))


@app.route("/admin/commandes")
@login_required
@admin_login_required
def admincommandes():
    clients = Client.query.all()
    commandes = Commande.query.all()
    L = []
    for x in commandes:
        client_id = x.client_id
        client = Client.query.filter_by(id=client_id).first()
        if client == None:
            client_prenom = "-"
            client_nom = "-"
            client_id = "-"
        else:
            client_prenom = client.prenom
            client_nom = client.nom
        L.append([x.id, client_id, client_nom, client_prenom, x.numero])
    return render_template("admincommandes.html", **locals())


@app.route("/admin/detailscommannde/<int:id>", methods=["GET"])
@login_required
@admin_login_required
def detailscommande(id):
    produits_commandes = Commande_produit.query.filter_by(commande_id=id).all()
    commande = Commande.query.filter_by(id=id).first()
    print(produits_commandes)
    print(commande)
    numero_commande = commande.numero
    nom_client = commande.client.nom
    prenom_client = commande.client.prenom
    L = []
    TOTAL = 0
    for x in produits_commandes:
        p = Produit.query.filter_by(id=x.produit_id).first()
        print(p)
        if p.remise == None:
            total = round((float(x.quantite) * float(p.prix)), 2)
            TOTAL += total
            L.append([p.id, p.nom, p.prix, x.quantite, total])
        else:
            remise = p.remise
            quantite = int(x.quantite)
            if quantite in range(0, 200):
                prix = float(p.prix) * ((float(1) - float(remise)) ** 0)
            if quantite in range(200, 300):
                prix = float(p.prix) * ((float(1) - float(remise)) ** 1)
            if quantite in range(300, 400):
                prix = float(p.prix) * ((float(1) - float(remise)) ** 2)
            if quantite in range(400, 500):
                prix = float(p.prix) * ((float(1) - float(remise)) ** 3)
            if quantite in range(600, 700):
                prix = float(p.prix) * ((float(1) - float(remise)) ** 4)
            if quantite in range(700, 800):
                prix = float(p.prix) * ((float(1) - float(remise)) ** 5)
            if quantite in range(800, 900):
                prix = float(p.prix) * ((float(1) - float(remise)) ** 6)
            if quantite in range(900, 1000):
                prix = float(p.prix) * ((float(1) - float(remise)) ** 7)
            if quantite in range(1000, 2000):
                prix = float(p.prix) * ((float(1) - float(remise)) ** 8)
            if quantite in range(1000, 2000):
                prix = float(p.prix) * ((float(1) - float(remise)) ** 9)
            if quantite in range(3000, 4000):
                prix = float(p.prix) * ((float(1) - float(remise)) ** 10)
            if quantite in range(4000, 5000):
                prix = float(p.prix) * ((float(1) - float(remise)) ** 11)
            if quantite >= 5000:
                prix = float(p.prix) * ((float(1) - float(remise)) ** 12)
            prix = round(prix, 3)
            total = round((float(quantite) * float(prix)), 2)
            TOTAL += total
            L.append([p.id, p.nom, prix, quantite, total])
    return render_template('detailscommande.html', **locals())


@app.route("/admin/supprimercommannde/<int:id>", methods=["GET"])
@login_required
@admin_login_required
def supprimercommande(id):
    produits_commandes = Commande_produit.query.filter_by(commande_id=id).all()
    print(produits_commandes)
    for x in produits_commandes:
        db.session.delete(x)
        db.session.commit()
    commande = Commande.query.filter_by(id=id).first()
    numero = commande.numero
    print(commande)
    db.session.delete(commande)
    db.session.commit()
    flash(f"la commande numéro {numero}, d'id {id}, a bien été supprimée")
    return redirect(url_for('admincommandes'))


@app.route("/admin/commandeproduit", methods=["POST", "GET"])
@login_required
@admin_login_required
def admincommandeproduit():
    commande_produits = Commande_produit.query.all()
    L = []
    for x in commande_produits:
        produit = Produit.query.filter_by(id=x.produit_id).first()
        produit_nom = produit.nom
        commande = Commande.query.filter_by(id=x.commande_id).first()
        numero = commande.numero
        L.append([x.commande_id, numero, x.produit_id, produit_nom, x.quantite])
    return render_template("admincommandeproduit.html", **locals())



@app.route("/admin/produits", methods=["GET", "POST"])
@login_required
@admin_login_required
def adminproduits():
    if request.method == "GET":
        categories = Categorie.query.all()
        L = []
        for cat in categories:
            print(cat)
            cat_ = []
            products = Produit.query.filter_by(categorie_id=cat.id).all()
            for x in products:
                cat_.append(
                    [x.id, x.nom,  x.prix, x.categorie.nom, x.categorie.id, x.sous_categorie.nom, x.sous_categorie.id,
                     x.remise, x.description , x.ordre, x.recurrence])
            L.append(cat_)
        print(len(L))
        return render_template("adminproduits.html", **locals())

@app.route("/admin/ajouterproduit", methods=["POST"])
@login_required
@admin_login_required
def ajouterproduit():
    if request.method == "POST":
        nom = request.form["nom_produit"];
        categorie = int(request.form["categorie_produit"])
        ordre = request.form["ordre_produit"]
        prix = request.form["prix_produit"];
        souscategorie = int(request.form["souscategorie_produit"])
        categories = Categorie.query.all()
        souscategories = Sous_categorie.query.all()
        cat_id = 0
        sscat_id = 0
        if isinstance(ordre, int) == False:
            ordre = 0
        if prix == "":
            prix = 0
        for cat in categories:
            if cat.id == categorie:
                cat_id = categorie
        for sscat in souscategories:
            if sscat.id == souscategorie:
                sscat_id = souscategorie
        new_produit = Produit(nom=nom, categorie_id=cat_id, prix=prix, sous_categorie_id=sscat_id)
        db.session.add(new_produit)
        db.session.commit()
        if ordre == 0 :
            new_produit.ordre = new_produit.id
            db.session.commit()
        flash(f"produit {nom}  ajouté")
        return redirect(url_for("adminproduits"))



@app.route("/admin/supprimerproduit/<int:id>", methods=["GET"])
@login_required
@admin_login_required
def supprimerproduit(id):
    if request.method == "GET":
        produit = Produit.query.filter_by(id=id).first()
        nom = produit.nom
        id = produit.id
        db.session.delete(produit)
        db.session.commit()
        flash(f"Le produit (id = {id} ; nom ={nom}), a bien été supprimé")
        return redirect(url_for("adminproduits"))

@app.route("/admin/modifierproduit/<int:id>" , methods=["POST", "GET"])
@login_required
@admin_login_required
def modifierproduit(id):
    if request.method=="GET":
        x = Produit.query.filter_by(id=id).first()
        return render_template("modifierproduit.html", **locals())
    else :
        produit = Produit.query.filter_by(id=id).first()
        ##prix
        new_prix = request.form["prix"]
        if new_prix != "":
            new_prix = ast.literal_eval(new_prix)
            new_prix= float(new_prix)
            produit.prix = new_prix
            db.session.commit()
        ##categorie
        new_cat= request.form["categorie"]
        if new_cat != "":
            new_cat=int(new_cat)
            produit.categorie_id = new_cat
            db.session.commit()
        ##ordre
        new_ordre = request.form["ordre"]
        if new_ordre != "":
            new_ordre= int(new_ordre)
            produit.ordre = new_ordre
            db.session.commit()
        ##sscategorie
        new_sscat = request.form["souscategorie"]
        if new_sscat != "":
            new_sscat=int(new_sscat)
            produit.sous_categorie_id = new_sscat
            db.session.commit()
        ##remise
        new_remise = request.form["remise"]
        if new_remise !="":
            new_remise = ast.literal_eval(new_remise)
            produit.remise = new_remise
            db.session.commit()
        ##nom
        new_nom = request.form["nom"]
        if new_nom != "":
            produit.nom = new_nom
            db.session.commit()
         ##nom
        new_rec = request.form["recurrence"]
        if new_rec != "":
            produit.recurrence = new_rec
            db.session.commit()
        ##description
        new_description = request.form["description"]
        if new_description != "":
            produit.description = new_description
            db.session.commit()
        return redirect(url_for("modifierproduit" ,  id=id ))


@app.route("/admin/modifierprix/<int:id>", methods=["POST"])
@login_required
@admin_login_required
def modifierprix(id):
    produit = Produit.query.filter_by(id=id).first()
    new_prix = request.form["prix"]
    new_prix = ast.literal_eval(new_prix)
    ancien_prix = produit.prix
    produit.prix = new_prix
    db.session.commit()
    flash(f"le prix du produit {produit.nom} est passé de {ancien_prix} € à {new_prix} €")
    return redirect(url_for("adminproduits"))


@app.route("/admin/modifierremise/<int:id>", methods=["POST"])
@login_required
@admin_login_required
def changerordre(id):
    produit = Produit.query.filter_by(id=id).first()
    ordre = request.form["ordre"]
    ordre= ast.literal_eval(ordre)
    produit.ordre = ordre
    db.session.commit()
    return redirect(url_for("adminproduits"))


@app.route("/admin/categories", methods=["GET", "POST"])
@login_required
@admin_login_required
def admincategories():
    if request.method == "GET":
        categories = Categorie.query.all()
        L = []
        for cat in categories:
            L.append([cat.id , cat.nom])
        return render_template("admincategories.html", **locals())

@app.route("/admin/ajoutercategorie", methods=["POST"])
@login_required
@admin_login_required
def ajoutercategorie():
    nom = request.form["nom"]
    cat = Categorie(nom=nom)
    db.session.add(cat)
    db.session.commit()
    return redirect(url_for("admincategories"))

@app.route("/admin/supprimercategorie/<int:id>", methods=["GET"])
@login_required
@admin_login_required
def supprimercategorie(id):
    if request.method == "GET":
        cat = Categorie.query.filter_by(id=id).first()
        nom = cat.nom
        id = cat.id
        db.session.delete(cat)
        db.session.commit()
        flash(f"La categorie (id = {id} ; nom ={nom}), a bien été supprimée")
        return redirect(url_for("admincategories"))

@app.route("/admin/souscategories", methods=["GET", "POST"])
@login_required
@admin_login_required
def adminsouscategories():
    if request.method == "GET":
        ss_categories = Sous_categorie.query.all()
        L = []
        for ss_cat in ss_categories:
            L.append([ss_cat.id , ss_cat.nom])
        return render_template("adminsouscategories.html", **locals())

@app.route("/admin/ajoutersouscategorie/", methods=["POST"])
@login_required
@admin_login_required
def ajoutersouscategorie():
    nom = request.form["nom"]
    sscat = Sous_categorie(nom=nom)
    db.session.add(sscat)
    db.session.commit()
    return redirect(url_for("adminsouscategories"))

@app.route("/admin/supprimersouscategorie/<int:id>", methods=["GET"])
@login_required
@admin_login_required
def supprimersouscategorie(id):
    if request.method == "GET":
        sscat = Sous_categorie.query.filter_by(id=id).first()
        nom = sscat.nom
        id = sscat.id
        db.session.delete(sscat)
        db.session.commit()
        flash(f"La sous categorie (id = {id} ; nom ={nom}), a bien été supprimée")
        return redirect(url_for("adminsouscategories"))




@app.route("/admin/devis/<int:id_client>", methods=["GET", "POST"])
@login_required
@admin_login_required
def admindevis(id_client):
    categories = Categorie.query.all()
    L = []
    for cat in categories:
        print(cat)
        cat_ = []
        products = Produit.query.filter_by(categorie_id=cat.id).all()
        for x in products:
            cat_.append(
                [x.id, x.nom, x.description, x.prix, x.categorie.nom])
        L.append(cat_)
    print(len(L))
    return render_template("admindevis.html", **locals())


@app.route("/admin/pdf/<int:id_client>", methods=["POST"])
@login_required
@admin_login_required
def adminpdf(id_client):
    ##client
    client_ = Client.query.filter_by(id=id_client).first()
    ##infos pour le tableau
    prixrec = []; ##liste des produits paiement mensuel
    prixpasrec= [] ##liste des produits prix à payer une seule fois
    TOTAL_PRIXREC = 0;
    TOTAL_PRIXPASREC = 0
    for i in request.form:
        req = request.form[i]
        quantite = ast.literal_eval(req)
        if quantite != "":
            if quantite !=0 :
                p = Produit.query.filter_by(id=i).first()
                if p.recurrence == 1:
                    if p.remise == None:  ##prix pas evolutifs
                        total = round((float(quantite) * float(p.prix)), 2)
                        TOTAL_PRIXREC += total
                        prixrec.append([i, quantite, p.id, p.nom, p.prix, total])
                    else: ##prix evolutifs
                        remise = p.remise
                        quantite = int(quantite)
                        if quantite in range(0, 200):
                            prix = float(p.prix) * ((float(1) - float(remise)) ** 0)
                        if quantite in range(200, 300):
                            prix = float(p.prix) * ((float(1) - float(remise)) ** 1)
                        if quantite in range(300, 400):
                            prix = float(p.prix) * ((float(1) - float(remise)) ** 2)
                        if quantite in range(400, 500):
                            prix = float(p.prix) * ((float(1) - float(remise)) ** 3)
                        if quantite in range(600, 700):
                            prix = float(p.prix) * ((float(1) - float(remise)) ** 4)
                        if quantite in range(700, 800):
                            prix = float(p.prix) * ((float(1) - float(remise)) ** 5)
                        if quantite in range(800, 900):
                            prix = float(p.prix) * ((float(1) - float(remise)) ** 6)
                        if quantite in range(900, 1000):
                            prix = float(p.prix) * ((float(1) - float(remise)) ** 7)
                        if quantite in range(1000, 2000):
                            prix = float(p.prix) * ((float(1) - float(remise)) ** 8)
                        if quantite in range(1000, 2000):
                            prix = float(p.prix) * ((float(1) - float(remise)) ** 9)
                        if quantite in range(3000, 4000):
                            prix = float(p.prix) * ((float(1) - float(remise)) ** 10)
                        if quantite in range(4000, 5000):
                            prix = float(p.prix) * ((float(1) - float(remise)) ** 11)
                        if quantite >= 5000:
                            prix = float(p.prix) * ((float(1) - float(remise)) ** 12)
                        prix = round(prix, 3)
                        total = round((float(quantite) * float(prix)), 2)
                        TOTAL_PRIXREC += total
                        prixrec.append([i, quantite, p.id, p.nom, prix, total])
            else:  ##produits à payer une seule fois
                total = round((float(quantite) * float(p.prix)), 2)
                TOTAL_PRIXPASREC += total
                prixpasrec.append([i, quantite, p.id, p.nom, p.prix, total])
    ##calcul des totaux
    reduction = client_.reduction
    TOTAL_REDUC_PRIXREC = float(TOTAL_PRIXREC) * (1 - float(reduction))
    TOTAL_REDUC_PRIXREC = round(TOTAL_REDUC_PRIXREC, 2)
    TOTAL_REDUC_PRIXPASREC = float(TOTAL_PRIXPASREC) * (1 - float(reduction))
    TOTAL_REDUC_PRIXPASREC= round(TOTAL_REDUC_PRIXPASREC, 2)
    ## création commande
    date = datetime.datetime.now()
    jour = (date.strftime('%d'))
    mois = (date.strftime('%m'))
    annee = (date.strftime('%Y'))
    new_commande = Commande(client_id=client_.id)
    db.session.add(new_commande)
    db.session.commit()
    numero = annee + mois + jour + '-bcd' + f'{new_commande.id}'
    new_commande.numero = numero
    db.session.commit()
    ##creation produits_commandes
    for x in prixrec:
        quantite = x[1]
        id_produit = x[2]
        id_commande = new_commande.id
        new_commande_produit = Commande_produit(commande_id=id_commande, produit_id=id_produit, quantite=quantite)
        db.session.add(new_commande_produit)
    if prixpasrec != []:
        for x in prixpasrec:
            quantite = x[1]
            id_produit = x[2]
            id_commande = new_commande.id
            new_commande_produit = Commande_produit(commande_id=id_commande, produit_id=id_produit, quantite=quantite)
            db.session.add(new_commande_produit)
    db.session.commit()
    ##creationpdf
    rendered = render_template("genererpdf2.html", **locals())
    pdf = pdfkit.from_string(rendered, False)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline ; filename = devisVNTX.pdf'
    return response


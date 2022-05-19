# Pricer
## Requirements


Flask

SQLAlchemy

flask_sqlalchemy

## installation et mise en route de l'application

- lancer l'environnement virtuel :  
        
        $source ./venv/bin/activate
        
- installer la librairié flask_sqlalchemy avec pip si ce n'est pas fait
- lancer l'application : 

        $python app.py


## 1. Base de données
Produits : id, nom, catégorie_id, sous_categorie_id, prix, recurrence (à payer une fois ou mensuel), description, remise, ordre (affichage)

Catégories : id, nom, remarques 

Sous_categorie : id, nom

Clients : id, nom, prenom , email, mdp, adresse, ville, pays, tel, code_postal, reduction, admin(0 ou 1)

Commandes : id, client_id, numero

Commande_produit : id, produit_id , commande_id, quantite


## 2. Côté Client
Il y a un template « base.html » qui sert de base à tous les autres templates  du site côté client.
La Navbar est présente sur toutes les pages du côté client.
En cliquant sur « pricer » on revient à la page principale.


**2.1. Page principale**



    @app.route('/')
    def main():
        return render_template("accueil.html")
 

**2.2. S’inscrire**

Accessible via la Navbar.

    @app.route('/inscription', methods = ["GET", "POST"])

    def inscription():

    template : « inscription.html »
 
Les mots de passe sont hachés avant d’être envoyés à la base de données : hashlib.sha224
 

**2.3. Se connecter**

On y accede via la navbar si nous ne sommes pas déjà connectés.

    @app.route('/connexion', methods=["POST", "GET"])
    def connexion():

 
template : « connexion.html »
 
 
Une fois connecté, le client est « enregistré » dans une session. Certaines pages lui sont alors accessibles. Si le client est admin il est redirigé sur la page admin après s’être connecté, sinon il est redirigé sur la page d’accueil.
 
Pour réserver certaines pages aux personnes connectées on utilise le décorateur :
 
    def login_required(f) 

**2.4. Se déconnecter**


On y accede via la navbar si on est déjà connecté (cf décorateur)

    @app.route('/deconnexion')
    @login_required
    def deconnexion():

template : « deconnexion.html »
 
Une fois déconnecté, on est renvoyé sur la page principale/d’accueil.


**2.5. Modifier le profil**


On y accède via la navbar lorsqu’on est connecté
On peut modifier les champs nom, prenom, ville, adresse, code_postal, pays, tel. Pour pouvoir modifier unn seul champ et garder les autres en mémoire on utilise un dictionnaire.

    @app.route('/modifierprofil', methods = ["POST", "GET"])
    @login_required
    def modifierprofil():

template : « modifierprofil.html »

Pour modifier le mot de passe on doit être redirigé sur une autre page :
@app.route('/modifierlemdp', methods =["GET", "POST"])
@login_required
def modifierlemdp():

template : « modifierlemdp.html »

   **2.6. Page Prix des disques**

On y accède via la Navbar. On peut changer le taux de réduction mais pas les tranches.

    app.route("/prixdisques")
    def prixdisques ():
    template : « prixdisques.html »

   **2.7. Catalogue**
   
On y accède via la NavBar.

    @app.route("/categories", methods=["GET", "POST"])
    def categories():

template : « categories.html »

Les produits sont rangés par catégorie dans un menu déroulant. Pour se faire on créer une liste de listes de listes :
L =  [ [Produits de la catégorie 1], [Produits de la catégorie 2],  … ]
Avec 
[Produits de la catégorie 1] = [ [ Champs du produit 1 de la catégorie 1],  [Champs du produit 2 de la catégorie 1 ] , ….]
Etc

 On ne peut pas faire un devis commun pour des produits de différentes catégorie. 
« Calculer devis » envoie un formulaire à la page devis et nous envoie dessus. 

    

**2.8. Devis avant pdf**

Le devis est seulement calculé, mais il n’est pas validé donc la commande n’est pas ajoutée à la base de données. Pour cela il faut cliquer sur « Valider et générer le devis ». 

    @app.route("/devis", methods=["POST","GET"])
    def devis():

template : « devis.html »

Pour calculer les prix, il faut différencier les prix mensuels et ceux à payer une seule fois. Dans la base de données on utilise le champ « récurrence » de la table « Produits » pour distinguer les cas. A la fin on a alors un total mensuel et un total à payer une seule fois.

Il faut également prendre en compte la quantité si certains produits sont des disques car ils ont un tarif dégréssif.


  **2.9. Devis  pdf**
  
On accède à cette page après avoir calculé le devis. Il est nécéssaire d’être connecté pour y accéder. Des que l’on accède à cette page, la commande est créée et ajoutée à la base de données.

    @app.route("/genererpdf2", methods=["POST"])
    @login_required
    def genererpdf2():
        if request.method == "POST":

template : « genererpdf2.html »

Les mêmes questions de prix récurrent ou non se posent.
On doit également gérer les remises attribuer individuellement à chaque client.
Dans le templates le « prix apes remise » s’affiche seulement s’il est dfférent de celui avant la remise.
Pour générer le pdf on utilise pdfkit qui semble fonctionner seulement sur linux.

## 3. Côté administrateur
Toutes les fonctions python liées à la page administrateur sont dans le script admin.py appelé par app.py

   **3.1. Accès limité aux administrateurs**
   
Comme pour restreindre certaines pages aux utilisateurs connectés, on utilise un décorateur pour limiter l’acces des pages suivantes aux utilisateurs qui ont les droits d’admin ( 1 dans la base de données)

    def login_required(f) 
    def admin_login_required(f)
 
 
   **3.2. Page d’accueil admin**
   
Lors de la connexion à un compte admin, on est redirigé vers la page d’accueil admin 

    @app.route("/admin", methods=["POST", "GET"])
    @login_required
    @admin_login_required
    def admin():
 
Templates : admin.html
 

  **3.3. Page produits**
    On y accede via la navbar.

    @app.route("/admin/produits", methods=["GET", "POST"])
    @login_required
    @admin_login_required
    def adminproduits():
 
 
Templates : adminproduits.html
 
 
**3.3.1 Liste des produits**

Les produits sont listés par catégorie. Si une catégorie ne contient pour le moment aucun produit, elle n’est pas affichée.
    
 **3.3.2. Modifier un produit**
 **3.3.3. Ajouter un produit**


    @app.route("/admin/ajouterproduit", methods=["POST"])
    @login_required
    @admin_login_required
    def ajouterproduit():

  **3.3.4. Supprimer un produit**

    @app.route("/admin/supprimerproduit/<int:id>", methods=["GET"])
    @login_required
    @admin_login_required
    def supprimerproduit(id):

**3.4. Page catégories**

Fonctionne comme la page produits
        
     **3.5. Page commandes**

    @app.route("/admin/commandes")
    @login_required
    @admin_login_required
    def admincommandes():
 
**3.5.1. Détails commandes**


    @app.route("/admin/detailscommannde/<int:id>", methods=["GET"])
    @login_required
    @admin_login_required
    def detailscommande(id):
 
 **3.5.2. Supprimer commande**

    @app.route("/admin/supprimercommannde/<int:id>", methods=["GET"])
    @login_required
    @admin_login_required
    def supprimercommande(id):
    
**3.6. Page Clients**
On y accede via la Navbar du côté admin.

    @app.route("/admin/clients", methods=["GET"])
    @login_required
    @admin_login_required
    def adminclients():


**3.6. Page client**
**3.6.1. Ajouter un client**


Possible depuis la page client du côté administrateur. Champs à remplir directement depuis cette page.

    @app.route("/admin/ajouterclient", methods=["POST"])
    @login_required
    @admin_login_required
    def ajouterclient():

**3.6.2. Supprimer un client**


Possible depuis la page client du côté administrateur.

    @app.route("/admin/supprimerclient/<int:id>", methods=["GET"])
    @login_required
    @admin_login_required
    def supprimerclient(id):
 
**3.6.3. Modifier la réduction d’un client**


Possible depuis la page client du côté administrateur.

    @app.route("/admin/modifierreduction/<int:id>", methods=["POST"])
    @login_required
    @admin_login_required
    def modifierreduction(id):
 
 
**3.6.4. Modifier les droits utilisateurs**


Possible depuis la page clients du côté administrateur.

    @app.route("/admin/modifieradmin/<int:id>", methods=["GET"])
    @login_required
    @admin_login_required
    def modifieradmin(id):
 
 
**3.6.5. Générer un devis à un client à sa place**



Possible depuis la page client « lui générer un devis ».  Renvoie sur la page admin devis qui ressemble à la page ______ du site côté client. 

    @app.route("/admin/devis/<int:id_client>", methods=["GET", "POST"])
    @login_required
    @admin_login_required
    def admindevis(id_client):
 On rentre les quantités des produits voulus, puis valide ce qui génère le pdf, ajoute la commande à la base de données et renvoie sur 


    @app.route("/admin/pdf/<int:id_client>", methods=["POST"])
    @login_required
    @admin_login_required
    def adminpdf(id_client):


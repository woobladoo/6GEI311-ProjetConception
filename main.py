from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user

app = Flask(__name__)
app.secret_key = "clesupersecrete"

# Informations d'utilisateur hardcoder
users = {
    "admin": "admin",
    "user": "user",
}

# Initialiser Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, user_id, username, email):
        self.user_id = user_id  # Set the user ID when the object is created
        self.username = username  # Set the username
        self.email = email  # Set the email

    def get_id(self):
        return str(self.user_id)  # Ensure it's returned as a string

    def get_username(self):
        return self.username

    def get_email(self):
        return self.email

# Charger l'utilisateur par ID
@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, email FROM users WHERE user_id = ?", (user_id,))
    user_data = cursor.fetchone()
    conn.close()

    if user_data:
        return User(user_id=user_data[0], username=user_data[1], email=user_data[2])
    return None

def get_auction(id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM auctions WHERE product_id = ?", (id,))
    auction = cursor.fetchone()

    if auction:
        # Récupérer le nom d'utilisateur du meilleur enchérisseur
        highest_bidder_id = auction[4]
        cursor.execute("SELECT username FROM users WHERE user_id = ?", (highest_bidder_id,))
        highest_bidder = cursor.fetchone()
        
        # Ajouter le nom d'utilisateur à l'objet auction
        if highest_bidder:
            auction = list(auction)  # Convertir le tuple en liste pour le modifier
            auction.append(highest_bidder[0])  # Ajouter le nom d'utilisateur
        else:
            auction = list(auction)
            auction.append(None)  # Si l'enchérisseur n'existe pas, ajouter `None`
    conn.close()
    return auction


def get_user(identifier, is_username=False):
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    if is_username:
        cursor.execute("SELECT * FROM users WHERE username = ?", (identifier,))
    else:
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (identifier,))
    
    user_data = cursor.fetchone()
    conn.close()
    
    if user_data:
        # Convert the result into a dictionary
        user = {
            'user_id': user_data[0],
            'username': user_data[1],
            'email': user_data[2],
            'password': user_data[3],  # Be careful with storing passwords in plain text
            'created_at': user_data[4]
        }
        return user
    return None


@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, username, email, password FROM users WHERE username = ?", (username,))
        user_data = cursor.fetchone()
        conn.close()

        if user_data and user_data[3] == password:  # Vérifier si le mot de passe correspond
            user = User(user_id=user_data[0], username=user_data[1], email=user_data[2])  # Créer un objet User avec tous les paramètres
            login_user(user)  # Connecter l'utilisateur
            flash(f"Bienvenue {username}!", "success")
            return redirect(url_for("accueil"))
        else:
            flash("Nom d'utilisateur ou mot de passe incorrect.", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route('/logout', methods=["GET", "POST"])
@login_required
def logout():
    logout_user()  # Déconnexion de l'utilisateur
    flash("Vous êtes maintenant déconnecté.", "info")
    return redirect(url_for('login'))

@login_required
@app.route("/accueil")
def accueil():

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Récupérer les articles
    cursor.execute("SELECT * FROM products")
    items = cursor.fetchall()
    conn.close()

    return render_template("accueil.html", items=items)

@app.route("/vente")
def vente():

    current_user_id = current_user.get_id()
    print("Current User ID:", current_user_id)    
    
    return render_template("vente.html", current_user_id = current_user_id)

@app.route('/submit_item', methods=['POST'])
def submit_item():

    print("Current user ID:", current_user.get_id())
    seller_id = request.form['sellerId']
    title = request.form['itemName']
    price = request.form['itemPrice']
    description = request.form['itemDescription']
    is_auction = bool(request.form.get('auction'))  # Convertit la case à cocher en booléen
    image_file = request.files['itemImage']

    # Enregistrez l'image dans le dossier statique
    image_path = None
    if image_file:
        image_path = f'images/{image_file.filename}'
        image_file.save(os.path.join('static', image_path))

    # Connexion à la base de données et insertion des données
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO products (seller_id, title, description, price, is_auction, image_url, sold, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (seller_id, title, description, price if not is_auction else None, is_auction, image_path, 0, datetime.now()))
    conn.commit()
    conn.close()

    return redirect(url_for('accueil'))

@app.route("/vitrine")
def vitrine():
     # Connexion à la base de données pour récupérer les articles de l'utilisateur connecté
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Récupérer les articles de l'utilisateur connecté (current_user.get_id() donne l'ID de l'utilisateur)
    cursor.execute("SELECT * FROM products WHERE seller_id = ?", (current_user.get_id(),))
    items = cursor.fetchall()
    conn.close()

    # Passer les articles au modèle
    return render_template("vitrine.html", items=items)

@app.route('/add_to_cart/<int:item_id>', methods=['POST'])
@login_required
def add_to_cart(item_id):
    # Vérifiez si le panier existe déjà dans la session
    if 'cart' not in session:
        session['cart'] = []

    # Ajoutez l'ID de l'article au panier
    session['cart'].append(item_id)
    session.modified = True  # Indique que la session a été modifiée

    flash("L'article a été ajouté au panier!", "success")
    return redirect(url_for('accueil'))

@app.route('/clear_cart', methods=['POST'])
@login_required
def clear_cart():
    # Clear the cart in the session
    if 'cart' in session:
        session.pop('cart')  # Remove the cart key from the session
        session.modified = True  # Mark the session as modified
    
    flash("Votre panier a été vidé avec succès!", "info")
    return {"message": "Cart cleared successfully"}, 200

@app.route('/remove_from_cart/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    if 'cart' in session:
        session['cart'] = [item for item in session['cart'] if item != item_id]
        session.modified = True
        flash("L'article a été supprimé du panier.", "info")
        return render_template("panier.html"), 200
    return {"error": "Panier vide"}, 400


@app.route('/panier')
@login_required
def panier():
    if 'cart' not in session or not session['cart']:
        flash("Votre panier est vide.", "info")
        return redirect(url_for('accueil'))

    # Récupérer les articles du panier depuis la base de données
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE product_id IN ({})".format(
        ','.join('?' * len(session['cart']))
    ), tuple(session['cart']))
    items = cursor.fetchall()
    conn.close()

    return render_template("panier.html", items=items)

@app.route('/enchere/<int:id>')
@login_required
def enchere(id):

     # Connexion à la base de données pour récupérer les articles de l'utilisateur connecté
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Récupérer les articles de l'utilisateur connecté (current_user.get_id() donne l'ID de l'utilisateur)
    cursor.execute("SELECT * FROM products WHERE product_id = ?", (id,))

    items = cursor.fetchall()
    conn.close()

    auction = get_auction(id)
    print(items)

    return render_template('enchere.html', item_id=id, items=items, auction = auction)


if __name__ == "__main__":
    app.run(debug=True)

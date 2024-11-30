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
        cursor.execute("SELECT user_id, password FROM users WHERE username = ?", (username,))
        user_data = cursor.fetchone()
        conn.close()

        if user_data and user_data[1] == password:  # Check password match
            user = User(user_id=user_data[0])
            login_user(user)  # Login the user
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
    return render_template("vitrine.html")

if __name__ == "__main__":
    app.run(debug=True)

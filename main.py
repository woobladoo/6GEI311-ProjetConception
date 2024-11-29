from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = "clesupersecrete"

# Informations d'utilisateur hardcoder
users = {
    "admin": "admin",
    "user": "user",
}

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Vérification des informations d'identification
        if username in users and users[username] == password:
            session['username'] = username
            flash(f"Bienvenue {username}!", "success")
            return redirect(url_for("accueil"))
        else:
            flash("Nom d'utilisateur ou mot de passe incorrect.", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route('/logout', methods=["GET", "POST"])
def logout():
    session.pop('user_id', None)  # Supprime l'identifiant de l'utilisateur de la session
    return redirect(url_for('login'))  # Redirige vers le login

@app.route("/accueil")
def accueil():
    return render_template("accueil.html")

@app.route("/vente")
def vente():
    return render_template("vente.html")

@app.route("/vitrine")
def vitrine():
    return render_template("vitrine.html")

if __name__ == "__main__":
    app.run(debug=True)

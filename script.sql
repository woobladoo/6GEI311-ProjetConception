CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table des produits
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    seller_id INTEGER NOT NULL, -- Vendeur
    title TEXT NOT NULL,
    description TEXT,
    price REAL, -- Null si c'est une enchère
    is_auction BOOLEAN DEFAULT 0, -- 0: Prix fixe, 1: Enchère
    image_url TEXT,
    sold BOOLEAN DEFAULT 0, -- 0: Disponible, 1: Vendu
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (seller_id) REFERENCES users (user_id) ON DELETE CASCADE
);

CREATE TABLE auctions (
    auction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    starting_price REAL NOT NULL,
    current_price REAL, -- Met à jour avec les enchères
    highest_bidder_id INTEGER, -- Acheteur potentiel (utilisateur avec la plus haute enchère)
    end_time DATETIME NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products (product_id) ON DELETE CASCADE,
    FOREIGN KEY (highest_bidder_id) REFERENCES users (user_id) ON DELETE CASCADE
);

CREATE TABLE bids (
    bid_id INTEGER PRIMARY KEY AUTOINCREMENT,
    auction_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL, -- Utilisateur qui fait une enchère
    bid_amount REAL NOT NULL,
    bid_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (auction_id) REFERENCES auctions (auction_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
);


CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    buyer_id INTEGER NOT NULL, -- Acheteur
    product_id INTEGER NOT NULL,
    quantity INTEGER DEFAULT 1, -- Quantité achetée (pour les produits fixes)
    total_price REAL NOT NULL, -- Prix total payé
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (buyer_id) REFERENCES users (user_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products (product_id) ON DELETE CASCADE
);
-- SQLite
-- Insertion de 6 produits différents dans la table 'products'
INSERT INTO products (seller_id, title, description, price, is_auction, image_url, sold)
VALUES 
(1, 'Montre classique', 'Montre en cuir avec cadran analogique', 150.0, 0, 'http://example.com/montre.jpg', 0),
(2, 'Canapé en cuir', 'Canapé 3 places en cuir de haute qualité', 500.0, 0, 'http://example.com/canape.jpg', 0),
(3, 'Vase décoratif', 'Vase en céramique fait main, bleu et blanc', 75.0, 0, 'http://example.com/vase.jpg', 0),
(4, 'Table en bois', 'Table en bois massif, idéale pour la salle à manger', 300.0, 0, 'http://example.com/table.jpg', 0),
(5, 'Lampe LED', 'Lampe LED à intensité réglable', 50.0, 0, 'http://example.com/lampe.jpg', 0),
(6, 'Appareil photo reflex', 'Appareil photo reflex numérique avec objectif 18-55mm', 350.0, 0, 'http://example.com/appareil.jpg', 0);

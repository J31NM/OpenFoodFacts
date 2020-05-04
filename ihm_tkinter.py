# -*- coding: utf-8 -*-

"""
Graphical User interface for the openfoodfacts program.
Site Map :

    __Main Window__

        ==> "Rechercher un produit"

            __Search Window__
                -- Click on a category to display his products
                -- Click on a product to display substitutes
                -- Click on "Ajouter à ma sélection" button to add it on the user
                    favorites list
                -- Click on "@" to open the product information in your browser

        ==> "Mes produits"

            __User favorites Window__
                -- Click on "Supprimer de ma sélection" button to delete the line
                -- Click on "Tout supprimer" button to delete all the lines
                    __Popup window__
                        -- Click "Yes" to confirm delete
                        -- Click "No" to cancel delete

        ==> "Mettre à jour les produits"

            --update products data

"""

import collections
import json
# pylint: disable=W0614
from tkinter import *
from tkinter import tix
from tkinter import ttk
import webbrowser
from PIL import ImageTk, Image
import mysql.connector
from constants import *


# pylint: disable=R0902
from script_purbeurre import OpenFoodFacts


class IHM:
    """Unique Class which constructs the HMI"""
    def __init__(self):

        self.db = OpenFoodFacts()

        self.ui_setup()
        self.favorites = None
        self.tree_favorites = None
        self.search_window = None
        self.tree = None
        self.tree2 = None
        self.tree3 = None
        # Connect to MySQL database
        self.dbconnect = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            passwd=MYSQL_PWD,
            database=MYSQL_DATABASE
        )
        self.my_cursor = self.dbconnect.cursor()

    # Display the main window
    def ui_setup(self):
        """Build the main Window"""
        self.root = root = Tk()
        root.title("Pur Beurre travaille")
        root.geometry("1000x450")
        root['background'] = '#916621'
        root.resizable(False, False)
        banner = Image.open("./images/banner2.jpg")
        render = ImageTk.PhotoImage(banner)
        img = Label(image=render)
        img.image = render
        img.place(x=0, y=0)

        search_substitute_button = Button(root, text="Rechercher un aliment", height=5, width=50,
                                          command=self.find_product)
        search_substitute_button.place(x=100, y=250)

        search_substitute_button = Button(root, text="Mettre à jour les produits", height=3,
                                          width=30, command=self.update_db)
        search_substitute_button.place(x=400, y=370)

        personal_substitute_button = Button(root, text="Consulter mes produits", height=5, width=50,
                                            command=self.show_favorites)
        personal_substitute_button.place(x=550, y=250)

    def add_products(self):
        """Function which add a selected product into the database"""
        current_item = self.tree2.focus()
        current_item = self.tree2.item(current_item)
        current_item = json.loads(current_item['text'])

        self.my_cursor.execute(
            f"INSERT IGNORE INTO favorites(products_ID) VALUES ({current_item[6]})"
        )
        self.dbconnect.commit()

    def add_favorites(self):
        """Function which add a selected favorite into the database"""
        current_item = self.tree3.focus()
        current_item = self.tree3.item(current_item)
        current_item = json.loads(current_item['text'])

        self.my_cursor.execute(
            f"INSERT IGNORE INTO favorites(products_ID) VALUES ({current_item[1][4]})"
        )
        self.dbconnect.commit()

    def delete_favorites(self):
        """Function which delete a selected favorite from the database"""
        current_child = self.tree_favorites.focus()
        current_item = self.tree_favorites.item(current_child)
        current_item = json.loads(current_item['text'])

        self.my_cursor.execute(
            f"DELETE FROM favorites WHERE products_ID = {current_item[1][0]}"
        )
        self.tree_favorites.delete(current_child)
        self.dbconnect.commit()

    def delete_all(self):
        """Function which delete all the favorites from the database"""
        self.my_cursor.execute(
            f"DELETE FROM favorites"
        )
        self.dbconnect.commit()

    def popup(self):
        """Ask confirmation to delete all lines"""
        def callback():
            self.delete_all()
            infos.destroy()
            self.tree_favorites.delete(*self.tree_favorites.get_children())

        infos = Toplevel(self.favorites)  # Popup -> Toplevel()
        infos.title('Validation')
        infos.geometry("350x100")
        infos.resizable(False, False)
        yes_button = Button(infos, text='Oui', height=2, width=10, command=callback)
        yes_button.place(x=65, y=50)
        no_button = Button(infos, text='Non', height=2, width=10, command=infos.destroy)
        no_button.place(x=175, y=50)
        lbl_info = Label(infos, text="Êtes vous sûr de vouloir supprimer tous vos produits ?",
                         font=("Arial", 10))
        lbl_info.place(x=5, y=5)
        infos.grab_set()  # Interaction avec fenetre jeu impossible


    # Display customers favorites in a new window
    def show_favorites(self):
        """Build the Favorites Window"""
        self.favorites = Toplevel(self.root)
        self.favorites.title('Pur Beurre travaille')
        self.favorites.geometry("1100x500")
        self.favorites.resizable(False, False)
        self.favorites['background'] = '#4687b0'
        self.favorites.grab_set()
        self.tree_favorites = tree = ttk.Treeview(self.favorites, columns=(1, 2, 3, 4), height=5,
                                                  show="headings")
        tree.place(x=10, y=60, width=1075, height=300)
        tree.heading(1, text="Mes Produits")
        tree.heading(2, text="Marques")
        tree.heading(3, text="Magasins")
        tree.heading(4, text="Nutriscores")
        tree.column(1, width=250)
        tree.column(2, width=100)
        tree.column(3, width=100)
        tree.column(4, width=1, anchor='center')

        self.my_cursor.execute(
            f"SELECT products.ID, products.productName, products.brand, products.store, "
            f"products.nutritionScore "
            f"FROM products"
            f" INNER JOIN favorites"
            f"  ON products.ID = favorites.products_ID"
        )

        result_favorites = self.my_cursor.fetchall()
        for favorite in enumerate(result_favorites):
            tree.insert('', END, text=json.dumps(favorite), values=favorite[1][1:])

        refresh_favorites_button = Button(self.favorites, text="Supprimer de ma sélection",
                                          height=5, width=20, command=self.delete_favorites)
        refresh_favorites_button.place(x=730, y=380)
        delete_favorites_button = Button(self.favorites, text="Tout supprimer", height=5, width=20,
                                         command=self.popup)
        delete_favorites_button.place(x=930, y=380)

        lbl_title1 = Label(self.favorites, text="Mes Produits",
                           font=("Arial", 21), bg="black", fg="white")
        lbl_title1.place(x=0, y=0, width=1100)


    def open_category_url(self):
        """Open the url of the selected category"""
        current_item = self.tree.focus()
        current_item = self.tree.item(current_item)
        current_item = json.loads(current_item['text'])
        url = current_item.get('url')
        webbrowser.open_new(url)

    def open_product_url(self):
        """Open the url of the selected product"""
        current_item = self.tree2.focus()
        current_item = self.tree2.item(current_item)
        current_item = json.loads(current_item['text'])
        url = current_item[5]
        webbrowser.open_new(url)

    def open_substitute_url(self):
        """Open the url of the selected substitute"""
        current_item = self.tree3.focus()
        current_item = self.tree3.item(current_item)
        current_item = json.loads(current_item['text'])
        url = current_item[1][5]
        webbrowser.open_new(url)

    def display_substitutes(self, event):
        """Display substitutes into the board"""
        current_item = self.tree2.focus()
        current_item = self.tree2.item(current_item)
        current_item = json.loads(current_item['text'])

        candidates = 'a,b,c,d,e'.split(current_item[4])[0][:-1]
        candidates = ', '.join([f'"{c}"' for c in candidates.split(',') if c])
        # candidates = ', '.join([f'"{c}"' for c in candidates.split(',') + [current_item[4]] if c])

        self.tree3.delete(*self.tree3.get_children())
        if not candidates.strip():
            return

        self.my_cursor.execute(
            f"SELECT productName, brand, store, nutritionScore, ID, url "
            f"FROM products WHERE nutritionScore IN ({candidates}) AND idcategory={current_item[0]}"
        )

        result_products = self.my_cursor.fetchall()
        for product in enumerate(result_products):
            self.tree3.insert('', END, text=json.dumps(product), values=product[1])

    def display_products(self, event):
        """Display products into the board"""
        current_item = self.tree.focus()
        current_item = self.tree.item(current_item)
        current_item = json.loads(current_item['text'])

        self.my_cursor.execute(
            f"SELECT idcategory, productName, brand, store, nutritionScore, url, ID "
            f"FROM products WHERE idcategory={current_item['idCategory']}"
        )
        self.tree2.delete(*self.tree2.get_children())
        result_products = self.my_cursor.fetchall()
        for product in enumerate(result_products):
            self.tree2.insert('', END, text=json.dumps(product[1]), values=product[1][1:])

    # pylint: disable=R0914
    # pylint: disable=R0915
    def find_product(self):
        """Build the Search Window"""
        # window set
        self.search_window = Toplevel(self.root)
        # self.search_window = tix.Tk()
        self.search_window.title('Pur Beurre travaille')
        self.search_window.geometry("1300x800")
        self.search_window['background'] = '#6b8a45'
        self.search_window.resizable(False, False)
        # bal = tix.Balloon(self.search_window)
        self.search_window.grab_set()

        lbl_title1 = Label(self.search_window, text="Sélectionnez la catégorie puis le produit "
                                                    "qui vous intéresse",
                           font=("Arial", 21), bg="black", fg="white")
        lbl_title1.place(x=0, y=0, width=1300)

        lbl_title2 = Label(self.search_window, text="Ces produits possédants un meilleur "
                                                    "nutriscore peuvent vous intéresser",
                           font=("Arial", 18), bg="black", fg="white")
        lbl_title2.place(x=10, y=520, width=1100)

        # display category
        self.tree = tree = ttk.Treeview(self.search_window, columns=("category",), height=5,
                                        show="headings")
        tree.place(x=10, y=50, width=300, height=200)
        tree.bind("<<TreeviewSelect>>", self.display_products)
        tree.column("category", width=300)
        tree.heading("category", text="Catégories")

        # display products
        self.tree2 = tree2 = ttk.Treeview(self.search_window, columns=(1, 2, 3, 4), height=5,
                                          show="headings")
        tree2.place(x=10, y=300, width=1100, height=200)
        tree2.bind("<<TreeviewSelect>>", self.display_substitutes)
        tree2.heading(1, text="Produits")
        tree2.heading(2, text="Marques")
        tree2.heading(3, text="Magasins")
        tree2.heading(4, text="Nutriscores")
        tree2.column(1, width=250)
        tree2.column(2, width=100)
        tree2.column(3, width=100)
        tree2.column(4, width=1, anchor='center')

        # display substitutes
        self.tree3 = tree3 = ttk.Treeview(self.search_window, columns=(1, 2, 3, 4), height=5,
                                          show="headings")
        tree3.place(x=10, y=550, width=1100, height=200)
        tree3.heading(1, text="Produits")
        tree3.heading(2, text="Marques")
        tree3.heading(3, text="Magasins")
        tree3.heading(4, text="Nutriscores")
        tree3.column(1, width=250)
        tree3.column(2, width=100)
        tree3.column(3, width=100)
        tree3.column(4, width=1, anchor='center')

        # button to open category in the browser
        browse_url_button1 = tix.Button(self.search_window, text="@",
                                        height=3, width=5, command=self.open_category_url)
        browse_url_button1.place(x=311, y=51)
        # bal.bind_widget(browse_url_button1, msg='Ouvrir la catégorie dans le navigateur')

        # button to open product in the browser
        browse_url_button2 = tix.Button(self.search_window, text="@", height=3,
                                        width=5, command=self.open_product_url)
        browse_url_button2.place(x=1110, y=301)
        # bal.bind_widget(browse_url_button2, msg='Ouvrir le produit dans le navigateur')

        # button to open substitute in the browser
        browse_url_button3 = tix.Button(self.search_window, text="@", height=3,
                                        width=5, command=self.open_substitute_url)
        browse_url_button3.place(x=1110, y=551)
        # bal.bind_widget(browse_url_button3, msg='Ouvrir le produit dans le navigateur')

        # button to add product into favorites
        add_product_button = tix.Button(self.search_window,
                                        text="Ajouter le produit à ma sélection",
                                        height=4, width=25, command=self.add_products)
        add_product_button.place(x=1110, y=430)

        # button to add substitute into favorites
        add_favorite_button = tix.Button(self.search_window,
                                         text="Ajouter le substitut à ma sélection",
                                         height=4, width=25, command=self.add_favorites)
        add_favorite_button.place(x=1110, y=680)

        # fill the categories board
        columns = ('idCategory', 'categoryName', 'url',)
        self.my_cursor.execute(f"SELECT {', '.join(columns)} FROM categories")
        CategoryRow = collections.namedtuple('CategoryRow', columns)
        result_categories = self.my_cursor.fetchall()
        for category in enumerate(result_categories):
            category = CategoryRow(*category[1])
            tree.insert(
                '', END, text=json.dumps(category._asdict()), values=(category.categoryName,)
            )

    def run(self):
        """Mainloop"""
        self.root.mainloop()

    def update_db(self):
        """run openfoodfacts from script_purbeurre.py"""
        self.db.run()


if __name__ == '__main__':
    IHM = IHM()
    IHM.run()

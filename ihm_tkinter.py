from tkinter import *
from tkinter import ttk
import webbrowser
from PIL import ImageTk, Image
from constants import *
import mysql.connector
# from script_purbeurre import *


class IHM:

    def __init__(self):
        self.ui_setup()

    # Display the main window
    def ui_setup(self):
        self.root = root = Tk()
        root.title("Pur Beurre travaille")
        root.geometry("1000x400")
        root.resizable(False, False)
        banner = Image.open("./images/banner2.jpg")
        render = ImageTk.PhotoImage(banner)
        img = Label(image=render)
        img.image = render
        img.grid(row=0, columnspan=2)

        search_substitute_button = Button(root, text="Rechercher un aliment", height=5, width=50, command=self.find_product)
        search_substitute_button.grid(row=3, column=0, padx=10, pady=50)

        personal_substitute_button = Button(root, text="Mes produits", height=5, width=50, command=self.show_favorites)
        personal_substitute_button.grid(row=3, column=1, padx=10, pady=50)

    def add_favorites(self):
        pass

    # Display customers favorites in a new window
    def show_favorites(self):
        self.favorites = Tk()
        self.favorites.title('Pur Beurre travaille')
        self.favorites.geometry("800x500")
        self.favorites.resizable(False, False)

        self.tree = tree = ttk.Treeview(self.favorites, columns=(1, 2), height=5, show="headings")
        tree.place(x=10, y=50, width=780, height=200)
        tree.heading(1, text="Mes Produits")
        tree.heading(2, text="Nutriscore")
        tree.column(1, width=600)
        tree.column(2, width=50)
        clicked = StringVar(self.favorites)
        clicked.set("Trier par :")
        drop = OptionMenu(self.favorites, clicked, "Ordre alphabetique", "Nutriscores croissants", "Nutriscores décroissants")
        drop.place(x=10, y=10)

        products_details = Text(self.favorites, width=50, height=10)
        products_details.place(x=10, y=270)

        refresh_favorites_button = Button(self.favorites, text="Rafraîchir ma sélection", height=5, width=20)
        refresh_favorites_button.place(x=470, y=260)
        delete_favorites_button = Button(self.favorites, text="Supprimer de ma sélection", height=5, width=20)
        delete_favorites_button.place(x=640, y=260)

    def tree_action_select(self, event):
        open_products = self.tree.item(self.tree.selection())
        # cate_id =
        # url = data['values'][2]
        # print(data)
        # print(f'Opening URI => {url}')
        # webbrowser.open_new(url)

    def find_product(self):
        self.search_window = Tk()
        self.search_window.title('Pur Beurre travaille')
        self.search_window.geometry("1050x600")
        self.search_window.resizable(False, False)

        self.tree = tree = ttk.Treeview(self.search_window, columns=(1, 2), height=5, show="headings")
        tree.place(x=10, y=10, width=500, height=200)
        tree.bind("<<TreeviewSelect>>", self.tree_action_select)
        # Add headings
        tree.heading(1, text="ID")
        tree.heading(2, text="Categorie")
        # tree.heading(3, text="Lien url")
        # Define column width
        tree.column(1, width=2)
        tree.column(2, width=300)
        # tree.column(3, width=500)

        self.tree2 = tree2 = ttk.Treeview(self.search_window, columns=(1, 2), height=5, show="headings")
        tree2.place(x=520, y=10, width=500, height=200)
        tree2.heading(1, text="ID")
        tree2.heading(2, text="Products")
        tree2.column(1, width=2)
        tree2.column(2, width=300)

        self.tree3 = tree3 = ttk.Treeview(self.search_window, columns=(1, 2, 3), height=5, show="headings")
        tree3.place(x=10, y=220, width=1010, height=200)
        tree3.heading(1, text="ID")
        tree3.heading(2, text="Product")
        tree3.heading(3, text="Nutriscore")
        tree3.column(1, width=2)
        tree3.column(2, width=800)
        tree3.column(3, width=2)

        browse_url_button = Button(self.search_window, text="Ouvrir dans le navigateur", height=5, width=50, command=self.tree_action_select)
        browse_url_button.place(x=100, y=450)

        add_favorites_button = Button(self.search_window, text="Ajouter à ma sélection", height=5, width=50, command=self.add_favorites)
        add_favorites_button.place(x=600, y=450)


        # Connect to MySQL database
        dbconnect = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            passwd=MYSQL_PWD,
            database=MYSQL_DATABASE
        )

        my_cursor = dbconnect.cursor()

        my_cursor.execute("SELECT idCategory, categoryName, url FROM categories")
        result_categories = my_cursor.fetchall()
        # my_cursor.close()
        test = list()
        for category in enumerate(result_categories):
            # test.append("{}, {}, {}".format(result[1][0], result[1][1], result[1][2]))
            tree.insert('', END, values=category[1])
            # tree.bind("<Double-1>", self.OnDoubleClick)

            # lookup_label.bind("<Button-

        my_cursor.execute("SELECT idProduct, productName FROM products")
        result_products = my_cursor.fetchall()
        for product in enumerate(result_products):
            tree2.insert('', END, values=product[1])


    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
    ihm = IHM()
    ihm.run()

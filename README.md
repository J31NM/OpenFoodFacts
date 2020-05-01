# OpenFoodFacts
OpenClassrooms, Python applications development : Project 5 .
```
https://github.com/J31NM/OpenFoodFacts
```

## Presentation
Small program which permit the user to look for healthier substitutes for the products he like.
This application get his data from the OpenFoodFacts API.

## Instructions

### Prerequisites
```
Python 3 : https://www.python.org/downloads/
MySQL Workbench : https://www.mysql.com/fr/products/workbench/
MySQL server account : https://dev.mysql.com/downloads/mysql/
```

### Setup
```
Install those modules with Pip:
_ virtualenv
_ requests
_ Tk
_ Pillow
_ install mysql-connector-python

connect to MySQL server and fill in the "constants.py" document with your credentials 

Launch ihm_tkinter.py

```

### How to use the program
```
The first launch will automatically download data from the OpenFoodFacts API and stock them into 
the database "openfoodfacts_db.
From main menu you have 2 choices:
    - 1 : Search a new product on clicking on the button "Rechercher un aliment".
            This action open a second window (Search product window).
            The "Search product" window automatically propose 50 categories.
                - 1a : Selecting a category display 10 products.
                - 1b : When Selecting a product display healthier substitutes 
                        in this category if they exist.
                - 1c : You can add a products or a substitute to your favorites with the button
                        "Ajouter"
                - 1d : You can open a category, product or substitute url in the webbrower 
                           when clicking on the "@" assiociate button.
    - 2 : Consult your favorites products with the "Consulter mes produits" button.
            This action open a third window (favorites window).
            The "favorites" window display all the products saved.
                - 2a : You can delete any line with the button "Supprimer de ma sélection"
                - 2b : You can delete all lines with the button "Tout Supprimer"
                    This action will open a popup window to ask a confirmation.
                        - Click "yes" to confirm order
                        - Click "no" to cancel order
```

## Files Informations

### script_purbeurre.py
This file is used by the main.py to create the database from the SQL script create.sql
```
- strip() : Cancel some database insertions format errors with SQL
Class Record : Format the upcomming data request with the OpenFoodFacts API
- json_url() : Method returning the url needed
- to_sql() : Method returning SQL representation of the record
- to_dict() : Return a dictionary for the needed data
- to_json() : Return data in json format
- build_api_url() : Use to requests as many pages needed for each category.
Class Category : Specify the categories data to get from the API
- to_dict() : Return products tags from categories
- to_sql() : Insert categories name and url into database
Class Product : Specify the products data to get from the API
- to_dict() : Return additional data for the products
- to_sql() : Insert data into the database
Class OpenFoodFacts : Fetch the data into the database
- requests_json() : Get a json format for the data categories
- last_inserted_id() : Return the last inserted id. Assign a category id to each product.
    Allows to link the products to his category.
- fetch_data() : Get categories from API's openfoodfacts
- products_by_category() : Get some products from each category
Class DataBaseMySql : Create the database with SQL script
- delete_sql() : Clear the tables before to fill them with update data
- create_sql() : Create tables
- execute_sql() : Commit the update
- create_db() : Run the SQl script

```

### create.sql
This is the SQL script used by Create.py to create the database.

### ihm_tkinter.py
This file build the user interface with tkinter.
```
class IHM
- ui_setup() : Build the main Window
- add_products() : Function which add a selected product into the database
- add_favorites() : Function which add a selected favorite into the database
- delete_favorites() : Function which delete a selected favorite from the database
- delete_all() : Function which delete all the favorites from the database
- popup() : Ask confirmation to delete all lines
- show_favorites() : Build the Favorites Window
- open_category_url() : Open the url of the selected category
- open_product_url() : Open the url of the selected product
- open_substitute_url() : Open the url of the selected substitute
- display_substitutes() : Display substitutes into the board
- display_products() : Display products into the board
- find_product() : Build the Search Window
- run() : run the main loop
```

### main.py
This file launch the program

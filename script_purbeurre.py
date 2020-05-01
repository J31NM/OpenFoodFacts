# -*- coding: utf-8 -*-

"""
USE OPENFOODFACTS API

Small program which allows to find substitutes for food products on the
OpenFoodFacts API.
The user will be able to search products by looking for a food category among 50. Each category
propose 10 products.
If the user select a product, the program suggests other products from the same category with
better Nutritioscore.
The user can manage a "favorites" list of the products he likes.

This main script requests the Openfoodfacts API in order to collect data and fill the database :
openfoodfacts_db.


Script Python
Files : script_purbeurre.py, ihm_tkinter.py, main.py, create.sql, constants.py

"""

import abc
import json
import requests
import mysql.connector
from constants import *


def strip(text):
    """Cancel some database insertions format errors with SQL"""
    for char, repl in (('\n', ''), ('\r', ''), ('"', "'")):
        text = text.replace(char, repl)
    return text


class Record(abc.ABC):
    """Define the data format which will be collected in the daughters-class :
        Category and Product."""
    @property
    def json_url(self):
        """Method returning the url needed"""
        return f'{self.url}?json=1'

    @property
    @abc.abstractmethod
    def to_sql(self):
        """
        Method returning SQL representation of the record

        :rtype: str
        :return: SQL representation
        """

    @property
    def to_dict(self):
        """return a dictionary for the needed data"""
        return dict(pk=self.pk, name=self.name, url=self.url)

    @property
    def to_json(self):
        """return data in json format"""
        return json.dumps(self.to_dict, indent=4)

    def build_api_url(self, page=1):
        """Use to requests as many pages needed for each category."""
        return f'{self.url}/{page}?json=1'

    def __init__(self, name, url, pk=None):
        # pylint: disable=C0103
        self.pk = pk
        self.name = strip(name)
        self.url = strip(url)

    def __str__(self):
        return self.to_json


class Category(Record):
    """Define the data to fill the "categories" table in the database "openfoodfacts_db" """

    @property
    def to_dict(self):
        data = super().to_dict
        data['products'] = self.products
        return data

    @property
    def to_sql(self):
        return f'INSERT IGNORE INTO categories(categoryName, url) ' \
            f'VALUES("{self.name}", "{self.url}")'

    def __init__(self, name, url, pk=None):
        super().__init__(name, url, pk=pk)
        self.products = []


class Product(Record):
    """Define the data to fill in the "products" table in the database "openfoodfacts_db" """

    @property
    def to_dict(self):
        data = super().to_dict
        data['store'] = self.store
        data['brand'] = self.brand
        data['quantity'] = self.quantity
        data['nutrition_score'] = self.nutrition_score
        return data

    @property
    def to_sql(self):
        return (
            f'INSERT INTO products(idcategory, productName, productQuantity, '
            f'nutritionScore, url, brand, store) '
            f'VALUES('
            f'{self.category_id}, "{self.name}", "{self.quantity}", '
            f'"{self.nutrition_score}", "{self.url}", '
            f'"{self.brand}", "{self.store}")')

    # pylint: disable=R0913
    def __init__(self, category_id, name, url, quantity, nutrition_score, brand, store, pk=None):
        super().__init__(name, url, pk=pk)

        self.quantity = strip(quantity)
        self.category_id = category_id
        self.nutrition_score = strip(nutrition_score)
        self.brand = strip(brand)
        self.store = strip(store)


class OpenFoodFacts:
    """Method requesting the OpenFoodFacts API url to fetch the data."""

    @classmethod
    def requests_json(cls, url):
        """get a json format for the data categories."""
        resp_category = requests.get(url)
        return resp_category.json()

    def last_inserted_id(self):
        """return the last inserted id. Assign a category id to each product.
            Allows to link the products to his category."""
        return self.data_base.execute_sql('SELECT LAST_INSERT_ID();')

    def __init__(self):
        self.data_base = DataBaseMySql()
        self.data_base.create_db()
        self.fetch_data()

    def fetch_data(self):
        """
        get categories from API's openfoodfacts
        """
        # the category "Boissons alcoolisées" hasn't Nutritionscore. We need to exclude it
        #   otherwise the request will break.
        excluded = [
            "Boissons alcoolisées"
        ]
        categories = []
        data_category_json = self.requests_json('https://fr.openfoodfacts.org/categories&json=1')
        i = 0
        for category_info in data_category_json.get('tags', {}):
            if i == 50:
                break

            name = category_info.get('name')
            url = category_info.get('url')
            if not all([url, name]) or name in excluded:
                continue

            category = Category(name=name, url=url)
            # print(category.to_sql)
            result = self.data_base.insert_sql(category.to_sql)
            category.pk = result

            print('Processed category =>', category.name)
            self.products_by_category(category)
            categories.append(category.to_dict)
            i += 1
        # print(json.dumps(categories, indent=

    def products_iterator(self, category):
        """

        Args:
            category (Category):

        Returns:

        """
        page = 1
        while page < 25:
            data = self.requests_json(category.build_api_url(page))
            for product in data.get('products'):
                yield product
            page += 1

    def products_by_category(self, category):
        """
        Get some products from each category

        Args:
            category (Category): The category instance
        """
        def is_french():
            nonlocal country
            country = str(country).lower()
            for pattern in ('france', 'belgium'):
                if pattern in country:
                    return True
            return False

        products = []
        i = 0

        for elem in self.products_iterator(category):
            if i == 10:
                break

            if not elem:
                continue

            name = elem.get('generic_name', elem.get('product_name', elem.get('product_name_fr')))
            quantity = elem.get('quantity', '')
            url = elem.get('url')
            brand = elem.get('brands_tags') or ''
            store = elem.get('stores')
            nutrition_score = elem.get('nutrition_grades')
            country = elem.get('countries_tags')
            if not all([name, url, store, nutrition_score, is_french()]):
                continue

            product = Product(
                category_id=category.pk, name=name, quantity=quantity, url=url,
                brand=', '.join(brand), store=store, nutrition_score=nutrition_score
            )
            # print(product.to_sql)
            result = self.data_base.insert_sql(product.to_sql)
            if result == -1:
                continue

            product.pk = result
            # self.products_by_category(product)
            products.append(product)
            # products.append(elem)
            # print('Processed product =>', product.name)
            i += 1

        print(f'[INSERT] {i} ({len(products)}) products for category {category.name}')
        print([product.name for product in products])


class DataBaseMySql:
    """Create the SQL database"""

    @property
    def delete_sql(self):
        """clear the tables before to fill them with update data"""
        return (
            "SET FOREIGN_KEY_CHECKS = 0;",
            "TRUNCATE TABLE openfoodfacts_db.categories;",
            "TRUNCATE TABLE openfoodfacts_db.products;",
            "SET FOREIGN_KEY_CHECKS = 1;",
            "SET FOREIGN_KEY_CHECKS = 0;",
            "DROP TABLE IF EXISTS `openfoodfacts_db.products`;",
            "DROP TABLE IF EXISTS `openfoodfacts_db.categories`;",
            "SET FOREIGN_KEY_CHECKS = 1;"
        )

    @property
    def create_sql(self):
        f = open("create.sql", "r")
        print("[INFO] EXECUTION DU SCRIPT SQL")
        return f
        # return """
        #         CREATE TABLE IF NOT EXISTS categories (
        #                 `idCategory` int(11) DEFAULT NOT NULL AUTO_INCREMENT,
        #                 `categoryName` varchar(100) NOT NULL,
        #                 `url` varchar(255) NOT NULL UNIQUE,
        #                 PRIMARY KEY (idCategory)
        #                 );
        #
        #         CREATE TABLE IF NOT EXISTS products (
        #                 `idProduct` int(11) NOT NULL AUTO_INCREMENT,
        #                 `productName` varchar(100) NOT NULL,
        #                 `productQuantity` varchar(100),
        #                 `nutritionScore` varchar(5) NOT NULL,
        #                 `url` varchar(255) NOT NULL UNIQUE
        #                 `brand` varchar(50) NOT NULL,
        #                 `store` varchar(100) NOT NULL,
        #                 PRIMARY KEY (idProductName)
        #                 );
        #
        #
        #         CREATE TABLE IF NOT EXISTS `substitutes` (
        #                 `idProductName` int(11) NOT NULL AUTO_INCREMENT,
        #                 `productName` varchar(50) NOT NULL,
        #                 `productQuantity` varchar(255),
        #                 `nutritionScore` varchar(5) NOT NULL,
        #                 `url` varchar(255) NOT NULL,
        #                 `brand` varchar(100) NOT NULL,
        #                 `store` varchar(100) NOT NULL,
        #                 PRIMARY KEY (idProductName)
        #         )
        #                 """

    def __init__(self):
        self.data_base = mysql.connector.connect(
            user=MYSQL_USER, password=MYSQL_PWD,
            host=MYSQL_HOST, database=MYSQL_DATABASE,
        )

    def __del__(self):
        try:
            self.data_base.close()
        # pylint: disable=W0703
        except Exception as error:
            print('DBError while closing', error)

    def execute_sql(self, sql, **options):
        """Commit the update"""
        result = -1
        self.cursor = self.data_base.cursor()
        try:
            self.cursor.execute(sql, **options)
            self.data_base.commit()
            result = self.cursor.getlastrowid()
        # pylint: disable=W0703
        except Exception as error:
            print('DB Error', error)
        finally:
            print('INSERTED ID', result)
            self.cursor.close()

        return result

    insert_sql = execute_sql

    def create_db(self):
        """Run the SQL script"""
        # DB DELETE
        for statement in self.delete_sql:
            self.insert_sql(statement)
        # DB CREATE
        self.insert_sql(self.create_sql, multi=True)


# pylint: disable=C0103
create_dataBase = OpenFoodFacts()

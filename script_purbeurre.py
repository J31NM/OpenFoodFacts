# -*- coding: utf-8 -*-

import abc
import json
import requests
import mysql.connector
from constants import *


class Record(abc.ABC):

    @property
    def json_url(self):
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
        return dict(pk=self.pk, name=self.name, url=self.url)

    @property
    def to_json(self):
        return json.dumps(self.to_dict, indent=4)

    def build_api_url(self, page=1):
        return f'{self.url}/{page}?json=1'

    def __init__(self, name, url, pk=None):
        self.pk = pk
        self.name = name
        self.url = url

    def __str__(self):
        return self.to_json


class Category(Record):

    @property
    def to_dict(self):
        data = super().to_dict
        data['products'] = self.products
        return data

    @property
    def to_sql(self):
        return f'INSERT IGNORE INTO categories(categoryName, url) VALUES("{self.name}", "{self.url}")'

    def __init__(self, name, url, pk=None):
        super().__init__(name, url, pk=pk)
        self.products = []


class Product(Record):

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
            f'INSERT IGNORE INTO products(productName, productQuantity, nutritionScore, url, brand, store) '
            f'VALUES('
            f'"{self.name}", "{self.quantity}", "{self.nutrition_score}", "{self.url}", '
            f'"{self.brand}", "{self.store}")')

    def __init__(self, name, url, quantity, nutrition_score, brand, store, pk=None):
        super().__init__(name, url, pk=pk)

        self.quantity = quantity
        self.nutrition_score = nutrition_score
        self.brand = brand
        self.store = store


class OpenFoodFacts:

    @classmethod
    def requests_json(cls, url):
        resp_category = requests.get(url)
        return resp_category.json()

    @property
    def last_inserted_id(self):
        pass
        # return f'SELECT LAST_INSERT_ID FROM categories;'

    def __init__(self):
        self.data_base = DataBaseMySql()
        self.data_base.create_db()
        self.fetch_data()

    def fetch_data(self):
        """
        get category from API's openfoodfacts
        """
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
            self.data_base.insert_sql(category.to_sql)
            category.pk = self.last_inserted_id

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
        while 1:
            data = self.requests_json(category.build_api_url(page))
            for product in data.get('products'):
                yield product
            page += 1

    def products_by_category(self, category):
        """
        get some products from each category

        Args:
            category (Category): The category instance
        """
        products = []
        i = 0

        for elem in self.products_iterator(category):
            if i == 3:
                break

            if not elem:
                continue

            name = elem.get('generic_name')
            quantity = elem.get('quantity', '')
            url = elem.get('url')
            brand = elem.get('brands_tags')
            store = elem.get('stores')
            nutrition_score = elem.get('nutrition_grades')
            country = elem.get('purchase_places')
            if not all([name, url, brand, store, nutrition_score, "france" in str(country).lower()]):
                continue

            product = Product(name=name, quantity=quantity, url=url, brand=brand, store=store, nutrition_score=nutrition_score)
            # print(product.to_sql)
            product.pk = self.data_base.insert_sql(product.to_sql)
            # self.products_by_category(product)
            products.append(elem)
            # products.append(elem)
            print('Processed product =>', product.name)
            i += 1


class DataBaseMySql:

    @property
    def delete_sql(self):
        return (
            "TRUNCATE TABLE openfoodfacts_db.categories;",
            "TRUNCATE TABLE openfoodfacts_db.products;",
            "SET FOREIGN_KEY_CHECKS = 0 ;",
            "DROP TABLE IF EXISTS `openfoodfacts_db.products`;",
            "DROP TABLE IF EXISTS `openfoodfacts_db.categories`;",
            "SET FOREIGN_KEY_CHECKS = 1 ;",
        )

        # pass
        # return (
        #     # "TRUNCATE TABLE off.Substitutes;",
        #     "SET FOREIGN_KEY_CHECKS=0;",
        #     "DROP TABLE IF EXISTS `products`;",
        #     "DROP TABLE IF EXISTS `categories`;",
        #     "SET FOREIGN_KEY_CHECKS=1;",
        # )

    @property
    def create_sql(self):
        return """
                CREATE TABLE IF NOT EXISTS categories (
                        `idCategory` int(11) DEFAULT NOT NULL AUTO_INCREMENT,
                        `categoryName` varchar(100) NOT NULL,
                        `url` varchar(255) NOT NULL UNIQUE, 
                        PRIMARY KEY (idCategory)
                        );
                        
                CREATE TABLE IF NOT EXISTS products (
                        `idProduct` int(11) NOT NULL AUTO_INCREMENT,
                        `productName` varchar(100) NOT NULL,
                        `productQuantity` varchar(100),
                        `nutritionScore` varchar(5) NOT NULL,
                        `url` varchar(255) NOT NULL UNIQUE
                        `brand` varchar(50) NOT NULL,
                        `store` varchar(100) NOT NULL,                       
                        PRIMARY KEY (idProductName)
                        );
                        
                        
                CREATE TABLE IF NOT EXISTS `substitutes` (
                        `idProductName` int(11) NOT NULL AUTO_INCREMENT,
                        `productName` varchar(50) NOT NULL,
                        `productQuantity` varchar(255),
                        `nutritionScore` varchar(5) NOT NULL,
                        `url` varchar(255) NOT NULL,
                        `brand` varchar(100) NOT NULL,
                        `store` varchar(100) NOT NULL,                       
                        PRIMARY KEY (idProductName)
                )
                        """

    def __init__(self):
        self.data_base = mysql.connector.connect(
            user=MYSQL_USER, password=MYSQL_PWD,
            host=MYSQL_HOST, database=MYSQL_DATABASE,
            # cursorclass=pymysql.cursors.DictCursor
        )

    def __del__(self):
        try:
            self.data_base.close()
        except Exception as error:
            print('DBError while closing', error)

    def insert_sql(self, sql, **options):
        self.cursor = self.data_base.cursor()
        try:
            self.cursor.execute(sql, **options)
            self.data_base.commit()
        except Exception as error:
            print('DB Error', error)
        finally:
            self.cursor.close()

    def create_db(self):
        # DB DELETE
        for statement in self.delete_sql:
            self.insert_sql(statement)
        # DB CREATE
        self.insert_sql(self.create_sql, multi=True)


create_dataBase = OpenFoodFacts()

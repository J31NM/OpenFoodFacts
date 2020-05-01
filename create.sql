-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema openfoodfacts_db
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `openfoodfacts_db` ;

-- -----------------------------------------------------
-- Schema openfoodfacts_db
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `openfoodfacts_db` DEFAULT CHARACTER SET utf8 ;
USE `openfoodfacts_db` ;

-- -----------------------------------------------------
-- Table `openfoodfacts_db`.`categories`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `openfoodfacts_db`.`categories` ;

CREATE TABLE IF NOT EXISTS `openfoodfacts_db`.`categories` (
  `idcategory` INT NOT NULL AUTO_INCREMENT,
  `categoryName` VARCHAR(100) NOT NULL,
  `url` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`idcategory`),
  UNIQUE INDEX `url_UNIQUE` (`url` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `openfoodfacts_db`.`products`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `openfoodfacts_db`.`products` ;

CREATE TABLE IF NOT EXISTS `openfoodfacts_db`.`products` (
  `productQuantity` VARCHAR(45) NULL,
  `productName` VARCHAR(100) NOT NULL,
  `nutritionScore` VARCHAR(5) NOT NULL,
  `url` VARCHAR(255) NOT NULL,
  `brand` VARCHAR(100) NOT NULL,
  `store` VARCHAR(100) NOT NULL,
  `ID` INT NOT NULL AUTO_INCREMENT,
  `idcategory` INT NOT NULL,
  PRIMARY KEY (`ID`),
  INDEX `fk_products_categories_idx` (`idcategory` ASC) VISIBLE,
  UNIQUE INDEX `url_UNIQUE` (`url` ASC) VISIBLE,
  CONSTRAINT `fk_products_categories`
    FOREIGN KEY (`idcategory`)
    REFERENCES `openfoodfacts_db`.`categories` (`idcategory`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `openfoodfacts_db`.`favorites`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `openfoodfacts_db`.`favorites` ;

CREATE TABLE IF NOT EXISTS `openfoodfacts_db`.`favorites` (
  `idfavorites` INT NOT NULL AUTO_INCREMENT,
  `products_ID` INT NOT NULL,
  PRIMARY KEY (`idfavorites`),
  INDEX `fk_favorites_products1_idx` (`products_ID` ASC) VISIBLE,
  UNIQUE INDEX `products_ID_UNIQUE` (`products_ID` ASC) VISIBLE,
  CONSTRAINT `fk_favorites_products1`
    FOREIGN KEY (`products_ID`)
    REFERENCES `openfoodfacts_db`.`products` (`ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

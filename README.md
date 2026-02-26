# 8INF349 – Projet de session

## Description

Ce projet consiste à développer une application Web en Python utilisant le framework Flask.
L’application permet de gérer des commandes de produits via une API REST et d’effectuer des paiements à l’aide d’un service distant.

---
## Membres de l’équipe
* Martin
* Dylane
* Nathan
---

## Installation
### 1. Cloner le projet
```bash
git clone https://github.com/BDylane/projet_session.git
cd projet_session
```
### 2. Créer un environnement virtuel Python
*Prérequis : Python 3.6+*
```bash
python3 -m venv venv
```
### 3. Activer l’environnement virtuel
Linux / Mac :
```bash
source venv/bin/activate
```
Windows :
```bash
venv\Scripts\activate
```
### 4. Installer les dépendances
```bash
pip install -r requirements.txt
```
---
## Initialisation de la base de données
Avant de lancer l’application, il faut initialiser la base de données :
```bash
FLASK_DEBUG=True FLASK_APP=inf349 flask init-db
```
Cette commande :
* Crée les tables nécessaires dans la base de données SQLite.
---
## Lancement de l’application
```bash
FLASK_DEBUG=True FLASK_APP=inf349 flask run
```
Au premier lancement :
* L’application récupère les produits depuis le service distant.
* Les produits sont sauvegardés.
---
## Collection Postman

Une collection Postman est disponible pour tester les différentes routes de l’API :
https://inf349-projet-session.postman.co/workspace/8INF349-Projet-session-Workspac~73745a7e-79e8-43ff-82a0-0597742f07a0/collection/43299978-14312d1c-406d-4ee3-a1b1-b9858e06e3f8?action=share&creator=43299978
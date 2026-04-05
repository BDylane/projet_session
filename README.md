# 8INF349 – Projet de session

## Description

Ce projet consiste à développer une application Web en Python utilisant le framework Flask.
L'application permet de gérer des commandes de produits via une API REST et d'effectuer des paiements à l'aide d'un service distant.

---
## Membres de l'équipe
* Martin
* Dylane
* Nathan
---

## Prérequis
* Python 3.6+
* Docker et Docker Compose

---

## Installation
### 1. Cloner le projet
```bash
git clone https://github.com/BDylane/projet_session.git
cd projet_session
```
### 2. Créer un environnement virtuel Python
```bash
python3 -m venv venv
```
### 3. Activer l'environnement virtuel
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
## Initialisation et lancement

### Initialisation (base de données + services)
Lance les conteneurs Docker (PostgreSQL + Redis) et initialise les tables :
```bash
./install
```

### Lancement de l'application
```bash
./start
```
Au premier appel à l'API :
* L'application récupère les produits depuis le service distant.
* Les produits sont sauvegardés dans PostgreSQL.

---
## Collection Postman

Une collection Postman est disponible pour tester les différentes routes de l'API :
https://inf349-projet-session.postman.co/workspace/8INF349-Projet-session-Workspac~73745a7e-79e8-43ff-82a0-0597742f07a0/collection/43299978-14312d1c-406d-4ee3-a1b1-b9858e06e3f8?action=share&creator=43299978
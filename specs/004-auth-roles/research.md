# Research: Authentification et gestion des rôles

**Feature**: 004-auth-roles | **Date**: 2026-03-20

## R1 : Librairie JWT pour Python

**Decision** : python-jose[cryptography]
**Rationale** : Librairie mature et largement adoptée dans l'écosystème FastAPI. Le backend cryptography offre de meilleures performances que le backend natif. Compatible Python 3.12+.
**Alternatives considered** :
- PyJWT : plus léger mais moins d'algorithmes supportés et nécessite pyjwt[crypto] séparément
- authlib : plus complet (OAuth2 serveur) mais surdimensionné pour du JWT simple

## R2 : Hashage des mots de passe

**Decision** : passlib[bcrypt] avec CryptContext
**Rationale** : passlib fournit une abstraction propre via CryptContext qui gère automatiquement la vérification de hash même en cas de changement d'algorithme futur. bcrypt est le standard recommandé : coût computationnel configurable, résistant aux attaques par table arc-en-ciel.
**Alternatives considered** :
- argon2-cffi : plus récent et gagnant de la Password Hashing Competition, mais bcrypt est explicitement requis par la constitution du projet
- hashlib (scrypt) : stdlib mais API moins ergonomique et pas de gestion de migration de schéma

## R3 : Gestion du dark/light mode Nuxt

**Decision** : @nuxtjs/color-mode
**Rationale** : Module officiel Nuxt pour la gestion des thèmes. Détecte automatiquement la préférence système, persiste le choix en cookie/localStorage, et ajoute la classe CSS correspondante sur `<html>`. S'intègre nativement avec Tailwind CSS via la stratégie `class`.
**Alternatives considered** :
- Implémentation manuelle (composable + localStorage) : fonctionnel mais réinvente la roue pour la détection système et la persistance
- VueUse useDark : bon mais ne gère pas le SSR aussi bien que @nuxtjs/color-mode

## R4 : Stratégie de stockage des tokens côté frontend

**Decision** : Access token en mémoire (state réactif), refresh token en cookie httpOnly
**Rationale** : L'access token en mémoire n'est pas accessible via XSS. Le refresh token en cookie httpOnly est protégé contre le XSS et envoyé automatiquement par le navigateur. Cette approche est le standard de sécurité recommandé pour les SPA.
**Alternatives considered** :
- Les deux tokens en localStorage : vulnérable au XSS
- Les deux tokens en cookies : fonctionnel mais l'access token en cookie ajoute du overhead à chaque requête et complexifie le CSRF
- Access token en mémoire seulement (pas de refresh) : mauvaise UX, déconnexion au rechargement de page

**Note d'implémentation** : Le refresh token sera positionné en cookie httpOnly par le backend (Set-Cookie dans la réponse /login et /refresh). Le frontend n'a jamais accès direct au refresh token.

## R5 : Verrouillage brute force

**Decision** : Compteur en base de données (champs failed_login_attempts + locked_until sur le modèle User)
**Rationale** : Simple et suffisant pour le volume attendu (< 100 utilisateurs). Pas besoin de Redis ou d'un rate limiter externe. Le compteur est réinitialisé après une connexion réussie. Le verrouillage est par compte (pas par IP) car les admins sont peu nombreux et identifiés.
**Alternatives considered** :
- Rate limiting par IP (slowapi/redis) : plus complexe, nécessite Redis, surdimensionné pour ce cas d'usage
- Rate limiting en mémoire : ne survit pas aux redémarrages, problématique en multi-instance (hors scope actuel)

## R6 : Structure du modèle Base SQLAlchemy

**Decision** : Base déclarative avec DeclarativeBase, mixin commun pour id (UUID) et created_at
**Rationale** : Le projet aura d'autres modèles (géographie, comptes). Un base model avec les champs communs (id UUID, created_at) évite la duplication. UUID v4 comme clé primaire pour éviter les ID séquentiels prévisibles.
**Alternatives considered** :
- ID entier auto-incrémenté : plus simple mais prévisible (sécurité) et problématique pour la synchronisation distribuée future
- ULID : ordonnancé temporellement mais ajout de dépendance inutile pour ce cas

## R7 : Test backend auth

**Decision** : pytest + httpx AsyncClient + base de données de test
**Rationale** : httpx.AsyncClient permet de tester les endpoints FastAPI de manière async sans serveur réel. Une base de données de test séparée (ou transactions rollback) garantit l'isolation des tests.
**Alternatives considered** :
- Mocks de la base de données : la constitution préfère les tests d'intégration réalistes
- TestClient synchrone de FastAPI : ne supporte pas les endpoints async natifs

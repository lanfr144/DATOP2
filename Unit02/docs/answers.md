# Unit 02 – réponses aux questions des labs

## Lab 02a – Installing and Running FastAPI
Les réponses au « Check your understanding » et aux challenges 1-5 sont en commentaires dans
`fastapi-lab/api/app/lab2a.py`. Résumé :
- **Path vs query parameter** : `/square/{n}` → `n` fait partie du chemin (obligatoire) ;
  `/add?a=3&b=4` → `a`, `b` après le `?` (souvent optionnels, filtres/options).
- **Virtual environment** : isole les versions de paquets par projet, rend l'installation reproductible.
- **`--reload`** : redémarre le serveur à chaque sauvegarde ; à éviter en production (coût CPU,
  requêtes coupées, code non figé).
- **Docs** : `/docs` (Swagger UI interactif), `/redoc` (référence), `/openapi.json` (schéma brut).
- **Your turn (Step 6)** : `/hello/Ada Lovelace` → le navigateur encode l'espace en `%20`
  (`/hello/Ada%20Lovelace`), FastAPI le décode : `{"greeting": "Hello, Ada Lovelace!"}`. `/hello/` → 404.
- **Challenge 2** : `/add?a=3&b=abc` → **422**, `loc = ["query","b"]`, `type = int_parsing`.

## Lab 02b – POST, Validation & Testing
**Your turn – prédire le code** (vérifié par les tests de `fastapi-post/api/tests/test_app.py`) :

| Requête | Code | Pourquoi |
|---|---|---|
| `GET /items/99` | 404 | levé par notre code (`HTTPException`) |
| POST `"rating": 6` | 422 | `le=5` |
| POST `"sizes": [1,2,3,4,5,6]` | 422 | `max_length=5` |
| POST `"price": "cheap"` | 422 | pas un nombre |
| `GET /items?limit=0` | 422 | la dépendance `pagination` exige `limit >= 1` (`ge=1`) |

**Réflexion 404 vs 422** : un **404** signifie que la ressource demandée n'existe pas (la requête est
correcte, mais l'item 99 n'est pas dans la base) ; c'est **notre code** qui le lève avec
`raise HTTPException(status_code=404)`. Un **422** signifie que la requête a été lue mais que ses
valeurs ne respectent pas le contrat (type, longueur, bornes) ; il est levé **automatiquement par
FastAPI/Pydantic**, avant même l'appel de notre fonction, avec le détail `loc`/`msg`/`type`.
Le client sait ainsi s'il doit corriger ses données (422) ou l'identifiant demandé (404).

## Lab 02c – Django REST Framework
**Your turn**
- `POST /hello/` → **405 Method Not Allowed** : `@api_view(["GET"])` n'autorise que GET.
- Admin : après `python manage.py createsuperuser`, les livres ajoutés dans `/admin/` apparaissent
  dans `GET /books/` (même table `core_book`).
- `"published": "2099-01-01"` → **400** `{"published": ["The publication date cannot be in the future."]}`.
- `get_object_or_404` : même comportement (404), seul le message change
  (`"No Book matches the given query."`), et le code est plus court.
- Pagination (`PAGE_SIZE = 2`) : la réponse n'est plus une liste mais
  `{"count": 3, "next": "...?page=2", "previous": null, "results": [...]}`.
- `/books/?ordering=-published` → les plus récents d'abord ; `?search=django&ordering=title&page=1` combine les trois.

**Check your understanding**
1. **Projet vs app** : le projet (`myproject`) contient la configuration globale (settings, URL racine) ;
   une app (`core`) est un module fonctionnel réutilisable (modèles, vues, URL).
2. **`makemigrations` puis `migrate`** : la 1re commande écrit un fichier de migration à partir des
   modèles (versionné avec le code), la 2e l'exécute sur la base. On peut relire/partager le changement avant de l'appliquer.
3. **Deux rôles du serializer** : convertir objets ↔ JSON (sérialisation) et valider les données entrantes.
4. **PUT vs PATCH** : PUT remplace toute la ressource (tous les champs requis :
   `PUT /books/1/ {"title":..,"author":..,"published":..}`), PATCH modifie seulement les champs envoyés
   (`PATCH /books/1/ {"title":"New"}`).
5. **Comparaison FastAPI** : les **serializers** jouent le rôle des modèles **Pydantic** ;
   la **browsable API** de DRF joue le rôle de **`/docs`** (Swagger UI).

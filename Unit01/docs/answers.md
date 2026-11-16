# Unit 01 – API Basics : réponses aux exercices théoriques

## Exercise 1 – HTTP
**Part A.1**
| Méthode | Rôle | Idempotente ? |
|---|---|---|
| GET | Lire une ressource, sans la modifier | oui |
| POST | Créer une ressource (ou déclencher une action) | non |
| PUT | Remplacer entièrement une ressource | oui |
| PATCH | Modifier partiellement une ressource | pas forcément |
| DELETE | Supprimer une ressource | oui |

**Part A.2** : 200 → B (succès) · 404 → A (ressource introuvable) · 500 → C (erreur interne du serveur).

**Part B** (vérifié avec `exercises/ex1_http.py`)
1. `GET /posts/1` → title = `"sunt aut facere repellat provident occaecati excepturi optio reprehenderit"`.
2. `POST /posts` → `201 Created`, id = `101` (JSONPlaceholder simule l'écriture).
3. `GET /posts/999999` → `404`, corps `{}`.

**Réflexion** : les méthodes indiquent l'intention (lire / créer / modifier / supprimer) et les codes
de statut indiquent le résultat de façon standard (2xx succès, 4xx erreur du client, 5xx erreur du serveur).
Un client peut donc réagir automatiquement (réessayer un 503, corriger un 422, ne pas réessayer un 404)
sans parser le message d'erreur.

## Exercise 2 – JSON
**Part A**
1. JSON (JavaScript Object Notation) est un format texte léger, lisible, indépendant du langage,
   supporté nativement par tous les langages → standard de fait pour les API REST.
2. JSON vs XML : JSON est plus compact (pas de balises fermantes) ; JSON a des types natifs
   (nombre, booléen, tableau, null) alors qu'en XML tout est texte ; XML a des attributs, des namespaces
   et des schémas (XSD) plus riches.
3. Clés toujours des chaînes : **Vrai** · JSON peut contenir des tableaux : **Vrai** ·
   JSON dépend du langage : **Faux**.

**Part B** : `"Book Title"` · `genres` est un tableau (array) de chaînes · `"available": true`
signifie que le livre est disponible (empruntable / en stock).

**Part C**
```json
{
  "id": 101,
  "name": "Alice",
  "age": 22,
  "enrolled": true,
  "courses": ["APIs", "Databases", "Networking"]
}
```

## Exercise 3 – gRPC
1. gRPC est un framework RPC (Google) : le client appelle une méthode distante comme une fonction locale.
   REST manipule des ressources via des URL + verbes HTTP et échange en général du JSON.
2. Protocol Buffers est un format binaire typé, défini par un contrat `.proto` : messages plus petits,
   (dé)sérialisation plus rapide et génération de code client/serveur.
3. Communication interne entre microservices, systèmes à faible latence, streaming bidirectionnel,
   clients mobiles/IoT avec peu de bande passante.
4. Basé sur HTTP/2 : **Vrai** · messages lisibles comme du JSON : **Faux** (binaire) ·
   courant dans les microservices : **Vrai**.

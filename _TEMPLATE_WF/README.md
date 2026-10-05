# <Nom du workflow>

> Gabarit. Copier ce dossier, le renommer, remplir chaque section, supprimer les `<...>`.

**En une phrase** : <ce que le workflow produit, à partir de quoi>.

## Pipeline

1. <Étape 1 — modèle utilisé, entrée → sortie>
2. <Étape 2>
3. <Étape 3>

## Modèles requis

| Type | Nom exact | Source |
|---|---|---|
| Checkpoint | <...> | <lien> |
| LoRA | <...> | <lien> |
| VAE / Text encoder | <...> | <lien> |

## Nodes custom

- <nom du pack> — <ce qu'il apporte ici>

## Réglages clés

| Paramètre | Valeur | Pourquoi |
|---|---|---|
| Steps / CFG | <...> | <...> |
| Résolution | <...> | <...> |
| Denoise | <...> | <...> |

## Entrées attendues

- `images/in_*.png` — <nature des images d'entrée, résolution, cadrage>

## Prompt Set

Coller [CONTEXT_prompt-set_<nom>.md](CONTEXT_prompt-set_<nom>.md) dans une conversation Claude, puis donner le brief et joindre les références. Claude renvoie les champs à coller dans le workflow.

## Exemples

| Entrée | Résultat |
|---|---|
| ![in](images/in_exemple.png) | ![out](images/out_exemple.png) |

## Limites connues

- <ce qui ne marche pas, les pièges, les cas à éviter>

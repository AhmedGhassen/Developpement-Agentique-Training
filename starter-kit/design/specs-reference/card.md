# Spécification de référence — composant Card (facture)

**Document formateur.** À ne pas distribuer avant l'étape 4 de l'atelier A8 : les
participants doivent produire leur propre spécification d'abord, puis comparer.

C'est un exemple de ce à quoi ressemble une spécification **exploitable** : chaque
valeur est un token, chaque état est décrit, et les manques sont signalés comme tels.

---

## Structure

```
Card
├── header
│   ├── reference   (texte, tronqué si nécessaire)
│   └── badge       (statut, largeur fixe, jamais compressé)
├── client          (texte secondaire)
├── amount          (montant, chiffres à largeur fixe)
└── footer          (date d'émission | date d'échéance, séparés par un filet)
```

## Conteneur

| Propriété | Token | Valeur |
|---|---|---|
| Largeur | — | `320px` (fixe au-dessus de 360px de viewport) |
| Fond | `color.surface` | `#FFFFFF` |
| Bordure | `border.width` + `color.border` | `1px solid #DDE2EB` |
| Rayon | `radius.md` | `8px` |
| Padding | `spacing.md` | `16px` (uniforme sur les 4 côtés) |
| Espacement interne vertical | `spacing.sm` | `8px` entre blocs |

## Typographie

| Élément | Taille | Graisse | Interligne | Couleur |
|---|---|---|---|---|
| `reference` | `font.size.title` 16px | 700 | `line-height.tight` 1.25 | `color.text` |
| `badge` | `font.size.caption` 12px | 500 | 1 | `color.surface` sur fond de statut |
| `client` | `font.size.body` 14px | 400 | `line-height.body` 1.5 | `color.text.muted` |
| `amount` | `font.size.amount` 24px | 700 | `line-height.tight` 1.25 | `color.text` |
| `footer` | `font.size.caption` 12px | 400 | `line-height.body` 1.5 | `color.text.muted` |

`amount` utilise des chiffres à largeur fixe (`font-variant-numeric: tabular-nums`)
pour que les montants s'alignent verticalement dans une liste.

## Badge de statut

| Statut | Token de fond | Valeur |
|---|---|---|
| Payée | `color.success` | `#1F935E` |
| En attente | `color.warning` | `#C27A0A` |
| En retard | `color.danger` | `#C0393C` |

Rayon `radius.pill`, padding `spacing.xs` vertical et `spacing.sm` horizontal.
Le badge ne se compresse jamais : la référence est tronquée avant lui.

## Séparateur du footer

Filet supérieur `1px solid color.border`, précédé d'un padding `spacing.sm`.

## États

| État | Différences avec `default` |
|---|---|
| `default` | référence |
| `hover` | bordure `color.accent`, ombre `shadow.hover` (`0 2px 8px rgba(18,24,38,0.08)`), curseur pointeur |
| `disabled` | opacité `0.5`, aucune interaction (`pointer-events: none`). **Aucune couleur n'est modifiée** : seule l'opacité change |

Transition sur `border-color` et `box-shadow` uniquement :
`duration.fast` 150ms, `easing.standard` `cubic-bezier(0.2, 0, 0.2, 1)`.
Aucune transition sur l'opacité de l'état `disabled`.

## Responsive

Sous `360px` de viewport, la carte passe en largeur `100%`. Aucune autre
modification : les tailles de police et les espacements sont inchangés.

## Valeurs sans token correspondant — à signaler

Ces valeurs n'ont pas d'équivalent dans un système de tokens standard. Une
spécification honnête les **signale** au lieu de les coder en dur silencieusement :

- `shadow.hover` — à créer si le projet n'a pas d'échelle d'ombres
- `radius.pill` (`999px`) — souvent absent des échelles de rayons
- la largeur `320px` du conteneur — relève de la mise en page, pas du composant
- `font.size.amount` (24px) — vérifier s'il correspond à un niveau typographique existant

## Points de vérification pour l'étape 4

- [ ] Padding uniforme de `16px`, pas `12px` ni `20px`
- [ ] Rayon `8px` sur le conteneur, `pill` sur le badge
- [ ] Le montant est en 24px gras, avec chiffres à largeur fixe
- [ ] `hover` change la bordure **et** ajoute une ombre
- [ ] `disabled` ne change que l'opacité
- [ ] Le filet du footer est présent, avec son padding
- [ ] Aucune valeur codée en dur dans l'implémentation

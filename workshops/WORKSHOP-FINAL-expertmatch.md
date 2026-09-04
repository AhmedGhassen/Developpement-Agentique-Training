# Workshop final — ExpertMatch Agent

**Jour 2 · 15:45 – 17:10 · binômes · 85 min**

Code de référence : `projects/expert-match-agent/` — 30 tests + 9 évaluations.

## Objectif

Assembler un système agentique complet à partir de tout ce qui a été construit. **Rien n'est à réécrire — le capstone assemble.**

```
« Je cherche un expert Data Engineer avec expérience Spark, Azure et
  Databricks pour une mission de 6 mois, démarrage en janvier. »
```

Rien dans cette phrase ne dit si « janvier » est négociable. C'est exactement le genre d'ambiguïté qu'un agent tranche silencieusement — et que `Criteria.unresolved` matérialise.

## La boucle, en 30 lignes

```python
def run(self, brief: str, state: SessionState | None = None) -> MatchResult:
    state = state or SessionState()
    criteria   = self._extractor.extract(brief)              # 1. OBSERVATION
    candidates = readonly.search_experts(criteria, state)    # 2. ACTION
    ranked     = rank(candidates, criteria, ...)             # 3. REASONING
    return MatchResult(criteria=criteria, ranked=ranked,     # 4. FEEDBACK
                       explanation=explain(ranked, criteria), state=state)
```

Aucun framework. Le modèle extrait et rédige ; **il ne calcule pas** (ADR-08).

---

## Jalons

| Jalon | Contenu | Preuve démontrable | Statut |
|---|---|---|---|
| 1 | Critères typés + état de session borné | Demande française → `Criteria` validé | **Obligatoire** |
| 2 | MCP, récupération, scoring déterministe | Classement de candidats réels | **Obligatoire** |
| 3 | Explication + barrière d'approbation | Action **bloquée** sans validation | **Obligatoire** |
| 4 | Superviseur + mesure comparée | Tableau coût / latence / qualité | Optionnel |
| 5 | Docker + CI exécutant les évaluations | `docker compose up`, workflow vert | Optionnel |

**16:45 — dernier moment pour committer.**

---

# Jalon 1 — Critères typés et bornes

## Le modèle

```python
class Criteria(BaseModel):
    role: str
    required_skills: list[str] = Field(min_length=1)
    duration_months: int | None = None
    start_date: date | None = None
    start_is_firm: bool = False        # « janvier » est-il négociable ?
    seniority_years: int | None = None
    unresolved: list[str] = []         # ce que l'extraction n'a pas su trancher
```

`unresolved` est la meilleure idée du capstone : **un agent qui invente une valeur par défaut sans le dire est plus dangereux qu'un agent qui déclare son incertitude.**

## Les bornes ne sont pas des métriques

```python
def charge(self, *, calls: int = 1, cost: float = 0.0) -> None:
    self.tool_calls += calls
    if self.tool_calls > self.max_tool_calls:
        raise BudgetExceeded(...)
```
i
Sans cela, la boucle ne s'arrête pas. Deux tests le garantissent.

## Prompt

```text
Lis CLAUDE.md, src/tools/ et le schéma du serveur MCP. Ne modifie rien.

Propose un plan pour extraire des critères typés depuis une demande en
français libre : quel modèle Pydantic, quelle stratégie face aux champs
absents, quels cas d'ambiguïté. Liste les cas de test avant le code.

Règle absolue : n'invente aucune valeur. Tout champ que la demande ne permet
pas de trancher vaut None ET figure dans `unresolved`.
```

## Critères de validation

- [ ] La sortie du modèle est validée par Pydantic avant tout usage
- [ ] Une demande sans compétence lève une erreur typée avec un `hint`
- [ ] « senior » → `seniority_years is None` et `"seniority_years" in unresolved`
- [ ] « 8 ans » → `seniority_years == 8`, pas dans `unresolved`
- [ ] Les bornes mordent : deux tests le prouvent

---

# Jalon 2 — MCP, récupération, scoring

## Spécification du scoring

| Composante | Poids | Règle |
|---|---|---|
| Compétences requises | 50 % | Proportion couverte |
| Compétences souhaitées | 15 % | Proportion couverte |
| Séniorité | 20 % | Saturation à la valeur demandée |
| Disponibilité | 15 % | 1 si disponible ; **0 si `start_is_firm`** ; sinon décroissance sur 90 j |

Chaque score s'accompagne du **détail par composante** — sinon l'explication du jalon 3 n'a rien sur quoi se fonder.

## Le plancher de couverture

```python
def rank(candidates, criteria, *, limit=5, min_required_coverage=0.0):
    """
    0.0  -> sourcing large : tout candidat couvrant au moins une compétence.
    1.0  -> « requis » signifie requis : couverture totale exigée.
    """
```

Ce paramètre n'existait pas au départ. Il a été ajouté après **trois échecs d'évaluation** — voir ADR-09. C'est un exemple de décision d'architecture révélée par un harnais de test.

## Critères de validation

- [ ] Le scoring est testé sans réseau, avec des cas construits à la main
- [ ] Une date impérative **élimine** (score 0), une date souple décroît
- [ ] Un candidat sans aucune compétence requise ne peut pas être classé
- [ ] Égalité départagée par le taux journalier — et un test le prouve

---

# Jalon 3 — Explication et barrière

## L'explication part du score, pas des profils

```python
deltas = {k: getattr(first.breakdown, k) - getattr(second.breakdown, k) ...}
decisive = max(deltas, key=lambda k: abs(deltas[k]))
```

Elle cite **la composante qui a fait la différence** entre le premier et le deuxième. Une explication qui paraphrase les CV ne justifie pas le rang.

## La barrière est du code

```python
if not state.approvals[approval_id]:
    raise ActionNotApproved(f"action non approuvée : {approval_id}",
        hint="attendre la décision humaine ; ne pas réessayer en boucle")
```

Plus la clé d'idempotence : `f"{state.request_id}:{expert_id}"`. Deux appels identiques, un seul effet.

## Le prompt anti-test-complaisant

```text
Écris un test qui tente de déclencher propose_assignment sans approbation
enregistrée, et qui échoue si l'action aboutit. Puis exécute-le.

Si le test passe du premier coup, c'est qu'il ne teste rien : montre-moi
pourquoi il devrait échouer sur la version actuelle.
```

## Ce qui est démontré à 17:10

Vous tentez l'affectation sans validation, **devant la salle**, et le système refuse. Pas de « ça marche » — on montre.

## Critères de validation

- [ ] L'explication cite des composantes de score, pas des généralités
- [ ] L'explication signale les critères `unresolved`
- [ ] Le refus vient du **code**, pas d'une consigne au modèle
- [ ] L'idempotence est prouvée : double appel, un seul enregistrement
- [ ] Le test de non-régression échouait avant

---

# Jalon 4 — Superviseur et mesure *(optionnel)*

Avant de découper, posez le **test d'indépendance** : les sous-tâches sont-elles réellement indépendantes ?

Ici, non — le scoring a besoin de *tous* les candidats et des critères. Le découpage ajoute deux passages de relais pour zéro parallélisme.

Mesurez quand même, sur le même jeu de cas :

| | Un seul agent | Superviseur |
|---|---|---|
| Tours | | |
| Tokens | | |
| Latence | | |
| Taux de réussite sur 8 cas | | |

**Le résultat n'est pas connu d'avance.** Sur une tâche à sous-problèmes disjoints — analyser trente contrats indépendants — la conclusion s'inverse. Le critère est l'indépendance, pas la complexité apparente.

---

# Jalon 5 — Docker et CI *(optionnel)*

```yaml
  tests:
      - run: pytest -q -m "not eval and not llm"    # BLOQUANT
  evaluations:
    needs: tests
      - run: pytest -q -m eval --json-report
        continue-on-error: true                     # NON BLOQUANT — ADR-05
```

Un gate dur sur un taux non déterministe produit une CI que l'équipe contourne.

---

## Restitution — 17:10

Deux binômes, cinq minutes chacun :

1. Une demande en français entre → un classement expliqué sort
2. Une tentative d'affectation sans validation → **refus démontré**
3. Un chiffre : coût par exécution, ou taux de réussite sur les 8 cas

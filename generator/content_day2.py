"""Jour 2 — GitHub Copilot, orchestration multi-agents et SDLC agentique."""

from deck_builder import (AMBER, CLAUDE, COPILOT, GREEN, RED, VIOLET, Badge,
                          Deck)

FOOTER = "Développement agentique · Claude Code & GitHub Copilot · Jour 2"

INTER = Badge("INTERMÉDIAIRE", COPILOT)
EXPERT = Badge("EXPERT", VIOLET)
BOTH = Badge("INTER. + EXPERT", GREEN)


def build(path):
    d = Deck(FOOTER, accent=COPILOT)

    # ===================================================================== #
    # Ouverture
    # ===================================================================== #

    d.title_slide(
        "Jour 2 · de l'agent maîtrisé à l'organisation outillée",
        "Copilot, orchestration\net SDLC agentique",
        "Déléguer une tâche jusqu'à la pull request, piloter plusieurs agents, "
        "et tenir la chaîne avec des barrières qui ne se négocient pas.",
        [
            "**Matin** — Copilot agentique : custom agents, handoffs, CLI, Agent HQ",
            "**Après-midi** — Design & navigateur, agent teams, SDLC agentique",
            "**16:10** — Capstone : du ticket au merge, avec vérification automatique",
        ],
        notes="""
Rappeler le fil rouge : déplacer l'effort de la génération vers la vérification.
Le Jour 1 outillait un agent. Le Jour 2 outille une équipe : plusieurs agents,
plusieurs surfaces (IDE, terminal, CI, navigateur), et une gouvernance.
Vérifier en 2 minutes que Copilot CLI est installé chez tout le monde avant de démarrer.
""",
    )

    d.agenda(
        "Jour 2 — Copilot, orchestration, industrialisation",
        [
            ("09:00", "**M6** Retour du Jour 1 · carte des outils · quel agent pour quoi", "theorie"),
            ("09:20", "**M7** Copilot agentique : agent mode, plan agent, custom agents", "theorie"),
            ("09:50", "**Atelier 6** Custom agents et handoff plan → implémentation", "atelier"),
            ("10:45", "Pause", "pause"),
            ("11:05", "**M8** Copilot CLI, coding agent, Agent HQ  +  **Atelier 7**", "atelier"),
            ("12:20", "Déjeuner", "pause"),
            ("13:30", "**M9** Design & navigateur : la boucle visuelle  +  **Atelier 8**", "atelier"),
            ("14:45", "**M10** Agent teams et orchestration  +  **Atelier 9**", "atelier"),
            ("16:00", "**M11** SDLC agentique : CI, coûts, sécurité, mesure", "theorie"),
            ("16:25", "**Capstone** Du ticket au merge, barrières comprises", "capstone"),
            ("17:20", "Restitution, plan 30/60/90, clôture", "theorie"),
        ],
        kicker="Programme",
        notes="""
La journée est dense : tenir les horaires est la principale difficulté.
Point de non-retour : à 16:25 le capstone démarre, même si l'atelier 9 n'est pas fini.
Le capstone est conçu pour assembler ce qui existe déjà — rien à réécrire.
""",
    )

    d.table(
        "Quel agent pour quelle tâche : la grille de décision",
        ["Situation", "Surface la plus adaptée", "Pourquoi"],
        [
            ("Refactor guidé, dépôt que je connais",
             "**Claude Code** ou **Copilot agent mode** en IDE",
             "Boucle serrée, contrôle du diff, vérification immédiate"),
            ("Chantier long, contexte lourd à explorer",
             "**Claude Code** + subagents / worktrees",
             "Isolation de contexte, contrôle fin des permissions"),
            ("Tâche bien spécifiée, je veux une PR sans y toucher",
             "**Copilot coding agent** (Agent HQ)",
             "Exécution asynchrone, PR revue par les mêmes gates que les humains"),
            ("Automatisation, script, pipeline",
             "**Copilot CLI** ou **`claude -p`** en headless",
             "Sortie machine, intégrable, mesurable"),
            ("Vérification systématique sur chaque PR",
             "**CI** : `claude-code-action`, Copilot code review",
             "Aucun humain dans la boucle, donc aucun oubli"),
        ],
        kicker="M6 · orientation",
        lead="La question n'est pas « quel outil est le meilleur » mais « quelle surface pour "
             "quel niveau de spécification et quel niveau de risque ».",
        widths=[2.6, 2.4, 2.9],
        size=10.5,
        notes="""
Cette grille est la slide la plus utile à ramener en équipe. La variable cachée est
le niveau de spécification : plus la tâche est spécifiée, plus on peut la rendre asynchrone.
Corollaire : investir dans la spécification (issue bien écrite, AGENTS.md) est ce qui débloque
la délégation asynchrone. C'est un travail humain, pas un réglage d'outil.
""",
    )

    d.two_col(
        "Ce qui diffère réellement entre les deux outils",
        left={
            "title": "Claude Code",
            "color": CLAUDE,
            "items": [
                "Contrôle fin du contexte : `/context`, `/compact`, subagents, `/rewind`",
                "Permissions déclaratives versionnées, `deny` prioritaire",
                "**Hooks** sur le cycle de vie : le garde-fou déterministe",
                "Terrain de jeu du terminal : worktrees, headless, agent teams",
                "Point faible : moins intégré au cycle GitHub natif",
            ],
        },
        right={
            "title": "GitHub Copilot",
            "color": COPILOT,
            "items": [
                "Intégration native au cycle **issue → PR → revue → merge**",
                "Agent HQ : plusieurs fournisseurs d'agents, une surface de pilotage",
                "Gouvernance d'entreprise : politiques, quotas, agents au niveau organisation",
                "`/fleet` pour comparer N tentatives sur la même tâche",
                "Point faible : contrôle du contexte moins granulaire",
            ],
        },
        kicker="M6 · comparatif",
        badges=[BOTH],
        lead="Les deux convergent (MCP, `.agent.md`, AGENTS.md, plan puis exécution). "
             "Ce qui reste vraiment différent tient en deux mots : granularité contre intégration.",
        notes="""
Éviter le match d'outils : la question posée en entreprise est « lequel choisir »,
la bonne réponse est « les deux, sur des surfaces différentes ».
Le point de convergence à retenir : MCP et AGENTS.md rendent l'investissement portable.
C'est l'argument qui protège d'un enfermement fournisseur.
""",
    )

    # ===================================================================== #
    # M7 — Copilot agentique
    # ===================================================================== #

    d.section(
        "07",
        "Copilot agentique dans l'IDE",
        "Agent mode, plan agent, custom agents et passages de relais",
        [
            "La couche d'instructions : AGENTS.md, instructions ciblées, prompt files",
            "Les custom agents `.agent.md` : rôle, outils, modèle, handoffs",
            "Plan → implémentation : le relais explicite entre deux agents",
        ],
        notes="""
Public souvent inégal ici : certains n'utilisent que la complétion inline.
Cadrer d'emblée les trois modes : complétion, chat/ask, agent mode. Le saut de valeur
est entre chat et agent mode, parce que l'agent exécute et vérifie lui-même.
""",
    )

    d.table(
        "La couche d'instructions Copilot : quatre fichiers, quatre portées",
        ["Fichier", "Portée", "Usage"],
        [
            ("`AGENTS.md` (racine)", "Tous les agents compatibles, tout le dépôt",
             "**Le standard à privilégier** : build, tests, conventions, limites"),
            ("`.github/copilot-instructions.md`", "Copilot, tout le dépôt",
             "Spécificités Copilot si nécessaire"),
            ("`*.instructions.md` + `applyTo`", "Ciblée par motif de fichiers",
             "Règles propres à `**/*.tsx`, `**/tests/**`, l'infra…"),
            ("`*.prompt.md`", "Invoquée à la demande dans le chat",
             "Tâche répétitive paramétrable — l'équivalent d'une skill"),
        ],
        kicker="M7 · instructions",
        badges=[INTER],
        lead="Monorepo : les agents lisent le fichier `AGENTS.md` **le plus proche** dans "
             "l'arborescence. Un fichier par sous-projet, plutôt qu'un fichier racine géant.",
        widths=[2.5, 2.3, 3.2],
        size=11,
        notes="""
Point de convergence important : AGENTS.md est lu par Copilot, Codex, Cursor, Gemini CLI, Jules…
Claude Code lit CLAUDE.md ; l'usage établi est de faire un CLAUDE.md court qui importe @AGENTS.md.
On évite ainsi de maintenir deux vérités. Le montrer concrètement à l'atelier 6.
""",
    )

    d.code(
        "AGENTS.md : le fichier qui rend une tâche déléguable",
        """
# AGENTS.md  (racine du depot)

Service de facturation. Python 3.12, FastAPI, PostgreSQL.

## Setup
uv sync --all-extras          # installation
docker compose up -d db       # base locale

## Tests
pytest -q                     # unitaires — doivent passer avant tout commit
pytest -q -m integration      # necessite la base locale

## Style
ruff format . && ruff check --fix .
Typage strict obligatoire sur src/. Aucune fonction publique sans docstring.

## Boundaries
### Always
- Ajouter un test pour tout changement de comportement
- Mettre a jour CHANGELOG.md pour tout changement d'API publique
### Ask first
- Migration de schema (alembic), ajout de dependance, changement de contrat public
### Never
- Modifier src/billing/ledger.py sans validation d'un mainteneur
- Committer un secret, un .env, ou un dump de donnees
- Pousser directement sur main
""",
        kicker="M7 · instructions",
        badges=[INTER],
        caption="Les trois niveaux **Always / Ask first / Never** transforment un fichier "
                "descriptif en fichier actionnable. Viser moins de 300 lignes.",
        notes="""
C'est le gabarit à reprendre tel quel. Les commandes doivent être copiables-collables :
un agent qui doit deviner entre `pytest` et `make test` perd des tours et échoue en CI.
La section Never est celle qui protège : elle nomme des chemins précis, pas des principes.
Rappeler que Claude Code lit CLAUDE.md : on y met une importation `@AGENTS.md` et rien d'autre.
""",
    )

    d.code(
        "Un custom agent Copilot : le rôle avant le prompt",
        """
# .github/agents/revue-api.agent.md
---
name: revue-api
description: Revue des changements d'API publique et de compatibilite
model: GPT-5.2 (copilot)
tools: [search, codebase, fetch, problems, testFailure]
agents: []                 # aucun subagent : perimetre volontairement ferme
handoffs:
  - label: Corriger les ruptures detectees
    agent: implementation
    prompt: Corrige uniquement les ruptures de compatibilite listees ci-dessus.
    send: false
---

Tu analyses les changements d'API publique de cette branche.

Pour chaque symbole exporte modifie : signature avant / apres, verdict
(compatible / rupture / ambigu), et impact appelant. Aucun avis de style.

Si le diff ne touche aucune API publique, reponds exactement :
« Aucun changement d'API publique. » et arrete-toi.
""",
        kicker="M7 · custom agents",
        badges=[BOTH],
        caption="`.github/agents/` pour l'équipe, `~/.copilot/agents` pour vous, `.claude/agents` "
                "pour la compatibilité Claude Code. `agents: []` ferme le périmètre.",
        notes="""
Trois points à souligner :
1. La sortie de secours (« Aucun changement d'API publique ») évite les rapports inventés
   quand il n'y a rien à dire — c'est le remède le plus efficace au bruit.
2. `handoffs` rend le relais explicite : l'agent de revue ne corrige pas, il propose de passer
   la main. Même principe que le duo constructeur/critique du Jour 1.
3. Les anciens `.chatmode.md` se renomment en `.agent.md`.
""",
    )

    d.two_col(
        "Plan agent : le mode le plus rentable, dans les deux outils",
        left={
            "title": "Comment ça marche",
            "color": COPILOT,
            "items": [
                "`/plan` dans le chat, ou l'agent **Plan** dans le sélecteur",
                "Produit un résumé, des étapes d'implémentation **et de vérification**",
                "On itère sur le plan — pas sur le code",
                "« Start Implementation » transmet plan et contexte à l'agent d'implémentation",
                "Personnalisable : modèle du plan, modèle de l'implémentation, outils du plan",
            ],
        },
        right={
            "title": "Pourquoi ça change tout",
            "color": GREEN,
            "items": [
                "Une erreur de plan coûte une phrase ; une erreur de code coûte un diff et une revue",
                "Le plan est un **artefact critiquable par un humain en 60 secondes**",
                "Symétrie avec Claude Code : mode `plan`, puis exécution",
                "Sur une tâche ambiguë, planifier d'abord **réduit** le temps total",
                "Limite à connaître : la mémoire de session du plan disparaît avec la conversation",
            ],
        },
        kicker="M7 · planification",
        notes="""
Faire le parallèle explicite avec le Jour 1 : c'est le même geste dans les deux outils.
Le message d'adoption : « ne demandez pas du code sur une tâche que vous ne savez pas décrire ;
demandez un plan ». C'est le conseil qui fait gagner le plus de temps aux équipes.
Mentionner qu'un custom agent de planification permet d'imposer un gabarit de plan maison.
""",
    )

    d.workshop(
        "Atelier 6 — Un binôme d'agents dans l'IDE",
        ["55 min", "INTER. + EXPERT"],
        [
            "Écrire un `AGENTS.md` à la racine : setup, tests, style, section **Boundaries** "
            "(Always / Ask first / Never)",
            "Faire pointer `CLAUDE.md` vers lui (`@AGENTS.md`) : une seule source de vérité",
            "Créer `.github/agents/revue-api.agent.md` avec `tools` restreints et une sortie de secours",
            "Créer un second agent `implementation` et déclarer le `handoff` entre les deux",
            "Lancer `/plan` sur la **tâche T4**, critiquer le plan, puis « Start Implementation »",
            "Faire passer la revue par `revue-api`, puis utiliser le handoff pour corriger",
        ],
        objective="Reproduire dans Copilot le duo produire / juger du Jour 1, et n'avoir "
                  "qu'un seul fichier d'instructions partagé par les deux outils.",
        expected=[
            "Les deux agents apparaissent dans le sélecteur du chat",
            "`revue-api` répond la phrase de secours quand le diff ne touche aucune API",
            "Le handoff transmet le contexte sans copier-coller",
        ],
        trap=[
            "`tools` trop large : l'agent de revue se met à éditer.",
            "Deux fichiers d'instructions divergents (`AGENTS.md` et `CLAUDE.md`) : les règles se contredisent.",
        ],
        expert=[
            "Faites exécuter la **même** tâche T4 par Claude Code et par Copilot agent mode.",
            "Comparez : tours, diff produit, tests ajoutés, temps humain de revue. Notez les chiffres.",
        ],
        notes="""
La section Boundaries en trois niveaux (Always / Ask first / Never) est la partie la plus utile
de l'AGENTS.md : c'est ce qui rend le fichier actionnable plutôt que descriptif.
Vérifier en circulant que la sortie de secours fonctionne : c'est le test qui révèle
si l'agent respecte vraiment ses instructions ou s'il invente pour faire plaisir.
Timing : 15 min AGENTS.md, 20 min agents, 20 min plan et handoff.
""",
    )

    # ===================================================================== #
    # M8 — CLI, coding agent, Agent HQ
    # ===================================================================== #

    d.section(
        "08",
        "Copilot CLI, coding agent et Agent HQ",
        "Sortir de l'IDE : terminal, asynchrone, et pilotage multi-agents",
        [
            "Copilot CLI : plan, fleet, MCP, plugins, autopilot",
            "Coding agent : de l'issue à la pull request, sans vous",
            "Agent HQ : plusieurs fournisseurs d'agents sur le même dépôt",
        ],
        notes="""
C'est le module qui parle le plus aux tech leads : il touche l'organisation du travail,
pas seulement l'outillage individuel. Garder du temps pour les questions de gouvernance.
""",
    )

    d.code(
        "Copilot CLI : l'essentiel en dix lignes",
        """
# Installation (Node 22+) — aussi WinGet, Homebrew, script
$ npm install -g @github/copilot
$ copilot                    # a lancer DANS le depot, jamais depuis le home

/login                       # OAuth ; en CI : COPILOT_GITHUB_TOKEN puis GH_TOKEN
/init                        # genere les instructions adaptees au projet
/plan                        # planifier avant d'implementer
/fleet                       # meme tache sur N subagents en parallele, puis convergence
/mcp add                     # serveur MCP (GitHub MCP est deja integre)
/plugin install owner/repo   # paquet : MCP + agents + skills + hooks

# Hors session
$ copilot mcp add --transport http gitlab https://gitlab.example.com/api/v4/mcp
# Config : ~/.copilot/mcp-config.json  |  .copilot/mcp.json (par depot)
""",
        kicker="M8 · terminal",
        badges=[BOTH],
        caption="`/fleet` répond à une question que `--parallel` ne pose pas : quand plusieurs "
                "tentatives valent mieux qu'une, on compare puis on choisit.",
        notes="""
Insister sur « lancer dans le dépôt » : le périmètre de confiance et l'accès fichiers en dépendent.
/fleet est l'équivalent conceptuel des dynamic workflows de Claude Code : N tentatives, une décision.
Cas d'usage réel : une migration risquée, trois approches en parallèle, on garde la plus propre.
Sur l'auth CI : ordre de précédence COPILOT_GITHUB_TOKEN > GH_TOKEN > GITHUB_TOKEN.
""",
    )

    d.cards(
        "Agent HQ : plusieurs agents, un seul dépôt",
        [
            {
                "title": "Ce que c'est",
                "color": COPILOT,
                "body": [
                    "Une surface de pilotage unique : GitHub.com, VS Code, mobile, CLI.",
                    "Plusieurs fournisseurs d'agents assignables sur le même dépôt.",
                    "Chaque session d'agent produit une **branche et une PR**.",
                ],
            },
            {
                "title": "Ce qu'il faut savoir avant",
                "color": AMBER,
                "body": [
                    "Plan payant requis ; les agents tiers demandent un niveau supérieur.",
                    "Les agents non-Copilot sont **désactivés par défaut**, à activer par dépôt.",
                    "Chaque session consomme un quota — le coût est réel et mesurable.",
                ],
            },
            {
                "title": "Le vrai levier",
                "color": GREEN,
                "body": [
                    "Ce n'est pas « plus d'agents », c'est **spécialisation + politique**.",
                    "Branch protection : un agent ouvre une PR, il ne merge pas.",
                    "`AGENTS.md` avant toute assignation, sinon la PR est inexploitable.",
                ],
            },
        ],
        kicker="M8 · asynchrone",
        cols=3,
        notes="""
L'erreur d'adoption dominante : lancer cinq agents sur la même tâche en espérant un miracle.
Ce qui marche : un agent par rôle, des instructions écrites, et les mêmes gates de merge
que pour un humain. Une PR d'agent doit passer la CI et une revue humaine, sans exception.
Question à poser au groupe : « qui, chez vous, aurait le droit de merger une PR d'agent ? »
""",
    )

    d.bullets(
        "Déléguer une tâche : les conditions de réussite",
        [
            "La délégation asynchrone échoue presque toujours pour la **même** raison : "
            "la tâche n'était pas assez spécifiée",
            "Une issue déléguable contient quatre choses :",
            ("Le **comportement attendu**, formulé de façon testable", 1),
            ("Les fichiers ou modules concernés, ou comment les trouver", 1),
            ("Le **critère de vérification** : quel test, quelle commande", 1),
            ("Ce qu'il ne faut **pas** toucher", 1),
            "Sans `AGENTS.md`, l'agent réinvente les conventions à chaque tâche",
            "Réflexe : si vous ne pouvez pas écrire le critère de vérification, la tâche n'est "
            "pas prête à être déléguée — elle est prête à être **planifiée**",
        ],
        kicker="M8 · pratique",
        badges=[BOTH],
        notes="""
La dernière puce est le message du module. Elle donne un critère net, applicable en réunion
de sprint : « écris-moi le test qui prouvera que c'est fait ». Si personne ne sait, on planifie.
Cela transforme la question « l'agent est-il assez bon ? » en « notre spécification est-elle assez bonne ? »
""",
    )

    d.two_col(
        "Industrialiser : revue automatique et diffusion d'équipe",
        left={
            "title": "La revue automatique",
            "color": COPILOT,
            "items": [
                "Copilot code review sur chaque PR, humaines comprises",
                "En complément : un job CI avec `claude-code-action` sur un axe précis",
                "**Un axe par revue** : sécurité, ou API publique, ou tests manquants",
                "Le piège : une revue générique produit 30 commentaires cosmétiques et se fait désactiver",
                "Mesure : part des commentaires qui ont provoqué un changement",
            ],
        },
        right={
            "title": "La diffusion à l'équipe",
            "color": GREEN,
            "items": [
                "Copilot : agents au niveau **organisation**, plugins `/plugin install owner/repo`",
                "Claude Code : **plugin** maison = skills + hooks + subagents + MCP",
                "Un dépôt `agent-config` versionné, avec revue de code sur la politique",
                "Règle : ce qui est adopté par trois personnes doit devenir un paquet",
                "Sans diffusion, chaque développeur reconstruit sa propre configuration",
            ],
        },
        kicker="M8 · échelle",
        badges=[EXPERT],
        notes="""
Le chiffre à retenir sur la revue automatique : le taux de commentaires actionnés.
En dessous de 30 %, la revue nuit — elle entraîne l'équipe à ignorer les commentaires d'agents,
y compris les bons. Mieux vaut une revue étroite et respectée qu'une revue large et ignorée.
Sur la diffusion : le dépôt agent-config est le geste organisationnel le plus rentable du Jour 2.
""",
    )

    d.workshop(
        "Atelier 7 — Du ticket à la pull request, sans y toucher",
        ["55 min", "INTER. + EXPERT"],
        [
            "Rédiger une issue **déléguable** pour la tâche T5 : comportement, périmètre, "
            "critère de vérification, interdits",
            "Faire relire l'issue par votre binôme : est-elle exécutable sans question ?",
            "Assigner la tâche au coding agent (ou lancer `copilot` en autopilot sur une branche dédiée)",
            "Pendant l'exécution : lancer `/fleet` sur une **variante** et comparer les approches",
            "À l'arrivée de la PR : la passer par votre agent `revue-api` du matin",
            "Décider : merge, correction guidée, ou rejet — et **écrire pourquoi**",
        ],
        objective="Mesurer ce que coûte et ce que rend une délégation asynchrone, et constater "
                  "que la qualité du résultat suit la qualité de l'issue.",
        expected=[
            "Une PR ouverte par un agent, passée par une revue automatisée",
            "Une décision argumentée en trois lignes, écrite dans la PR",
        ],
        trap=[
            "Issue vague → PR hors sujet. C'est l'issue qu'il faut corriger, pas l'agent.",
            "Agents tiers non activés sur le dépôt : à vérifier **avant** l'atelier.",
        ],
        expert=[
            "Comparez le coût complet : quota consommé, temps humain de rédaction, temps de revue.",
            "Concluez par un chiffre : cette tâche valait-elle une délégation asynchrone ?",
        ],
        notes="""
Le temps d'attente de la PR est une contrainte réelle : c'est pourquoi l'étape 4 occupe le groupe.
Prévoir un dépôt de secours avec une PR d'agent déjà ouverte si les quotas ou les droits bloquent.
La question de l'étape 6 (« écrire pourquoi ») est la plus formatrice : elle force l'explicitation
des critères d'acceptation d'un travail d'agent, ce que peu d'équipes ont écrit.
""",
    )

    # ===================================================================== #
    # M9 — Design & browser
    # ===================================================================== #

    d.section(
        "09",
        "Design et navigateur : fermer la boucle visuelle",
        "L'agent voit le résultat, pas seulement le code qui le produit",
        [
            "De la maquette au composant : MCP design et conventions",
            "Claude Code + Chrome : tester, lire la console, corriger",
            "Vérification visuelle et régression",
        ],
        notes="""
Module très démonstratif : privilégier la démo live sur les slides.
Le point de fond : sans retour visuel, l'agent optimise du code qu'il ne peut pas évaluer.
Fermer la boucle visuelle, c'est donner à l'étape 4 (vérification) un signal en frontend.
""",
    )

    d.bullets(
        "Pourquoi le frontend résistait à l'agentique",
        [
            "Un test unitaire dit « la fonction retourne 3 ». Aucun test ne disait « le bouton "
            "est mal aligné de 4 pixels »",
            "L'agent produisait du code plausible, non **évaluable** par lui-même",
            "Trois briques changent la donne :",
            ("**MCP design** (Figma et équivalents) : la maquette devient une donnée structurée, "
             "pas une image à deviner", 1),
            ("**Navigateur piloté** : `claude --chrome` ou `/chrome`, plus les serveurs MCP "
             "Playwright / Chrome DevTools", 1),
            ("**Capture et comparaison** : l'agent voit son rendu et le confronte à la référence", 1),
            "Résultat : la boucle build → rendu → écart → correction tourne sans intervention",
        ],
        kicker="M9 · le verrou",
        badges=[INTER],
        notes="""
Nuance à porter : « voir » reste imparfait. L'agent détecte bien les écarts grossiers
(espacement, couleur, alignement) et mal les intentions de design.
Le bon découpage : l'agent fait converger le mesurable, l'humain tranche l'intention.
""",
    )

    d.two_col(
        "Deux façons de piloter un navigateur, deux usages",
        left={
            "title": "Chrome piloté (extension)",
            "color": CLAUDE,
            "items": [
                "`claude --chrome` ou `/chrome` — depuis le CLI ou l'extension VS Code",
                "Travaille dans **votre** navigateur, donc sur vos sessions authentifiées",
                "Lecture de la console et du DOM, clics, saisie, capture, enregistrement GIF",
                "En mode `plan` : les lectures passent, les actions d'écriture demandent approbation",
                "Idéal pour **déboguer** une application réelle et vérifier un rendu",
            ],
        },
        right={
            "title": "MCP navigateur (Playwright / DevTools)",
            "color": COPILOT,
            "items": [
                "Navigateur isolé, jetable, scriptable",
                "Pas de session personnelle exposée : plus sûr en CI",
                "Idéal pour **reproduire** un parcours de façon déterministe",
                "Marche dans Copilot CLI et VS Code comme dans Claude Code",
                "À privilégier dès que le résultat doit être rejouable",
            ],
        },
        kicker="M9 · outillage",
        badges=[BOTH],
        lead="Règle simple : navigateur personnel pour explorer et déboguer, navigateur isolé "
             "dès qu'il faut rejouer ou automatiser.",
        notes="""
Avertissement sécurité à donner explicitement : un navigateur piloté sur votre profil
donne accès à tout ce à quoi vous êtes connecté. Restreindre les sites autorisés dans l'extension.
Attention aussi au coût en contexte : les captures et le DOM consomment beaucoup de tokens.
""",
    )

    d.code(
        "La boucle visuelle, en prompts",
        """
# 1 — Extraire la specification depuis la maquette (MCP design)
> Recupere le composant Card de la maquette : espacements, typographies,
  couleurs, etats. Ecris la specification dans specs/card.md.
  N'ecris aucun code a cette etape.

# 2 — Implementer contre la specification, pas contre l'image
> Implemente Card en respectant specs/card.md et nos tokens existants
  dans src/theme/. Aucune valeur codee en dur : uniquement des tokens.

# 3 — Fermer la boucle dans le navigateur
> Ouvre http://localhost:3000/storybook?id=card dans Chrome.
  Compare le rendu a specs/card.md. Liste les ecarts mesures en pixels
  ou en tokens. Corrige, puis reverifie. Boucle jusqu'a zero ecart mesurable.

# 4 — Verrouiller contre la regression
> Ajoute un test Playwright de capture de reference pour les etats
  default, hover et disabled.
""",
        kicker="M9 · pratique",
        badges=[BOTH],
        caption="L'étape 1 est celle qu'on saute et qu'il ne faut pas sauter : sans spécification "
                "écrite, l'étape 3 n'a aucune référence à laquelle se comparer.",
        notes="""
Le passage par specs/card.md est le cœur du module : il transforme une intention visuelle
en critère vérifiable. C'est exactement le fil rouge appliqué au frontend.
L'étape 4 convertit la vérification manuelle en garde-fou permanent : même logique que le hook Stop.
""",
    )

    d.workshop(
        "Atelier 8 — De la maquette au composant vérifié",
        ["55 min", "INTER. + EXPERT"],
        [
            "Brancher un MCP design (Figma ou équivalent) **ou** partir de la maquette fournie",
            "Étape 1 : produire `specs/<composant>.md` — aucun code à ce stade",
            "Étape 2 : implémenter contre la spécification, avec les tokens existants",
            "Étape 3 : activer `/chrome`, comparer le rendu à la spécification, corriger, reboucler",
            "Étape 4 : ajouter un test de capture de référence sur trois états",
            "Casser volontairement un espacement et vérifier que le test **échoue**",
        ],
        objective="Constater qu'un écart visuel devient détectable automatiquement dès lors "
                  "qu'il existe une spécification écrite et une capture de référence.",
        expected=[
            "Un composant sans valeur codée en dur",
            "Un test de capture qui échoue quand on casse l'espacement",
        ],
        trap=[
            "Sauter l'étape 1 : l'agent compare alors le rendu à… rien.",
            "Captures et DOM saturent le contexte : mesurer avec `/context`, cibler les sélecteurs.",
        ],
        expert=[
            "Intégrez le test de capture en CI et faites-le tourner sur navigateur isolé.",
            "Mesurez le surcoût en contexte de la boucle navigateur, et proposez une façon de le réduire.",
        ],
        notes="""
Prévoir absolument la maquette de secours : les accès Figma bloquent souvent en entreprise.
Le dernier pas (casser puis constater l'échec) est non négociable : un test qui n'a jamais
échoué ne prouve rien. C'est le même principe que le prompt anti-test-complaisant.
Timing : 10 min setup, 10 min spec, 15 min implémentation, 15 min boucle navigateur, 5 min test.
""",
    )

    # ===================================================================== #
    # M10 — Agent teams
    # ===================================================================== #

    d.section(
        "10",
        "Agent teams et orchestration",
        "Quand plusieurs agents valent mieux qu'un — et comment le prouver",
        [
            "Le test d'indépendance avant tout découpage",
            "Lead, teammates, liste de tâches partagée, messagerie",
            "La mesure comparée : la seule réponse honnête",
        ],
        notes="""
Module où il faut résister à la mode. L'orchestration multi-agents a un coût de coordination
réel. La bonne pratique est de mesurer, pas de supposer. C'est le sens de l'atelier 9.
""",
    )

    d.bullets(
        "Le test d'indépendance : à poser avant de découper",
        [
            "**Question unique** : les sous-tâches peuvent-elles avancer sans se parler ?",
            "Si oui → parallélisme réel, gain réel",
            ("Trente contrats à analyser, quarante fichiers à migrer, N approches à comparer", 1),
            "Si non → chaque relais ajoute une perte d'information pour zéro parallélisme",
            ("Concevoir un scoring qui a besoin de **tous** les candidats : découper ne gagne rien", 1),
            "Le critère est l'**indépendance**, pas la complexité apparente de la tâche",
            "Corollaire : une tâche difficile mais séquentielle se traite mieux avec un seul agent "
            "bien outillé qu'avec une équipe",
        ],
        kicker="M10 · discernement",
        badges=[EXPERT],
        notes="""
Ce test évite l'essentiel des déceptions sur le multi-agents. Le faire appliquer à voix haute
sur deux exemples issus du groupe avant de lancer l'atelier.
Le piège cognitif : plus une tâche paraît complexe, plus on a envie de la découper — alors que
la complexité vient souvent du couplage, qui est précisément ce qui interdit le découpage.
""",
    )

    d.table(
        "Subagents, agent view, agent teams, fleet : ce qui les distingue",
        ["Mécanisme", "Qui parle à qui", "Coût de coordination"],
        [
            ("**Subagents**", "Rapport au parent uniquement", "Faible — un résumé par subagent"),
            ("**Agent view** / sessions de fond", "Rapport à vous uniquement",
             "Faible, mais **vous** êtes le relais"),
            ("**Agent teams**", "Teammates entre eux, lead superviseur",
             "Élevé : messages, liste de tâches, arbitrages"),
            ("**Copilot `/fleet`**", "Aucun échange : N tentatives, une convergence",
             "Nul, mais coût en quota multiplié"),
        ],
        kicker="M10 · panorama",
        lead="Agent teams est expérimental et désactivé par défaut "
             "(`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`). À manipuler en connaissance de cause.",
        widths=[2.2, 2.7, 2.9],
        size=11,
        notes="""
Faire remarquer que /fleet et agent teams répondent à des questions opposées :
/fleet explore plusieurs solutions au même problème ; agent teams découpe un problème en parties.
Confondre les deux est l'erreur d'architecture la plus fréquente sur ce sujet.
""",
    )

    d.workshop(
        "Atelier 9 — Orchestrer, puis mesurer",
        ["50 min", "EXPERT"],
        [
            "Choisir la **tâche T6** et appliquer le test d'indépendance à voix haute avec votre binôme",
            "Exécution A : un seul agent, bien outillé (skills et subagents du Jour 1)",
            "Exécution B : une agent team (lead + 2 teammates) **ou** `/fleet` selon votre verdict",
            "Remplir le tableau comparatif : tours, tokens, latence, tâche réussie oui/non",
            "Formuler la conclusion en une phrase, chiffres à l'appui",
            "Décider ce que vous **recommanderez** à votre équipe — et à quelle condition",
        ],
        objective="Produire une conclusion argumentée sur l'orchestration multi-agents, "
                  "fondée sur une mesure faite par vous et non sur une intuition.",
        expected=[
            "Un tableau comparatif rempli, avec quatre chiffres réels",
            "Une conclusion en une phrase, qui peut très bien être « ça ne valait pas le coup »",
        ],
        trap=[
            "Comparer deux exécutions sur des tâches différentes : la mesure ne veut plus rien dire.",
            "Oublier d'activer le drapeau expérimental et conclure que « ça ne marche pas ».",
        ],
        expert=[
            "Refaites la mesure sur une tâche **réellement** disjointe (N fichiers indépendants).",
            "La conclusion s'inverse-t-elle ? Formulez la règle de décision qui en découle.",
        ],
        notes="""
Le résultat n'est pas connu d'avance et c'est l'intérêt de l'atelier : sur une tâche couplée,
l'agent unique gagne très souvent. Accueillir ce résultat comme un succès pédagogique.
La piste experte est essentielle pour ne pas repartir avec la conclusion inverse et trop générale.
Timing : 5 min test d'indépendance, 15 min A, 20 min B, 10 min tableau et conclusion.
""",
    )

    # ===================================================================== #
    # M11 — SDLC agentique
    # ===================================================================== #

    d.section(
        "11",
        "SDLC agentique",
        "Faire tenir la chaîne : CI, sécurité, coûts, mesure d'adoption",
        [
            "L'agent dans la pipeline : headless et sorties machine",
            "Les barrières qui ne se négocient pas",
            "Ce qu'on mesure pour savoir si ça marche",
        ],
        notes="""
Dernier module théorique. Il répond à la question du management : « comment on sait que ça marche
et que ça ne nous explose pas à la figure ? » Rester concret : quatre chiffres, trois barrières.
""",
    )

    d.code(
        "L'agent dans la pipeline : headless des deux côtés",
        """
# Claude Code en mode headless
$ claude -p "Revois le diff vs origin/main. Signale uniquement les
             regressions de securite. Aucun commentaire de style." \\
    --output-format json \\
    --allowedTools "Read,Grep,Glob,Bash(git diff:*)" \\
    --max-turns 12 > review.json

# stream-json exige --verbose ; sinon la sortie reste minimale
$ claude -p "..." --output-format stream-json --verbose | tee run.jsonl

# GitHub Actions — action officielle
- uses: anthropics/claude-code-action@v1
  with:
    anthropic-api-key: ${{ secrets.ANTHROPIC_API_KEY }}
    prompt: |
      Revois cette PR : securite, ruptures d'API publique, tests manquants.
      Poste un unique commentaire de synthese.
    allowed-tools: "Read,Grep,Glob,Bash(git diff),Bash(git log)"

# Copilot CLI en CI : jeton par variable d'environnement
$ COPILOT_GITHUB_TOKEN=$TOKEN copilot -p "Resume les changements de cette PR"
""",
        kicker="M11 · CI/CD",
        badges=[EXPERT],
        caption="Les quatre garde-fous non négociables en CI : `--max-turns`, `--allowedTools`, "
                "un budget de tokens, et un `timeout` de job.",
        notes="""
Détail qui fait perdre du temps à tout le monde : --output-format stream-json sans --verbose
ne produit presque rien. À dire explicitement.
Sur l'authentification : OAuth ne fonctionne pas en CI, il faut une clé d'API ou un jeton.
Message de fond : en CI il n'y a aucun humain pour freiner. Les bornes remplacent le jugement.
""",
    )

    d.cards(
        "Trois barrières, et pourquoi elles tiennent",
        [
            {
                "title": "Barrière d'approbation",
                "color": RED,
                "body": [
                    "Toute action irréversible passe par une validation **enregistrée**.",
                    "Le refus vient du code, jamais d'une consigne au modèle.",
                    "Clé d'idempotence : deux appels identiques, un seul effet.",
                ],
            },
            {
                "title": "Barrière de vérification",
                "color": GREEN,
                "body": [
                    "Tests bloquants sur la PR, y compris pour les PR d'agents.",
                    "Hook `Stop` en local, gate dur en CI.",
                    "Les évaluations non déterministes restent **non bloquantes**.",
                ],
            },
            {
                "title": "Barrière de coût",
                "color": AMBER,
                "body": [
                    "Bornes explicites : tours, tokens, durée de job, quota.",
                    "Journaliser le coût par exécution, alerter sur la **dérive**.",
                    "Une hausse de coût à prompt constant est un signal, pas un détail.",
                ],
            },
        ],
        kicker="M11 · gouvernance",
        cols=3,
        notes="""
Le point le plus contre-intuitif : rendre bloquant un taux non déterministe (évaluations LLM)
produit une CI que l'équipe contourne. On sépare donc tests (bloquants) et évaluations (mesurées).
La barrière de coût est celle qu'on oublie et qui fait annuler les programmes d'adoption
au premier trimestre. Journaliser dès le premier jour.
""",
    )

    d.table(
        "Cinq risques, cinq contre-mesures qui tiennent",
        ["Risque", "Contre-mesure **de code** (pas une consigne)"],
        [
            ("**Injection de prompt** via ticket, page web, commentaire, dépendance",
             "`deny` de permission sur les actions sensibles + barrière d'approbation"),
            ("**Exfiltration de secrets** : lecture d'un `.env` recopié ailleurs",
             "`Read(./.env)` en `deny`, hook de détection de secrets avant commit"),
            ("**Serveur MCP ou plugin compromis** (chaîne d'approvisionnement)",
             "Sources approuvées, épinglage de version, revue du `.mcp.json` en MR"),
            ("**Action irréversible** : push, migration, suppression, appel réseau",
             "Hook `PreToolUse` qui refuse, plus branch protection côté dépôt"),
            ("**Dérive de coût** silencieuse en CI",
             "`--max-turns`, budget de tokens, `timeout` de job, alerte sur la tendance"),
        ],
        kicker="M11 · sécurité",
        badges=[BOTH],
        widths=[3.2, 4.0],
        size=11,
        lead="Une seule règle traverse ce tableau : aucune contre-mesure ne repose sur "
             "une instruction donnée au modèle. Le modèle n'est pas un mécanisme de sécurité.",
        notes="""
Slide à garder pour les échanges avec la sécurité et la conformité : elle parle leur langage.
Le point non négociable : « demander gentiment au modèle » n'est pas un contrôle.
Sur la chaîne d'approvisionnement : un plugin installé depuis un dépôt inconnu peut apporter
des hooks qui s'exécutent sur votre poste. Le traiter comme n'importe quelle dépendance.
""",
    )

    d.table(
        "Mesurer l'adoption : quatre indicateurs, zéro vanité",
        ["Indicateur", "Comment le lire"],
        [
            ("**Taux de PR d'agent mergées sans reprise**",
             "Le seul indicateur de qualité qui compte. En dessous de 50 %, le problème est la spécification"),
            ("**Temps humain de revue par PR d'agent**",
             "S'il augmente, l'agent déplace la charge au lieu de la réduire"),
            ("**Coût par tâche aboutie**",
             "Pas le coût par exécution : les tentatives échouées font partie du coût"),
            ("**Incidents évités par les barrières**",
             "Comptez les blocages de hooks et de permissions : c'est la valeur invisible"),
        ],
        kicker="M11 · mesure",
        badges=[BOTH],
        widths=[2.6, 4.6],
        size=11.5,
        lead="Les indicateurs à ne pas suivre : lignes de code générées, nombre de suggestions "
             "acceptées, nombre de sessions. Ils montent quand la situation se dégrade.",
        notes="""
Ces quatre indicateurs sont ce qu'un participant doit pouvoir présenter à son management.
Le quatrième surprend : les blocages de garde-fous sont une production de valeur, il faut les compter.
Sinon la sécurité reste un coût invisible qu'on finit par supprimer pour aller plus vite.
""",
    )

    # ===================================================================== #
    # Capstone
    # ===================================================================== #

    d.section(
        "12",
        "Capstone — du ticket au merge",
        "Assembler ce qui existe déjà : rien à réécrire",
        [
            "Une chaîne complète, démontrée devant le groupe",
            "Trois barrières qui tiennent, dont une prouvée en direct",
            "Un chiffre",
        ],
        notes="""
55 minutes. Le message d'ouverture : « le capstone assemble, il ne construit pas ».
Tout ce qui est demandé existe déjà dans le dépôt de chacun depuis le Jour 1.
Annoncer immédiatement l'heure limite de commit : 17:15.
""",
    )

    d.workshop(
        "Capstone — la chaîne complète",
        ["55 min", "binômes"],
        [
            "**Entrée** : une issue déléguable (format de l'atelier 7), rédigée en 5 minutes",
            "**Instructions** : `AGENTS.md` + `CLAUDE.md` qui l'importe — une seule vérité",
            "**Exécution** : plan critiqué, puis implémentation avec les tests",
            "**Revue** : votre subagent critique du Jour 1 + votre agent `revue-api` du matin",
            "**Barrières** : hook `Stop` en local, gate de tests en CI, action irréversible bloquée",
            "**Mesure** : un chiffre — coût par tâche aboutie, ou temps humain de revue",
        ],
        objective="Démontrer une chaîne du ticket au merge dans laquelle chaque étape produit "
                  "un artefact vérifiable, et où au moins une barrière refuse une action en direct.",
        expected=[
            "Une PR avec plan, diff, tests et rapport de revue automatique",
            "Un refus démontré **devant le groupe**, pas raconté",
            "Un chiffre écrit dans la description de la PR",
        ],
        trap=[
            "Vouloir tout reconstruire : le capstone assemble, il ne construit pas.",
            "Une barrière jamais testée n'est pas une barrière. Provoquez le refus.",
        ],
        expert=[
            "Ajoutez un job CI d'évaluation **non bloquant** à côté des tests bloquants.",
            "Produisez le tableau coût / latence / qualité sur trois exécutions de la même tâche.",
        ],
        kicker="Capstone",
        notes="""
Circuler avec un seul objectif : que chaque binôme ait un refus démontrable à 17:15.
C'est le moment de la formation qui reste en mémoire six mois plus tard.
Rappels de temps : 16:45 « il reste 30 minutes », 17:10 « dernier commit ».
Choisir deux binômes pour la restitution dès 16:50, pour qu'ils s'y préparent.
""",
    )

    d.bullets(
        "Restitution — 17:20",
        [
            "Deux binômes, cinq minutes chacun, trois choses à montrer :",
            ("Une issue entre, une PR vérifiée sort", 1),
            ("Une action irréversible est **refusée en direct**", 1),
            ("Un chiffre : coût par tâche aboutie, ou temps humain de revue", 1),
            "Ce qu'on ne montre pas : des slides, un diff qu'on n'a pas exécuté, un « ça marche »",
        ],
        kicker="Capstone · restitution",
        size=15.5,
        notes="""
Tenir la règle « on montre, on ne raconte pas ». C'est ce qui distingue cette formation
d'une présentation d'outils. Un binôme qui n'a pas de refus à montrer présente ce qui bloque :
c'est aussi instructif, et souvent plus.
""",
    )

    # ===================================================================== #
    # Clôture
    # ===================================================================== #

    d.key_idea(
        "Un agent devient fiable non pas quand il se trompe moins,\n"
        "mais quand **se tromper devient détectable et bon marché**.",
        "C'est pourquoi ces deux jours parlent surtout de contexte, de permissions, de hooks, "
        "de tests et de mesure — et si peu de prompts.",
        kicker="Le mot de la fin",
        notes="""
Boucler explicitement avec le fil rouge annoncé au Jour 1 : la vérification est le goulot.
Tout ce qui a été construit sert à automatiser la détection, pas à améliorer la génération.
""",
    )

    d.two_col(
        "Plan 30 / 60 / 90 — ce que vous faites en rentrant",
        left={
            "title": "30 jours · votre dépôt",
            "color": COPILOT,
            "items": [
                "Committer `AGENTS.md` + `CLAUDE.md` court qui l'importe",
                "Un `settings.json` de permissions, avec un `deny` testé",
                "Deux hooks : formatage automatique et refus de conclure sur suite rouge",
                "Une skill sur votre procédure la plus répétée",
                "Mesurer une baseline `/context` et la noter",
            ],
        },
        right={
            "title": "60 / 90 jours · votre équipe",
            "color": VIOLET,
            "items": [
                "60 j : une revue automatisée en CI, non bloquante d'abord",
                "60 j : un serveur MCP interne — l'investissement mutualisé entre outils",
                "60 j : les quatre indicateurs, relevés chaque semaine",
                "90 j : délégation asynchrone sur une catégorie de tâches bien spécifiées",
                "90 j : un plugin d'équipe qui diffuse skills, hooks et agents",
            ],
        },
        kicker="Clôture · adoption",
        notes="""
Faire écrire à chacun UNE action pour lundi matin, à voix haute si le groupe s'y prête.
Insister sur l'ordre : les garde-fous avant l'échelle. Une équipe qui industrialise
la délégation sans barrières produit du volume non vérifiable, et le programme s'arrête au premier incident.
""",
    )

    d.checklist(
        "Ce que vous emportez",
        [
            "Un dépôt configuré : instructions, permissions, hooks, MCP",
            "Une skill, un subagent critique, deux custom agents Copilot",
            "Une chaîne CI avec revue automatisée et gates",
            "Un composant frontend vérifié par capture de référence",
            "Une mesure comparée sur l'orchestration multi-agents",
            "Les guides d'atelier pas-à-pas, réutilisables en interne",
            "Le starter-kit : gabarits prêts à copier dans vos dépôts",
            "Quatre indicateurs présentables à votre management",
            "Une grille de décision : quelle surface pour quelle tâche",
            "Un plan 30/60/90 écrit de votre main",
        ],
        kicker="Clôture",
        lead="Les supports, les guides d'atelier et le starter-kit sont à vous : ils sont conçus "
             "pour être rejoués en interne, module par module.",
        notes="""
Terminer sur le fait que la formation est rejouable : les guides d'atelier sont autonomes.
Encourager chacun à animer un module chez lui dans les 30 jours — c'est le meilleur ancrage.
Distribuer la fiche d'évaluation et récupérer les fiches de suivi (elles contiennent les chiffres).
""",
    )

    d.bullets(
        "Pour continuer après la formation",
        [
            "**Documentation de référence** — `code.claude.com/docs` (skills, subagents, hooks, "
            "chrome, agent teams) et `docs.github.com/copilot` (custom agents, CLI, coding agent)",
            "**Le standard partagé** — `agents.md` : un seul fichier d'instructions pour tous les agents",
            "**Les guides d'atelier de cette formation** — autonomes, rejouables module par module "
            "en interne",
            "**Le starter-kit** — gabarits à copier : `AGENTS.md`, `settings.json`, skill, subagent, "
            "hooks, `.agent.md`, workflow CI",
            "**Le geste à garder** — avant chaque tâche : « quel est le critère de vérification ? ». "
            "S'il n'existe pas, on planifie au lieu de générer",
        ],
        kicker="Ressources",
        size=14.5,
        notes="""
Terminer sur la dernière puce : c'est la seule chose qui reste si tout le reste est oublié.
Les noms de produits et les commandes changeront ; la question du critère de vérification, non.
Rappeler que les décks sont générés par script : le support est maintenable et regénérable.
""",
    )

    return d.save(path)

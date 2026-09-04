"""Génère les deux supports PPTX de la formation.

    python build.py [dossier_de_sortie]
"""

import sys
from pathlib import Path

import content_day1
import content_day2

DECKS = [
    (content_day1, "Jour1-Claude-Code-Agentique.pptx"),
    (content_day2, "Jour2-Copilot-Orchestration-SDLC.pptx"),
]


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent.parent / "slides"
    out.mkdir(parents=True, exist_ok=True)
    for module, filename in DECKS:
        path = module.build(str(out / filename))
        from pptx import Presentation

        n = len(Presentation(path).slides)
        print(f"{filename:<44} {n:>3} slides")


if __name__ == "__main__":
    main()

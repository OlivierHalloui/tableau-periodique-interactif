# Tableau périodique interactif — Chimie Informatique

Application web interactive du tableau périodique de Mendeleïev, développée dans le cadre du Master 1 Chimie Informatique.

**Auteur : Saloua EL FAKIR**

---

## Présentation

Tableau périodique interactif orienté chimie computationnelle, construit avec [Dash](https://dash.plotly.com/) (Plotly) et Python. L'interface permet d'explorer les 118 éléments avec des données adaptées à la modélisation moléculaire.

### Fonctionnalités

- **Visualisation** — grille interactive, cases uniformes, code couleur par famille chimique
- **Filtres** — par groupe, bloc orbital (s/p/d/f), traitement ECP, recherche par nom ou symbole
- **Panneau de détail** (clic sur un élément) :
  - Structure électronique : états d'oxydation, multiplicité de spin (2S+1), IE₁, affinité électronique
  - Propriétés atomiques : polarisabilité α, rayon de van der Waals, volume molaire
  - Données computationnelles : traitement ECP, basis sets recommandés, pseudopotentiel, fonctionnelle DFT, correction de dispersion D3BJ, effets relativistes
- **Lien direct** vers [Basis Set Exchange](https://www.basissetexchange.org/)

---

## Installation

```bash
git clone https://github.com/OlivierHalloui/tableau-periodique-interactif.git
cd tableau-periodique-interactif
python -m venv .venv
source .venv/bin/activate      # Windows : .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Ouvrir `http://127.0.0.1:8050` dans le navigateur.

---

## Stack technique

| Composant | Version |
|---|---|
| Python | 3.12 |
| Dash | 2.18.2 |
| Plotly | 5.17.0 |
| Pandas | 2.2.3 |

---

## Sources des données

- Énergies d'ionisation, affinités électroniques : [NIST Atomic Spectra Database](https://www.nist.gov/pml/atomic-spectra-database)
- Masses atomiques, configurations : [IUPAC 2021](https://iupac.org/)
- Rayons de van der Waals : Bondi (1964), Alvarez (2013)
- Polarisabilités : CRC Handbook of Chemistry and Physics
- Pseudopotentiels : [Stuttgart/Cologne ECP library](https://www.tc.uni-koeln.de/PP/index.en.html)
- Basis sets : [Basis Set Exchange](https://www.basissetexchange.org/)

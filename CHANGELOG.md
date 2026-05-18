# CHANGELOG — СПЕКТР

> *Système Périodique des Éléments pour les Calculs Quantico-chimiques Théoriques et les Recommandations*
> *Система Периодических Элементов, Квантовохимических Теоретических Расчётов*

---

## [V4.0] — 2026-05-18 — СПЕКТР

### Renommage
- L'application est renommée **СПЕКТР** (acronyme bilingue FR/RU)
- Mise à jour du titre dans l'UI, `translations.py`, `README.md`, `SOUTENANCE_V3.md`

### 8 nouvelles fonctionnalités (nouveaux onglets)

| Onglet | Description |
|--------|-------------|
| **Coût CPU/RAM** | Estimation du temps et de la RAM selon la méthode, la base et le nombre d'atomes (loi de scaling N^p, 3 plateformes : laptop / workstation / HPC) |
| **HPC Script** | Génération de scripts de soumission SLURM, PBS ou SGE pour ORCA |
| **Solvant** | Mots-clés PCM/CPCM/SMD pour 15 solvants courants (ORCA, Gaussian, PySCF) |
| **Champ de ligand** | Diagramme de splitting des niveaux d, remplissage électronique haut/bas spin, calcul CFSE |
| **Benchmark** | Comparaison de précision (MAD) sur GMTKN55, S22, W4-17, BARRIER pour ~15 méthodes |
| **Parser sortie** | Extraction automatique depuis une sortie ORCA ou Gaussian : énergie, T₁, convergence SCF, gap HOMO-LUMO, charges Mulliken, fréquences |
| **DFT Map** | Carte interactive Jacob's Ladder — coût relatif vs MAD GMTKN55, 19 fonctionnelles |
| **SMILES** | Parsing SMILES via RDKit → formule brute + image 2D + recommandations de calcul |

### Nouvelles données JSON
- `data/scaling_data.json` — paramètres de scaling par méthode
- `data/solvents.json` — 15 solvants avec ε et mots-clés logiciels
- `data/hpc_templates.json` — templates SLURM / PBS / SGE
- `data/ligand_field.json` — géométries Oh/Td/D4h, métaux de transition, Δₒ typiques
- `data/benchmarks.json` — résultats GMTKN55, S22, W4-17, BARRIER (29 entrées)
- `data/dft_functionals.json` — 19 fonctionnelles sur la Jacob's Ladder

### Corrections scientifiques
- **Bloc La/Ac** : Z=57 (La) et Z=89 (Ac) reclassés bloc **d** (configuration d¹, IUPAC) — étaient incorrectement en bloc f
- **T₁ diagnostic** : avertissement ajouté dans les recommandations CCSD(T) sur bloc d/f (T₁ > 0.02 → multiréférence)
- **Sélection de basis** : priorité à la plage la plus étroite — corrige le bug lanthanides (def2 au lieu de SARC)
- **Espace actif CASSCF** : dynamique selon le bloc (d → (n,5), f → (n,7)) au lieu de (2,2) figé
- **Orbitales** : disclaimer hydrogénoïde ajouté + cache `lru_cache` + résolution grille 35³ → 50³
- **Normalisation radar** : correctif `IndexError` dans le comparateur (dict `{z: val}`)
- **Assistant moléculaire** : champs charge et multiplicité ajoutés, pris en compte dans les recommandations
- **Validation `recommend()`** : `ValueError` explicite si method_key ou prop_key inconnu
- **Doublon Yb** : supprimé de `_SYMBOLS_SORTED` dans `molecule_assistant.py`
- **`_block_for_z`** : supprimé de `molecule_assistant.py`, remplacé par import depuis `data_loader.py`

### Tests
- **241 tests pytest** (0 en V3.1)
- 11 fichiers de tests nouveaux couvrant : `recommendation_engine`, `input_generator`, `molecule_assistant`, `cost_estimator`, `hpc_generator`, `solvation`, `ligand_field`, `benchmark`, `output_parser`, `dft_map`, `smiles_tab`

### Dépendances
- `rdkit >= 2023.3.1` ajouté à `requirements.txt`

---

## [V3.1] — 2026-05-17

- Correction des callbacks Dash en architecture multi-pages (IDs dupliqués)
- Stabilisation du graphique radar dans le comparateur d'éléments

---

## [V3.0] — 2026-05-16

- Migration vers l'architecture multi-pages Dash (`use_pages=True`)
- 4 pages : Tableau, Tendances, Comparateur, Orbitales 3D
- API REST `/api/v1/*` (éléments, recommandations, inputs, RMN)
- Moteur de recommandations `recommendation_engine.py`
- Générateur de fichiers d'entrée ORCA / Gaussian / PySCF
- Assistant moléculaire (parsing formule + recommandation multi-éléments)
- Visualisation 3D des orbitales hydrogénoïdes (Plotly Volume)
- Comparateur d'éléments (radar normalisé + tableau)
- Interface bilingue FR / RU avec bascule instantanée

---

## [V2.0] — 2026-05-15

- Refonte complète de l'interface (thème sombre, CSS Grid)
- Ajout des données de chimie computationnelle (ECP, basis sets, fonctionnelles DFT)
- Internationalisation FR / RU
- Panneau de détails enrichi (RMN, orbitales, relativiste)

---

## [V1.0] — 2026-05-15

- Version initiale : tableau périodique interactif (118 éléments)
- Filtres groupe / période / recherche
- Code couleur par famille chimique
- Panneau de propriétés atomiques basiques

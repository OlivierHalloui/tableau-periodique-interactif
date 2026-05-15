# Интерактивная таблица Менделеева — Вычислительная химия
# Tableau périodique interactif — Chimie Informatique

**Автор / Auteur : Saloua EL FAKIR**
Магистратура 1-й год, Вычислительная химия / Master 1 Chimie Informatique

---

## Содержание / Sommaire

1. [Описание / Présentation](#описание)
2. [Функциональность / Fonctionnalités](#функциональность)
3. [Структура приложения / Architecture](#структура)
4. [Установка / Installation](#установка)
5. [Запуск / Lancement](#запуск)
6. [Использование / Utilisation](#использование)
7. [API REST](#api-rest)
8. [Технический стек / Stack technique](#стек)
9. [Источники данных / Sources des données](#источники)

---

## Описание

**RU :** Интерактивное веб-приложение таблицы Менделеева, разработанное в рамках учебного задания первого года магистратуры по вычислительной химии. Приложение объединяет в одном месте все данные, необходимые для квантово-химических расчётов: псевдопотенциалы, базисные наборы, функционалы DFT, мультиплетность спина, релятивистские поправки — а также инструменты для планирования расчётов: рекомендательный модуль, генератор входных файлов и 3D-визуализацию орбиталей.

Приложение доступно на двух языках — **русском и французском** — с мгновенным переключением без перезагрузки страницы.

**FR :** Application web interactive du tableau périodique de Mendeleïev, développée dans le cadre d'un devoir de Master 1 Chimie Informatique. Elle centralise toutes les données utiles aux calculs quantiques (pseudopotentiels, basis sets, fonctionnelles DFT, multiplicité de spin, effets relativistes) et propose des outils de planification : module de recommandation, générateur de fichiers d'entrée et visualisation 3D des orbitales.

L'application est disponible en **russe et en français**, avec bascule instantanée sans rechargement de page.

---

## Функциональность

**RU :**

### Onglet 1 — Таблица Менделеева
- 118 элементов в стандартной компоновке; лантаноиды и актиноиды — в отдельных строках (6\* и 7\*)
- Цветовое кодирование по химическому семейству с постоянной легендой
- Всплывающая подсказка: символ, название, Z, блок, IE₁
- Фильтры: группа, блок (s/p/d/f), тип ЭКП, поиск по названию или символу
- Несовпадающие элементы затемняются (14% непрозрачности) — контекст не теряется

### Панель «Свойства» (клик по элементу)
| Раздел | Данные |
|---|---|
| Электронная структура | Степени окисления, мультиплетность (2S+1), IE₁ (эВ), EA (эВ) |
| Атомные свойства | Поляризуемость α (Å³), радиус ВдВ (Å), молярный объём |
| Вычислительная химия | ЭКП, базисные наборы, псевдопотенциал, функционал DFT, дисперсия D3BJ, релятивистика |
| ЯМР | Активные изотопы (спин, распространённость, рекомендуемый базис) |
| Орбиталь | Тип ВЗМО, сложность для DFT, энергия остова 1s (РФЭС) |

### Панель «Рекомендации» (клик по элементу)
- Выбор метода расчёта: HF, DFT-GGA, DFT гибридный, мета-GGA, range-sep., MP2, CCSD(T), CASSCF/NEVPT2
- Выбор целевого свойства: геометрия, энергия, возбуждённые состояния, ЯМР, ЭПР, дисперсия, ионизация, спиновая плотность
- Автоматический подбор базисного набора, ЭКП, функционала, поправки на дисперсию и релятивистики
- Значки совместимых программ (ORCA, Gaussian, PySCF, ADF, Molpro…)
- Готовые сниппеты входных файлов ORCA и Gaussian
- Экспорт входного файла для ORCA / Gaussian 16 / PySCF одним кликом

### Молекулярный ассистент
- Ввод молекулярной формулы (H₂O, FeCl₃, Fe₂(SO₄)₃, комплексы…)
- Автоматический разбор формулы и определение тяжёлых атомов
- Рекомендация метода, базиса, ЭКП с учётом d- и f-блока

### Onglet 2 — Тенденции
- 10 периодических свойств: IE₁, EA, электроотрицательность, атомный радиус, радиус ВдВ, поляризуемость, плотность, температуры плавления/кипения, мультиплетность
- 3 режима отображения: по атомному номеру Z, по группе, по периоду
- Цветовое кодирование по блоку (s/p/d/f)

### Onglet 3 — Сравнение элементов
- Мультивыбор 2–4 элементов
- Радарная диаграмма (8 нормированных свойств)
- Сравнительная таблица с числовыми значениями

### Onglet 4 — 3D-орбитали
- Визуализация водородоподобных атомных орбиталей (n = 1–4)
- 14 орбиталей: 1s, 2s, 2p, 3s, 3p, 3d, 4s, 4p, 4d, 4f
- Изоповерхность |ψ|² методом объёмного рендеринга Plotly
- Квантовые числа n, ℓ, mℓ и число узлов

---

**FR :**

### Onglet 1 — Tableau périodique
- 118 éléments en disposition standard ; lanthanides et actinides en lignes séparées (6\* et 7\*)
- Code couleur par famille chimique, légende permanente
- Infobulle au survol : symbole, nom, Z, bloc, IE₁
- Filtres : groupe, bloc (s/p/d/f), traitement ECP, recherche par nom ou symbole
- Éléments non correspondants atténués (14 % opacité) — contexte préservé

### Panneau « Détails » (clic sur un élément)
| Section | Données |
|---|---|
| Structure électronique | États d'oxydation, multiplicité (2S+1), IE₁ (eV), EA (eV) |
| Propriétés atomiques | Polarisabilité α (Å³), rayon VdW (Å), volume molaire |
| Modélisation | ECP, basis sets, pseudopotentiel, fonctionnelle DFT, dispersion D3BJ, relativiste |
| RMN | Isotopes actifs (spin, abondance, basis set recommandé) |
| Orbital | Type HOMO, difficulté DFT, énergie cœur 1s (XPS) |

### Panneau « Recommandations » (clic sur un élément)
- Méthode : HF, DFT-GGA, DFT hybride, méta-GGA, séparation de portée, MP2, CCSD(T), CASSCF/NEVPT2
- Propriété cible : géométrie, énergie, états excités, RMN, RPE, dispersion, ionisation, densité de spin
- Sélection automatique du basis set, ECP, fonctionnelle, dispersion, relativiste
- Badges des logiciels compatibles avec liens officiels
- Snippets ORCA et Gaussian prêts à l'emploi
- Export fichier d'entrée ORCA / Gaussian 16 / PySCF en un clic

### Assistant moléculaire
- Saisie d'une formule moléculaire (H₂O, FeCl₃, Fe₂(SO₄)₃, complexes…)
- Analyse automatique et identification des atomes lourds
- Recommandation méthode, basis, ECP selon le bloc d/f détecté

### Onglet 2 — Tendances
- 10 propriétés : IE₁, EA, électronégativité, rayon atomique, rayon VdW, polarisabilité, densité, points de fusion/ébullition, multiplicité
- 3 vues : par numéro atomique Z, par groupe, par période
- Code couleur par bloc (s/p/d/f)

### Onglet 3 — Comparateur d'éléments
- Multi-sélection 2–4 éléments
- Radar normalisé (8 propriétés)
- Tableau comparatif numérique

### Onglet 4 — Orbitales 3D
- Visualisation des orbitales hydrogénoïdes (n = 1–4)
- 14 orbitales : 1s, 2s, 2p, 3s, 3p, 3d, 4s, 4p, 4d, 4f
- Isosurface |ψ|² par rendu volumique Plotly
- Nombres quantiques n, ℓ, mℓ et nombre de nœuds

---

## Структура

```
Mendeliev/
├── app.py                    # Point d'entrée Dash — layout + callbacks principaux
├── data_loader.py            # Chargement et validation des 118 éléments
├── recommendation_engine.py  # Moteur de recommandations (méthode, basis, ECP…)
├── input_generator.py        # Génération fichiers ORCA / Gaussian / PySCF
├── molecule_assistant.py     # Analyse formule moléculaire + recommandation
├── trends_tab.py             # Onglet Tendances (layout + callback)
├── comparator_tab.py         # Onglet Comparateur (layout + callback)
├── orbital_viewer.py         # Onglet Orbitales 3D (calcul + layout + callback)
├── api.py                    # Endpoints REST /api/v1/*
├── data/
│   ├── elements.json         # 118 éléments — propriétés atomiques complètes
│   ├── recommendations.json  # Règles basis sets, méthodes, fonctionnelles
│   ├── software.json         # Catalogue logiciels (ORCA, Gaussian, PySCF…)
│   ├── nmr_isotopes.json     # Isotopes RMN actifs par élément
│   ├── orbital_info.json     # Type HOMO, défi DFT, énergie XPS
│   └── compchem.json         # Paramètres vychislitelnaya khimiya
├── assets/
│   └── style.css             # Thème sombre, CSS Grid responsive
├── tests/
│   └── test_data_loader.py   # 65 tests pytest (masses, ECP, blocs, spin…)
├── Dockerfile                # Image Docker pour déploiement
├── render.yaml               # Configuration Render (gunicorn, 2 workers)
└── requirements.txt
```

**RU :** Приложение разбито на модули: `data_loader.py` отвечает за данные, `recommendation_engine.py` — за логику рекомендаций, каждый onglet — в отдельном файле. `app.py` связывает всё воедино. Данные хранятся в JSON-файлах в папке `data/`.

**FR :** Architecture modulaire : chaque onglet a son propre module. `app.py` est le point d'entrée qui importe et enregistre les callbacks de chaque module. Les données sont externalisées dans `data/`.

---

## Установка

**RU :** Требования: Python 3.10 или выше.

```bash

# Создать виртуальное окружение
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows

# Установить зависимости
pip install -r requirements.txt
```

---

## Запуск

```bash
python app.py
```

Открыть в браузере : **http://127.0.0.1:8050**

**RU :** Для продакшн-деплоя:

```bash
gunicorn app:server --bind 0.0.0.0:8050 --workers 2
```

**FR :** Pour un déploiement en production :

```bash
gunicorn app:server --bind 0.0.0.0:8050 --workers 2
```

---

## Использование

**RU :**

1. **Переключение языка** — кнопки **FR** / **RU** в правом верхнем углу заголовка.
2. **Таблица** — выберите фильтр или введите текст в поле поиска; несовпадающие элементы затемняются.
3. **Свойства элемента** — нажмите на ячейку таблицы; правая панель покажет подробные данные.
4. **Рекомендации** — перейдите на вкладку «Рекомендации», выберите метод и целевое свойство.
5. **Экспорт** — разверните раздел «Экспорт входного файла», выберите программу (ORCA / Gaussian / PySCF) и нажмите «Создать файл».
6. **Молекулярный ассистент** — разверните раздел внизу, введите формулу молекулы и нажмите «Анализировать».
7. **Тенденции** — перейдите на вкладку «Тенденции», выберите свойство и режим отображения.
8. **Сравнение** — перейдите на вкладку «Сравнение», выберите 2–4 элемента из списка.
9. **3D-орбитали** — перейдите на вкладку «3D-орбитали», выберите орбиталь в меню.

**FR :**

1. **Langue** — boutons **FR** / **RU** en haut à droite.
2. **Tableau** — choisissez un filtre ou saisissez dans la recherche.
3. **Détails** — cliquez sur une case ; le panneau de droite affiche les propriétés.
4. **Recommandations** — onglet « Recommandations », choisissez méthode et propriété cible.
5. **Export** — dépliez « Exporter le fichier d'entrée », choisissez le logiciel et cliquez « Générer ».
6. **Assistant moléculaire** — section en bas du tableau, saisissez une formule et cliquez « Analyser ».
7. **Tendances** — onglet « Tendances », choisissez la propriété et le mode d'affichage.
8. **Comparateur** — onglet « Comparateur », sélectionnez 2 à 4 éléments.
9. **Orbitales 3D** — onglet « Orbitales 3D », sélectionnez une orbitale dans le menu.

---

## API REST

Les endpoints suivants sont disponibles sur le serveur Dash :

| Endpoint | Description |
|---|---|
| `GET /api/v1/elements` | Liste compacte des 118 éléments |
| `GET /api/v1/elements/<z>` | Toutes les données pour l'élément Z |
| `GET /api/v1/recommend?z=&method=&prop=&lang=` | Recommandation complète |
| `GET /api/v1/methods?lang=` | Liste des méthodes disponibles |
| `GET /api/v1/properties?lang=` | Liste des propriétés disponibles |
| `GET /api/v1/nmr/<z>` | Isotopes RMN actifs pour l'élément Z |
| `GET /api/v1/input?z=&method=&prop=&software=` | Fichier d'entrée (texte brut) |

---

## Стек

| Компонент | Версия |
|---|---|
| Python | ≥ 3.10 |
| Dash | 2.18.2 |
| Plotly | 5.17.0 |
| Pandas | 2.2.3 |
| NumPy | ≥ 1.26 |
| qcelemental | ≥ 0.27 |
| periodictable | ≥ 1.6.1 |
| gunicorn | ≥ 21.2 |

---

## Источники данных

**RU :**
- Потенциалы ионизации и сродство к электрону : [NIST Atomic Spectra Database](https://www.nist.gov/pml/atomic-spectra-database)
- Атомные массы и электронные конфигурации : [IUPAC 2021](https://iupac.org/)
- Радиусы ван-дер-Ваальса : Бонди (1964), Альварес (2013)
- Статические поляризуемости : CRC Handbook of Chemistry and Physics
- Псевдопотенциалы ECP Stuttgart/MDF : [Кёльнский университет](https://www.tc.uni-koeln.de/PP/index.en.html)
- Базисные наборы : [Basis Set Exchange](https://www.basissetexchange.org/)
- Степени окисления : IUPAC Recommendations 2005
- Мультиплетность спина : правило Хунда + правило «дырок» для f-элементов
- ЯМР-данные изотопов : Harris et al., Pure Appl. Chem. 2002

**FR :**
- Énergies d'ionisation et affinités électroniques : [NIST Atomic Spectra Database](https://www.nist.gov/pml/atomic-spectra-database)
- Masses atomiques et configurations électroniques : [IUPAC 2021](https://iupac.org/)
- Rayons de van der Waals : Bondi (1964), Alvarez (2013)
- Polarisabilités statiques : CRC Handbook of Chemistry and Physics
- Pseudopotentiels ECP Stuttgart/MDF : [Université de Cologne](https://www.tc.uni-koeln.de/PP/index.en.html)
- Basis sets : [Basis Set Exchange](https://www.basissetexchange.org/)
- Degrés d'oxydation : IUPAC Recommendations 2005
- Multiplicités de spin : règle de Hund + règle des « trous » pour les éléments f
- Données RMN isotopiques : Harris et al., Pure Appl. Chem. 2002

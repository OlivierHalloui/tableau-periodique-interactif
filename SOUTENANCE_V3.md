# Советы по защите — V3 / Conseils pour la soutenance — V3

**RU :** Этот документ поможет подготовиться к устной защите веб-приложения **V3**.
По сравнению с V1.5 (модульная архитектура, 5 файлов) V3 — полноценное
многостраничное приложение с четырьмя страницами, REST API, движком рекомендаций
для вычислительной химии, генератором входных файлов ORCA/Gaussian/PySCF,
3D-визуализацией орбиталей и помощником по молекулам.

**FR :** Ce document aide à préparer la soutenance orale de l'application **V3**.
Par rapport à la V1.5 (architecture modulaire, 5 fichiers), la V3 est une application
multi-pages complète avec quatre pages, une API REST, un moteur de recommandations
en chimie computationnelle, un générateur de fichiers d'entrée ORCA/Gaussian/PySCF,
une visualisation 3D des orbitales et un assistant moléculaire.

---

## 1. Présentation de l'application — quoi dire / Презентация приложения — что говорить

**RU :** Начните с демонстрации в браузере. Покажите все четыре страницы, затем объясните
эволюцию от V1 до V3.

1. **Четыре страницы приложения:**
   - `/` — интерактивная таблица Менделеева с фильтрами, панелью сведений,
     движком рекомендаций и генератором входных файлов.
   - `/tendances` — графики тенденций (электроотрицательность, радиус, IE1…)
     по группам и периодам.
   - `/comparateur` — сравнение двух элементов по всем свойствам.
   - `/orbitales` — 3D-визуализация атомных орбиталей (1s → 4f)
     с изоповерхностью Plotly.

2. **Структура файлов** (показать в редакторе):
   ```
   app.py                  — точка входа, шапка, навигация, глобальные callbacks
   api.py                  — REST API (/api/v1/*)
   data_loader.py          — загрузка и обогащение данных из JSON
   recommendation_engine.py— движок рекомендаций (метод, базис, ECP)
   input_generator.py      — генератор файлов ORCA / Gaussian / PySCF
   molecule_assistant.py   — парсер формул + многоэлементные рекомендации
   orbital_viewer.py       — 3D-вычисление и рендеринг орбиталей
   comparator_tab.py       — layout и callbacks страницы сравнения
   trends_tab.py           — layout и callbacks страницы тенденций
   translations.py         — тексты FR/RU
   pages/
     tableau.py            — главная страница
     tendances.py          — страница тенденций
     comparateur.py        — страница сравнения
     orbitales.py          — страница орбиталей
   data/
     elements.json         — 118 элементов
     recommendations.json  — матрица метод × свойство
     software.json         — список ПО (ORCA, Gaussian, PySCF…)
     nmr_isotopes.json     — ЯМР-активные изотопы
     orbital_info.json     — параметры орбиталей
   ```

**FR :** Commencez par la démonstration dans le navigateur. Montrez les quatre pages,
puis expliquez l'évolution de la V1 à la V3.

1. **Les quatre pages de l'application :**
   - `/` — tableau périodique interactif avec filtres, panneau de détails,
     moteur de recommandations et générateur de fichiers d'entrée.
   - `/tendances` — graphiques de tendances (électronégativité, rayon, IE1…)
     par groupe et par période.
   - `/comparateur` — comparaison de deux éléments sur toutes leurs propriétés.
   - `/orbitales` — visualisation 3D des orbitales atomiques (1s → 4f)
     avec isosurface Plotly.

2. **Structure des fichiers** (montrer dans l'éditeur) :
   ```
   app.py                  — point d'entrée, en-tête, navigation, callbacks globaux
   api.py                  — API REST (/api/v1/*)
   data_loader.py          — chargement et enrichissement des données depuis JSON
   recommendation_engine.py— moteur de recommandations (méthode, base, ECP)
   input_generator.py      — générateur de fichiers ORCA / Gaussian / PySCF
   molecule_assistant.py   — parseur de formules + recommandations multi-éléments
   orbital_viewer.py       — calcul et rendu 3D des orbitales
   comparator_tab.py       — layout et callbacks de la page comparateur
   trends_tab.py           — layout et callbacks de la page tendances
   translations.py         — textes FR/RU
   pages/
     tableau.py            — page principale
     tendances.py          — page tendances
     comparateur.py        — page comparateur
     orbitales.py          — page orbitales
   data/
     elements.json         — 118 éléments
     recommendations.json  — matrice méthode × propriété
     software.json         — liste des logiciels (ORCA, Gaussian, PySCF…)
     nmr_isotopes.json     — isotopes actifs en RMN
     orbital_info.json     — paramètres des orbitales
   ```

---

## 2. Architecture — comment l'expliquer en 2 minutes / Архитектура — как объяснить за 2 минуты

**RU :** Используйте эту схему устно:

> «Приложение разделено на три горизонтальных слоя.
> **Слой данных** : `data_loader.py` читает JSON из папки `data/`,
> обогащает данные (тип ECP, рекомендованный базис) и предоставляет
> `build_dataframe()` и словарь `ELEMENTS_BY_Z`.
> **Вычислительный слой** : `recommendation_engine.py` выбирает метод,
> базис и ECP для пары (элемент, задача); `input_generator.py` превращает
> рекомендацию в готовый текст файла; `molecule_assistant.py` разбирает
> химические формулы и агрегирует рекомендации по нескольким элементам.
> `orbital_viewer.py` вычисляет волновые функции и строит изоповерхность.
> **Слой представления** : `pages/` + вспомогательные модули `*_tab.py`
> описывают layout и callbacks каждой страницы; `app.py` регистрирует
> глобальный layout, шапку, навигацию и REST API.»

Нарисуйте на доске:

```
data/ (JSON) → data_loader.py → ELEMENTS_BY_Z / DataFrame
                      ↓
        recommendation_engine.py
        input_generator.py
        molecule_assistant.py
        orbital_viewer.py
                      ↓
   pages/tableau.py   pages/tendances.py   pages/comparateur.py   pages/orbitales.py
                      ↓
               app.py (use_pages=True)  +  api.py (Flask REST)
                      ↕  HTTP / JSON
                    БРАУЗЕР
```

**FR :** Utilisez ce schéma à l'oral :

> «L'application est divisée en trois couches horizontales.
> **Couche données** : `data_loader.py` lit les JSON du dossier `data/`,
> enrichit les données (type ECP, base recommandée) et fournit
> `build_dataframe()` et le dictionnaire `ELEMENTS_BY_Z`.
> **Couche calcul** : `recommendation_engine.py` sélectionne la méthode,
> la base et l'ECP pour un couple (élément, propriété) ;
> `input_generator.py` transforme la recommandation en fichier texte prêt
> à l'emploi ; `molecule_assistant.py` analyse les formules chimiques et
> agrège les recommandations pour plusieurs éléments.
> `orbital_viewer.py` calcule les fonctions d'onde et construit l'isosurface.
> **Couche présentation** : `pages/` + modules `*_tab.py` décrivent le layout
> et les callbacks de chaque page ; `app.py` enregistre le layout global,
> l'en-tête, la navigation et l'API REST.»

Dessinez au tableau :

```
data/ (JSON) → data_loader.py → ELEMENTS_BY_Z / DataFrame
                      ↓
        recommendation_engine.py
        input_generator.py
        molecule_assistant.py
        orbital_viewer.py
                      ↓
   pages/tableau.py   pages/tendances.py   pages/comparateur.py   pages/orbitales.py
                      ↓
               app.py (use_pages=True)  +  api.py (Flask REST)
                      ↕  HTTP / JSON
                   NAVIGATEUR
```

---

## 3. Questions probables sur le code et réponses / Вероятные вопросы по коду и ответы

---

### «Pourquoi passer des dictionnaires Python à des fichiers JSON ?» / «Зачем переходить от словарей Python к JSON-файлам?»

**RU :**
> «В V1.5 данные хранились непосредственно в Python-словарях в `data.py`.
> В V3 данные вынесены в JSON, потому что файл JSON можно редактировать
> без знания Python — важно при добавлении новых элементов или обновлении
> констант. Кроме того, один и тот же JSON потребляется и веб-интерфейсом
> (через `data_loader.py`) и REST API (через `api.py`) без дублирования.
> Наконец, `lru_cache` кэширует разобранный JSON в памяти при первом обращении —
> последующие запросы обходятся без IO.»

**FR :**
> «Dans la V1.5, les données étaient stockées directement dans des dictionnaires
> Python dans `data.py`. Dans la V3, les données sont déplacées en JSON parce qu'un
> fichier JSON peut être édité sans connaître Python — utile pour ajouter de nouveaux
> éléments ou mettre à jour des constantes. De plus, le même JSON est consommé
> à la fois par l'interface web (via `data_loader.py`) et par l'API REST (via
> `api.py`) sans duplication. Enfin, `lru_cache` met en cache le JSON parsé
> en mémoire au premier accès — les requêtes suivantes n'ont plus d'I/O.»

---

### «Qu'est-ce que l'API REST et pourquoi l'avoir ajoutée ?» / «Что такое REST API и зачем его добавили?»

**RU :**
> «REST API — это набор HTTP-эндпоинтов, зарегистрированных непосредственно
> на Flask-сервере Dash. Dash построен поверх Flask, поэтому `api.py` добавляет
> маршруты (`/api/v1/*`) к тому же серверу, что обслуживает веб-интерфейс.
> Это значит, что данные приложения доступны программно: другой скрипт,
> Jupyter-ноутбук или внешний инструмент может получить свойства элементов,
> рекомендации или сгенерированный входной файл одним HTTP-запросом.
> Приложение из учебного инструмента превращается в сервис.»

**Доступные маршруты:**
```
GET /api/v1/elements          → список 118 элементов (компактный)
GET /api/v1/elements/<z>      → все данные элемента Z
GET /api/v1/recommend?z=&method=&prop=&lang=  → рекомендация
GET /api/v1/methods?lang=     → список методов расчёта
GET /api/v1/properties?lang=  → список вычисляемых свойств
GET /api/v1/nmr/<z>           → ЯМР-активные изотопы
GET /api/v1/input?z=&method=&prop=&software=  → входной файл (текст)
```

**FR :**
> «L'API REST est un ensemble d'endpoints HTTP enregistrés directement sur le
> serveur Flask de Dash. Dash est construit au-dessus de Flask, donc `api.py`
> ajoute des routes (`/api/v1/*`) au même serveur qui sert l'interface web.
> Cela signifie que les données de l'application sont accessibles de manière
> programmatique : un autre script, un notebook Jupyter ou un outil externe peut
> obtenir les propriétés d'un élément, une recommandation ou un fichier d'entrée
> généré avec une seule requête HTTP. L'application passe d'un outil pédagogique
> à un service.»

**Routes disponibles :**
```
GET /api/v1/elements          → liste des 118 éléments (compacte)
GET /api/v1/elements/<z>      → toutes les données de l'élément Z
GET /api/v1/recommend?z=&method=&prop=&lang=  → recommandation
GET /api/v1/methods?lang=     → liste des méthodes de calcul
GET /api/v1/properties?lang=  → liste des propriétés calculables
GET /api/v1/nmr/<z>           → isotopes actifs en RMN
GET /api/v1/input?z=&method=&prop=&software=  → fichier d'entrée (texte)
```

---

### «Comment fonctionne le moteur de recommandations ?» / «Как работает движок рекомендаций?»

**RU :**
> «`recommendation_engine.py` получает три параметра: `z` (номер элемента),
> `method_key` (например `dft_hybrid`) и `prop_key` (например `geometry`).
> Движок определяет категорию базиса по номеру элемента (Z ≤ 18 → все электроны,
> Z ≤ 36 → ECP опционален и т.д.), читает матрицу метод × свойство из
> `recommendations.json` и выбирает оптимальный базис с учётом требований задачи.
> Результат — словарь с полями `method`, `basis`, `ecp`, `functional`,
> `dispersion`, `software` и текстовыми пояснениями на выбранном языке.
> `lru_cache` гарантирует, что JSON читается только один раз при старте.»

**FR :**
> «`recommendation_engine.py` reçoit trois paramètres : `z` (numéro de l'élément),
> `method_key` (ex. `dft_hybrid`) et `prop_key` (ex. `geometry`).
> Le moteur détermine la catégorie de base selon le numéro atomique (Z ≤ 18 →
> tous-électrons, Z ≤ 36 → ECP optionnel, etc.), lit la matrice méthode × propriété
> depuis `recommendations.json` et choisit la base optimale selon les exigences de
> la propriété. Le résultat est un dictionnaire avec les champs `method`, `basis`,
> `ecp`, `functional`, `dispersion`, `software` et des explications textuelles
> dans la langue choisie. `lru_cache` garantit que le JSON n'est lu qu'une seule
> fois au démarrage.»

---

### «Qu'est-ce que `lru_cache` et pourquoi l'utilisez-vous ?» / «Что такое `lru_cache` и зачем он нужен?»

**RU :**
> «`lru_cache` — стандартный декоратор Python из модуля `functools`.
> Он запоминает результат функции по её аргументам. Здесь он применяется к функциям
> чтения JSON: первый вызов `_load("recommendations.json")` открывает файл,
> разбирает JSON и сохраняет результат в кэш. Все последующие вызовы с тем же
> аргументом возвращают кэшированный объект без IO. Это особенно важно в Dash,
> где каждый пользовательский клик потенциально вызывает несколько callback-функций,
> каждая из которых могла бы читать один и тот же файл.»

**FR :**
> «`lru_cache` est un décorateur standard de Python du module `functools`.
> Il mémorise le résultat d'une fonction selon ses arguments. Il est appliqué ici
> aux fonctions de lecture JSON : le premier appel à `_load("recommendations.json")`
> ouvre le fichier, parse le JSON et stocke le résultat dans le cache. Tous les
> appels suivants avec le même argument retournent l'objet mis en cache sans I/O.
> C'est particulièrement important dans Dash, où chaque clic utilisateur peut
> déclencher plusieurs callbacks, chacun pouvant autrement lire le même fichier.»

---

### «Comment fonctionne le générateur de fichiers d'entrée ?» / «Как работает генератор входных файлов?»

**RU :**
> «`input_generator.py` содержит функцию `generate_input(software, el, method, prop,
> basis, ecp, functional, dispersion)`. Она принимает рекомендацию из движка
> и форматирует её в синтаксис выбранного программного обеспечения.
> Для ORCA — блок ключевых слов `! ... OPT` с секцией `%basis`.
> Для Gaussian — строка `#P B3LYP/def2-TZVP ...`.
> Для PySCF — Python-код с блоком `mol.basis`.
> Это позволяет скопировать файл и запустить расчёт напрямую.»

**FR :**
> «`input_generator.py` contient la fonction `generate_input(software, el, method,
> prop, basis, ecp, functional, dispersion)`. Elle reçoit la recommandation du moteur
> et la formate dans la syntaxe du logiciel choisi.
> Pour ORCA — un bloc de mots-clés `! ... OPT` avec une section `%basis`.
> Pour Gaussian — une ligne `#P B3LYP/def2-TZVP ...`.
> Pour PySCF — du code Python avec un bloc `mol.basis`.
> Cela permet de copier le fichier généré et de lancer le calcul directement.»

---

### «Qu'est-ce que l'assistant moléculaire ?» / «Что такое помощник по молекулам?»

**RU :**
> «`molecule_assistant.py` разбирает химическую формулу (например `Fe2(CO)5`)
> с помощью регулярных выражений, чтобы извлечь все присутствующие элементы.
> Затем он вызывает движок рекомендаций для каждого элемента отдельно и
> агрегирует результаты по самому консервативному варианту (наибольший Z
> определяет требования к ECP). Это полезно для молекул с несколькими
> тяжёлыми атомами — пользователь вводит формулу, а не ищет элементы вручную.»

**FR :**
> «`molecule_assistant.py` analyse une formule chimique (ex. `Fe2(CO)5`) avec des
> expressions régulières pour en extraire tous les éléments présents.
> Il appelle ensuite le moteur de recommandations pour chaque élément séparément
> et agrège les résultats selon le choix le plus conservateur (le Z le plus élevé
> détermine les exigences en ECP). C'est utile pour les molécules avec plusieurs
> atomes lourds — l'utilisateur saisit la formule, sans chercher les éléments
> un par un.»

---

### «Comment fonctionnent les orbitales 3D ?» / «Как работает 3D-визуализация орбиталей?»

**RU :**
> «`orbital_viewer.py` вычисляет волновую функцию ψ_nlm (n, l, m — квантовые числа)
> на трёхмерной сетке NumPy. Радиальная часть R_nl вычисляется через полиномы Лагерра,
> угловая часть Y_lm — через сферические гармоники.
> Plotly строит изоповерхность через `go.Isosurface` — трёхмерную поверхность,
> где |ψ|² равно заданному порогу (обычно 85% от максимума).
> Пользователь выбирает орбиталь из списка (1s, 2p_z, 3d_z², 4f_z³…)
> и получает интерактивное 3D-изображение.»

**FR :**
> «`orbital_viewer.py` calcule la fonction d'onde ψ_nlm (n, l, m — nombres quantiques)
> sur une grille 3D NumPy. La partie radiale R_nl est calculée via les polynômes de
> Laguerre, la partie angulaire Y_lm via les harmoniques sphériques.
> Plotly construit l'isosurface via `go.Isosurface` — une surface 3D où |ψ|² est
> égal à un seuil donné (en général 85% du maximum).
> L'utilisateur choisit une orbitale dans la liste (1s, 2p_z, 3d_z², 4f_z³…)
> et obtient une visualisation 3D interactive.»

---

### «Pourquoi `suppress_callback_exceptions=True` dans `app.py` ?» / «Зачем `suppress_callback_exceptions=True` в `app.py`?»

**RU :**
> «В многостраничном приложении компоненты другой страницы физически отсутствуют
> в DOM при загрузке первой страницы. Без этого параметра Dash выбрасывал бы
> исключение при регистрации callback, чей `Output` или `Input` ещё не существует
> в DOM. `suppress_callback_exceptions=True` говорит Dash не проверять DOM
> при регистрации callback — проверка происходит только в момент вызова,
> когда нужная страница уже загружена.»

**FR :**
> «Dans une application multi-pages, les composants d'une autre page sont physiquement
> absents du DOM lors du chargement de la première page. Sans ce paramètre, Dash
> lèverait une exception à l'enregistrement d'un callback dont l'`Output` ou l'`Input`
> n'existe pas encore dans le DOM. `suppress_callback_exceptions=True` dit à Dash
> de ne pas vérifier le DOM à l'enregistrement des callbacks — la vérification
> n'a lieu qu'au moment de l'appel, quand la page concernée est déjà chargée.»

---

### «Qu'est-ce qu'un ECP et comment l'application le détermine-t-elle ?» / «Что такое ECP и как приложение его определяет?»

**RU :**
> «ECP (Effective Core Potential) — псевдопотенциал, заменяющий ядро и внутренние
> электроны тяжёлого атома математической функцией. Это ускоряет расчёт
> и частично учитывает релятивистские эффекты.
> В `data_loader.py` функция `_ecp_type(z)` назначает тип по диапазону Z :
> Z ≤ 18 → все электроны, Z 19–36 → ECP опционален, Z 37–54 → ECP рекомендован,
> Z 55–86 → ECP обязателен, Z > 86 → ECP/релятивист.
> `recommendation_engine.py` учитывает этот тип при выборе базисного набора.»

**FR :**
> «Un ECP (Effective Core Potential) est un pseudo-potentiel qui remplace le noyau
> et les électrons de cœur d'un atome lourd par une fonction mathématique.
> Cela accélère le calcul et prend partiellement en compte les effets relativistes.
> Dans `data_loader.py`, la fonction `_ecp_type(z)` attribue le type selon la plage
> de Z : Z ≤ 18 → tous-électrons, Z 19–36 → ECP optionnel, Z 37–54 → ECP
> recommandé, Z 55–86 → ECP requis, Z > 86 → ECP/relativiste.
> `recommendation_engine.py` tient compte de ce type lors du choix de la base.»

---

### «Pourquoi les pages délèguent-elles leur layout à des modules `*_tab.py` ?» / «Зачем страницы делегируют layout модулям `*_tab.py`?»

**RU :**
> «Файлы в папке `pages/` (например `pages/tendances.py`) содержат только
> `dash.register_page()` и импорт `layout` из соответствующего `*_tab.py`.
> Фактическое построение интерфейса вынесено в `trends_tab.py` и
> `comparator_tab.py`. Это разделение позволяет тестировать и разрабатывать
> layout независимо от системы маршрутизации Dash. Файлы в `pages/` —
> только «регистраторы», а не разработчики.»

**FR :**
> «Les fichiers dans `pages/` (ex. `pages/tendances.py`) contiennent seulement
> `dash.register_page()` et l'import du `layout` depuis le `*_tab.py` correspondant.
> La construction réelle de l'interface est déléguée à `trends_tab.py` et
> `comparator_tab.py`. Cette séparation permet de tester et développer le layout
> indépendamment du système de routage de Dash. Les fichiers `pages/` sont de
> simples « enregistreurs », pas des constructeurs.»

---

### «Comment fonctionne le partage d'état entre les pages (dcc.Store) ?» / «Как работает общее состояние между страницами (dcc.Store)?»

**RU :**
> «`app.py` объявляет несколько `dcc.Store` в глобальном layout :
> `lang` (выбранный язык), `selected-element-z` (Z выбранного элемента),
> `selected-element-block` (блок элемента) и `last-recommendation`.
> Эти Store существуют всегда, независимо от активной страницы.
> Callback на странице `/tendances` может читать `selected-element-z`,
> установленный на странице `/`, без какого-либо дополнительного механизма —
> данные хранятся в браузере как JSON и синхронизируются автоматически.»

**FR :**
> «`app.py` déclare plusieurs `dcc.Store` dans le layout global :
> `lang` (langue choisie), `selected-element-z` (Z de l'élément sélectionné),
> `selected-element-block` (bloc de l'élément) et `last-recommendation`.
> Ces Stores existent en permanence, quelle que soit la page active.
> Un callback sur la page `/tendances` peut lire `selected-element-z`
> défini depuis la page `/`, sans aucun mécanisme supplémentaire — les données
> sont stockées dans le navigateur en JSON et synchronisées automatiquement.»

---

## 4. Questions sur le CSS et réponses / Вопросы по CSS и ответы

---

### «Qu'est-ce qui a changé dans le CSS entre V1.5 et V3 ?» / «Что изменилось в CSS между V1.5 и V3?»

**RU :**
> «В V1.5 была одна сетка для таблицы + панель деталей.
> В V3 добавились: навигационная панель (`main-tabs-bar`) с четырьмя вкладками
> и классом `main-tab--selected` для активной вкладки; стили для страниц
> тенденций (графики в полную ширину) и сравнения (сетка 2 столбца);
> стили для REST-панели и блока генератора входных файлов.
> CSS остался единым файлом `assets/style.css` — Dash подгружает его
> автоматически.»

**FR :**
> «Dans la V1.5, il n'y avait qu'une seule grille pour le tableau + panneau de
> détails. Dans la V3, ont été ajoutés : une barre de navigation (`main-tabs-bar`)
> avec quatre onglets et la classe `main-tab--selected` pour l'onglet actif ;
> des styles pour les pages tendances (graphiques pleine largeur) et comparateur
> (grille 2 colonnes) ; des styles pour le panneau REST et le bloc générateur de
> fichiers d'entrée. Le CSS reste un fichier unique `assets/style.css` — Dash le
> charge automatiquement.»

---

### «Comment l'onglet actif est-il mis en évidence dans la navigation ?» / «Как выделяется активная вкладка в навигации?»

**RU :**
> «В `app.py` есть callback `update_active_nav`, который слушает `url.pathname`.
> При изменении URL он сравнивает `pathname` с путями каждой вкладки и
> назначает класс `main-tab main-tab--selected` активной вкладке и
> `main-tab` всем остальным. CSS задаёт отличие только визуально —
> нижняя граница и цвет. Это стандартный паттерн Dash для навигации.»

**FR :**
> «Dans `app.py`, le callback `update_active_nav` écoute `url.pathname`.
> Lors d'un changement d'URL, il compare le `pathname` avec les chemins de chaque
> onglet et attribue la classe `main-tab main-tab--selected` à l'onglet actif
> et `main-tab` à tous les autres. Le CSS ne définit qu'une différence visuelle
> — une bordure inférieure et une couleur. C'est le pattern standard Dash pour
> la navigation.»

---

## 5. Conseils généraux / Общие советы

**RU :**

- **Подчеркните масштаб проекта цифрами.**  
  *«V3 — это 3 028 строк Python, 4 страницы, 7 REST-маршрутов, 3 поддерживаемых
  программных пакета (ORCA, Gaussian, PySCF), данные для 118 элементов в 5 JSON-файлах
  и 3D-визуализация с изоповерхностями.»*

- **Объясните, почему вычислительная химия требует именно таких решений.**  
  Тяжёлые элементы требуют ECP — это не произвольный выбор, а физическое требование.
  Правильный базис меняет результат расчёта.

- **Если спросят про REST API** — скажите, что это открывает данные для Jupyter-ноутбуков
  и внешних скриптов без установки всего приложения.

- **Структура ответа на любой технический вопрос:**  
  1. Что это такое (одно предложение)  
  2. Зачем это нужно в данном проекте  
  3. Конкретный пример из кода

- **Если не знаете ответа** — скажите честно:  
  *«Точную спецификацию я сейчас не помню, но это можно проверить
  в документации Dash / NumPy / Plotly.»*

**FR :**

- **Soulignez l'ampleur du projet avec des chiffres.**  
  *«La V3 représente 3 028 lignes de Python, 4 pages, 7 routes REST, 3 logiciels
  supportés (ORCA, Gaussian, PySCF), des données pour 118 éléments dans 5 fichiers
  JSON et une visualisation 3D avec isosurfaces.»*

- **Expliquez pourquoi la chimie computationnelle impose ces choix.**  
  Les éléments lourds nécessitent des ECP — ce n'est pas un choix arbitraire, c'est
  une contrainte physique. La bonne base modifie le résultat du calcul.

- **Si on vous interroge sur l'API REST** — expliquez qu'elle ouvre les données
  aux notebooks Jupyter et aux scripts externes sans installer toute l'application.

- **Structure de réponse pour toute question technique :**  
  1. Ce que c'est (une phrase)  
  2. Pourquoi c'est utile dans ce projet  
  3. Un exemple concret tiré du code

- **Si vous ne connaissez pas la réponse** — dites-le honnêtement :  
  *«Je ne me souviens pas exactement de la spécification en ce moment, mais cela
  peut se vérifier dans la documentation de Dash / NumPy / Plotly.»*

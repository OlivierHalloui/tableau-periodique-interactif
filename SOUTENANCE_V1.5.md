# Советы по защите — V1.5 / Conseils pour la soutenance — V1.5

**RU :** Этот документ поможет подготовиться к устной защите веб-приложения **V1.5**.
Преподаватель оценивает три вещи: понимание кода, понимание CSS и умение объяснить
архитектуру приложения. V1.5 вводит модульную архитектуру — именно на это будут
направлены большинство вопросов.

**FR :** Ce document aide à préparer la soutenance orale de l'application web **V1.5**.
Le professeur évalue trois choses : la compréhension du code, la compréhension du CSS
et la capacité à expliquer l'architecture de l'application. La V1.5 introduit une
architecture modulaire — c'est sur ce point que porteront la majorité des questions.

---

## 1. Презентация приложения — что говорить / Présentation de l'application — quoi dire

**RU :** Начните с демонстрации, а не с объяснения. Покажите приложение в браузере, затем:

1. Объясните **что изменилось по сравнению с V1** (один абзац).  
   *«V1 содержала весь код в одном файле `app.py` — 1 314 строк. В V1.5
   я разделил приложение на пять специализированных файлов, каждый из которых
   отвечает только за одну задачу. Функциональность осталась идентичной,
   но код стал читаемым, тестируемым и расширяемым.»*

2. Покажите **структуру файлов** в редакторе:
   ```
   app.py            — точка входа (96 строк)
   data.py           — данные и вычисления (616 строк)
   translations.py   — тексты FR/RU
   figure.py         — построение графика
   pages/tableau.py  — страница + callback-функции
   ```

3. Продемонстрируйте **три главных действия** пользователя:
   - Фильтрация (выбрать блок f → затемнение остальных)
   - Клик по элементу → панель сведений
   - Переключение языка FR ↔ RU

**FR :** Commencez par la démonstration, pas par l'explication. Montrez l'application
dans le navigateur, puis :

1. Expliquez **ce qui a changé par rapport à la V1** (un paragraphe).  
   *«La V1 contenait tout le code dans un seul fichier `app.py` — 1 314 lignes.
   Dans la V1.5, j'ai séparé l'application en cinq fichiers spécialisés, chacun
   responsable d'une seule tâche. La fonctionnalité est restée identique, mais
   le code est devenu lisible, testable et extensible.»*

2. Montrez la **structure des fichiers** dans l'éditeur :
   ```
   app.py            — point d'entrée (96 lignes)
   data.py           — données et calculs (616 lignes)
   translations.py   — textes FR/RU
   figure.py         — construction du graphique
   pages/tableau.py  — page + fonctions callback
   ```

3. Démontrez les **trois actions principales** de l'utilisateur :
   - Filtrage (sélectionner le bloc f → assombrissement des autres)
   - Clic sur un élément → panneau de détails
   - Changement de langue FR ↔ RU

---

## 2. Структура кода — как объяснить за 2 минуты / Structure du code — comment l'expliquer en 2 minutes

**RU :** Используйте эту схему устно:

> «Приложение разделено на пять слоёв.
> **`data.py`** — хранит 118 элементов, вычисляет производные свойства и
> предоставляет `build_dataframe()`.
> **`translations.py`** — хранит все тексты интерфейса на двух языках.
> **`figure.py`** — строит график Plotly из DataFrame, принимает его как параметр.
> **`pages/tableau.py`** — описывает layout страницы и все callback-функции.
> **`app.py`** — точка входа: создаёт объект Dash, подключает store и шапку,
> регистрирует глобальные callbacks (язык, footer).»

Нарисуйте на доске:

```
data.py ──────→ figure.py
     ↘                ↓
translations.py → pages/tableau.py
                         ↓
               app.py (use_pages=True)
                         ↕  JSON / HTTP
                       БРАУЗЕР
```

**FR :** Utilisez ce schéma à l'oral :

> «L'application est divisée en cinq couches.
> **`data.py`** — stocke 118 éléments, calcule les propriétés dérivées et
> fournit `build_dataframe()`.
> **`translations.py`** — stocke tous les textes de l'interface dans les deux langues.
> **`figure.py`** — construit le graphique Plotly à partir d'un DataFrame, qu'il
> reçoit en paramètre.
> **`pages/tableau.py`** — décrit le layout de la page et toutes les fonctions callback.
> **`app.py`** — point d'entrée : crée l'objet Dash, connecte le store et l'en-tête,
> enregistre les callbacks globaux (langue, footer).»

Dessinez au tableau :

```
data.py ──────→ figure.py
     ↘                ↓
translations.py → pages/tableau.py
                         ↓
               app.py (use_pages=True)
                         ↕  JSON / HTTP
                      NAVIGATEUR
```

---

## 3. Вероятные вопросы по коду и ответы / Questions probables sur le code et réponses

---

### «Зачем разбивать монолит на модули?» / «Pourquoi diviser le monolithe en modules ?»

**RU :**
> «Монолитный `app.py` в 1 314 строк решал три задачи одновременно:
> хранение данных, построение интерфейса и логика обработки событий.
> При модульной архитектуре каждый файл решает одну задачу.
> Практические последствия: `data.py` можно тестировать без запуска Dash;
> `figure.py` можно заменить без изменения callback-функций;
> `translations.py` можно дополнить новым языком одной правкой.»

**FR :**
> «Le `app.py` monolithique de 1 314 lignes remplissait trois tâches simultanément :
> le stockage des données, la construction de l'interface et la logique de traitement
> des événements. Avec l'architecture modulaire, chaque fichier remplit une seule tâche.
> Conséquences pratiques : `data.py` peut être testé sans lancer Dash ;
> `figure.py` peut être remplacé sans modifier les callbacks ;
> `translations.py` peut être étendu à une nouvelle langue en une seule modification.»

---

### «Что такое `use_pages=True` в Dash?» / «Qu'est-ce que `use_pages=True` dans Dash ?»

**RU :**
> «`use_pages=True` активирует встроенную систему маршрутизации Dash 2.
> Dash автоматически сканирует папку `pages/`, импортирует каждый файл
> и регистрирует переменную `layout` как содержимое соответствующего маршрута.
> `dash.page_container` в `app.layout` — это точка монтирования, где Dash
> подставляет нужный layout в зависимости от URL.
> В V1.5 только одна страница (`/`), но архитектура уже готова к расширению.»

**Пример из `app.py`:**
```python
app = dash.Dash(__name__, use_pages=True)
# ...
dash.page_container   # в app.layout — сюда подставляется pages/tableau.py
```

**FR :**
> «`use_pages=True` active le système de routage intégré de Dash 2.
> Dash scanne automatiquement le dossier `pages/`, importe chaque fichier
> et enregistre la variable `layout` comme contenu de la route correspondante.
> `dash.page_container` dans `app.layout` est le point de montage où Dash
> insère le bon layout en fonction de l'URL.
> Dans la V1.5, il n'y a qu'une seule page (`/`), mais l'architecture est déjà
> prête à être étendue.»

**Exemple tiré de `app.py` :**
```python
app = dash.Dash(__name__, use_pages=True)
# ...
dash.page_container   # dans app.layout — c'est ici qu'est monté pages/tableau.py
```

---

### «Что такое `dash.register_page()` и зачем он нужен?» / «Qu'est-ce que `dash.register_page()` et à quoi sert-il ?»

**RU :**
> «`dash.register_page(__name__, path="/")` вызывается в начале каждого файла
> в папке `pages/`. Он сообщает Dash: «этот файл — страница, её URL — `/`,
> её имя — "Tableau".» `__name__` передаётся, чтобы Dash знал, из какого
> модуля регистрируется страница. Без этого вызова Dash не включит файл
> в маршрутизацию.»

**Из `pages/tableau.py`:**
```python
dash.register_page(__name__, path="/", name="Tableau", order=1)
```

**FR :**
> «`dash.register_page(__name__, path="/")` est appelé au début de chaque fichier
> dans le dossier `pages/`. Il indique à Dash : "ce fichier est une page, son URL
> est `/`, son nom est `Tableau`." `__name__` est passé pour que Dash sache depuis
> quel module la page est enregistrée. Sans cet appel, Dash n'inclurait pas le fichier
> dans le routage.»

**Tiré de `pages/tableau.py` :**
```python
dash.register_page(__name__, path="/", name="Tableau", order=1)
```

---

### «Почему `@callback` вместо `@app.callback`?» / «Pourquoi `@callback` plutôt que `@app.callback` ?»

**RU :**
> «В монолитном приложении все callback-функции находились в том же файле,
> что и объект `app`, поэтому `@app.callback` работал напрямую.
> В модульной архитектуре `pages/tableau.py` не имеет доступа к объекту `app`.
> `@callback` (без `app`) — это глобальный декоратор Dash 2, который
> регистрирует callback в реестре приложения независимо от того, где
> находится код. Объект `app` создаётся в `app.py`, но callback,
> определённые в `pages/tableau.py`, всё равно к нему привязываются.»

**Сравнение:**
```python
# V1 — нужен объект app
@app.callback(Output("periodic-figure", "figure"), ...)

# V1.5 — не нужен объект app
@callback(Output("periodic-figure", "figure"), ...)
```

**FR :**
> «Dans l'application monolithique, tous les callbacks se trouvaient dans le même
> fichier que l'objet `app`, donc `@app.callback` fonctionnait directement.
> Dans l'architecture modulaire, `pages/tableau.py` n'a pas accès à l'objet `app`.
> `@callback` (sans `app`) est un décorateur global de Dash 2 qui enregistre le
> callback dans le registre de l'application indépendamment de l'endroit où se trouve
> le code. L'objet `app` est créé dans `app.py`, mais les callbacks définis dans
> `pages/tableau.py` y sont quand même rattachés.»

**Comparaison :**
```python
# V1 — l'objet app est nécessaire
@app.callback(Output("periodic-figure", "figure"), ...)

# V1.5 — l'objet app n'est pas nécessaire
@callback(Output("periodic-figure", "figure"), ...)
```

---

### «Почему `build_periodic_figure` теперь принимает `df` как параметр?» / «Pourquoi `build_periodic_figure` reçoit maintenant `df` en paramètre ?»

**RU :**
> «В V1 функция `build_periodic_figure` использовала глобальную переменную `df`,
> определённую в том же файле. В V1.5 функция перенесена в `figure.py`,
> который не должен зависеть от глобального состояния другого модуля.
> Передача `df` как параметра делает функцию чистой: её результат зависит
> только от её аргументов. Это делает её тестируемой изолированно.»

**Из `figure.py`:**
```python
def build_periodic_figure(df: pd.DataFrame,
                          group_filter=None, block_filter=None, ...):
    # df явно передан — нет зависимости от глобального состояния
```

**FR :**
> «Dans la V1, la fonction `build_periodic_figure` utilisait la variable globale `df`
> définie dans le même fichier. Dans la V1.5, la fonction a été déplacée dans
> `figure.py`, qui ne doit pas dépendre de l'état global d'un autre module.
> Passer `df` en paramètre rend la fonction pure : son résultat dépend uniquement
> de ses arguments. Cela la rend testable de manière isolée.»

**Tiré de `figure.py` :**
```python
def build_periodic_figure(df: pd.DataFrame,
                          group_filter=None, block_filter=None, ...):
    # df est passé explicitement — aucune dépendance à l'état global
```

---

### «Что такое callback в Dash?» / «Qu'est-ce qu'un callback dans Dash ?»

**RU :**
> «Callback — это Python-функция, декорированная `@callback`. Декоратор
> принимает `Output` (что обновить), `Input` (что слушать) и опционально `State`
> (что читать без запуска callback). Когда значение `Input` меняется в браузере,
> Dash отправляет POST-запрос на сервер, вызывает функцию и возвращает результат
> в виде JSON. Браузер применяет обновление без перезагрузки страницы.»

**Пример из `pages/tableau.py`:**
```python
@callback(
    Output("periodic-figure", "figure"),
    Input("block-filter", "value"),
    Input("lang", "data"),
)
def update_graph(block_value, lang):
    return build_periodic_figure(_df, block_filter=block_value, lang=lang)
```

**FR :**
> «Un callback est une fonction Python décorée avec `@callback`. Le décorateur
> prend un `Output` (ce qu'il faut mettre à jour), un `Input` (ce qu'il faut écouter)
> et optionnellement un `State` (ce qu'il faut lire sans déclencher le callback).
> Quand la valeur d'un `Input` change dans le navigateur, Dash envoie une requête
> POST au serveur, appelle la fonction et renvoie le résultat en JSON. Le navigateur
> applique la mise à jour sans rechargement de page.»

**Exemple tiré de `pages/tableau.py` :**
```python
@callback(
    Output("periodic-figure", "figure"),
    Input("block-filter", "value"),
    Input("lang", "data"),
)
def update_graph(block_value, lang):
    return build_periodic_figure(_df, block_filter=block_value, lang=lang)
```

---

### «Почему лантаниды и актиниды расположены отдельно?» / «Pourquoi les lanthanides et les actinides sont-ils placés séparément ?»

**RU :**
> «В стандартном формате таблицы Менделеева лантаниды (57–71) и актиниды
> (89–103) выносятся в отдельные строки под основной таблицей, чтобы она
> не была слишком широкой. Я реализовал это, добавив дублирующие записи
> для La (Z=57) и Ac (Z=89) с `row=8` и `row=9` соответственно.
> Исходные записи с `row=6` и `row=7` показывают ячейку-заглушку.»

**FR :**
> «Dans le format standard du tableau périodique, les lanthanides (57–71) et les
> actinides (89–103) sont placés dans des rangées séparées sous le tableau principal,
> afin que celui-ci ne soit pas trop large. J'ai implémenté cela en ajoutant des
> entrées dupliquées pour La (Z=57) et Ac (Z=89) avec `row=8` et `row=9`
> respectivement. Les entrées originales avec `row=6` et `row=7` affichent
> une cellule placeholder.»

---

### «Почему данные в `data.py`, а не в CSV?» / «Pourquoi les données sont dans `data.py` et non dans un CSV ?»

**RU :**
> «Данные в `data.py` — это по-прежнему Python-словари, как в V1.
> Перенос в отдельный файл не меняет формат хранения, только место.
> Преимущество перед CSV: нет IO-операций при старте, нет зависимости
> от файловой системы, типы данных (float, None) сохраняются без
> преобразований. Приложение остаётся автономным — один `pip install`
> и оно готово к запуску.»

**FR :**
> «Les données dans `data.py` sont toujours des dictionnaires Python, comme dans la V1.
> Le déplacement dans un fichier séparé ne change pas le format de stockage, seulement
> l'emplacement. Avantage par rapport au CSV : aucune opération I/O au démarrage,
> aucune dépendance au système de fichiers, les types de données (float, None) sont
> conservés sans conversion. L'application reste autonome — un seul `pip install`
> et elle est prête à fonctionner.»

---

### «Как работает переключение языка?» / «Comment fonctionne le changement de langue ?»

**RU :**
> «`dcc.Store(id="lang")` хранит строку `"fr"` или `"ru"` в браузере.
> В `app.py` кнопки FR/RU запускают `toggle_lang`, который записывает
> новое значение в Store. Изменение Store автоматически запускает:
> `update_global_language` в `app.py` (заголовок, footer, кнопки)
> и `update_tableau_language` в `pages/tableau.py` (фильтры, легенда,
> панель деталей). Таким образом, один клик обновляет весь интерфейс
> через цепочку callbacks без перезагрузки страницы.»

**FR :**
> «`dcc.Store(id="lang")` stocke la chaîne `"fr"` ou `"ru"` dans le navigateur.
> Dans `app.py`, les boutons FR/RU déclenchent `toggle_lang`, qui écrit la nouvelle
> valeur dans le Store. Le changement du Store déclenche automatiquement :
> `update_global_language` dans `app.py` (en-tête, footer, boutons) et
> `update_tableau_language` dans `pages/tableau.py` (filtres, légende, panneau
> de détails). Ainsi, un seul clic met à jour toute l'interface via une chaîne
> de callbacks sans rechargement de page.»

---

## 4. Вопросы по CSS и ответы / Questions sur le CSS et réponses

---

### «Как вы реализовали адаптивную вёрстку?» / «Comment avez-vous implémenté le layout responsive ?»

**RU :**
> «Я использовал CSS Grid. Основная сетка задаётся как
> `grid-template-columns: 2fr 1fr` — таблица занимает две трети ширины,
> панель деталей — одну треть. Блок фильтров — `repeat(4, 1fr)`.
> Через `@media`-запросы при ширине менее 1 024 px обе сетки переключаются
> на одну колонку для читаемости на планшете.»

**FR :**
> «J'ai utilisé CSS Grid. La grille principale est définie avec
> `grid-template-columns: 2fr 1fr` — le tableau occupe deux tiers de la largeur,
> le panneau de détails un tiers. Le bloc de filtres est `repeat(4, 1fr)`.
> Via des `@media`-queries, en dessous de 1 024 px de largeur, les deux grilles
> passent à une colonne pour une meilleure lisibilité sur tablette.»

---

### «Почему вы использовали `!important` в CSS для выпадающих меню?» / «Pourquoi avez-vous utilisé `!important` en CSS pour les menus déroulants ?»

**RU :**
> «Dash генерирует собственные инлайн-стили для `dcc.Dropdown` через React.
> Эти инлайн-стили имеют более высокую специфичность, чем любой внешний класс.
> Без `!important` тёмная тема игнорировалась и текст оставался чёрным
> на тёмном фоне. Это известное ограничение Dash v2 при кастомизации Dropdown.»

**FR :**
> «Dash génère ses propres styles inline pour `dcc.Dropdown` via React.
> Ces styles inline ont une spécificité plus élevée que n'importe quelle classe
> externe. Sans `!important`, le thème sombre était ignoré et le texte restait
> noir sur fond sombre. C'est une limitation connue de Dash v2 lors de la
> personnalisation des Dropdown.»

---

### «Что означает `rgba(255,255,255,0.14)` у затемнённых элементов?» / «Que signifie `rgba(255,255,255,0.14)` pour les éléments assombris ?»

**RU :**
> «Я не меняю цвет ячейки при фильтрации — я меняю параметр `opacity`
> в `layout.shapes`. Значение `0.14` означает 14% непрозрачности:
> ячейка почти прозрачна, но структура таблицы остаётся видимой.
> Пользователь не теряет контекст расположения элементов.»

**FR :**
> «Je ne change pas la couleur de la cellule lors du filtrage — je modifie le
> paramètre `opacity` dans `layout.shapes`. La valeur `0.14` signifie 14%
> d'opacité : la cellule est presque transparente, mais la structure du tableau
> reste visible. L'utilisateur ne perd pas le contexte de position des éléments.»

---

## 5. Общие советы / Conseils généraux

**RU :**

- **Говорите про «зачем», а не только про «что».**  
  Не «я разделил код на файлы», а «я разделил код, *потому что* монолит
  в 1 314 строк невозможно тестировать по частям и трудно читать».

- **Подчеркните принцип единственной ответственности.**  
  *«Каждый файл отвечает за одну задачу — это принцип SRP из SOLID.
  Если нужно добавить новый язык, я трогаю только `translations.py`.
  Если нужно изменить график — только `figure.py`.»*

- **Если не знаете ответа** — скажите честно:  
  *«Точную спецификацию я сейчас не помню, но это можно проверить
  в документации Dash.»*

- **Покажите комментарии в коде.** В `data.py` они написаны на двух языках
  именно для объяснения логики преподавателю.

- **Структура ответа на любой технический вопрос:**  
  1. Что это такое (одно предложение)  
  2. Зачем это нужно в данном проекте  
  3. Конкретный пример из кода

**FR :**

- **Parlez du « pourquoi », pas seulement du « quoi ».**  
  Pas « j'ai séparé le code en fichiers », mais « j'ai séparé le code *parce que*
  un monolithe de 1 314 lignes est impossible à tester partiellement et difficile
  à lire ».

- **Soulignez le principe de responsabilité unique.**  
  *«Chaque fichier est responsable d'une seule tâche — c'est le principe SRP de
  SOLID. Si l'on veut ajouter une nouvelle langue, je ne touche que
  `translations.py`. Si l'on veut modifier le graphique — seulement `figure.py`.»*

- **Si vous ne connaissez pas la réponse** — dites-le honnêtement :  
  *«Je ne me souviens pas exactement de la spécification en ce moment, mais cela
  peut se vérifier dans la documentation de Dash.»*

- **Montrez les commentaires dans le code.** Dans `data.py`, ils sont écrits dans
  les deux langues précisément pour expliquer la logique au professeur.

- **Structure de réponse pour toute question technique :**  
  1. Ce que c'est (une phrase)  
  2. Pourquoi c'est utile dans ce projet  
  3. Un exemple concret tiré du code

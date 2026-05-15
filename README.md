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
7. [Технический стек / Stack technique](#стек)
8. [Источники данных / Sources des données](#источники)

---

## Описание

**RU :** Интерактивное веб-приложение таблицы Менделеева, разработанное в рамках учебного задания первого года магистратуры по вычислительной химии. Интерфейс ориентирован на задачи молекулярного моделирования: в первую очередь отображаются данные, необходимые для квантово-химических расчётов (псевдопотенциалы, базисные наборы, мультиплетность спина, потенциалы ионизации, релятивистские эффекты, поправки на дисперсию).

Приложение доступно на двух языках — **русском и французском** — с мгновенным переключением без перезагрузки страницы.

**FR :** Application web interactive du tableau périodique de Mendeleïev, développée dans le cadre d'un devoir de Master 1 Chimie Informatique. L'interface est orientée modélisation moléculaire : elle affiche en priorité les données utiles aux calculs quantiques (pseudopotentiels, basis sets, multiplicité de spin, énergies d'ionisation, effets relativistes, correction de dispersion).

L'application est disponible en **russe et en français**, avec bascule instantanée sans rechargement de page.

---

## Функциональность

**RU :**

### Таблица Менделеева
- Все 118 элементов отображаются в стандартном формате периодической таблицы
- Лантаноиды и актиноиды вынесены в отдельные строки (6\* и 7\*)
- Цветовое кодирование по химическому семейству с постоянной легендой
- Атомный символ и номер Z отображаются в каждой ячейке
- Всплывающая подсказка при наведении: символ, название, Z, блок, IE₁

### Интерактивные фильтры
| Фильтр | Описание |
|---|---|
| **Группа** | Фильтрация по одной из 18 групп ИЮПАК |
| **Блок** | s / p / d / f — по типу заполняемой орбитали |
| **Обработка ЭКП** | Все электроны / ЭКП необязателен / рекомендуется / необходим / релятивистский |
| **Поиск** | По названию элемента (на активном языке) или символу |

Несовпадающие элементы затемняются (прозрачность 14%), совпадающие остаются яркими — контекст не теряется.

### Панель сведений (клик по элементу)

**Электронная структура**
- Степени окисления (актуальные для моделирования)
- Мультиплетность спинового основного состояния (2S+1) по правилу Хунда
- 1-й потенциал ионизации IE₁ (эВ) — источник NIST
- Сродство к электрону EA (эВ)

**Атомные свойства**
- Статическая поляризуемость α (Å³)
- Радиус ван-дер-Ваальса (Å) — Бонди 1964, Альварес 2013
- Молярный объём (см³/моль)

**Вычислительное моделирование**
- Тип обработки ЭКП (эффективный остовный потенциал)
- Рекомендуемые базисные наборы (cc-pVTZ, def2-TZVP, SARC-DKH2…)
- Псевдопотенциал Stuttgart/MDF
- Рекомендуемый DFT-функционал
- Поправка на дисперсию (D3BJ, Гримме)
- Релятивистские эффекты (уровень трактовки)

Прямая ссылка на [Basis Set Exchange](https://www.basissetexchange.org/) для загрузки базисных наборов.

### Двуязычный интерфейс
Кнопки **FR** / **RU** в заголовке переключают язык всего интерфейса:
- Названия элементов, заголовки разделов, подписи полей
- Метки фильтров и их варианты
- Легенда, подвал
- Поиск по названию работает на активном языке

---

**FR :**

### Tableau périodique
- 118 éléments en disposition standard, lanthanides et actinides en lignes séparées (6\* et 7\*)
- Code couleur par famille chimique avec légende permanente
- Infobulle au survol : symbole, nom, Z, bloc, IE₁

### Filtres interactifs
| Filtre | Description |
|---|---|
| **Groupe** | Filtrage par l'un des 18 groupes IUPAC |
| **Bloc** | s / p / d / f |
| **Traitement ECP** | Tous-électrons / ECP optionnel / recommandé / requis / relativiste |
| **Recherche** | Par nom (dans la langue active) ou symbole |

### Panneau de détails (clic sur un élément)
- *Structure électronique* : états d'oxydation, multiplicité de spin (2S+1), IE₁, EA
- *Propriétés atomiques* : polarisabilité α, rayon de van der Waals, volume molaire
- *Modélisation computationnelle* : ECP, basis sets, pseudopotentiel, fonctionnelle DFT, dispersion D3BJ, effets relativistes
- Lien direct vers Basis Set Exchange

### Interface bilingue FR / RU
Bascule instantanée sans rechargement — noms des éléments, libellés, filtres, légende.

---

## Структура

```
Mendeliev/
├── app.py              # Единственный файл приложения (~1 100 строк)
│   ├── ELEMENTS        # Список из 120 словарей (118 + La/Ac дублированы)
│   ├── _POLARISABILITE, _IE1, _EA, _SPIN_MULT, _VDW  # Данные вычхим
│   ├── _NAME_RU        # Русские названия 118 элементов
│   ├── LANG            # Словарь переводов FR/RU
│   ├── CATEGORY_COLORS # Цветовая палитра по семействам
│   ├── app.layout      # Структура интерфейса Dash
│   └── Callbacks (4)   # Реактивная логика
│       ├── toggle_lang            # FR ↔ RU
│       ├── update_ui_language     # Перевод всех строк интерфейса
│       ├── update_graph           # Перестройка таблицы по фильтрам
│       └── display_element_details # Панель сведений при клике
└── assets/
    └── style.css       # Тёмная тема, адаптивная вёрстка (CSS Grid)
```

**RU :** Приложение полностью автономно: все данные хранятся в Python-структурах внутри `app.py`, без базы данных и внешних API. Dash (надстройка над Flask) обрабатывает HTTP-запросы и JSON-сериализацию между браузером и сервером автоматически.

**FR :** L'application est entièrement autonome : toutes les données sont encodées en Python dans `app.py`, sans base de données ni API externe.

---

## Установка

**RU :** Требования: Python 3.10 или выше.

```bash
# Клонировать репозиторий
git clone https://github.com/OlivierHalloui/tableau-periodique-interactif.git
cd tableau-periodique-interactif

# Создать виртуальное окружение
python -m venv .venv

# Активировать окружение
source .venv/bin/activate          # Linux / macOS
# .venv\Scripts\activate           # Windows

# Установить зависимости
pip install -r requirements.txt
```

**FR :** Prérequis : Python 3.10 ou supérieur.

```bash
python -m venv .venv
source .venv/bin/activate          # Linux / macOS
# .venv\Scripts\activate           # Windows
pip install -r requirements.txt
```

---

## Запуск

```bash
python app.py
```

Открыть в браузере: **http://127.0.0.1:8050**

**RU :** Сервер запускается в режиме отладки (`debug=True`) с автоматической перезагрузкой при изменении файлов. Для продакшн-деплоя используйте Gunicorn:

```bash
gunicorn app:server -b 0.0.0.0:8050
```

**FR :** Le serveur démarre en mode debug avec rechargement automatique. Pour un déploiement en production, utilisez Gunicorn :

```bash
gunicorn app:server -b 0.0.0.0:8050
```

---

## Использование

**RU :**

1. **Переключение языка** — нажмите кнопку **FR** или **RU** в правом верхнем углу заголовка.
2. **Фильтрация** — выберите группу, блок или тип обработки ЭКП в выпадающих меню. Несовпадающие элементы затемняются.
3. **Поиск** — введите название элемента (на русском или французском) или его символ в поле поиска.
4. **Сброс фильтров** — нажмите × в выпадающем меню или сотрите текст из поля поиска.
5. **Сведения об элементе** — нажмите на любую ячейку таблицы; правая панель отобразит подробные данные.
6. **Basis Set Exchange** — в нижней части правой панели находится ссылка на базу данных базисных наборов.

**FR :**

1. **Langue** — cliquez sur **FR** ou **RU** en haut à droite.
2. **Filtres** — choisissez groupe, bloc ou traitement ECP dans les menus déroulants.
3. **Recherche** — saisissez un nom (dans la langue active) ou un symbole.
4. **Réinitialiser** — cliquez sur × dans le menu ou effacez le champ de recherche.
5. **Détails** — cliquez sur une case ; le panneau de droite affiche les propriétés complètes.
6. **Basis Set Exchange** — lien en bas du panneau de détails.

---

## Стек

| Компонент | Версия |
|---|---|
| Python | ≥ 3.10 |
| Dash | 2.18.2 |
| Plotly | 5.17.0 |
| Pandas | 2.2.3 |

---

## Источники данных

**RU :**
- Потенциалы ионизации и сродство к электрону: [NIST Atomic Spectra Database](https://www.nist.gov/pml/atomic-spectra-database)
- Атомные массы и электронные конфигурации: [IUPAC 2021](https://iupac.org/)
- Радиусы ван-дер-Ваальса: Бонди (1964), Альварес (2013)
- Статические поляризуемости: CRC Handbook of Chemistry and Physics
- Псевдопотенциалы ECP Stuttgart/MDF: [Кёльнский университет](https://www.tc.uni-koeln.de/PP/index.en.html)
- Базисные наборы: [Basis Set Exchange](https://www.basissetexchange.org/)
- Степени окисления: IUPAC Recommendations 2005
- Мультиплетность спина: правило Хунда + правило «дырок» для f-элементов

**FR :**
- Énergies d'ionisation et affinités électroniques : [NIST Atomic Spectra Database](https://www.nist.gov/pml/atomic-spectra-database)
- Masses atomiques et configurations électroniques : [IUPAC 2021](https://iupac.org/)
- Rayons de van der Waals : Bondi (1964), Alvarez (2013)
- Polarisabilités statiques : CRC Handbook of Chemistry and Physics
- Pseudopotentiels ECP Stuttgart/MDF : [Université de Cologne](https://www.tc.uni-koeln.de/PP/index.en.html)
- Basis sets : [Basis Set Exchange](https://www.basissetexchange.org/)

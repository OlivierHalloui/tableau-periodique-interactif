# Tableau périodique interactif — Chimie Informatique
# Интерактивная таблица Менделеева — Вычислительная химия

**Auteur / Автор : Saloua EL FAKIR**
Master 1 Chimie Informatique / Магистратура 1-й год, Вычислительная химия

---

## Présentation / Описание

**FR :** Application web interactive du tableau périodique de Mendeleïev, développée dans le cadre du Master 1 Chimie Informatique. L'interface est orientée chimie computationnelle : elle affiche en priorité les données utiles à la modélisation moléculaire (pseudopotentiels, basis sets, multiplicité de spin, énergies d'ionisation, effets relativistes…).

**RU :** Интерактивное веб-приложение таблицы Менделеева, разработанное в рамках первого года магистратуры по вычислительной химии. Интерфейс ориентирован на вычислительную химию: в первую очередь отображаются данные, необходимые для молекулярного моделирования (псевдопотенциалы, базисные наборы, мультиплетность спина, потенциалы ионизации, релятивистские эффекты…).

---

## Fonctionnalités / Функциональность

**FR :**
- Visualisation des 118 éléments avec code couleur par famille chimique et légende permanente
- Filtres interactifs : groupe, bloc orbital (s / p / d / f), traitement ECP, recherche par nom ou symbole
- Panneau de détail au clic sur un élément :
  - *Structure électronique* : états d'oxydation, multiplicité de spin (2S+1), 1ʳᵉ énergie d'ionisation (IE₁), affinité électronique (EA)
  - *Propriétés atomiques* : polarisabilité α (Å³), rayon de van der Waals (Å), volume molaire (cm³/mol)
  - *Modélisation computationnelle* : traitement ECP, basis sets recommandés, pseudopotentiel (Stuttgart/MDF), fonctionnelle DFT conseillée, correction de dispersion D3BJ, effets relativistes
- Lien direct vers [Basis Set Exchange](https://www.basissetexchange.org/)

**RU :**
- Отображение всех 118 элементов с цветовым кодированием по химическому семейству и постоянной легендой
- Интерактивные фильтры: группа, орбитальный блок (s / p / d / f), обработка ECP, поиск по названию или символу
- Панель детализации при клике на элемент:
  - *Электронная структура*: степени окисления, мультиплетность спина (2S+1), первый потенциал ионизации (IE₁), сродство к электрону (EA)
  - *Атомные свойства*: поляризуемость α (Å³), радиус ван-дер-Ваальса (Å), молярный объём (см³/моль)
  - *Вычислительное моделирование*: обработка ECP, рекомендуемые базисные наборы, псевдопотенциал (Stuttgart/MDF), рекомендуемый DFT-функционал, поправка на дисперсию D3BJ, релятивистские эффекты
- Прямая ссылка на [Basis Set Exchange](https://www.basissetexchange.org/)

---

## Installation / Установка

**FR :**
```bash
git clone https://github.com/OlivierHalloui/tableau-periodique-interactif.git
cd tableau-periodique-interactif
python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Ouvrir `http://127.0.0.1:8050` dans le navigateur.

**RU :**
```bash
git clone https://github.com/OlivierHalloui/tableau-periodique-interactif.git
cd tableau-periodique-interactif
python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Открыть `http://127.0.0.1:8050` в браузере.

---

## Stack technique / Технический стек

| Composant / Компонент | Version |
|---|---|
| Python | 3.12 |
| Dash | 2.18.2 |
| Plotly | 5.17.0 |
| Pandas | 2.2.3 |

---

## Sources des données / Источники данных

**FR :**
- Énergies d'ionisation et affinités électroniques : [NIST Atomic Spectra Database](https://www.nist.gov/pml/atomic-spectra-database)
- Masses atomiques et configurations électroniques : [IUPAC 2021](https://iupac.org/)
- Rayons de van der Waals : Bondi (1964), Alvarez (2013)
- Polarisabilités statiques : CRC Handbook of Chemistry and Physics
- Pseudopotentiels ECP Stuttgart/MDF : [Université de Cologne](https://www.tc.uni-koeln.de/PP/index.en.html)
- Basis sets : [Basis Set Exchange](https://www.basissetexchange.org/)

**RU :**
- Потенциалы ионизации и сродство к электрону: [NIST Atomic Spectra Database](https://www.nist.gov/pml/atomic-spectra-database)
- Атомные массы и электронные конфигурации: [IUPAC 2021](https://iupac.org/)
- Радиусы ван-дер-Ваальса: Бонди (1964), Альварес (2013)
- Статические поляризуемости: CRC Handbook of Chemistry and Physics
- Псевдопотенциалы ECP Stuttgart/MDF: [Кёльнский университет](https://www.tc.uni-koeln.de/PP/index.en.html)
- Базисные наборы: [Basis Set Exchange](https://www.basissetexchange.org/)

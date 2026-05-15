# =============================================================================
# Tableau périodique interactif — Master 1 Chimie Informatique
# Интерактивная таблица Менделеева — 1-й год магистратуры, вычислительная химия
# Interactive Periodic Table — MSc Chemistry (Computational), Year 1
# =============================================================================

import dash
from dash import html, dcc, Input, Output, State, ctx, no_update
import plotly.graph_objs as go
import pandas as pd

from data_loader import ELEMENTS, CATEGORY_COLORS, COLOR_DEFAULT, build_dataframe
from recommendation_engine import recommend, list_methods, list_properties
from input_generator import generate_input
from molecule_assistant import recommend_for_molecule, parse_formula

# ─── Language dict ──────────────────────────────────────────────────────────

LANG = {
    "fr": {
        "title": "Tableau périodique interactif",
        "subtitle": "Propriétés atomiques, recommandations de méthodes de calcul (ECP, bases, fonctionnelles DFT), génération de fichiers d'entrée ORCA/Gaussian/PySCF, visualisation 3D des orbitales et comparateur d'éléments.",
        "detail_title": "Détails de l'élément",
        "click_hint": "Cliquez sur une case du tableau pour afficher les propriétés de l'élément.",
        "group_ph": "Filtrer par groupe",
        "group_label": "Groupe",
        "block_ph": "Filtrer par bloc",
        "ecp_ph": "Filtrer par traitement ECP",
        "search_ph": "Rechercher par nom ou symbole",
        "blocks": [
            {"label": "Bloc s  (alcalins, alcalino-terreux, H, He)", "value": "s"},
            {"label": "Bloc p  (non-métaux, halogènes, gaz nobles…)", "value": "p"},
            {"label": "Bloc d  (métaux de transition)", "value": "d"},
            {"label": "Bloc f  (lanthanides & actinides)", "value": "f"},
        ],
        "ecps": [
            {"label": "Tous-électrons (Z ≤ 18)", "value": "Tous-électrons"},
            {"label": "ECP optionnel (Z 19–36)", "value": "ECP optionnel"},
            {"label": "ECP recommandé (Z 37–54)", "value": "ECP recommandé"},
            {"label": "ECP requis (Z 55–86)", "value": "ECP requis"},
            {"label": "ECP / relativiste (Z ≥ 87)", "value": "ECP/relativiste"},
        ],
        "categories": {
            "métal alcalin": "Métal alcalin",
            "métal alcalino-terreux": "Métal alcalino-terreux",
            "lanthanide": "Lanthanide",
            "actinide": "Actinide",
            "métal de transition": "Métal de transition",
            "post-transition metal": "Métal post-transition",
            "métalloïde": "Métalloïde",
            "non-metal": "Non-métal",
            "halogène": "Halogène",
            "gaz noble": "Gaz noble",
            "métal": "Métal",
        },
        "ecp_values": {
            "Tous-électrons": "Tous-électrons",
            "ECP optionnel": "ECP optionnel",
            "ECP recommandé": "ECP recommandé",
            "ECP requis": "ECP requis",
            "ECP/relativiste": "ECP/relativiste",
        },
        "relat_values": {
            "Négligeable": "Négligeable",
            "Faible (optionnel)": "Faible (optionnel)",
            "Scalaire (DKH2 / ZORA)": "Scalaire (DKH2 / ZORA)",
            "Scalaire + spin-orbite partiel": "Scalaire + spin-orbite partiel",
            "Spin-orbite requis (X2C / 4c-DHF)": "Spin-orbite requis (X2C / 4c-DHF)",
        },
        "disp_values": {"D3BJ (Grimme)": "D3BJ (Grimme)", "N/A": "N/A"},
        "pseudo_none": "Aucun",
        "sec_electronic": "Structure électronique",
        "sec_atomic": "Propriétés atomiques",
        "sec_compchem": "Modélisation computationnelle",
        "lbl_ox": "États d'oxydation",
        "lbl_spin": "Multiplicité de spin (2S+1)",
        "lbl_ie1": "1ʳᵉ énergie d'ionisation",
        "lbl_ea": "Affinité électronique",
        "lbl_alpha": "Polarisabilité (α)",
        "lbl_vdw": "Rayon de van der Waals",
        "lbl_vol": "Volume molaire",
        "lbl_ecp": "Traitement ECP",
        "lbl_basis": "Basis sets recommandés",
        "lbl_pseudo": "Pseudopotentiel",
        "lbl_func": "Fonctionnelle DFT",
        "lbl_disp": "Correction de dispersion",
        "lbl_relat": "Effets relativistes",
        "lbl_group": "Groupe",
        "lbl_period": "Période",
        "lbl_block": "Bloc",
        "bse_link": "Basis Set Exchange →",
        "footer_data": "Données scientifiques : IUPAC, CRC Handbook, NIST · Basis Set Exchange (basissetexchange.org)",
        "footer_credit": "Développé par Saloua EL FAKIR — Master 1 Chimie Informatique",
        "hover_bloc": "Bloc",
        "na": "N/A",
        # Phase 2
        "tab_details": "Détails",
        "tab_reco": "Recommandations",
        "reco_method_ph": "Méthode de calcul",
        "reco_prop_ph": "Propriété cible",
        "reco_no_element": "← Cliquez sur un élément du tableau pour obtenir des recommandations.",
        "reco_no_filters": "Sélectionnez une méthode et une propriété cible.",
        "reco_basis_lbl": "Base",
        "reco_aux_lbl": "Base auxiliaire",
        "reco_ecp_lbl": "ECP / Pseudopotentiel",
        "reco_func_lbl": "Fonctionnelle",
        "reco_disp_lbl": "Correction de dispersion",
        "reco_relat_lbl": "Relativiste",
        "reco_software_lbl": "Logiciels compatibles",
        "reco_links_lbl": "Liens utiles",
        "reco_snippet_orca": "Exemple ORCA",
        "reco_snippet_gaussian": "Exemple Gaussian",
        "reco_notes_lbl": "Notes",
        "sec_nmr": "Isotopes RMN actifs",
        "no_nmr": "Aucun isotope RMN actif connu.",
        "sec_orbital": "Informations orbitales",
        "lbl_homo_type": "Type HOMO",
        "lbl_dft_challenge": "Défi DFT",
        "lbl_core_1s": "Énergie cœur 1s (XPS approx.)",
        "na_ecp": "Aucun (tous-électrons)",
        "free_badge": "Gratuit",
        "commercial_badge": "Commercial",
        # Phase 3 — nouveaux onglets
        "main_tab_table":  "Tableau",
        "main_tab_trends": "Tendances",
        "main_tab_comp":   "Comparateur",
        "main_tab_orb":    "Orbitales 3D",
        # Phase 3 — export input
        "export_title":     "Exporter le fichier d'entrée",
        "export_sw_ph":     "Logiciel cible",
        "export_btn":       "Générer le fichier",
        "export_no_reco":   "Générez d'abord une recommandation ci-dessus.",
        # Phase 3 — assistant molécule
        "mol_title":        "Assistant moléculaire",
        "mol_ph":           "Formule moléculaire (ex : H2O, FeCl3, Fe2(SO4)3)",
        "mol_btn":          "Analyser",
        "mol_no_result":    "Entrez une formule et cliquez sur Analyser.",
        "mol_method":       "Méthode suggérée",
        "mol_basis":        "Base suggérée",
        "mol_ecp":          "ECP",
        "mol_none":         "Aucun",
    },
    "ru": {
        "title": "Интерактивная таблица Менделеева",
        "subtitle": "Атомные свойства, рекомендации методов расчёта (ЭКП, базисные наборы, функционалы DFT), генерация входных файлов ORCA/Gaussian/PySCF, 3D-визуализация орбиталей и сравнение элементов.",
        "detail_title": "Свойства элемента",
        "click_hint": "Нажмите на ячейку таблицы, чтобы просмотреть свойства элемента.",
        "group_ph": "Фильтр по группе",
        "group_label": "Группа",
        "block_ph": "Фильтр по орбитальному блоку",
        "ecp_ph": "Фильтр по типу ЭКП",
        "search_ph": "Поиск по названию или символу",
        "blocks": [
            {"label": "Блок s  (щелочные, щёлочноземельные, H, He)", "value": "s"},
            {"label": "Блок p  (неметаллы, галогены, благородные газы…)", "value": "p"},
            {"label": "Блок d  (переходные металлы)", "value": "d"},
            {"label": "Блок f  (лантаноиды и актиноиды)", "value": "f"},
        ],
        "ecps": [
            {"label": "Все электроны (Z ≤ 18)", "value": "Tous-électrons"},
            {"label": "ЭКП не обязателен (Z 19–36)", "value": "ECP optionnel"},
            {"label": "ЭКП рекомендуется (Z 37–54)", "value": "ECP recommandé"},
            {"label": "ЭКП необходим (Z 55–86)", "value": "ECP requis"},
            {"label": "ЭКП / релятивистский (Z ≥ 87)", "value": "ECP/relativiste"},
        ],
        "categories": {
            "métal alcalin": "Щелочной металл",
            "métal alcalino-terreux": "Щёлочноземельный металл",
            "lanthanide": "Лантаноид",
            "actinide": "Актиноид",
            "métal de transition": "Переходный металл",
            "post-transition metal": "Постпереходный металл",
            "métalloïde": "Металлоид",
            "non-metal": "Неметалл",
            "halogène": "Галоген",
            "gaz noble": "Благородный газ",
            "métal": "Металл",
        },
        "ecp_values": {
            "Tous-électrons": "Все электроны",
            "ECP optionnel": "ЭКП не обязателен",
            "ECP recommandé": "ЭКП рекомендуется",
            "ECP requis": "ЭКП необходим",
            "ECP/relativiste": "ЭКП / релятивистский",
        },
        "relat_values": {
            "Négligeable": "Пренебрежимо малы",
            "Faible (optionnel)": "Слабые (учёт не обязателен)",
            "Scalaire (DKH2 / ZORA)": "Скалярные (DKH2 / ZORA)",
            "Scalaire + spin-orbite partiel": "Скалярные + частичный спин-орбитальный",
            "Spin-orbite requis (X2C / 4c-DHF)": "Требуется спин-орбитальный (X2C / 4c-DHF)",
        },
        "disp_values": {"D3BJ (Grimme)": "D3BJ (Гримме)", "N/A": "Н/П"},
        "pseudo_none": "Отсутствует",
        "sec_electronic": "Электронная структура",
        "sec_atomic": "Атомные свойства",
        "sec_compchem": "Данные вычислительной химии",
        "lbl_ox": "Степени окисления",
        "lbl_spin": "Мультиплетность основного состояния (2S+1)",
        "lbl_ie1": "1-й потенциал ионизации IE₁",
        "lbl_ea": "Сродство к электрону EA",
        "lbl_alpha": "Статическая поляризуемость α",
        "lbl_vdw": "Радиус ван-дер-Ваальса",
        "lbl_vol": "Молярный объём",
        "lbl_ecp": "Тип ЭКП",
        "lbl_basis": "Рекомендуемые базисные наборы",
        "lbl_pseudo": "Псевдопотенциал",
        "lbl_func": "Рекомендуемый функционал DFT",
        "lbl_disp": "Поправка на дисперсию",
        "lbl_relat": "Релятивистские эффекты",
        "lbl_group": "Группа",
        "lbl_period": "Период",
        "lbl_block": "Блок",
        "bse_link": "Basis Set Exchange →",
        "footer_data": "Данные: IUPAC, CRC Handbook, NIST · Basis Set Exchange (basissetexchange.org)",
        "footer_credit": "Разработано Салуа ЭЛЬ ФАКИР — Магистратура 1-й год, вычислительная химия",
        "hover_bloc": "Блок",
        "na": "Н/П",
        "tab_details": "Свойства",
        "tab_reco": "Рекомендации",
        "reco_method_ph": "Метод расчёта",
        "reco_prop_ph": "Целевое свойство",
        "reco_no_element": "← Нажмите на элемент в таблице для получения рекомендаций.",
        "reco_no_filters": "Выберите метод и целевое свойство.",
        "reco_basis_lbl": "Базис",
        "reco_aux_lbl": "Вспомогательный базис",
        "reco_ecp_lbl": "ЭКП / Псевдопотенциал",
        "reco_func_lbl": "Функционал",
        "reco_disp_lbl": "Поправка на дисперсию",
        "reco_relat_lbl": "Релятивистика",
        "reco_software_lbl": "Совместимые программы",
        "reco_links_lbl": "Полезные ссылки",
        "reco_snippet_orca": "Пример ORCA",
        "reco_snippet_gaussian": "Пример Gaussian",
        "reco_notes_lbl": "Заметки",
        "sec_nmr": "ЯМР-активные изотопы",
        "no_nmr": "Активных ЯМР-изотопов не обнаружено.",
        "sec_orbital": "Орбитальные сведения",
        "lbl_homo_type": "Тип ВЗМО",
        "lbl_dft_challenge": "Сложность для DFT",
        "lbl_core_1s": "Энергия остова 1s (РФЭС прибл.)",
        "na_ecp": "Отсутствует (все электроны)",
        "free_badge": "Бесплатно",
        "commercial_badge": "Коммерческий",
        "main_tab_table":  "Таблица",
        "main_tab_trends": "Тенденции",
        "main_tab_comp":   "Сравнение",
        "main_tab_orb":    "3D-орбитали",
        "export_title":    "Экспорт входного файла",
        "export_sw_ph":    "Программа",
        "export_btn":      "Создать файл",
        "export_no_reco":  "Сначала получите рекомендацию выше.",
        "mol_title":       "Молекулярный ассистент",
        "mol_ph":          "Молекулярная формула (пр: H2O, FeCl3, Fe2(SO4)3)",
        "mol_btn":         "Анализировать",
        "mol_no_result":   "Введите формулу и нажмите Анализировать.",
        "mol_method":      "Предлагаемый метод",
        "mol_basis":       "Предлагаемый базис",
        "mol_ecp":         "ЭКП",
        "mol_none":        "Нет",
    },
    "en": {
        "title": "Interactive Periodic Table",
        "subtitle": "Explore all 118 chemical elements with scientific properties and computational chemistry recommendations.",
        "detail_title": "Element Details",
        "click_hint": "Click an element in the table to display its properties.",
        "group_ph": "Filter by group",
        "group_label": "Group",
        "block_ph": "Filter by block",
        "ecp_ph": "Filter by ECP type",
        "search_ph": "Search by name or symbol",
        "blocks": [
            {"label": "s-block  (alkali, alkaline-earth, H, He)", "value": "s"},
            {"label": "p-block  (non-metals, halogens, noble gases…)", "value": "p"},
            {"label": "d-block  (transition metals)", "value": "d"},
            {"label": "f-block  (lanthanides & actinides)", "value": "f"},
        ],
        "ecps": [
            {"label": "All-electron (Z ≤ 18)", "value": "Tous-électrons"},
            {"label": "ECP optional (Z 19–36)", "value": "ECP optionnel"},
            {"label": "ECP recommended (Z 37–54)", "value": "ECP recommandé"},
            {"label": "ECP required (Z 55–86)", "value": "ECP requis"},
            {"label": "ECP / relativistic (Z ≥ 87)", "value": "ECP/relativiste"},
        ],
        "categories": {
            "métal alcalin": "Alkali Metal",
            "métal alcalino-terreux": "Alkaline Earth Metal",
            "lanthanide": "Lanthanide",
            "actinide": "Actinide",
            "métal de transition": "Transition Metal",
            "post-transition metal": "Post-transition Metal",
            "métalloïde": "Metalloid",
            "non-metal": "Non-metal",
            "halogène": "Halogen",
            "gaz noble": "Noble Gas",
            "métal": "Metal",
        },
        "ecp_values": {
            "Tous-électrons": "All-electron",
            "ECP optionnel": "ECP optional",
            "ECP recommandé": "ECP recommended",
            "ECP requis": "ECP required",
            "ECP/relativiste": "ECP / relativistic",
        },
        "relat_values": {
            "Négligeable": "Negligible",
            "Faible (optionnel)": "Weak (optional)",
            "Scalaire (DKH2 / ZORA)": "Scalar (DKH2 / ZORA)",
            "Scalaire + spin-orbite partiel": "Scalar + partial spin-orbit",
            "Spin-orbite requis (X2C / 4c-DHF)": "Spin-orbit required (X2C / 4c-DHF)",
        },
        "disp_values": {"D3BJ (Grimme)": "D3BJ (Grimme)", "N/A": "N/A"},
        "pseudo_none": "None",
        "sec_electronic": "Electronic Structure",
        "sec_atomic": "Atomic Properties",
        "sec_compchem": "Computational Chemistry",
        "lbl_ox": "Oxidation States",
        "lbl_spin": "Spin Multiplicity (2S+1)",
        "lbl_ie1": "1st Ionization Energy",
        "lbl_ea": "Electron Affinity",
        "lbl_alpha": "Polarizability (α)",
        "lbl_vdw": "Van der Waals Radius",
        "lbl_vol": "Molar Volume",
        "lbl_ecp": "ECP Treatment",
        "lbl_basis": "Recommended Basis Sets",
        "lbl_pseudo": "Pseudopotential",
        "lbl_func": "DFT Functional",
        "lbl_disp": "Dispersion Correction",
        "lbl_relat": "Relativistic Effects",
        "lbl_group": "Group",
        "lbl_period": "Period",
        "lbl_block": "Block",
        "bse_link": "Basis Set Exchange →",
        "footer_data": "Data: IUPAC, CRC Handbook, NIST · Basis Set Exchange (basissetexchange.org)",
        "footer_credit": "Developed by Saloua EL FAKIR — MSc Computational Chemistry, Year 1",
        "hover_bloc": "Block",
        "na": "N/A",
        "tab_details": "Details",
        "tab_reco": "Recommendations",
        "reco_method_ph": "Calculation method",
        "reco_prop_ph": "Target property",
        "reco_no_element": "← Click an element in the table to get recommendations.",
        "reco_no_filters": "Select a method and a target property.",
        "reco_basis_lbl": "Basis",
        "reco_aux_lbl": "Auxiliary basis",
        "reco_ecp_lbl": "ECP / Pseudopotential",
        "reco_func_lbl": "Functional",
        "reco_disp_lbl": "Dispersion correction",
        "reco_relat_lbl": "Relativistic",
        "reco_software_lbl": "Compatible software",
        "reco_links_lbl": "Useful links",
        "reco_snippet_orca": "ORCA example",
        "reco_snippet_gaussian": "Gaussian example",
        "reco_notes_lbl": "Notes",
        "sec_nmr": "NMR-active isotopes",
        "no_nmr": "No known NMR-active isotopes.",
        "sec_orbital": "Orbital information",
        "lbl_homo_type": "HOMO type",
        "lbl_dft_challenge": "DFT challenge",
        "lbl_core_1s": "Core 1s energy (XPS approx.)",
        "na_ecp": "None (all-electron)",
        "free_badge": "Free",
        "commercial_badge": "Commercial",
        "main_tab_table":  "Periodic Table",
        "main_tab_trends": "Trends",
        "main_tab_comp":   "Comparator",
        "main_tab_orb":    "3D Orbitals",
        "export_title":    "Export Input File",
        "export_sw_ph":    "Target software",
        "export_btn":      "Generate file",
        "export_no_reco":  "Generate a recommendation above first.",
        "mol_title":       "Molecule Assistant",
        "mol_ph":          "Molecular formula (e.g. H2O, FeCl3, Fe2(SO4)3)",
        "mol_btn":         "Analyse",
        "mol_no_result":   "Enter a formula and click Analyse.",
        "mol_method":      "Suggested method",
        "mol_basis":       "Suggested basis",
        "mol_ecp":         "ECP",
        "mol_none":        "None",
    },
}

# ─── App init ────────────────────────────────────────────────────────────────

app = dash.Dash(__name__)
server = app.server

df = build_dataframe()
df["color"] = df["category"].map(CATEGORY_COLORS).fillna(COLOR_DEFAULT)

ELEMENTS_BY_Z: dict[int, dict] = {}
for _el in ELEMENTS:
    _z = _el["atomic_number"]
    if _z not in ELEMENTS_BY_Z:
        ELEMENTS_BY_Z[_z] = _el

ELEMENTS_BY_SYM: dict[str, dict] = {el["symbol"]: el for el in ELEMENTS_BY_Z.values()}

_INIT_METHODS = list_methods("fr")
_INIT_PROPS   = list_properties("fr")

# Register REST API routes
from api import register_api_routes
register_api_routes(server, ELEMENTS_BY_Z)

# Import tab modules
from trends_tab   import create_trends_layout, register_callbacks as _reg_trends
from comparator_tab import create_comparator_layout, register_callbacks as _reg_comp
from orbital_viewer import create_orbital_layout, register_callbacks as _reg_orb

# ─── Layout ──────────────────────────────────────────────────────────────────

app.layout = html.Div(
    className="app-container",
    children=[
        dcc.Store(id="lang", data="fr"),
        dcc.Store(id="selected-element-z", data=None),
        dcc.Store(id="selected-element-block", data=None),
        # Stores recommendation result for the export feature
        dcc.Store(id="last-recommendation", data=None),
        html.Header(
            className="hero",
            children=[
                html.Div(
                    className="hero-top",
                    children=[
                        html.H1("Tableau périodique interactif", id="app-title"),
                        html.Div(
                            className="lang-toggle",
                            children=[
                                html.Button("FR", id="btn-fr", className="lang-btn active", n_clicks=0),
                                html.Button("RU", id="btn-ru", className="lang-btn", n_clicks=0),
                            ],
                        ),
                    ],
                ),
                html.P(
                    "Explorez les 118 éléments chimiques avec leurs propriétés scientifiques.",
                    id="app-subtitle",
                ),
            ],
        ),
        dcc.Tabs(
            id="main-tabs",
            value="tab-main",
            className="main-tabs-bar",
            children=[
                # ── Onglet 1 : Tableau ──────────────────────────────────────
                dcc.Tab(
                    label="Tableau",
                    value="tab-main",
                    id="main-tab-tableau",
                    className="main-tab",
                    selected_className="main-tab--selected",
                    children=[
                        html.Div(
                            className="controls-row",
                            children=[
                                dcc.Dropdown(
                                    id="group-filter",
                                    options=[{"label": f"Groupe {int(g)}", "value": int(g)} for g in sorted(df[df["row"] <= 7]["group"].unique())],
                                    placeholder="Filtrer par groupe",
                                    clearable=True,
                                    className="filter-dropdown",
                                ),
                                dcc.Dropdown(
                                    id="block-filter",
                                    options=[
                                        {"label": "Bloc s  (alcalins, alcalino-terreux, H, He)", "value": "s"},
                                        {"label": "Bloc p  (non-métaux, halogènes, gaz nobles…)", "value": "p"},
                                        {"label": "Bloc d  (métaux de transition)", "value": "d"},
                                        {"label": "Bloc f  (lanthanides & actinides)", "value": "f"},
                                    ],
                                    placeholder="Filtrer par bloc",
                                    clearable=True,
                                    className="filter-dropdown",
                                ),
                                dcc.Dropdown(
                                    id="ecp-filter",
                                    options=[
                                        {"label": "Tous-électrons (Z ≤ 18)", "value": "Tous-électrons"},
                                        {"label": "ECP optionnel (Z 19–36)", "value": "ECP optionnel"},
                                        {"label": "ECP recommandé (Z 37–54)", "value": "ECP recommandé"},
                                        {"label": "ECP requis (Z 55–86)", "value": "ECP requis"},
                                        {"label": "ECP / relativiste (Z ≥ 87)", "value": "ECP/relativiste"},
                                    ],
                                    placeholder="Filtrer par traitement ECP",
                                    clearable=True,
                                    className="filter-dropdown",
                                ),
                                dcc.Input(
                                    id="search-input",
                                    type="text",
                                    placeholder="Rechercher par nom ou symbole",
                                    className="search-input",
                                ),
                            ],
                        ),
                        html.Div(
                            id="legend-row",
                            className="legend-row",
                            children=[
                                html.Span([
                                    html.Span(className="legend-dot", style={"background": color}),
                                    html.Span(label, className="legend-label"),
                                ], className="legend-item")
                                for label, color in CATEGORY_COLORS.items()
                            ],
                        ),
                        html.Div(
                            className="main-grid",
                            children=[
                                html.Div(
                                    className="chart-card",
                                    children=[
                                        dcc.Graph(
                                            id="periodic-figure",
                                            config={"displayModeBar": False},
                                            className="periodic-graph",
                                        )
                                    ],
                                ),
                                html.Div(
                                    className="right-panel",
                                    children=[
                                        dcc.Tabs(
                                            id="right-tabs",
                                            value="tab-details",
                                            className="right-tabs",
                                            children=[
                                                dcc.Tab(
                                                    label="Détails",
                                                    value="tab-details",
                                                    id="tab-label-details",
                                                    className="panel-tab",
                                                    selected_className="panel-tab--selected",
                                                    children=[
                                                        html.Div(
                                                            className="detail-card",
                                                            children=[
                                                                html.H2("Détails de l'élément", id="detail-card-title"),
                                                                html.Div(
                                                                    id="element-details",
                                                                    className="details-content",
                                                                    children=[html.P("Cliquez sur une case du tableau.")],
                                                                ),
                                                            ],
                                                        ),
                                                    ],
                                                ),
                                                dcc.Tab(
                                                    label="Recommandations",
                                                    value="tab-reco",
                                                    id="tab-label-reco",
                                                    className="panel-tab",
                                                    selected_className="panel-tab--selected",
                                                    children=[
                                                        html.Div(
                                                            className="reco-card",
                                                            children=[
                                                                html.Div(
                                                                    className="reco-controls-row",
                                                                    children=[
                                                                        dcc.Dropdown(
                                                                            id="method-filter",
                                                                            options=_INIT_METHODS,
                                                                            placeholder="Méthode de calcul",
                                                                            clearable=True,
                                                                            optionHeight=40,
                                                                            className="filter-dropdown",
                                                                        ),
                                                                        dcc.Dropdown(
                                                                            id="prop-filter",
                                                                            options=_INIT_PROPS,
                                                                            placeholder="Propriété cible",
                                                                            clearable=True,
                                                                            optionHeight=40,
                                                                            className="filter-dropdown",
                                                                        ),
                                                                    ],
                                                                ),
                                                                html.Div(
                                                                    id="recommendations-output",
                                                                    className="reco-output",
                                                                    children=[html.P("← Cliquez sur un élément.", className="reco-hint")],
                                                                ),
                                                                # Export section
                                                                html.Hr(className="reco-separator"),
                                                                html.Details(
                                                                    className="export-section",
                                                                    children=[
                                                                        html.Summary(
                                                                            "Exporter le fichier d'entrée",
                                                                            id="export-summary",
                                                                            className="export-summary",
                                                                        ),
                                                                        html.Div(className="export-controls", children=[
                                                                            dcc.Dropdown(
                                                                                id="export-sw-select",
                                                                                options=[
                                                                                    {"label": "ORCA", "value": "orca"},
                                                                                    {"label": "Gaussian 16", "value": "gaussian"},
                                                                                    {"label": "PySCF (Python)", "value": "pyscf"},
                                                                                ],
                                                                                value="orca",
                                                                                clearable=False,
                                                                                className="filter-dropdown",
                                                                            ),
                                                                            html.Button(
                                                                                "Générer le fichier",
                                                                                id="export-btn",
                                                                                className="export-btn",
                                                                                n_clicks=0,
                                                                            ),
                                                                        ]),
                                                                        html.Pre(
                                                                            id="export-output",
                                                                            className="snippet-pre export-pre",
                                                                            children="Générez d'abord une recommandation ci-dessus.",
                                                                        ),
                                                                    ],
                                                                ),
                                                            ],
                                                        ),
                                                    ],
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        # Molecule assistant (below main grid, in the Tableau tab)
                        html.Details(
                            className="mol-assistant-section",
                            children=[
                                html.Summary(
                                    "Assistant moléculaire",
                                    id="mol-summary",
                                    className="export-summary",
                                ),
                                html.Div(className="mol-controls-row", children=[
                                    dcc.Input(
                                        id="mol-formula-input",
                                        type="text",
                                        placeholder="Formule moléculaire (ex : H2O, FeCl3)",
                                        className="search-input mol-input",
                                    ),
                                    dcc.Dropdown(
                                        id="mol-prop-select",
                                        options=_INIT_PROPS,
                                        value="geometry",
                                        clearable=False,
                                        className="filter-dropdown mol-prop-dd",
                                    ),
                                    html.Button(
                                        "Analyser",
                                        id="mol-analyse-btn",
                                        className="export-btn",
                                        n_clicks=0,
                                    ),
                                ]),
                                html.Div(id="mol-output", className="mol-output",
                                         children=[html.P("Entrez une formule et cliquez sur Analyser.", className="reco-hint")]),
                            ],
                        ),
                    ],
                ),
                # ── Onglet 2 : Tendances ────────────────────────────────────
                dcc.Tab(
                    label="Tendances",
                    value="tab-trends",
                    id="main-tab-trends",
                    className="main-tab",
                    selected_className="main-tab--selected",
                    children=[create_trends_layout()],
                ),
                # ── Onglet 3 : Comparateur ──────────────────────────────────
                dcc.Tab(
                    label="Comparateur",
                    value="tab-comp",
                    id="main-tab-comp",
                    className="main-tab",
                    selected_className="main-tab--selected",
                    children=[create_comparator_layout(df)],
                ),
                # ── Onglet 4 : Orbitales 3D ─────────────────────────────────
                dcc.Tab(
                    label="Orbitales 3D",
                    value="tab-orb",
                    id="main-tab-orb",
                    className="main-tab",
                    selected_className="main-tab--selected",
                    children=[create_orbital_layout()],
                ),
            ],
        ),
        html.Footer(
            className="footer",
            children=[
                html.P(id="footer-data",
                       children="Données scientifiques : IUPAC, CRC Handbook, NIST · Basis Set Exchange (basissetexchange.org)"),
                html.P(id="footer-credit",
                       className="footer-credit",
                       children="Développé par Saloua EL FAKIR — Master 1 Chimie Informatique"),
            ],
        ),
    ],
)


# ─── Register callbacks from sub-modules ────────────────────────────────────

_reg_trends(app, df)
_reg_comp(app, df)
_reg_orb(app)


# ─── Periodic figure ─────────────────────────────────────────────────────────

def build_periodic_figure(group_filter=None, block_filter=None, ecp_filter=None,
                          search_value="", lang="fr"):
    search_value = (search_value or "").strip().lower()
    is_match = pd.Series(True, index=df.index)

    if group_filter  is not None: is_match &= df["group"]    == group_filter
    if block_filter  is not None: is_match &= df["block"]    == block_filter
    if ecp_filter    is not None: is_match &= df["ecp_type"] == ecp_filter
    if search_value:
        name_col = "name_ru" if lang == "ru" else "name"
        is_match &= df.apply(
            lambda row: search_value in row[name_col].lower() or search_value in row["symbol"].lower(),
            axis=1,
        )

    customdata_cols = df[[
        "atomic_number", "symbol", "name", "group", "period",
        "block", "ecp_type", "basis_rec", "pseudo",
        "polarisabilite", "etats_ox", "volume_molaire",
        "ie1", "ea", "spin_mult", "vdw_radius",
        "functional", "dispersion", "relativistic", "name_ru",
    ]].values

    t = LANG[lang]
    name_idx = 19 if lang == "ru" else 2
    hover = (
        f"%{{customdata[1]}}<br>%{{customdata[{name_idx}]}}"
        f"<br>Z = %{{customdata[0]}} · {t['hover_bloc']} %{{customdata[5]}}"
        f"<br>IE₁ = %{{customdata[12]}} eV<extra></extra>"
    )

    fig = go.Figure()
    for idx, el in df.iterrows():
        matched = bool(is_match[idx])
        fig.add_shape(
            type="rect",
            x0=el["col"] - 0.46, x1=el["col"] + 0.46,
            y0=el["row"] - 0.46, y1=el["row"] + 0.46,
            fillcolor=el["color"],
            opacity=1.0 if matched else 0.14,
            line=dict(color="#1a2a33" if matched else "#37474f", width=1),
            layer="below",
        )

    fig.add_trace(go.Scatter(
        x=df["col"], y=df["row"],
        mode="markers+text",
        marker=dict(size=2, color="rgba(0,0,0,0)", symbol="square"),
        text=df["symbol"],
        textposition="middle center",
        textfont=dict(
            color=["rgba(255,255,255,1)" if m else "rgba(255,255,255,0.18)" for m in is_match],
            size=11, family="Inter",
        ),
        customdata=customdata_cols,
        hovertemplate=hover,
        showlegend=False,
    ))
    fig.add_trace(go.Scatter(
        x=df["col"] - 0.33, y=df["row"] - 0.33,
        mode="text",
        text=[str(int(n)) for n in df["atomic_number"]],
        textfont=dict(
            color=[f"rgba(255,255,255,{0.7 if m else 0.08})" for m in is_match],
            size=7, family="Inter",
        ),
        hoverinfo="skip", showlegend=False,
    ))

    for period in sorted(df[df["row"] <= 7]["period"].unique()):
        fig.add_annotation(x=0.3, y=period, xanchor="right", text=f"P{int(period)}",
                           showarrow=False, font=dict(color="#eceff1", size=11))
    fig.add_annotation(x=0.3, y=8, xanchor="right", text="6*", showarrow=False,
                       font=dict(color="#cfd8dc", size=10))
    fig.add_annotation(x=0.3, y=9, xanchor="right", text="7*", showarrow=False,
                       font=dict(color="#cfd8dc", size=10))

    fig.update_xaxes(title="", tickmode="array", tickvals=list(range(1, 19)),
                     ticktext=[str(n) for n in range(1, 19)], range=[0.5, 18.5],
                     showgrid=False, zeroline=False, showline=False,
                     tickfont=dict(color="#cfd8dc", size=10), fixedrange=True)
    fig.update_yaxes(title="", tickmode="array",
                     tickvals=[1,2,3,4,5,6,7,8,9],
                     ticktext=["1","2","3","4","5","6","7","6*","7*"],
                     range=[9.5, 0.5], showgrid=False, zeroline=False, showline=False,
                     tickfont=dict(color="#cfd8dc", size=10),
                     scaleanchor="x", scaleratio=1, fixedrange=True)
    fig.update_layout(
        plot_bgcolor="#102027", paper_bgcolor="#102027",
        margin=dict(l=20, r=20, t=15, b=25),
        hoverlabel=dict(bgcolor="#263238", font_size=12, font_family="Inter"),
        dragmode=False, showlegend=False, hoverdistance=40,
    )
    return fig


# ─── Callbacks ───────────────────────────────────────────────────────────────

@app.callback(
    Output("periodic-figure", "figure"),
    Input("group-filter", "value"),
    Input("block-filter", "value"),
    Input("ecp-filter", "value"),
    Input("search-input", "value"),
    Input("lang", "data"),
)
def update_graph(group_value, block_value, ecp_value, search_value, lang):
    return build_periodic_figure(group_value, block_value, ecp_value, search_value, lang or "fr")


@app.callback(
    Output("selected-element-z", "data"),
    Output("selected-element-block", "data"),
    Input("periodic-figure", "clickData"),
)
def update_selected_element(click_data):
    if not click_data or not click_data.get("points"):
        return no_update, no_update
    d = click_data["points"][0]["customdata"]
    return int(d[0]), d[5]


@app.callback(
    Output("element-details", "children"),
    Input("periodic-figure", "clickData"),
    Input("lang", "data"),
)
def display_element_details(click_data, lang):
    t = LANG[lang or "fr"]
    if not click_data or not click_data.get("points"):
        return [html.P(t["click_hint"])]

    d = click_data["points"][0]["customdata"]
    z, sym = int(d[0]), d[1]
    name = d[19] if lang == "ru" else d[2]
    group, period, block = int(d[3]), int(d[4]), d[5]

    def fmt(v, unit="", decimals=3):
        return f"{round(v, decimals)} {unit}".strip() if v is not None else t["na"]

    def section(title, rows):
        return html.Div(className="detail-section", children=[
            html.H4(title, className="detail-section-title"),
            html.Ul(className="detail-list", children=[
                html.Li([html.Strong(lbl + " : "), val]) for lbl, val in rows
            ]),
        ])

    ecp_val    = t["ecp_values"].get(d[6], d[6])
    relat_val  = t["relat_values"].get(d[18], d[18])
    disp_val   = t["disp_values"].get(d[17], d[17])
    pseudo_val = t["pseudo_none"] if d[8] == "Aucun" else d[8]

    result = [
        html.Div(className="detail-header", children=[
            html.H3(f"{name} ({sym})"),
            html.Span(
                f"Z = {z}  ·  {t['lbl_group']} {group}  ·  {t['lbl_period']} {period}  ·  {t['lbl_block']} {block}",
                className="detail-subtitle",
            ),
        ]),
        section(t["sec_electronic"], [
            (t["lbl_ox"], d[10]),
            (t["lbl_spin"], str(int(d[14])) if d[14] is not None else t["na"]),
            (t["lbl_ie1"], fmt(d[12], "eV")),
            (t["lbl_ea"], fmt(d[13], "eV")),
        ]),
        section(t["sec_atomic"], [
            (t["lbl_alpha"], fmt(d[9], "Å³")),
            (t["lbl_vdw"], fmt(d[15], "Å")),
            (t["lbl_vol"], fmt(d[11], "cm³/mol", 2)),
        ]),
        section(t["sec_compchem"], [
            (t["lbl_ecp"], ecp_val),
            (t["lbl_basis"], d[7]),
            (t["lbl_pseudo"], pseudo_val),
            (t["lbl_func"], d[16]),
            (t["lbl_disp"], disp_val),
            (t["lbl_relat"], relat_val),
        ]),
    ]

    # Phase 2 — NMR isotopes
    el_data = ELEMENTS_BY_Z.get(z, {})
    nmr_isotopes = el_data.get("nmr_isotopes", [])
    notes_key = f"notes_{lang}"
    if nmr_isotopes:
        nmr_items = []
        for iso in nmr_isotopes:
            mass  = iso.get("mass", "?")
            spin  = iso.get("spin", "?")
            abund = iso.get("abund", "?")
            basis = iso.get("basis_rec", "")
            note  = iso.get(notes_key, "")
            line  = f"{sym}-{mass}  ·  spin={spin}  ·  {abund}%"
            if basis:
                line += f"  ·  {basis}"
            children_li = [line]
            if note:
                children_li += [html.Br(), html.Em(note, style={"color": "#90a4ae", "fontSize": "0.72rem"})]
            nmr_items.append(html.Li(children_li))
        result.append(html.Div(className="detail-section", children=[
            html.H4(t["sec_nmr"], className="detail-section-title"),
            html.Ul(className="detail-list", children=nmr_items),
        ]))
    else:
        result.append(html.Div(className="detail-section", children=[
            html.H4(t["sec_nmr"], className="detail-section-title"),
            html.P(t["no_nmr"], style={"fontSize": "0.78rem", "color": "#90a4ae", "margin": "4px 0"}),
        ]))

    # Phase 2 — Orbital info
    orbital_info = el_data.get("orbital_info", {})
    if orbital_info:
        orb_rows = []
        if orbital_info.get("homo_type"):
            orb_rows.append((t["lbl_homo_type"], orbital_info["homo_type"]))
        if orbital_info.get("dft_challenge"):
            orb_rows.append((t["lbl_dft_challenge"], orbital_info["dft_challenge"]))
        if orbital_info.get("core_1s_eV") is not None:
            orb_rows.append((t["lbl_core_1s"], f"{orbital_info['core_1s_eV']} eV"))
        if orb_rows:
            result.append(section(t["sec_orbital"], orb_rows))

    result.append(html.Div(className="bse-link", children=[
        html.A(t["bse_link"], href="https://www.basissetexchange.org/",
               target="_blank", className="bse-anchor"),
    ]))
    return result


@app.callback(
    Output("lang", "data"),
    Input("btn-fr", "n_clicks"),
    Input("btn-ru", "n_clicks"),
    State("lang", "data"),
    prevent_initial_call=True,
)
def toggle_lang(n_fr, n_ru, current_lang):
    triggered = ctx.triggered_id
    if triggered == "btn-fr": return "fr"
    if triggered == "btn-ru": return "ru"
    return current_lang


@app.callback(
    Output("app-title", "children"),
    Output("app-subtitle", "children"),
    Output("detail-card-title", "children"),
    Output("group-filter", "options"),
    Output("group-filter", "placeholder"),
    Output("block-filter", "options"),
    Output("block-filter", "placeholder"),
    Output("ecp-filter", "options"),
    Output("ecp-filter", "placeholder"),
    Output("search-input", "placeholder"),
    Output("legend-row", "children"),
    Output("footer-data", "children"),
    Output("footer-credit", "children"),
    Output("btn-fr", "className"),
    Output("btn-ru", "className"),
    Output("tab-label-details", "label"),
    Output("tab-label-reco", "label"),
    Output("method-filter", "options"),
    Output("method-filter", "placeholder"),
    Output("prop-filter", "options"),
    Output("prop-filter", "placeholder"),
    Output("main-tab-tableau", "label"),
    Output("main-tab-trends", "label"),
    Output("main-tab-comp", "label"),
    Output("main-tab-orb", "label"),
    Output("export-summary", "children"),
    Output("mol-summary", "children"),
    Input("lang", "data"),
)
def update_ui_language(lang):
    t = LANG[lang or "fr"]
    lk = lang if lang in ("fr", "ru") else "fr"
    groups = [
        {"label": f"{t['group_label']} {int(g)}", "value": int(g)}
        for g in sorted(df[df["row"] <= 7]["group"].unique())
    ]
    legend = [
        html.Span([
            html.Span(className="legend-dot", style={"background": color}),
            html.Span(t["categories"].get(cat, cat), className="legend-label"),
        ], className="legend-item")
        for cat, color in CATEGORY_COLORS.items()
    ]
    active = "lang-btn active"
    inactive = "lang-btn"
    return (
        t["title"],
        t["subtitle"],
        t["detail_title"],
        groups, t["group_ph"],
        t["blocks"], t["block_ph"],
        t["ecps"], t["ecp_ph"],
        t["search_ph"],
        legend,
        t["footer_data"],
        t["footer_credit"],
        active if lk == "fr" else inactive,
        active if lk == "ru" else inactive,
        t["tab_details"],
        t["tab_reco"],
        list_methods(lk),
        t["reco_method_ph"],
        list_properties(lk),
        t["reco_prop_ph"],
        t["main_tab_table"],
        t["main_tab_trends"],
        t["main_tab_comp"],
        t["main_tab_orb"],
        t["export_title"],
        t["mol_title"],
    )


@app.callback(
    Output("recommendations-output", "children"),
    Output("last-recommendation", "data"),
    Input("selected-element-z", "data"),
    Input("selected-element-block", "data"),
    Input("method-filter", "value"),
    Input("prop-filter", "value"),
    Input("lang", "data"),
)
def update_recommendations(z, block, method_key, prop_key, lang):
    lang = lang or "fr"
    t = LANG[lang]

    if z is None:
        return [html.P(t["reco_no_element"], className="reco-hint")], None
    if not method_key or not prop_key:
        return [html.P(t["reco_no_filters"], className="reco-hint")], None

    el_data   = ELEMENTS_BY_Z.get(z, {})
    el_name   = el_data.get("name_ru", el_data.get("name", "?")) if lang == "ru" else el_data.get("name", "?")
    sym       = el_data.get("symbol", "?")
    eff_block = block or el_data.get("block", "s")

    rec = recommend(z, eff_block, method_key, prop_key, lang)

    # Store compact rec for export feature
    store_data = {
        "z": z, "method_key": method_key, "prop_key": prop_key,
        "basis": rec["basis"], "ecp": rec["ecp"],
        "functional": rec["functional"], "dispersion": rec["dispersion"],
    }

    children = []
    method_lbl = rec["method_info"].get(f"label_{lang}", method_key)
    prop_lbl   = rec["property_info"].get(f"label_{lang}", prop_key)
    children.append(html.Div(className="reco-header", children=[
        html.H3(f"{el_name} ({sym})  ·  Z = {z}"),
        html.P(f"{method_lbl}  →  {prop_lbl}", className="reco-subheader"),
    ]))

    rows = [(t["reco_basis_lbl"], rec["basis"])]
    if rec["aux_basis"]:
        rows.append((t["reco_aux_lbl"], rec["aux_basis"]))
    rows.append((t["reco_ecp_lbl"], rec["ecp"] if rec["ecp"] else t["na_ecp"]))
    if rec["functional"]:
        disp = f"  +  {rec['dispersion']}" if rec["dispersion"] else ""
        rows.append((t["reco_func_lbl"], rec["functional"] + disp))
    rows.append((t["reco_relat_lbl"], rec["relativistic"]))
    children.append(html.Div(className="reco-summary-box detail-section", children=[
        html.Ul(className="detail-list", children=[
            html.Li([html.Strong(lbl + " : "), val]) for lbl, val in rows
        ])
    ]))

    if rec["notes"]:
        children.append(html.Div(className="reco-notes detail-section", children=[
            html.H4(t["reco_notes_lbl"], className="detail-section-title"),
            dcc.Markdown(rec["notes"], className="reco-notes-text"),
        ]))

    if rec["software"]:
        badges = [
            html.A(
                href=sw["url"], target="_blank", className="sw-badge",
                style={"background": sw.get("badge_color", "#888")},
                children=[
                    html.Span(sw.get(f"label_{lang}", sw["name"]), className="sw-badge-name"),
                    html.Span(t["free_badge"] if sw.get("free") else t["commercial_badge"], className="sw-badge-type"),
                ],
            )
            for sw in rec["software"]
        ]
        children.append(html.Div(className="reco-software detail-section", children=[
            html.H4(t["reco_software_lbl"], className="detail-section-title"),
            html.Div(badges, className="sw-badges-row"),
        ]))

    if rec["orca_snippet"]:
        children.append(html.Div(className="reco-snippet detail-section", children=[
            html.H4(t["reco_snippet_orca"], className="detail-section-title"),
            html.Pre(rec["orca_snippet"], className="snippet-pre"),
        ]))
    if rec["gaussian_snippet"]:
        children.append(html.Div(className="reco-snippet detail-section", children=[
            html.H4(t["reco_snippet_gaussian"], className="detail-section-title"),
            html.Pre(rec["gaussian_snippet"], className="snippet-pre"),
        ]))

    if rec["links"]:
        children.append(html.Div(className="reco-links detail-section", children=[
            html.H4(t["reco_links_lbl"], className="detail-section-title"),
            html.Ul(className="detail-list", children=[
                html.Li(html.A(lnk["label"], href=lnk["url"], target="_blank", className="reco-link"))
                for lnk in rec["links"]
            ]),
        ]))

    return children, store_data


@app.callback(
    Output("export-output", "children"),
    Input("export-btn", "n_clicks"),
    State("last-recommendation", "data"),
    State("export-sw-select", "value"),
    State("lang", "data"),
    prevent_initial_call=True,
)
def generate_export(n_clicks, store_data, software, lang):
    lang = lang or "fr"
    t = LANG[lang]
    if not store_data:
        return t["export_no_reco"]
    z  = store_data["z"]
    el = ELEMENTS_BY_Z.get(z, {})
    return generate_input(
        software or "orca", el,
        store_data["method_key"], store_data["prop_key"],
        store_data["basis"], store_data["ecp"],
        store_data["functional"], store_data["dispersion"],
    )


@app.callback(
    Output("mol-output", "children"),
    Output("mol-prop-select", "options"),
    Output("mol-prop-select", "placeholder"),
    Input("mol-analyse-btn", "n_clicks"),
    State("mol-formula-input", "value"),
    State("mol-prop-select", "value"),
    Input("lang", "data"),
    prevent_initial_call=False,
)
def analyse_molecule(n_clicks, formula, prop_key, lang):
    lang = lang or "fr"
    t = LANG[lang]
    lk = lang if lang in ("fr", "ru") else "fr"
    opts = list_properties(lk)
    ph = t["reco_prop_ph"]

    if not formula or not n_clicks:
        return html.P(t["mol_no_result"], className="reco-hint"), opts, ph

    res = recommend_for_molecule(formula.strip(), prop_key or "geometry", lang, ELEMENTS_BY_SYM)
    if res.get("error"):
        err = {"fr": f"Formule non reconnue : « {formula} »",
               "ru": f"Формула не распознана: «{formula}»",
               "en": f"Unrecognized formula: '{formula}'"}.get(lk, formula)
        return html.P(err, className="reco-hint"), opts, ph

    elem_str = "  ·  ".join(f"{s}×{c}" for s, c in sorted(res["elements"].items()))
    ecp_str  = res["ecp"] or t["mol_none"]

    children = [
        html.Div(className="reco-header", children=[
            html.H3(res["formula"]),
            html.P(elem_str, className="reco-subheader"),
        ]),
        html.Div(className="reco-summary-box detail-section", children=[
            html.Ul(className="detail-list", children=[
                html.Li([html.Strong(t["mol_method"] + " : "), res["method"]]),
                html.Li([html.Strong(t["mol_basis"]  + " : "), res["basis"]]),
                html.Li([html.Strong(t["mol_ecp"]    + " : "), ecp_str]),
            ])
        ]),
        html.Div(className="detail-section", children=[
            html.H4("Notes", className="detail-section-title"),
            html.P(res["method_note"], style={"fontSize": "0.78rem", "color": "#cfd8dc"}),
            *[html.P(note, style={"fontSize": "0.78rem", "color": "#ffb74d"})
              for note in res["extra_notes"]],
        ]),
    ]
    return children, opts, ph


if __name__ == "__main__":
    app.run_server(debug=True)

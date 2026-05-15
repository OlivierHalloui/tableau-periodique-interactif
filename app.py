# =============================================================================
# Tableau périodique interactif — Master 1 Chimie Informatique
# Интерактивная таблица Менделеева — 1-й год магистратуры, вычислительная химия
#
# FR : J'ai choisi Dash (Plotly) car il permet de créer une application web
#      réactive en Python pur, sans JavaScript. Le rendu côté serveur simplifie
#      la logique des callbacks et la maintenance du code.
# RU : Я выбрал Dash (Plotly), так как он позволяет строить реактивные
#      веб-приложения на чистом Python. Серверный рендеринг упрощает логику
#      обратных вызовов и сопровождение кода.
# =============================================================================

import dash
from dash import html, dcc, Input, Output, State, ctx
import plotly.graph_objs as go
import pandas as pd

# FR : Toutes les données sont encodées dans une liste de dictionnaires Python.
#      J'ai choisi cette structure plutôt qu'un fichier CSV externe pour garder
#      l'application autonome (un seul fichier, pas de dépendance de lecture).
#      Chaque dict décrit un élément ; les champs "row" et "col" définissent
#      sa position dans la grille du tableau périodique.
# RU : Все данные закодированы в списке словарей Python. Я выбрал эту структуру
#      вместо внешнего CSV-файла, чтобы приложение было автономным (один файл,
#      никаких зависимостей). Поля "row" и "col" задают позицию элемента в
#      сетке таблицы Менделеева.
ELEMENTS = [
    {"atomic_number": 1, "symbol": "H", "name": "Hydrogène", "atomic_mass": 1.008, "electron_configuration": "1s1", "electronegativity": 2.20, "atomic_radius": 53, "melting_point": 14.01, "boiling_point": 20.28, "density": 0.0000899, "state_at_25C": "Gaz", "group": 1, "period": 1, "row": 1, "col": 1, "col": 1, "category": "non-metal"},
    {"atomic_number": 2, "symbol": "He", "name": "Hélium", "atomic_mass": 4.002602, "electron_configuration": "1s2", "electronegativity": None, "atomic_radius": 31, "melting_point": 0.95, "boiling_point": 4.22, "density": 0.0001785, "state_at_25C": "Gaz", "group": 18, "period": 1, "row": 1, "col": 18, "col": 18, "category": "gaz noble"},
    {"atomic_number": 3, "symbol": "Li", "name": "Lithium", "atomic_mass": 6.94, "electron_configuration": "[He] 2s1", "electronegativity": 0.98, "atomic_radius": 167, "melting_point": 453.69, "boiling_point": 1603, "density": 0.534, "state_at_25C": "Solide", "group": 1, "period": 2, "row": 2, "col": 1, "category": "métal alcalin"},
    {"atomic_number": 4, "symbol": "Be", "name": "Béryllium", "atomic_mass": 9.0121831, "electron_configuration": "[He] 2s2", "electronegativity": 1.57, "atomic_radius": 112, "melting_point": 1560, "boiling_point": 2742, "density": 1.85, "state_at_25C": "Solide", "group": 2, "period": 2, "row": 2, "col": 2, "category": "métal alcalino-terreux"},
    {"atomic_number": 5, "symbol": "B", "name": "Bore", "atomic_mass": 10.81, "electron_configuration": "[He] 2s2 2p1", "electronegativity": 2.04, "atomic_radius": 87, "melting_point": 2349, "boiling_point": 4200, "density": 2.34, "state_at_25C": "Solide", "group": 13, "period": 2, "row": 2, "col": 13, "category": "métalloïde"},
    {"atomic_number": 6, "symbol": "C", "name": "Carbone", "atomic_mass": 12.011, "electron_configuration": "[He] 2s2 2p2", "electronegativity": 2.55, "atomic_radius": 67, "melting_point": 3823, "boiling_point": 4300, "density": 2.267, "state_at_25C": "Solide", "group": 14, "period": 2, "row": 2, "col": 14, "category": "non-metal"},
    {"atomic_number": 7, "symbol": "N", "name": "Azote", "atomic_mass": 14.007, "electron_configuration": "[He] 2s2 2p3", "electronegativity": 3.04, "atomic_radius": 56, "melting_point": 63.15, "boiling_point": 77.36, "density": 0.0012506, "state_at_25C": "Gaz", "group": 15, "period": 2, "row": 2, "col": 15, "category": "non-metal"},
    {"atomic_number": 8, "symbol": "O", "name": "Oxygène", "atomic_mass": 15.999, "electron_configuration": "[He] 2s2 2p4", "electronegativity": 3.44, "atomic_radius": 48, "melting_point": 54.36, "boiling_point": 90.20, "density": 0.001429, "state_at_25C": "Gaz", "group": 16, "period": 2, "row": 2, "col": 16, "category": "non-metal"},
    {"atomic_number": 9, "symbol": "F", "name": "Fluor", "atomic_mass": 18.998403163, "electron_configuration": "[He] 2s2 2p5", "electronegativity": 3.98, "atomic_radius": 42, "melting_point": 53.48, "boiling_point": 85.03, "density": 0.001696, "state_at_25C": "Gaz", "group": 17, "period": 2, "row": 2, "col": 17, "category": "halogène"},
    {"atomic_number": 10, "symbol": "Ne", "name": "Néon", "atomic_mass": 20.1797, "electron_configuration": "[He] 2s2 2p6", "electronegativity": None, "atomic_radius": 38, "melting_point": 24.56, "boiling_point": 27.07, "density": 0.0008999, "state_at_25C": "Gaz", "group": 18, "period": 2, "row": 2, "col": 18, "category": "gaz noble"},
    {"atomic_number": 11, "symbol": "Na", "name": "Sodium", "atomic_mass": 22.98976928, "electron_configuration": "[Ne] 3s1", "electronegativity": 0.93, "atomic_radius": 190, "melting_point": 370.87, "boiling_point": 1156, "density": 0.968, "state_at_25C": "Solide", "group": 1, "period": 3, "row": 3, "col": 1, "category": "métal alcalin"},
    {"atomic_number": 12, "symbol": "Mg", "name": "Magnésium", "atomic_mass": 24.305, "electron_configuration": "[Ne] 3s2", "electronegativity": 1.31, "atomic_radius": 145, "melting_point": 923, "boiling_point": 1363, "density": 1.738, "state_at_25C": "Solide", "group": 2, "period": 3, "row": 3, "col": 2, "category": "métal alcalino-terreux"},
    {"atomic_number": 13, "symbol": "Al", "name": "Aluminium", "atomic_mass": 26.9815385, "electron_configuration": "[Ne] 3s2 3p1", "electronegativity": 1.61, "atomic_radius": 118, "melting_point": 933.47, "boiling_point": 2792, "density": 2.70, "state_at_25C": "Solide", "group": 13, "period": 3, "row": 3, "col": 13, "category": "métal"},
    {"atomic_number": 14, "symbol": "Si", "name": "Silicium", "atomic_mass": 28.085, "electron_configuration": "[Ne] 3s2 3p2", "electronegativity": 1.90, "atomic_radius": 111, "melting_point": 1687, "boiling_point": 3538, "density": 2.33, "state_at_25C": "Solide", "group": 14, "period": 3, "row": 3, "col": 14, "category": "métalloïde"},
    {"atomic_number": 15, "symbol": "P", "name": "Phosphore", "atomic_mass": 30.973761998, "electron_configuration": "[Ne] 3s2 3p3", "electronegativity": 2.19, "atomic_radius": 98, "melting_point": 317.30, "boiling_point": 553.65, "density": 1.82, "state_at_25C": "Solide", "group": 15, "period": 3, "row": 3, "col": 15, "category": "non-metal"},
    {"atomic_number": 16, "symbol": "S", "name": "Soufre", "atomic_mass": 32.06, "electron_configuration": "[Ne] 3s2 3p4", "electronegativity": 2.58, "atomic_radius": 88, "melting_point": 388.36, "boiling_point": 717.87, "density": 2.07, "state_at_25C": "Solide", "group": 16, "period": 3, "row": 3, "col": 16, "category": "non-metal"},
    {"atomic_number": 17, "symbol": "Cl", "name": "Chlore", "atomic_mass": 35.45, "electron_configuration": "[Ne] 3s2 3p5", "electronegativity": 3.16, "atomic_radius": 79, "melting_point": 172.2, "boiling_point": 239.11, "density": 0.003214, "state_at_25C": "Gaz", "group": 17, "period": 3, "row": 3, "col": 17, "category": "halogène"},
    {"atomic_number": 18, "symbol": "Ar", "name": "Argon", "atomic_mass": 39.948, "electron_configuration": "[Ne] 3s2 3p6", "electronegativity": None, "atomic_radius": 71, "melting_point": 83.80, "boiling_point": 87.30, "density": 0.001784, "state_at_25C": "Gaz", "group": 18, "period": 3, "row": 3, "col": 18, "category": "gaz noble"},
    {"atomic_number": 19, "symbol": "K", "name": "Potassium", "atomic_mass": 39.0983, "electron_configuration": "[Ar] 4s1", "electronegativity": 0.82, "atomic_radius": 243, "melting_point": 336.53, "boiling_point": 1032, "density": 0.862, "state_at_25C": "Solide", "group": 1, "period": 4, "row": 4, "col": 1, "category": "métal alcalin"},
    {"atomic_number": 20, "symbol": "Ca", "name": "Calcium", "atomic_mass": 40.078, "electron_configuration": "[Ar] 4s2", "electronegativity": 1.00, "atomic_radius": 194, "melting_point": 1115, "boiling_point": 1757, "density": 1.55, "state_at_25C": "Solide", "group": 2, "period": 4, "row": 4, "col": 2, "category": "métal alcalino-terreux"},
    {"atomic_number": 21, "symbol": "Sc", "name": "Scandium", "atomic_mass": 44.955908, "electron_configuration": "[Ar] 3d1 4s2", "electronegativity": 1.36, "atomic_radius": 184, "melting_point": 1814, "boiling_point": 3109, "density": 2.99, "state_at_25C": "Solide", "group": 3, "period": 4, "row": 4, "col": 3, "category": "métal de transition"},
    {"atomic_number": 22, "symbol": "Ti", "name": "Titane", "atomic_mass": 47.867, "electron_configuration": "[Ar] 3d2 4s2", "electronegativity": 1.54, "atomic_radius": 176, "melting_point": 1941, "boiling_point": 3560, "density": 4.51, "state_at_25C": "Solide", "group": 4, "period": 4, "row": 4, "col": 4, "category": "métal de transition"},
    {"atomic_number": 23, "symbol": "V", "name": "Vanadium", "atomic_mass": 50.9415, "electron_configuration": "[Ar] 3d3 4s2", "electronegativity": 1.63, "atomic_radius": 171, "melting_point": 2183, "boiling_point": 3680, "density": 6.11, "state_at_25C": "Solide", "group": 5, "period": 4, "row": 4, "col": 5, "category": "métal de transition"},
    {"atomic_number": 24, "symbol": "Cr", "name": "Chrome", "atomic_mass": 51.9961, "electron_configuration": "[Ar] 3d5 4s1", "electronegativity": 1.66, "atomic_radius": 166, "melting_point": 2180, "boiling_point": 2944, "density": 7.19, "state_at_25C": "Solide", "group": 6, "period": 4, "row": 4, "col": 6, "category": "métal de transition"},
    {"atomic_number": 25, "symbol": "Mn", "name": "Manganèse", "atomic_mass": 54.938044, "electron_configuration": "[Ar] 3d5 4s2", "electronegativity": 1.55, "atomic_radius": 161, "melting_point": 1519, "boiling_point": 2334, "density": 7.21, "state_at_25C": "Solide", "group": 7, "period": 4, "row": 4, "col": 7, "category": "métal de transition"},
    {"atomic_number": 26, "symbol": "Fe", "name": "Fer", "atomic_mass": 55.845, "electron_configuration": "[Ar] 3d6 4s2", "electronegativity": 1.83, "atomic_radius": 156, "melting_point": 1811, "boiling_point": 3134, "density": 7.87, "state_at_25C": "Solide", "group": 8, "period": 4, "row": 4, "col": 8, "category": "métal de transition"},
    {"atomic_number": 27, "symbol": "Co", "name": "Cobalt", "atomic_mass": 58.933194, "electron_configuration": "[Ar] 3d7 4s2", "electronegativity": 1.88, "atomic_radius": 152, "melting_point": 1768, "boiling_point": 3200, "density": 8.90, "state_at_25C": "Solide", "group": 9, "period": 4, "row": 4, "col": 9, "category": "métal de transition"},
    {"atomic_number": 28, "symbol": "Ni", "name": "Nickel", "atomic_mass": 58.6934, "electron_configuration": "[Ar] 3d8 4s2", "electronegativity": 1.91, "atomic_radius": 149, "melting_point": 1728, "boiling_point": 3186, "density": 8.91, "state_at_25C": "Solide", "group": 10, "period": 4, "row": 4, "col": 10, "category": "métal de transition"},
    {"atomic_number": 29, "symbol": "Cu", "name": "Cuivre", "atomic_mass": 63.546, "electron_configuration": "[Ar] 3d10 4s1", "electronegativity": 1.90, "atomic_radius": 145, "melting_point": 1357.77, "boiling_point": 2835, "density": 8.96, "state_at_25C": "Solide", "group": 11, "period": 4, "row": 4, "col": 11, "category": "métal de transition"},
    {"atomic_number": 30, "symbol": "Zn", "name": "Zinc", "atomic_mass": 65.38, "electron_configuration": "[Ar] 3d10 4s2", "electronegativity": 1.65, "atomic_radius": 142, "melting_point": 693.15, "boiling_point": 1180, "density": 7.14, "state_at_25C": "Solide", "group": 12, "period": 4, "row": 4, "col": 12, "category": "métal de transition"},
    {"atomic_number": 31, "symbol": "Ga", "name": "Gallium", "atomic_mass": 69.723, "electron_configuration": "[Ar] 3d10 4s2 4p1", "electronegativity": 1.81, "atomic_radius": 136, "melting_point": 302.91, "boiling_point": 2477, "density": 5.91, "state_at_25C": "Solide", "group": 13, "period": 4, "row": 4, "col": 13, "category": "post-transition metal"},
    {"atomic_number": 32, "symbol": "Ge", "name": "Germanium", "atomic_mass": 72.630, "electron_configuration": "[Ar] 3d10 4s2 4p2", "electronegativity": 2.01, "atomic_radius": 125, "melting_point": 1211.40, "boiling_point": 3106, "density": 5.323, "state_at_25C": "Solide", "group": 14, "period": 4, "row": 4, "col": 14, "category": "métalloïde"},
    {"atomic_number": 33, "symbol": "As", "name": "Arsenic", "atomic_mass": 74.921595, "electron_configuration": "[Ar] 3d10 4s2 4p3", "electronegativity": 2.18, "atomic_radius": 114, "melting_point": 1090, "boiling_point": 887, "density": 5.72, "state_at_25C": "Solide", "group": 15, "period": 4, "row": 4, "col": 15, "category": "métalloïde"},
    {"atomic_number": 34, "symbol": "Se", "name": "Sélénium", "atomic_mass": 78.971, "electron_configuration": "[Ar] 3d10 4s2 4p4", "electronegativity": 2.55, "atomic_radius": 103, "melting_point": 218.79, "boiling_point": 685, "density": 4.81, "state_at_25C": "Solide", "group": 16, "period": 4, "row": 4, "col": 16, "category": "non-metal"},
    {"atomic_number": 35, "symbol": "Br", "name": "Brome", "atomic_mass": 79.904, "electron_configuration": "[Ar] 3d10 4s2 4p5", "electronegativity": 2.96, "atomic_radius": 94, "melting_point": 265.8, "boiling_point": 332.0, "density": 3.12, "state_at_25C": "Liquide", "group": 17, "period": 4, "row": 4, "col": 17, "category": "halogène"},
    {"atomic_number": 36, "symbol": "Kr", "name": "Krypton", "atomic_mass": 83.798, "electron_configuration": "[Ar] 3d10 4s2 4p6", "electronegativity": None, "atomic_radius": 88, "melting_point": 115.79, "boiling_point": 119.93, "density": 0.003749, "state_at_25C": "Gaz", "group": 18, "period": 4, "row": 4, "col": 18, "category": "gaz noble"},
    {"atomic_number": 37, "symbol": "Rb", "name": "Rubidium", "atomic_mass": 85.4678, "electron_configuration": "[Kr] 5s1", "electronegativity": 0.82, "atomic_radius": 248, "melting_point": 312.46, "boiling_point": 961, "density": 1.53, "state_at_25C": "Solide", "group": 1, "period": 5, "row": 5, "col": 1, "category": "métal alcalin"},
    {"atomic_number": 38, "symbol": "Sr", "name": "Strontium", "atomic_mass": 87.62, "electron_configuration": "[Kr] 5s2", "electronegativity": 0.95, "atomic_radius": 215, "melting_point": 1042, "boiling_point": 1655, "density": 2.63, "state_at_25C": "Solide", "group": 2, "period": 5, "row": 5, "col": 2, "category": "métal alcalino-terreux"},
    {"atomic_number": 39, "symbol": "Y", "name": "Yttrium", "atomic_mass": 88.90584, "electron_configuration": "[Kr] 4d1 5s2", "electronegativity": 1.22, "atomic_radius": 180, "melting_point": 1799, "boiling_point": 3609, "density": 4.47, "state_at_25C": "Solide", "group": 3, "period": 5, "row": 5, "col": 3, "category": "métal de transition"},
    {"atomic_number": 40, "symbol": "Zr", "name": "Zirconium", "atomic_mass": 91.224, "electron_configuration": "[Kr] 4d2 5s2", "electronegativity": 1.33, "atomic_radius": 160, "melting_point": 2128, "boiling_point": 4682, "density": 6.52, "state_at_25C": "Solide", "group": 4, "period": 5, "row": 5, "col": 4, "category": "métal de transition"},
    {"atomic_number": 41, "symbol": "Nb", "name": "Niobium", "atomic_mass": 92.90637, "electron_configuration": "[Kr] 4d4 5s1", "electronegativity": 1.6, "atomic_radius": 146, "melting_point": 2750, "boiling_point": 5017, "density": 8.57, "state_at_25C": "Solide", "group": 5, "period": 5, "row": 5, "col": 5, "category": "métal de transition"},
    {"atomic_number": 42, "symbol": "Mo", "name": "Molybdène", "atomic_mass": 95.95, "electron_configuration": "[Kr] 4d5 5s1", "electronegativity": 2.16, "atomic_radius": 139, "melting_point": 2896, "boiling_point": 4912, "density": 10.28, "state_at_25C": "Solide", "group": 6, "period": 5, "row": 5, "col": 6, "category": "métal de transition"},
    {"atomic_number": 43, "symbol": "Tc", "name": "Technétium", "atomic_mass": 98, "electron_configuration": "[Kr] 4d5 5s2", "electronegativity": 1.9, "atomic_radius": 136, "melting_point": 2430, "boiling_point": 4538, "density": 11.5, "state_at_25C": "Solide", "group": 7, "period": 5, "row": 5, "col": 7, "category": "métal de transition"},
    {"atomic_number": 44, "symbol": "Ru", "name": "Ruthénium", "atomic_mass": 101.07, "electron_configuration": "[Kr] 4d7 5s1", "electronegativity": 2.2, "atomic_radius": 134, "melting_point": 2607, "boiling_point": 4423, "density": 12.37, "state_at_25C": "Solide", "group": 8, "period": 5, "row": 5, "col": 8, "category": "métal de transition"},
    {"atomic_number": 45, "symbol": "Rh", "name": "Rhodium", "atomic_mass": 102.90550, "electron_configuration": "[Kr] 4d8 5s1", "electronegativity": 2.28, "atomic_radius": 135, "melting_point": 2237, "boiling_point": 3968, "density": 12.41, "state_at_25C": "Solide", "group": 9, "period": 5, "row": 5, "col": 9, "category": "métal de transition"},
    {"atomic_number": 46, "symbol": "Pd", "name": "Palladium", "atomic_mass": 106.42, "electron_configuration": "[Kr] 4d10", "electronegativity": 2.20, "atomic_radius": 137, "melting_point": 1828.05, "boiling_point": 3236, "density": 12.02, "state_at_25C": "Solide", "group": 10, "period": 5, "row": 5, "col": 10, "category": "métal de transition"},
    {"atomic_number": 47, "symbol": "Ag", "name": "Argent", "atomic_mass": 107.8682, "electron_configuration": "[Kr] 4d10 5s1", "electronegativity": 1.93, "atomic_radius": 144, "melting_point": 1234.93, "boiling_point": 2435, "density": 10.49, "state_at_25C": "Solide", "group": 11, "period": 5, "row": 5, "col": 11, "category": "métal de transition"},
    {"atomic_number": 48, "symbol": "Cd", "name": "Cadmium", "atomic_mass": 112.414, "electron_configuration": "[Kr] 4d10 5s2", "electronegativity": 1.69, "atomic_radius": 151, "melting_point": 594.22, "boiling_point": 1040, "density": 8.65, "state_at_25C": "Solide", "group": 12, "period": 5, "row": 5, "col": 12, "category": "métal de transition"},
    {"atomic_number": 49, "symbol": "In", "name": "Indium", "atomic_mass": 114.818, "electron_configuration": "[Kr] 4d10 5s2 5p1", "electronegativity": 1.78, "atomic_radius": 167, "melting_point": 429.75, "boiling_point": 2345, "density": 7.31, "state_at_25C": "Solide", "group": 13, "period": 5, "row": 5, "col": 13, "category": "post-transition metal"},
    {"atomic_number": 50, "symbol": "Sn", "name": "Étain", "atomic_mass": 118.71, "electron_configuration": "[Kr] 4d10 5s2 5p2", "electronegativity": 1.96, "atomic_radius": 145, "melting_point": 505.08, "boiling_point": 2875, "density": 7.31, "state_at_25C": "Solide", "group": 14, "period": 5, "row": 5, "col": 14, "category": "post-transition metal"},
    {"atomic_number": 51, "symbol": "Sb", "name": "Antimoine", "atomic_mass": 121.760, "electron_configuration": "[Kr] 4d10 5s2 5p3", "electronegativity": 2.05, "atomic_radius": 133, "melting_point": 903.78, "boiling_point": 1860, "density": 6.69, "state_at_25C": "Solide", "group": 15, "period": 5, "row": 5, "col": 15, "category": "métalloïde"},
    {"atomic_number": 52, "symbol": "Te", "name": "Tellure", "atomic_mass": 127.60, "electron_configuration": "[Kr] 4d10 5s2 5p4", "electronegativity": 2.1, "atomic_radius": 123, "melting_point": 722.66, "boiling_point": 1261, "density": 6.24, "state_at_25C": "Solide", "group": 16, "period": 5, "row": 5, "col": 16, "category": "non-metal"},
    {"atomic_number": 53, "symbol": "I", "name": "Iode", "atomic_mass": 126.90447, "electron_configuration": "[Kr] 4d10 5s2 5p5", "electronegativity": 2.66, "atomic_radius": 115, "melting_point": 386.85, "boiling_point": 457.4, "density": 4.93, "state_at_25C": "Solide", "group": 17, "period": 5, "row": 5, "col": 17, "category": "halogène"},
    {"atomic_number": 54, "symbol": "Xe", "name": "Xénon", "atomic_mass": 131.293, "electron_configuration": "[Kr] 4d10 5s2 5p6", "electronegativity": None, "atomic_radius": 108, "melting_point": 161.40, "boiling_point": 165.03, "density": 0.005894, "state_at_25C": "Gaz", "group": 18, "period": 5, "row": 5, "col": 18, "category": "gaz noble"},
    {"atomic_number": 55, "symbol": "Cs", "name": "Césium", "atomic_mass": 132.90545196, "electron_configuration": "[Xe] 6s1", "electronegativity": 0.79, "atomic_radius": 260, "melting_point": 301.59, "boiling_point": 944, "density": 1.93, "state_at_25C": "Solide", "group": 1, "period": 6, "row": 6, "col": 1, "category": "métal alcalin"},
    {"atomic_number": 56, "symbol": "Ba", "name": "Baryum", "atomic_mass": 137.327, "electron_configuration": "[Xe] 6s2", "electronegativity": 0.89, "atomic_radius": 222, "melting_point": 1000, "boiling_point": 2118, "density": 3.62, "state_at_25C": "Solide", "group": 2, "period": 6, "row": 6, "col": 2, "category": "métal alcalino-terreux"},
    {"atomic_number": 57, "symbol": "La", "name": "Lanthane", "atomic_mass": 138.90547, "electron_configuration": "[Xe] 5d1 6s2", "electronegativity": 1.10, "atomic_radius": 195, "melting_point": 1193, "boiling_point": 3737, "density": 6.16, "state_at_25C": "Solide", "group": 3, "period": 6, "row": 6, "col": 3, "category": "lanthanide"},
    {"atomic_number": 57, "symbol": "La", "name": "Lanthane", "atomic_mass": 138.90547, "electron_configuration": "[Xe] 5d1 6s2", "electronegativity": 1.10, "atomic_radius": 195, "melting_point": 1193, "boiling_point": 3737, "density": 6.16, "state_at_25C": "Solide", "group": 3, "period": 6, "row": 8, "col": 3, "category": "lanthanide"},
    {"atomic_number": 58, "symbol": "Ce", "name": "Cérium", "atomic_mass": 140.116, "electron_configuration": "[Xe] 4f1 5d1 6s2", "electronegativity": 1.12, "atomic_radius": 185, "melting_point": 1068, "boiling_point": 3716, "density": 6.77, "state_at_25C": "Solide", "group": 3, "period": 6, "row": 8, "col": 4, "category": "lanthanide"},
    {"atomic_number": 59, "symbol": "Pr", "name": "Praséodyme", "atomic_mass": 140.90766, "electron_configuration": "[Xe] 4f3 6s2", "electronegativity": 1.13, "atomic_radius": 182, "melting_point": 1208, "boiling_point": 3793, "density": 6.77, "state_at_25C": "Solide", "group": 3, "period": 6, "row": 8, "col": 5, "category": "lanthanide"},
    {"atomic_number": 60, "symbol": "Nd", "name": "Néodyme", "atomic_mass": 144.242, "electron_configuration": "[Xe] 4f4 6s2", "electronegativity": 1.14, "atomic_radius": 181, "melting_point": 1297, "boiling_point": 3347, "density": 7.01, "state_at_25C": "Solide", "group": 3, "period": 6, "row": 8, "col": 6, "category": "lanthanide"},
    {"atomic_number": 61, "symbol": "Pm", "name": "Prométhium", "atomic_mass": 145, "electron_configuration": "[Xe] 4f5 6s2", "electronegativity": 1.13, "atomic_radius": 183, "melting_point": 1315, "boiling_point": 3273, "density": 7.26, "state_at_25C": "Solide", "group": 3, "period": 6, "row": 8, "col": 7, "category": "lanthanide"},
    {"atomic_number": 62, "symbol": "Sm", "name": "Samarium", "atomic_mass": 150.36, "electron_configuration": "[Xe] 4f6 6s2", "electronegativity": 1.17, "atomic_radius": 180, "melting_point": 1345, "boiling_point": 2076, "density": 7.52, "state_at_25C": "Solide", "group": 3, "period": 6, "row": 8, "col": 8, "category": "lanthanide"},
    {"atomic_number": 63, "symbol": "Eu", "name": "Europium", "atomic_mass": 151.964, "electron_configuration": "[Xe] 4f7 6s2", "electronegativity": 1.2, "atomic_radius": 199, "melting_point": 1095, "boiling_point": 1802, "density": 5.24, "state_at_25C": "Solide", "group": 3, "period": 6, "row": 8, "col": 9, "category": "lanthanide"},
    {"atomic_number": 64, "symbol": "Gd", "name": "Gadolinium", "atomic_mass": 157.25, "electron_configuration": "[Xe] 4f7 5d1 6s2", "electronegativity": 1.20, "atomic_radius": 180, "melting_point": 1585, "boiling_point": 3273, "density": 7.90, "state_at_25C": "Solide", "group": 3, "period": 6, "row": 8, "col": 10, "category": "lanthanide"},
    {"atomic_number": 65, "symbol": "Tb", "name": "Terbium", "atomic_mass": 158.92535, "electron_configuration": "[Xe] 4f9 6s2", "electronegativity": 1.2, "atomic_radius": 177, "melting_point": 1629, "boiling_point": 3503, "density": 8.23, "state_at_25C": "Solide", "group": 3, "period": 6, "row": 8, "col": 11, "category": "lanthanide"},
    {"atomic_number": 66, "symbol": "Dy", "name": "Dysprosium", "atomic_mass": 162.500, "electron_configuration": "[Xe] 4f10 6s2", "electronegativity": 1.22, "atomic_radius": 175, "melting_point": 1680, "boiling_point": 2840, "density": 8.55, "state_at_25C": "Solide", "group": 3, "period": 6, "row": 8, "col": 12, "category": "lanthanide"},
    {"atomic_number": 67, "symbol": "Ho", "name": "Holmium", "atomic_mass": 164.93033, "electron_configuration": "[Xe] 4f11 6s2", "electronegativity": 1.23, "atomic_radius": 173, "melting_point": 1747, "boiling_point": 2973, "density": 8.79, "state_at_25C": "Solide", "group": 3, "period": 6, "row": 8, "col": 13, "category": "lanthanide"},
    {"atomic_number": 68, "symbol": "Er", "name": "Erbium", "atomic_mass": 167.259, "electron_configuration": "[Xe] 4f12 6s2", "electronegativity": 1.24, "atomic_radius": 173, "melting_point": 1802, "boiling_point": 3141, "density": 9.07, "state_at_25C": "Solide", "group": 3, "period": 6, "row": 8, "col": 14, "category": "lanthanide"},
    {"atomic_number": 69, "symbol": "Tm", "name": "Thulium", "atomic_mass": 168.93422, "electron_configuration": "[Xe] 4f13 6s2", "electronegativity": 1.25, "atomic_radius": 176, "melting_point": 1818, "boiling_point": 2223, "density": 9.32, "state_at_25C": "Solide", "group": 3, "period": 6, "row": 8, "col": 15, "category": "lanthanide"},
    {"atomic_number": 70, "symbol": "Yb", "name": "Ytterbium", "atomic_mass": 173.045, "electron_configuration": "[Xe] 4f14 6s2", "electronegativity": 1.1, "atomic_radius": 194, "melting_point": 1097, "boiling_point": 1469, "density": 6.97, "state_at_25C": "Solide", "group": 3, "period": 6, "row": 8, "col": 16, "category": "lanthanide"},
    {"atomic_number": 71, "symbol": "Lu", "name": "Lutétium", "atomic_mass": 174.9668, "electron_configuration": "[Xe] 4f14 5d1 6s2", "electronegativity": 1.27, "atomic_radius": 173, "melting_point": 1925, "boiling_point": 3675, "density": 9.84, "state_at_25C": "Solide", "group": 3, "period": 6, "row": 8, "col": 17, "category": "lanthanide"},
    {"atomic_number": 72, "symbol": "Hf", "name": "Hafnium", "atomic_mass": 178.49, "electron_configuration": "[Xe] 4f14 5d2 6s2", "electronegativity": 1.3, "atomic_radius": 159, "melting_point": 2506, "boiling_point": 4876, "density": 13.31, "state_at_25C": "Solide", "group": 4, "period": 6, "row": 6, "col": 4, "category": "métal de transition"},
    {"atomic_number": 73, "symbol": "Ta", "name": "Tantale", "atomic_mass": 180.94788, "electron_configuration": "[Xe] 4f14 5d3 6s2", "electronegativity": 1.5, "atomic_radius": 146, "melting_point": 3290, "boiling_point": 5731, "density": 16.65, "state_at_25C": "Solide", "group": 5, "period": 6, "row": 6, "col": 5, "category": "métal de transition"},
    {"atomic_number": 74, "symbol": "W", "name": "Tungstène", "atomic_mass": 183.84, "electron_configuration": "[Xe] 4f14 5d4 6s2", "electronegativity": 2.36, "atomic_radius": 139, "melting_point": 3695, "boiling_point": 5828, "density": 19.25, "state_at_25C": "Solide", "group": 6, "period": 6, "row": 6, "col": 6, "category": "métal de transition"},
    {"atomic_number": 75, "symbol": "Re", "name": "Rhénium", "atomic_mass": 186.207, "electron_configuration": "[Xe] 4f14 5d5 6s2", "electronegativity": 1.9, "atomic_radius": 137, "melting_point": 3459, "boiling_point": 5869, "density": 21.02, "state_at_25C": "Solide", "group": 7, "period": 6, "row": 6, "col": 7, "category": "métal de transition"},
    {"atomic_number": 76, "symbol": "Os", "name": "Osmium", "atomic_mass": 190.23, "electron_configuration": "[Xe] 4f14 5d6 6s2", "electronegativity": 2.2, "atomic_radius": 135, "melting_point": 3306, "boiling_point": 5285, "density": 22.61, "state_at_25C": "Solide", "group": 8, "period": 6, "row": 6, "col": 8, "category": "métal de transition"},
    {"atomic_number": 77, "symbol": "Ir", "name": "Iridium", "atomic_mass": 192.217, "electron_configuration": "[Xe] 4f14 5d7 6s2", "electronegativity": 2.20, "atomic_radius": 136, "melting_point": 2739, "boiling_point": 4701, "density": 22.56, "state_at_25C": "Solide", "group": 9, "period": 6, "row": 6, "col": 9, "category": "métal de transition"},
    {"atomic_number": 78, "symbol": "Pt", "name": "Platine", "atomic_mass": 195.084, "electron_configuration": "[Xe] 4f14 5d9 6s1", "electronegativity": 2.28, "atomic_radius": 139, "melting_point": 2041.4, "boiling_point": 4098, "density": 21.45, "state_at_25C": "Solide", "group": 10, "period": 6, "row": 6, "col": 10, "category": "métal de transition"},
    {"atomic_number": 79, "symbol": "Au", "name": "Or", "atomic_mass": 196.966569, "electron_configuration": "[Xe] 4f14 5d10 6s1", "electronegativity": 2.54, "atomic_radius": 144, "melting_point": 1337.33, "boiling_point": 3129, "density": 19.32, "state_at_25C": "Solide", "group": 11, "period": 6, "row": 6, "col": 11, "category": "métal de transition"},
    {"atomic_number": 80, "symbol": "Hg", "name": "Mercure", "atomic_mass": 200.592, "electron_configuration": "[Xe] 4f14 5d10 6s2", "electronegativity": 2.00, "atomic_radius": 151, "melting_point": 234.32, "boiling_point": 629.88, "density": 13.534, "state_at_25C": "Liquide", "group": 12, "period": 6, "row": 6, "col": 12, "category": "métal de transition"},
    {"atomic_number": 81, "symbol": "Tl", "name": "Thallium", "atomic_mass": 204.38, "electron_configuration": "[Xe] 4f14 5d10 6s2 6p1", "electronegativity": 1.62, "atomic_radius": 156, "melting_point": 577, "boiling_point": 1746, "density": 11.85, "state_at_25C": "Solide", "group": 13, "period": 6, "row": 6, "col": 13, "category": "post-transition metal"},
    {"atomic_number": 82, "symbol": "Pb", "name": "Plomb", "atomic_mass": 207.2, "electron_configuration": "[Xe] 4f14 5d10 6s2 6p2", "electronegativity": 2.33, "atomic_radius": 154, "melting_point": 600.61, "boiling_point": 2022, "density": 11.34, "state_at_25C": "Solide", "group": 14, "period": 6, "row": 6, "col": 14, "category": "post-transition metal"},
    {"atomic_number": 83, "symbol": "Bi", "name": "Bismuth", "atomic_mass": 208.98040, "electron_configuration": "[Xe] 4f14 5d10 6s2 6p3", "electronegativity": 2.02, "atomic_radius": 143, "melting_point": 544.7, "boiling_point": 1837, "density": 9.78, "state_at_25C": "Solide", "group": 15, "period": 6, "row": 6, "col": 15, "category": "post-transition metal"},
    {"atomic_number": 84, "symbol": "Po", "name": "Polonium", "atomic_mass": 209, "electron_configuration": "[Xe] 4f14 5d10 6s2 6p4", "electronegativity": 2.0, "atomic_radius": 140, "melting_point": 527, "boiling_point": 1235, "density": 9.2, "state_at_25C": "Solide", "group": 16, "period": 6, "row": 6, "col": 16, "category": "métalloïde"},
    {"atomic_number": 85, "symbol": "At", "name": "Astate", "atomic_mass": 210, "electron_configuration": "[Xe] 4f14 5d10 6s2 6p5", "electronegativity": 2.2, "atomic_radius": 150, "melting_point": 575, "boiling_point": 610, "density": 7.0, "state_at_25C": "Solide", "group": 17, "period": 6, "row": 6, "col": 17, "category": "halogène"},
    {"atomic_number": 86, "symbol": "Rn", "name": "Radon", "atomic_mass": 222, "electron_configuration": "[Xe] 4f14 5d10 6s2 6p6", "electronegativity": None, "atomic_radius": 120, "melting_point": 202, "boiling_point": 211.45, "density": 0.00973, "state_at_25C": "Gaz", "group": 18, "period": 6, "row": 6, "col": 18, "category": "gaz noble"},
    {"atomic_number": 87, "symbol": "Fr", "name": "Francium", "atomic_mass": 223, "electron_configuration": "[Rn] 7s1", "electronegativity": 0.7, "atomic_radius": 260, "melting_point": 300, "boiling_point": 950, "density": 2.48, "state_at_25C": "Solide (estimé)", "group": 1, "period": 7, "row": 7, "col": 1, "category": "métal alcalin"},
    {"atomic_number": 88, "symbol": "Ra", "name": "Radium", "atomic_mass": 226, "electron_configuration": "[Rn] 7s2", "electronegativity": 0.9, "atomic_radius": 215, "melting_point": 973, "boiling_point": 2010, "density": 5.5, "state_at_25C": "Solide", "group": 2, "period": 7, "row": 7, "col": 2, "category": "métal alcalino-terreux"},
    {"atomic_number": 89, "symbol": "Ac", "name": "Actinium", "atomic_mass": 227, "electron_configuration": "[Rn] 6d1 7s2", "electronegativity": 1.1, "atomic_radius": 188, "melting_point": 1323, "boiling_point": 3471, "density": 10.07, "state_at_25C": "Solide", "group": 3, "period": 7, "row": 7, "col": 3, "category": "actinide"},
    {"atomic_number": 89, "symbol": "Ac", "name": "Actinium", "atomic_mass": 227, "electron_configuration": "[Rn] 6d1 7s2", "electronegativity": 1.1, "atomic_radius": 188, "melting_point": 1323, "boiling_point": 3471, "density": 10.07, "state_at_25C": "Solide", "group": 3, "period": 7, "row": 9, "col": 3, "category": "actinide"},
    {"atomic_number": 90, "symbol": "Th", "name": "Thorium", "atomic_mass": 232.0377, "electron_configuration": "[Rn] 6d2 7s2", "electronegativity": 1.3, "atomic_radius": 179, "melting_point": 2023, "boiling_point": 5061, "density": 11.72, "state_at_25C": "Solide", "group": 3, "period": 7, "row": 9, "col": 4, "category": "actinide"},
    {"atomic_number": 91, "symbol": "Pa", "name": "Protactinium", "atomic_mass": 231.03588, "electron_configuration": "[Rn] 5f2 6d1 7s2", "electronegativity": 1.5, "atomic_radius": 169, "melting_point": 1841, "boiling_point": 4300, "density": 15.37, "state_at_25C": "Solide", "group": 3, "period": 7, "row": 9, "col": 5, "category": "actinide"},
    {"atomic_number": 92, "symbol": "U", "name": "Uranium", "atomic_mass": 238.02891, "electron_configuration": "[Rn] 5f3 6d1 7s2", "electronegativity": 1.38, "atomic_radius": 175, "melting_point": 1405.3, "boiling_point": 4404, "density": 19.05, "state_at_25C": "Solide", "group": 3, "period": 7, "row": 9, "col": 6, "category": "actinide"},
    {"atomic_number": 93, "symbol": "Np", "name": "Neptunium", "atomic_mass": 237, "electron_configuration": "[Rn] 5f4 6d1 7s2", "electronegativity": 1.36, "atomic_radius": 175, "melting_point": 917, "boiling_point": 4273, "density": 20.45, "state_at_25C": "Solide", "group": 3, "period": 7, "row": 9, "col": 7, "category": "actinide"},
    {"atomic_number": 94, "symbol": "Pu", "name": "Plutonium", "atomic_mass": 244, "electron_configuration": "[Rn] 5f6 7s2", "electronegativity": 1.28, "atomic_radius": 175, "melting_point": 912.5, "boiling_point": 3235, "density": 19.84, "state_at_25C": "Solide", "group": 3, "period": 7, "row": 9, "col": 8, "category": "actinide"},
    {"atomic_number": 95, "symbol": "Am", "name": "Américium", "atomic_mass": 243, "electron_configuration": "[Rn] 5f7 7s2", "electronegativity": 1.3, "atomic_radius": 175, "melting_point": 1449, "boiling_point": 2607, "density": 13.67, "state_at_25C": "Solide", "group": 3, "period": 7, "row": 9, "col": 9, "category": "actinide"},
    {"atomic_number": 96, "symbol": "Cm", "name": "Curium", "atomic_mass": 247, "electron_configuration": "[Rn] 5f7 6d1 7s2", "electronegativity": 1.3, "atomic_radius": 171, "melting_point": 1618, "boiling_point": 3383, "density": 13.51, "state_at_25C": "Solide", "group": 3, "period": 7, "row": 9, "col": 10, "category": "actinide"},
    {"atomic_number": 97, "symbol": "Bk", "name": "Berkélium", "atomic_mass": 247, "electron_configuration": "[Rn] 5f9 7s2", "electronegativity": 1.3, "atomic_radius": 168, "melting_point": 1259, "boiling_point": 2900, "density": 14.78, "state_at_25C": "Solide", "group": 3, "period": 7, "row": 9, "col": 11, "category": "actinide"},
    {"atomic_number": 98, "symbol": "Cf", "name": "Californium", "atomic_mass": 251, "electron_configuration": "[Rn] 5f10 7s2", "electronegativity": 1.3, "atomic_radius": 168, "melting_point": 1173, "boiling_point": 1743, "density": 15.1, "state_at_25C": "Solide", "group": 3, "period": 7, "row": 9, "col": 12, "category": "actinide"},
    {"atomic_number": 99, "symbol": "Es", "name": "Einsteinium", "atomic_mass": 252, "electron_configuration": "[Rn] 5f11 7s2", "electronegativity": 1.3, "atomic_radius": 165, "melting_point": 1133, "boiling_point": 1269, "density": 8.84, "state_at_25C": "Solide", "group": 3, "period": 7, "row": 9, "col": 13, "category": "actinide"},
    {"atomic_number": 100, "symbol": "Fm", "name": "Fermium", "atomic_mass": 257, "electron_configuration": "[Rn] 5f12 7s2", "electronegativity": 1.3, "atomic_radius": 157, "melting_point": 1800, "boiling_point": None, "density": 20.0, "state_at_25C": "Solide", "group": 3, "period": 7, "row": 9, "col": 14, "category": "actinide"},
    {"atomic_number": 101, "symbol": "Md", "name": "Mendélévium", "atomic_mass": 258, "electron_configuration": "[Rn] 5f13 7s2", "electronegativity": 1.3, "atomic_radius": 155, "melting_point": 1100, "boiling_point": None, "density": 23.2, "state_at_25C": "Solide", "group": 3, "period": 7, "row": 9, "col": 15, "category": "actinide"},
    {"atomic_number": 102, "symbol": "No", "name": "Nobelium", "atomic_mass": 259, "electron_configuration": "[Rn] 5f14 7s2", "electronegativity": 1.3, "atomic_radius": 149, "melting_point": 1100, "boiling_point": None, "density": 9.9, "state_at_25C": "Solide", "group": 3, "period": 7, "row": 9, "col": 16, "category": "actinide"},
    {"atomic_number": 103, "symbol": "Lr", "name": "Lawrencium", "atomic_mass": 266, "electron_configuration": "[Rn] 5f14 7s2 7p1", "electronegativity": 1.3, "atomic_radius": 162, "melting_point": 1900, "boiling_point": None, "density": 15.6, "state_at_25C": "Solide", "group": 3, "period": 7, "row": 9, "col": 17, "category": "actinide"},
    {"atomic_number": 104, "symbol": "Rf", "name": "Rutherfordium", "atomic_mass": 267, "electron_configuration": "[Rn] 5f14 6d2 7s2", "electronegativity": None, "atomic_radius": 152, "melting_point": None, "boiling_point": None, "density": 23.2, "state_at_25C": "Solide", "group": 4, "period": 7, "row": 7, "col": 4, "category": "métal de transition"},
    {"atomic_number": 105, "symbol": "Db", "name": "Dubnium", "atomic_mass": 268, "electron_configuration": "[Rn] 5f14 6d3 7s2", "electronegativity": None, "atomic_radius": 145, "melting_point": None, "boiling_point": None, "density": 29.3, "state_at_25C": "Solide", "group": 5, "period": 7, "row": 7, "col": 5, "category": "métal de transition"},
    {"atomic_number": 106, "symbol": "Sg", "name": "Seaborgium", "atomic_mass": 269, "electron_configuration": "[Rn] 5f14 6d4 7s2", "electronegativity": None, "atomic_radius": 144, "melting_point": None, "boiling_point": None, "density": 35, "state_at_25C": "Solide", "group": 6, "period": 7, "row": 7, "col": 6, "category": "métal de transition"},
    {"atomic_number": 107, "symbol": "Bh", "name": "Bohrium", "atomic_mass": 270, "electron_configuration": "[Rn] 5f14 6d5 7s2", "electronegativity": None, "atomic_radius": 143, "melting_point": None, "boiling_point": None, "density": 37.1, "state_at_25C": "Solide", "group": 7, "period": 7, "row": 7, "col": 7, "category": "métal de transition"},
    {"atomic_number": 108, "symbol": "Hs", "name": "Hassium", "atomic_mass": 269, "electron_configuration": "[Rn] 5f14 6d6 7s2", "electronegativity": None, "atomic_radius": 138, "melting_point": None, "boiling_point": None, "density": 40.7, "state_at_25C": "Solide", "group": 8, "period": 7, "row": 7, "col": 8, "category": "métal de transition"},
    {"atomic_number": 109, "symbol": "Mt", "name": "Meitnérium", "atomic_mass": 278, "electron_configuration": "[Rn] 5f14 6d7 7s2", "electronegativity": None, "atomic_radius": 138, "melting_point": None, "boiling_point": None, "density": 37.4, "state_at_25C": "Solide", "group": 9, "period": 7, "row": 7, "col": 9, "category": "métal de transition"},
    {"atomic_number": 110, "symbol": "Ds", "name": "Darmstadtium", "atomic_mass": 281, "electron_configuration": "[Rn] 5f14 6d8 7s2", "electronegativity": None, "atomic_radius": 138, "melting_point": None, "boiling_point": None, "density": 34.8, "state_at_25C": "Solide", "group": 10, "period": 7, "row": 7, "col": 10, "category": "métal de transition"},
    {"atomic_number": 111, "symbol": "Rg", "name": "Roentgénium", "atomic_mass": 282, "electron_configuration": "[Rn] 5f14 6d9 7s2", "electronegativity": None, "atomic_radius": 134, "melting_point": None, "boiling_point": None, "density": 28.7, "state_at_25C": "Solide", "group": 11, "period": 7, "row": 7, "col": 11, "category": "métal de transition"},
    {"atomic_number": 112, "symbol": "Cn", "name": "Copernicium", "atomic_mass": 285, "electron_configuration": "[Rn] 5f14 6d10 7s2", "electronegativity": None, "atomic_radius": 135, "melting_point": 300, "boiling_point": 340, "density": 23.7, "state_at_25C": "Solide (estimé)", "group": 12, "period": 7, "row": 7, "col": 12, "category": "métal de transition"},
    {"atomic_number": 113, "symbol": "Nh", "name": "Nihonium", "atomic_mass": 286, "electron_configuration": "[Rn] 5f14 6d10 7s2 7p1", "electronegativity": None, "atomic_radius": 156, "melting_point": 700, "boiling_point": 1430, "density": 16.0, "state_at_25C": "Solide", "group": 13, "period": 7, "row": 7, "col": 13, "category": "post-transition metal"},
    {"atomic_number": 114, "symbol": "Fl", "name": "Flerovium", "atomic_mass": 289, "electron_configuration": "[Rn] 5f14 6d10 7s2 7p2", "electronegativity": None, "atomic_radius": 173, "melting_point": 300, "boiling_point": 420, "density": 14.0, "state_at_25C": "Solide (estimé)", "group": 14, "period": 7, "row": 7, "col": 14, "category": "post-transition metal"},
    {"atomic_number": 115, "symbol": "Mc", "name": "Moscovium", "atomic_mass": 290, "electron_configuration": "[Rn] 5f14 6d10 7s2 7p3", "electronegativity": None, "atomic_radius": 170, "melting_point": 500, "boiling_point": 1400, "density": 13.5, "state_at_25C": "Solide", "group": 15, "period": 7, "row": 7, "col": 15, "category": "post-transition metal"},
    {"atomic_number": 116, "symbol": "Lv", "name": "Livermorium", "atomic_mass": 293, "electron_configuration": "[Rn] 5f14 6d10 7s2 7p4", "electronegativity": None, "atomic_radius": 180, "melting_point": 500, "boiling_point": 1200, "density": 12.9, "state_at_25C": "Solide", "group": 16, "period": 7, "row": 7, "col": 16, "category": "post-transition metal"},
    {"atomic_number": 117, "symbol": "Ts", "name": "Tennessine", "atomic_mass": 294, "electron_configuration": "[Rn] 5f14 6d10 7s2 7p5", "electronegativity": None, "atomic_radius": 170, "melting_point": 600, "boiling_point": 950, "density": 7.2, "state_at_25C": "Solide", "group": 17, "period": 7, "row": 7, "col": 17, "category": "halogène"},
    {"atomic_number": 118, "symbol": "Og", "name": "Oganesson", "atomic_mass": 294, "electron_configuration": "[Rn] 5f14 6d10 7s2 7p6", "electronegativity": None, "atomic_radius": 152, "melting_point": 325, "boiling_point": 450, "density": 0.0, "state_at_25C": "Gaz (estimé)", "group": 18, "period": 7, "row": 7, "col": 18, "category": "gaz noble"},
]

# =============================================================================
# Données de chimie computationnelle — enrichissement des éléments
# Данные вычислительной химии — обогащение записей об элементах
#
# FR : Cette section ajoute, pour chaque élément, les propriétés pertinentes
#      pour un calcul quantique : pseudopotentiels, bases, polarisabilité, etc.
#      J'ai délibérément séparé ces données du tableau ELEMENTS principal
#      pour ne pas alourdir la définition de base avec des champs spécialisés.
# RU : В этом разделе для каждого элемента добавляются свойства, важные
#      для квантового расчёта: псевдопотенциалы, базисные наборы,
#      поляризуемость и т.д. Я намеренно отделил эти данные от основного
#      списка ELEMENTS, чтобы не перегружать базовое определение.
# =============================================================================

# FR : La polarisabilité statique α (en Å³) mesure la déformabilité du nuage
#      électronique. C'est un paramètre clé pour les champs de force (AMBER,
#      OPLS) et pour estimer les interactions de dispersion London.
#      Valeurs issues du CRC Handbook et de la base NIST.
# RU : Статическая поляризуемость α (в Å³) измеряет деформируемость
#      электронного облака. Это ключевой параметр для силовых полей (AMBER,
#      OPLS) и для оценки дисперсионных взаимодействий Лондона.
#      Значения взяты из CRC Handbook и базы данных NIST.
_POLARISABILITE = {
    1: 0.667, 2: 0.205, 3: 24.3, 4: 5.60, 5: 3.03, 6: 1.76, 7: 1.10, 8: 0.802,
    9: 0.557, 10: 0.396, 11: 24.08, 12: 10.6, 13: 6.8, 14: 5.38, 15: 3.63,
    16: 2.90, 17: 2.18, 18: 1.64, 19: 43.4, 20: 22.8, 21: 17.8, 22: 14.6,
    23: 12.4, 24: 11.6, 25: 9.4, 26: 8.4, 27: 7.5, 28: 6.8, 29: 6.1, 30: 5.75,
    31: 8.12, 32: 6.07, 33: 4.31, 34: 3.77, 35: 3.05, 36: 2.484, 37: 47.3,
    38: 27.6, 39: 22.7, 40: 17.9, 41: 15.7, 42: 12.8, 43: 11.4, 44: 9.6,
    45: 8.6, 46: 4.8, 47: 7.2, 48: 7.2, 49: 10.2, 50: 7.7, 51: 6.6, 52: 5.5,
    53: 5.35, 54: 4.044, 55: 59.6, 56: 39.7, 57: 31.1, 58: 29.6, 59: 28.2,
    60: 26.9, 61: 25.7, 62: 24.5, 63: 23.5, 64: 22.7, 65: 21.8, 66: 20.9,
    67: 20.0, 68: 19.0, 69: 18.1, 70: 17.1, 71: 16.5, 72: 16.2, 73: 13.1,
    74: 11.1, 75: 9.7, 76: 8.5, 77: 7.6, 78: 6.5, 79: 5.8, 80: 5.7, 81: 7.6,
    82: 6.8, 83: 7.4, 84: 6.8, 85: 6.0, 86: 5.3, 87: 47.0, 88: 38.3, 89: 32.1,
    90: 32.1, 91: 25.0, 92: 24.9, 93: 24.8, 94: 24.5, 95: 23.3, 96: 23.0,
    97: 22.7, 98: 20.5, 99: 19.7, 100: 18.9, 101: 18.2, 102: 17.5, 103: 16.8,
    104: 16.0, 105: 15.0, 106: 14.0, 107: 13.0, 108: 12.0, 109: 11.0, 110: 10.5,
    111: 10.0, 112: 9.5, 113: 9.0, 114: 8.5, 115: 8.0, 116: 7.5, 117: 7.0, 118: 6.5,
}

# FR : États d'oxydation pertinents pour la modélisation moléculaire.
#      J'ai volontairement exclu les états très rares (ex. +8 pour Xe) qui
#      n'apparaissent pas dans les systèmes modélisés en pratique.
#      En DFT, connaître l'état d'oxydation est indispensable pour définir
#      la charge totale du système et éviter une convergence SCF incorrecte.
# RU : Степени окисления, важные для молекулярного моделирования.
#      Я намеренно исключил очень редкие состояния, которые практически
#      не встречаются в моделируемых системах. В DFT знание степени
#      окисления необходимо для правильного задания заряда системы
#      и предотвращения некорректной SCF-сходимости.
_ETATS_OX = {
    1: "−1, +1", 2: "0", 3: "+1", 4: "+2", 5: "+3", 6: "+2, +4",
    7: "−3, +1, +2, +3, +4, +5", 8: "−2", 9: "−1", 10: "0",
    11: "+1", 12: "+2", 13: "+3", 14: "+2, +4", 15: "−3, +3, +5",
    16: "−2, +2, +4, +6", 17: "−1, +1, +3, +5, +7", 18: "0",
    19: "+1", 20: "+2", 21: "+3", 22: "+2, +3, +4", 23: "+2, +3, +4, +5",
    24: "+2, +3, +6", 25: "+2, +3, +4, +7", 26: "+2, +3", 27: "+2, +3",
    28: "+2, +3", 29: "+1, +2", 30: "+2", 31: "+3", 32: "+2, +4",
    33: "−3, +3, +5", 34: "−2, +2, +4, +6", 35: "−1, +1, +3, +5",
    36: "0, +2", 37: "+1", 38: "+2", 39: "+3", 40: "+2, +4", 41: "+3, +5",
    42: "+2, +3, +4, +6", 43: "+4, +7", 44: "+2, +3, +4, +8", 45: "+3",
    46: "0, +2, +4", 47: "+1", 48: "+2", 49: "+3", 50: "+2, +4", 51: "+3, +5",
    52: "−2, +2, +4, +6", 53: "−1, +1, +3, +5, +7", 54: "0, +2",
    55: "+1", 56: "+2", 57: "+3", 58: "+3, +4", 59: "+3", 60: "+3",
    61: "+3", 62: "+2, +3", 63: "+2, +3", 64: "+3", 65: "+3, +4",
    66: "+3", 67: "+3", 68: "+3", 69: "+3", 70: "+2, +3", 71: "+3",
    72: "+4", 73: "+5", 74: "+4, +6", 75: "+4, +7", 76: "+3, +4, +8",
    77: "+3, +4", 78: "0, +2, +4", 79: "+1, +3", 80: "+1, +2", 81: "+1, +3",
    82: "+2, +4", 83: "+3, +5", 84: "+2, +4", 85: "−1, +1", 86: "0",
    87: "+1", 88: "+2", 89: "+3", 90: "+4", 91: "+3, +4, +5",
    92: "+3, +4, +5, +6", 93: "+3, +4, +5, +6, +7", 94: "+3, +4, +5, +6",
    95: "+3, +4, +5, +6", 96: "+3", 97: "+3, +4", 98: "+2, +3, +4",
    99: "+2, +3", 100: "+2, +3", 101: "+2, +3", 102: "+2, +3", 103: "+3",
    104: "+4", 105: "+5", 106: "+6", 107: "+7", 108: "+8", 109: "+3, +6",
    110: "+6", 111: "+1, +3", 112: "+2", 113: "+1, +3", 114: "+2, +4",
    115: "+1, +3", 116: "+2", 117: "−1, +1, +3, +5", 118: "0",
}


# FR : Classification du traitement des électrons de cœur selon Z.
#      Pour Z ≤ 18, tous les électrons sont traités explicitement (calcul
#      tous-électrons) : le coût est faible et la précision maximale.
#      Au-delà, on remplace les électrons de cœur par un ECP (Effective Core
#      Potential) qui reproduit leurs effets sur la valence, ce qui réduit
#      considérablement le temps de calcul.
#      Pour Z ≥ 87, les effets relativistes (contraction des orbitales s,
#      expansion des orbitales d/f) sont si importants qu'un ECP relativiste
#      ou un hamiltonien à 4 composantes devient indispensable.
# RU : Классификация обработки остовных электронов в зависимости от Z.
#      При Z ≤ 18 все электроны обрабатываются явно (all-electron расчёт):
#      стоимость мала, точность максимальна. При больших Z остовные
#      электроны заменяются псевдопотенциалом (ECP), который воспроизводит
#      их влияние на валентные электроны и значительно сокращает время
#      расчёта. При Z ≥ 87 релятивистские эффекты (сжатие s-орбиталей,
#      расширение d/f) столь значительны, что требуется релятивистский
#      ECP или 4-компонентный гамильтониан.
def _ecp_type(z):
    if z <= 18:
        return "Tous-électrons"
    elif z <= 36:
        return "ECP optionnel"
    elif z <= 54:
        return "ECP recommandé"
    elif z <= 86:
        return "ECP requis"
    else:
        return "ECP/relativiste"


# FR : Sélection des bases selon Z et le traitement ECP associé.
#      Pour les éléments légers (Z ≤ 18), les bases de Dunning (cc-pVTZ)
#      et de Weigend-Ahlrichs (def2-TZVP) offrent le meilleur compromis
#      précision/coût. Pour les métaux lourds et les lanthanides/actinides,
#      j'utilise les bases SARC optimisées pour les hamiltoniens DKH2 et
#      ZORA, car les bases Pople ou Dunning ne couvrent pas ces éléments.
# RU : Выбор базисных наборов в зависимости от Z и соответствующего ECP.
#      Для лёгких элементов (Z ≤ 18) базисы Даннинга (cc-pVTZ) и
#      Вейганда-Альрихса (def2-TZVP) дают наилучший баланс точности
#      и стоимости. Для тяжёлых металлов и лантаноидов/актиноидов
#      используются базисы SARC, оптимизированные для гамильтонианов
#      DKH2 и ZORA, поскольку базисы Попла или Даннинга не охватывают
#      эти элементы.
def _basis(z):
    if z <= 2:
        return "cc-pVTZ, aug-cc-pVTZ, 6-311G**"
    elif z <= 10:
        return "cc-pVTZ, def2-TZVP, aug-cc-pVTZ"
    elif z <= 18:
        return "cc-pVTZ, def2-TZVP, 6-311+G**"
    elif z <= 36:
        return "def2-TZVP, def2-SVP"
    elif z <= 54:
        return "def2-TZVP, def2-TZVPP"
    elif 55 <= z <= 57 or 72 <= z <= 86:
        return "def2-TZVPP, SARC-DKH2"
    elif 58 <= z <= 71:
        return "SARC-DKH2, ANO-RCC-VTZP"
    elif 87 <= z <= 89 or z >= 104:
        return "SARC2-QZV-DKH2, x2c-TZVPPall"
    else:
        return "SARC-DKH2, ANO-RCC-VTZP"


# FR : Pseudopotentiels Stuttgart/MDF (energy-consistent, avec correction
#      relativiste par ajustement multi-configuration Dirac-Fock).
#      Le nombre après "ECP-" indique combien d'électrons de cœur sont
#      remplacés : ECP-10 pour K-Kr (cœur [Ne]), ECP-28 pour Rb-Xe
#      (cœur [Ar]+3d), etc. Ces ECP sont disponibles dans Gaussian,
#      ORCA et Turbomole via le mot-clé SDD ou via Basis Set Exchange.
# RU : Псевдопотенциалы Stuttgart/MDF (energy-consistent, с релятивистской
#      поправкой на основе многоконфигурационного метода Дирака-Фока).
#      Число после "ECP-" указывает, сколько остовных электронов замещается:
#      ECP-10 для K-Kr (остов [Ne]), ECP-28 для Rb-Xe (остов [Ar]+3d) и т.д.
#      Эти ECP доступны в Gaussian, ORCA и Turbomole через ключевое слово
#      SDD или через Basis Set Exchange.
def _pseudo(z):
    if z <= 18:
        return "Aucun"
    elif z <= 36:
        return "ECP-10 (Stuttgart/MDF)"
    elif z <= 54:
        return "ECP-28 (Stuttgart/MDF)"
    elif z <= 71:
        return "ECP-28 / ECP-46 (Stuttgart)"
    elif z <= 86:
        return "ECP-60 (Stuttgart/MDF)"
    elif z <= 103:
        return "ECP-78 (Stuttgart/MDF)"
    else:
        return "ECP-92 (Stuttgart/MDF)"


# FR : Première énergie d'ionisation IE₁ (en eV), source NIST.
#      C'est l'énergie nécessaire pour arracher un électron à l'atome neutre
#      en phase gazeuse : A → A⁺ + e⁻. En chimie computationnelle, IE₁ sert
#      à valider les potentiels d'ionisation calculés et à paramétrer les
#      champs de force. Les valeurs Z > 103 sont des estimations théoriques.
# RU : Первый потенциал ионизации IE₁ (в эВ), источник — NIST.
#      Это энергия, необходимая для отрыва электрона от нейтрального атома
#      в газовой фазе: A → A⁺ + e⁻. В вычислительной химии IE₁ используется
#      для валидации рассчитанных потенциалов ионизации и параметризации
#      силовых полей. Значения для Z > 103 — теоретические оценки.
_IE1 = {
    1: 13.598, 2: 24.587, 3: 5.392, 4: 9.323, 5: 8.298, 6: 11.260,
    7: 14.534, 8: 13.618, 9: 17.423, 10: 21.565, 11: 5.139, 12: 7.646,
    13: 5.986, 14: 8.151, 15: 10.486, 16: 10.360, 17: 12.968, 18: 15.760,
    19: 4.341, 20: 6.113, 21: 6.562, 22: 6.828, 23: 6.746, 24: 6.767,
    25: 7.434, 26: 7.902, 27: 7.881, 28: 7.640, 29: 7.726, 30: 9.394,
    31: 5.999, 32: 7.900, 33: 9.815, 34: 9.752, 35: 11.814, 36: 13.999,
    37: 4.177, 38: 5.695, 39: 6.217, 40: 6.634, 41: 6.759, 42: 7.092,
    43: 7.280, 44: 7.360, 45: 7.459, 46: 8.337, 47: 7.576, 48: 8.994,
    49: 5.786, 50: 7.344, 51: 8.608, 52: 9.010, 53: 10.451, 54: 12.130,
    55: 3.894, 56: 5.212, 57: 5.577, 58: 5.539, 59: 5.464, 60: 5.525,
    61: 5.582, 62: 5.644, 63: 5.670, 64: 6.150, 65: 5.864, 66: 5.939,
    67: 6.022, 68: 6.108, 69: 6.184, 70: 6.254, 71: 5.426, 72: 6.825,
    73: 7.550, 74: 7.864, 75: 7.834, 76: 8.438, 77: 8.967, 78: 8.959,
    79: 9.226, 80: 10.438, 81: 6.108, 82: 7.417, 83: 7.286, 84: 8.414,
    85: 9.320, 86: 10.748, 87: 4.073, 88: 5.278, 89: 5.170, 90: 6.307,
    91: 5.890, 92: 6.194, 93: 6.266, 94: 6.026, 95: 5.974, 96: 5.992,
    97: 6.198, 98: 6.282, 99: 6.420, 100: 6.500, 101: 6.580, 102: 6.650,
    103: 4.963, 104: 6.01, 105: 6.80, 106: 7.80, 107: 7.70, 108: 7.60,
    109: 8.70, 110: 9.60, 111: 10.60, 112: 11.97, 113: 7.30, 114: 8.50,
    115: 5.60, 116: 6.70, 117: 7.70, 118: 8.50,
}

# FR : Affinité électronique EA (en eV) : énergie libérée lors de la capture
#      d'un électron par l'atome neutre (A + e⁻ → A⁻). Une valeur None indique
#      que l'anion correspondant est instable en phase gazeuse (gaz nobles,
#      Be, Mg, Zn, Cd…). En modélisation des anions et des ligands chargés,
#      cette donnée est indispensable pour paramétrer correctement les charges.
# RU : Сродство к электрону EA (в эВ): энергия, выделяемая при захвате
#      электрона нейтральным атомом (A + e⁻ → A⁻). Значение None означает,
#      что соответствующий анион нестабилен в газовой фазе (благородные газы,
#      Be, Mg, Zn, Cd…). При моделировании анионов и заряженных лигандов
#      эта величина необходима для корректной параметризации зарядов.
_EA = {
    1: 0.754, 2: None, 3: 0.618, 4: None, 5: 0.280, 6: 1.263,
    7: None, 8: 1.461, 9: 3.401, 10: None, 11: 0.548, 12: None,
    13: 0.433, 14: 1.385, 15: 0.747, 16: 2.077, 17: 3.613, 18: None,
    19: 0.502, 20: 0.025, 21: 0.188, 22: 0.079, 23: 0.526, 24: 0.666,
    25: None, 26: 0.151, 27: 0.662, 28: 1.156, 29: 1.235, 30: None,
    31: 0.430, 32: 1.233, 33: 0.804, 34: 2.021, 35: 3.364, 36: None,
    37: 0.486, 38: 0.048, 39: 0.307, 40: 0.426, 41: 0.917, 42: 0.748,
    43: 0.550, 44: 1.050, 45: 1.137, 46: 0.562, 47: 1.302, 48: None,
    49: 0.300, 50: 1.112, 51: 1.047, 52: 1.971, 53: 3.059, 54: None,
    55: 0.472, 56: 0.145, 57: 0.470, 58: 0.500, 59: 0.962, 60: 0.950,
    61: None, 62: None, 63: None, 64: 0.137, 65: 1.165, 66: None,
    67: None, 68: None, 69: 1.029, 70: None, 71: 0.352, 72: 0.018,
    73: 0.322, 74: 0.816, 75: 0.150, 76: 1.100, 77: 1.565, 78: 2.128,
    79: 2.309, 80: None, 81: 0.200, 82: 0.364, 83: 0.942, 84: 1.900,
    85: 2.800, 86: None, 87: 0.486, 88: 0.100, 89: 0.350, 90: 0.608,
    91: 0.550, 92: 0.536, 93: 0.480, 94: None, 95: 0.100, 96: None,
    97: None, 98: None, 99: None, 100: None, 101: None, 102: None,
    103: None, 104: None, 105: None, 106: None, 107: None, 108: None,
    109: None, 110: None, 111: None, 112: None, 113: None, 114: None,
    115: None, 116: None, 117: None, 118: None,
}

# FR : Multiplicité de spin de l'état fondamental (2S+1), appliquant la
#      règle de Hund : maximiser S sur chaque sous-couche partiellement
#      remplie. Quelques cas particuliers : Cr (d⁵s¹, mult=7), Mo (idem),
#      Nb (d⁴s¹, mult=6), Gd (f⁷d¹, mult=9). En DFT, cette valeur doit
#      être spécifiée comme "multiplicité" dans l'en-tête du calcul ; une
#      erreur ici entraîne une solution SCF de mauvaise symétrie de spin.
#      Pour les éléments f, j'applique la règle des "trous" : f^n avec n>7
#      a le même nombre de spins non appariés que f^(14-n).
# RU : Мультиплетность спинового основного состояния (2S+1) по правилу
#      Хунда: максимизация S на каждой частично заполненной подоболочке.
#      Особые случаи: Cr (d⁵s¹, mult=7), Mo (аналогично), Nb (d⁴s¹,
#      mult=6), Gd (f⁷d¹, mult=9). В DFT это значение задаётся как
#      "multiplicity" в заголовке расчёта; ошибка здесь приводит к SCF-
#      решению с неверной спиновой симметрией. Для f-элементов применяется
#      правило «дырок»: f^n при n>7 имеет столько же неспаренных спинов,
#      сколько f^(14-n).
_SPIN_MULT = {
    1: 2, 2: 1, 3: 2, 4: 1, 5: 2, 6: 3, 7: 4, 8: 3, 9: 2, 10: 1,
    11: 2, 12: 1, 13: 2, 14: 3, 15: 4, 16: 3, 17: 2, 18: 1,
    19: 2, 20: 1, 21: 2, 22: 3, 23: 4, 24: 7, 25: 6, 26: 5, 27: 4, 28: 3, 29: 2, 30: 1,
    31: 2, 32: 3, 33: 4, 34: 3, 35: 2, 36: 1,
    37: 2, 38: 1, 39: 2, 40: 3, 41: 6, 42: 7, 43: 6, 44: 5, 45: 4, 46: 1, 47: 2, 48: 1,
    49: 2, 50: 3, 51: 4, 52: 3, 53: 2, 54: 1,
    55: 2, 56: 1,
    57: 2, 58: 3, 59: 4, 60: 5, 61: 6, 62: 7, 63: 8, 64: 9, 65: 6, 66: 5, 67: 4, 68: 3, 69: 2, 70: 1, 71: 2,
    72: 3, 73: 4, 74: 5, 75: 6, 76: 5, 77: 4, 78: 3, 79: 2, 80: 1,
    81: 2, 82: 3, 83: 4, 84: 3, 85: 2, 86: 1,
    87: 2, 88: 1,
    89: 2, 90: 3, 91: 4, 92: 5, 93: 6, 94: 7, 95: 8, 96: 9, 97: 6, 98: 5, 99: 4, 100: 3, 101: 2, 102: 1, 103: 2,
    104: 3, 105: 4, 106: 5, 107: 6, 108: 5, 109: 4, 110: 3, 111: 2, 112: 1,
    113: 2, 114: 3, 115: 4, 116: 3, 117: 2, 118: 1,
}

# FR : Rayons de van der Waals (en Å), principalement issus de Bondi (1964)
#      complétés par Alvarez (2013). Ces rayons définissent le volume exclu
#      autour d'un atome dans les champs de force non-liants (Lennard-Jones).
#      Ils servent aussi à détecter les contacts intermoléculaires dans les
#      analyses de structures cristallographiques (CSD, PDB).
#      Pour Z > 103, faute de données expérimentales, j'utilise 2.50 Å
#      comme estimation conservative.
# RU : Радиусы ван-дер-Ваальса (в Å), главным образом по Бонди (1964),
#      дополненные данными Альвареса (2013). Эти радиусы определяют
#      исключённый объём вокруг атома в невалентных силовых полях
#      (Леннард-Джонс). Они также используются для обнаружения
#      межмолекулярных контактов в кристаллографических структурах
#      (CSD, PDB). Для Z > 103, при отсутствии экспериментальных данных,
#      используется консервативная оценка 2.50 Å.
_VDW = {
    1: 1.20, 2: 1.40, 3: 1.82, 4: 1.53, 5: 1.92, 6: 1.70, 7: 1.55, 8: 1.52,
    9: 1.47, 10: 1.54, 11: 2.27, 12: 1.73, 13: 1.84, 14: 2.10, 15: 1.80,
    16: 1.80, 17: 1.75, 18: 1.88, 19: 2.75, 20: 2.31, 21: 2.15, 22: 2.11,
    23: 2.07, 24: 2.06, 25: 2.05, 26: 2.04, 27: 2.00, 28: 1.97, 29: 1.96,
    30: 2.01, 31: 1.87, 32: 2.11, 33: 1.85, 34: 1.90, 35: 1.85, 36: 2.02,
    37: 3.03, 38: 2.49, 39: 2.32, 40: 2.23, 41: 2.18, 42: 2.17, 43: 2.16,
    44: 2.13, 45: 2.10, 46: 2.10, 47: 2.11, 48: 2.18, 49: 1.93, 50: 2.17,
    51: 2.06, 52: 2.06, 53: 1.98, 54: 2.16, 55: 3.43, 56: 2.68, 57: 2.43,
    58: 2.42, 59: 2.40, 60: 2.39, 61: 2.38, 62: 2.36, 63: 2.35, 64: 2.34,
    65: 2.33, 66: 2.31, 67: 2.30, 68: 2.29, 69: 2.27, 70: 2.26, 71: 2.24,
    72: 2.23, 73: 2.22, 74: 2.18, 75: 2.16, 76: 2.16, 77: 2.13, 78: 2.13,
    79: 2.14, 80: 2.23, 81: 1.96, 82: 2.02, 83: 2.07, 84: 1.97, 85: 2.02,
    86: 2.20, 87: 3.48, 88: 2.83, 89: 2.47, 90: 2.45, 91: 2.43, 92: 2.41,
    93: 2.39, 94: 2.43, 95: 2.44, 96: 2.45, 97: 2.44, 98: 2.45, 99: 2.45,
    100: 2.45, 101: 2.46, 102: 2.46, 103: 2.46, 104: 2.50, 105: 2.50,
    106: 2.50, 107: 2.50, 108: 2.50, 109: 2.50, 110: 2.50, 111: 2.50,
    112: 2.50, 113: 2.50, 114: 2.50, 115: 2.50, 116: 2.50, 117: 2.50, 118: 2.50,
}

# FR : Noms russes des 118 éléments, utilisés dans l'interface en langue russe.
#      J'ai conservé la translittération officielle adoptée par l'IUPAC et l'ИЮПАК.
# RU : Русские названия 118 элементов, используемые в русскоязычном интерфейсе.
_NAME_RU = {
    1: "Водород", 2: "Гелий", 3: "Литий", 4: "Бериллий", 5: "Бор",
    6: "Углерод", 7: "Азот", 8: "Кислород", 9: "Фтор", 10: "Неон",
    11: "Натрий", 12: "Магний", 13: "Алюминий", 14: "Кремний", 15: "Фосфор",
    16: "Сера", 17: "Хлор", 18: "Аргон", 19: "Калий", 20: "Кальций",
    21: "Скандий", 22: "Титан", 23: "Ванадий", 24: "Хром", 25: "Марганец",
    26: "Железо", 27: "Кобальт", 28: "Никель", 29: "Медь", 30: "Цинк",
    31: "Галлий", 32: "Германий", 33: "Мышьяк", 34: "Селен", 35: "Бром",
    36: "Криптон", 37: "Рубидий", 38: "Стронций", 39: "Иттрий", 40: "Цирконий",
    41: "Ниобий", 42: "Молибден", 43: "Технеций", 44: "Рутений", 45: "Родий",
    46: "Палладий", 47: "Серебро", 48: "Кадмий", 49: "Индий", 50: "Олово",
    51: "Сурьма", 52: "Теллур", 53: "Йод", 54: "Ксенон", 55: "Цезий",
    56: "Барий", 57: "Лантан", 58: "Церий", 59: "Празеодим", 60: "Неодим",
    61: "Прометий", 62: "Самарий", 63: "Европий", 64: "Гадолиний", 65: "Тербий",
    66: "Диспрозий", 67: "Гольмий", 68: "Эрбий", 69: "Тулий", 70: "Иттербий",
    71: "Лютеций", 72: "Гафний", 73: "Тантал", 74: "Вольфрам", 75: "Рений",
    76: "Осмий", 77: "Иридий", 78: "Платина", 79: "Золото", 80: "Ртуть",
    81: "Таллий", 82: "Свинец", 83: "Висмут", 84: "Полоний", 85: "Астат",
    86: "Радон", 87: "Франций", 88: "Радий", 89: "Актиний", 90: "Торий",
    91: "Протактиний", 92: "Уран", 93: "Нептуний", 94: "Плутоний", 95: "Америций",
    96: "Кюрий", 97: "Берклий", 98: "Калифорний", 99: "Эйнштейний", 100: "Фермий",
    101: "Менделевий", 102: "Нобелий", 103: "Лоуренсий", 104: "Резерфордий",
    105: "Дубний", 106: "Сиборгий", 107: "Борий", 108: "Хассий", 109: "Мейтнерий",
    110: "Дармштадтий", 111: "Рентгений", 112: "Коперниций", 113: "Нихоний",
    114: "Флеровий", 115: "Московий", 116: "Ливерморий", 117: "Теннессин",
    118: "Оганесон",
}

# FR : Dictionnaire de traductions FR/RU pour tous les textes de l'interface.
#      J'ai regroupé toutes les chaînes en un seul endroit pour faciliter la
#      maintenance : ajouter une langue (anglais, par exemple) ne nécessite
#      qu'un nouveau sous-dictionnaire, sans toucher aux callbacks.
# RU : Словарь переводов FR/RU для всех строк интерфейса. Я объединил все
#      строки в одном месте для удобства сопровождения: добавление нового
#      языка (например, английского) требует лишь нового подсловаря.
LANG = {
    "fr": {
        "title": "Tableau périodique interactif",
        "subtitle": "Explorez les 118 éléments chimiques avec leurs propriétés scientifiques et une interface responsive en français.",
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
    },
    "ru": {
        "title": "Интерактивная таблица Менделеева",
        "subtitle": "Исследуйте 118 химических элементов с их научными свойствами — интерфейс доступен на русском языке.",
        "detail_title": "Сведения об элементе",
        "click_hint": "Нажмите на ячейку таблицы, чтобы отобразить свойства элемента.",
        "group_ph": "Фильтр по группе",
        "group_label": "Группа",
        "block_ph": "Фильтр по блоку",
        "ecp_ph": "Фильтр по обработке ЭКП",
        "search_ph": "Поиск по названию или символу",
        "blocks": [
            {"label": "Блок s  (щелочные, щёлочноземельные, H, He)", "value": "s"},
            {"label": "Блок p  (неметаллы, галогены, благородные газы…)", "value": "p"},
            {"label": "Блок d  (переходные металлы)", "value": "d"},
            {"label": "Блок f  (лантаноиды и актиноиды)", "value": "f"},
        ],
        "ecps": [
            {"label": "Все электроны (Z ≤ 18)", "value": "Tous-électrons"},
            {"label": "ЭКП необязателен (Z 19–36)", "value": "ECP optionnel"},
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
            "ECP optionnel": "ЭКП необязателен",
            "ECP recommandé": "ЭКП рекомендуется",
            "ECP requis": "ЭКП необходим",
            "ECP/relativiste": "ЭКП / релятивистский",
        },
        "relat_values": {
            "Négligeable": "Пренебрежимо мал",
            "Faible (optionnel)": "Слабый (необязательно)",
            "Scalaire (DKH2 / ZORA)": "Скалярный (DKH2 / ZORA)",
            "Scalaire + spin-orbite partiel": "Скалярный + спин-орбитальный (частично)",
            "Spin-orbite requis (X2C / 4c-DHF)": "Спин-орбитальный необходим (X2C / 4c-DHF)",
        },
        "disp_values": {"D3BJ (Grimme)": "D3BJ (Гримме)", "N/A": "Н/П"},
        "pseudo_none": "Отсутствует",
        "sec_electronic": "Электронная структура",
        "sec_atomic": "Атомные свойства",
        "sec_compchem": "Вычислительное моделирование",
        "lbl_ox": "Степени окисления",
        "lbl_spin": "Мультиплетность (2S+1)",
        "lbl_ie1": "1-й потенциал ионизации",
        "lbl_ea": "Сродство к электрону",
        "lbl_alpha": "Поляризуемость (α)",
        "lbl_vdw": "Радиус ван-дер-Ваальса",
        "lbl_vol": "Молярный объём",
        "lbl_ecp": "Обработка ЭКП",
        "lbl_basis": "Рекомендуемые базисные наборы",
        "lbl_pseudo": "Псевдопотенциал",
        "lbl_func": "DFT-функционал",
        "lbl_disp": "Поправка на дисперсию",
        "lbl_relat": "Релятивистские эффекты",
        "lbl_group": "Группа",
        "lbl_period": "Период",
        "lbl_block": "Блок",
        "bse_link": "Basis Set Exchange →",
        "footer_data": "Научные данные: IUPAC, CRC Handbook, NIST · Basis Set Exchange (basissetexchange.org)",
        "footer_credit": "Разработано Saloua EL FAKIR — Магистратура, вычислительная химия",
        "hover_bloc": "Блок",
        "na": "Н/П",
    },
}


# FR : Attribution du bloc orbital (s/p/d/f) selon la configuration
#      électronique de l'état fondamental. J'utilise des ensembles Python
#      (set) plutôt que des conditions if/elif en cascade pour une lecture
#      plus claire. He est classé en bloc s malgré sa position en groupe 18,
#      conformément à la convention IUPAC. La sous-couche qui se remplit en
#      dernier détermine le bloc (règle de Klechkowski pour l'ordre de
#      remplissage, avec les exceptions connues : Cr, Cu, Pd, Au, etc.).
# RU : Определение орбитального блока (s/p/d/f) по электронной конфигурации
#      основного состояния. Я использую множества Python (set) вместо
#      каскадных if/elif для более чёткого чтения. He относится к блоку s
#      вопреки его положению в 18-й группе — в соответствии с соглашением
#      IUPAC. Блок определяется последней заполняемой подоболочкой (правило
#      Клечковского с известными исключениями: Cr, Cu, Pd, Au и др.).
def _block(z):
    s = {1, 2, 3, 4, 11, 12, 19, 20, 37, 38, 55, 56, 87, 88}
    p = set(range(5, 11)) | set(range(13, 19)) | set(range(31, 37)) | set(range(49, 55)) | set(range(81, 87)) | set(range(113, 119))
    d = set(range(21, 31)) | set(range(39, 49)) | set(range(72, 81)) | set(range(104, 113))
    if z in s:
        return "s"
    elif z in p:
        return "p"
    elif z in d:
        return "d"
    return "f"


# FR : Recommandation de fonctionnelle DFT selon le bloc et la période.
#      Pour H/He, CCSD(T) reste la référence "gold standard" abordable.
#      Pour le bloc p léger, B3LYP reste la fonctionnelle la plus utilisée
#      en chimie organique ; ωB97X-D et M06-2X sont plus précises pour les
#      barrières et les interactions non-covalentes.
#      Pour les métaux 3d, TPSS/TPSSh donne de meilleures géométries que
#      B3LYP ; M06-L est méta-GGA sans échange exact, adapté aux grands
#      systèmes. Pour les f-éléments (lanthanides/actinides), la
#      multiconfiguration est souvent inévitable : CASSCF/NEVPT2.
# RU : Рекомендация DFT-функционала в зависимости от блока и периода.
#      Для H/He CCSD(T) остаётся доступным «золотым стандартом».
#      Для лёгкого блока p B3LYP наиболее распространён в органической
#      химии; ωB97X-D и M06-2X точнее для барьеров и нековалентных
#      взаимодействий. Для 3d-металлов TPSS/TPSSh даёт лучшие геометрии,
#      чем B3LYP; M06-L — мета-GGA без точного обмена, подходит для
#      больших систем. Для f-элементов (лантаноиды/актиноиды)
#      многоконфигурационный подход часто неизбежен: CASSCF/NEVPT2.
def _functional(z):
    b = _block(z)
    if z <= 2:
        return "CCSD(T), MP2, B3LYP"
    elif b in ("s", "p") and z <= 36:
        return "B3LYP-D3BJ, ωB97X-D, M06-2X"
    elif b in ("s", "p"):
        return "PBE0-D3BJ, M06-2X"
    elif b == "d" and z <= 30:
        return "TPSS-D3BJ, TPSSh, M06-L"
    elif b == "d":
        return "PBE0-D3BJ, TPSS-D3BJ"
    elif b == "f" and z <= 71:
        return "CASSCF/NEVPT2, TPSS-D3BJ"
    return "CASSCF/NEVPT2, PBE0-D3BJ"


# FR : La correction de dispersion D3BJ (Grimme 2010) ajoute les interactions
#      de London (C6/R^6) manquantes dans les fonctionnelles GGA et hybrides.
#      Elle est indispensable pour les systèmes avec empilement aromatique,
#      liaisons hydrogène faibles, ou interactions hôte-invité. Les gaz
#      nobles n'ont pas de liaisons covalentes : D3BJ est sans objet.
# RU : Поправка на дисперсию D3BJ (Гримме 2010) добавляет взаимодействия
#      Лондона (C6/R^6), отсутствующие в GGA и гибридных функционалах.
#      Она необходима для систем с ароматическим стэкингом, слабыми
#      водородными связями или взаимодействиями хозяин-гость.
#      Благородные газы не образуют ковалентных связей: D3BJ неприменима.
def _dispersion(z):
    return "N/A" if z in {2, 10, 18, 36, 54, 86, 118} else "D3BJ (Grimme)"


# FR : Importance des effets relativistes selon Z. Pour Z > 54, la vitesse
#      des électrons 1s dépasse 60 % de c, ce qui contracte les orbitales s
#      (et indirectement expande les d/f). Conséquences pratiques : couleur
#      de l'or, fluidité du mercure à 25 °C, potentiel de réduction élevé
#      de Pt. Le hamiltonien scalaire DKH2 ou ZORA capture l'essentiel ;
#      pour Z ≥ 87, le couplage spin-orbite devient dominant et requiert
#      un traitement à deux ou quatre composantes (X2C, 4c-DHF).
# RU : Важность релятивистских эффектов в зависимости от Z. При Z > 54
#      скорость 1s-электронов превышает 60% от c, что приводит к сжатию
#      s-орбиталей (и косвенному расширению d/f). Практические следствия:
#      цвет золота, жидкость ртути при 25 °C, высокий восстановительный
#      потенциал Pt. Скалярный гамильтониан DKH2 или ZORA улавливает
#      основное; при Z ≥ 87 спин-орбитальная связь становится доминирующей
#      и требует двух- или четырёхкомпонентного подхода (X2C, 4c-DHF).
def _relativistic(z):
    if z <= 18:
        return "Négligeable"
    elif z <= 36:
        return "Faible (optionnel)"
    elif z <= 54:
        return "Scalaire (DKH2 / ZORA)"
    elif z <= 86:
        return "Scalaire + spin-orbite partiel"
    return "Spin-orbite requis (X2C / 4c-DHF)"


# FR : Enrichissement en place (in-place) de chaque dict d'élément.
#      Je modifie directement la liste ELEMENTS plutôt que de créer une
#      nouvelle structure, ce qui évite la duplication en mémoire.
#      Le préfixe "_" sur les variables de boucle (_el, _z, _d) indique
#      qu'elles sont temporaires et ne doivent pas être réutilisées après.
# RU : Обогащение каждого словаря элемента «на месте» (in-place).
#      Я модифицирую список ELEMENTS напрямую, а не создаю новую структуру,
#      что позволяет избежать дублирования в памяти. Префикс "_" у
#      переменных цикла (_el, _z, _d) означает, что они временные и не
#      должны использоваться за пределами цикла.
for _el in ELEMENTS:
    _z = _el["atomic_number"]
    _el["ecp_type"] = _ecp_type(_z)
    _el["basis_rec"] = _basis(_z)
    _el["pseudo"] = _pseudo(_z)
    _el["polarisabilite"] = _POLARISABILITE.get(_z)
    _el["etats_ox"] = _ETATS_OX.get(_z, "N/A")
    _d = _el.get("density")
    _el["volume_molaire"] = round(_el["atomic_mass"] / _d, 2) if _d and _d > 0 else None
    _el["block"] = _block(_z)
    _el["ie1"] = _IE1.get(_z)
    _el["ea"] = _EA.get(_z)
    _el["spin_mult"] = _SPIN_MULT.get(_z)
    _el["vdw_radius"] = _VDW.get(_z)
    _el["functional"] = _functional(_z)
    _el["dispersion"] = _dispersion(_z)
    _el["relativistic"] = _relativistic(_z)
    _el["name_ru"] = _NAME_RU.get(_z, _el["name"])

# FR : Palette de couleurs par catégorie chimique. J'ai choisi des teintes
#      pastel saturées sur fond sombre pour maximiser la lisibilité sans
#      fatiguer l'œil lors d'une utilisation prolongée. Chaque couleur
#      correspond à une famille chimique cohérente (alcalins orangés,
#      métaux de transition bleutés, gaz nobles bleu clair, etc.).
# RU : Цветовая палитра по химическим категориям. Я выбрал насыщенные
#      пастельные оттенки на тёмном фоне для максимальной читаемости
#      без усталости глаз при длительном использовании. Каждый цвет
#      соответствует связанному химическому семейству (оранжевый для
#      щелочных, голубой для переходных металлов, светло-голубой для
#      благородных газов и т.д.).
CATEGORY_COLORS = {
    "métal alcalin": "#ff8a65",
    "métal alcalino-terreux": "#ffb74d",
    "lanthanide": "#ba68c8",
    "actinide": "#ab47bc",
    "métal de transition": "#64b5f6",
    "post-transition metal": "#90a4ae",
    "métalloïde": "#aed581",
    "non-metal": "#a5d6a7",
    "halogène": "#4dd0e1",
    "gaz noble": "#81d4fa",
    "métal": "#b0bec5",
}

COLOR_DEFAULT = "#37474f"

# FR : Initialisation de l'application Dash. L'attribut "server" expose
#      l'objet Flask sous-jacent, nécessaire pour un déploiement en
#      production (Gunicorn, uWSGI). En développement, app.run_server()
#      suffit avec le rechargement automatique (debug=True).
# RU : Инициализация приложения Dash. Атрибут "server" открывает доступ
#      к базовому объекту Flask, необходимому для продакшн-деплоя
#      (Gunicorn, uWSGI). При разработке достаточно app.run_server()
#      с автоперезагрузкой (debug=True).
app = dash.Dash(__name__)
server = app.server

# FR : Conversion de la liste de dicts en DataFrame pandas pour permettre
#      les opérations vectorisées (filtrage booléen, map de couleurs).
#      La colonne "color" est calculée une seule fois au démarrage ;
#      fillna() gère les catégories inconnues avec la couleur par défaut.
# RU : Преобразование списка словарей в DataFrame pandas для векторных
#      операций (булева фильтрация, отображение цветов). Столбец "color"
#      вычисляется один раз при запуске; fillna() обрабатывает неизвестные
#      категории цветом по умолчанию.
df = pd.DataFrame(ELEMENTS)
df["color"] = df["category"].map(CATEGORY_COLORS).fillna(COLOR_DEFAULT)

app.layout = html.Div(
    className="app-container",
    children=[
        dcc.Store(id="lang", data="fr"),
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
                    "Explorez les 118 éléments chimiques avec leurs propriétés scientifiques et une interface responsive en français.",
                    id="app-subtitle",
                ),
            ],
        ),
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
                    className="detail-card",
                    children=[
                        html.H2("Détails de l'élément", id="detail-card-title"),
                        html.Div(
                            id="element-details",
                            className="details-content",
                            children=[
                                html.P("Cliquez sur une case du tableau pour afficher les propriétés de l'élément."),
                            ],
                        ),
                    ],
                ),
            ],
        ),
        html.Footer(
            className="footer",
            children=[
                html.P("Données scientifiques : IUPAC, CRC Handbook, NIST · Basis Set Exchange (basissetexchange.org)", id="footer-data"),
                html.P("Développé par Saloua EL FAKIR — Master 1 Chimie Informatique", className="footer-credit", id="footer-credit"),
            ],
        ),
    ],
)


# FR : Fonction centrale de rendu du tableau périodique.
#      J'ai choisi de représenter chaque case par un "shape" rectangulaire
#      en coordonnées de données plutôt que par un marqueur Scatter de taille
#      fixe en pixels. Avantage : la taille des cases reste identique quelle
#      que soit la résolution ou le zoom, car elle est définie en unités du
#      graphique (col ± 0.46, row ± 0.46). Un marqueur en pixels deviendrait
#      inégal dès que le rapport largeur/hauteur change.
#      Les éléments filtrés sont mis en évidence (opacité 1.0) tandis que les
#      autres sont estompés (opacité 0.14), ce qui guide visuellement l'œil
#      sans supprimer l'information de contexte.
# RU : Центральная функция отрисовки таблицы Менделеева.
#      Я представляю каждую ячейку прямоугольником "shape" в координатах
#      данных, а не маркером Scatter фиксированного размера в пикселях.
#      Преимущество: размер ячеек остаётся одинаковым при любом разрешении
#      или масштабе, поскольку задан в единицах графика (col ± 0.46,
#      row ± 0.46). Пиксельный маркер стал бы неравномерным при изменении
#      соотношения сторон. Отфильтрованные элементы выделяются (opacity 1.0),
#      остальные затемняются (opacity 0.14) — так взгляд направляется,
#      не теряя контекстной информации.
def build_periodic_figure(group_filter=None, block_filter=None, ecp_filter=None, search_value="", lang="fr"):
    search_value = (search_value or "").strip().lower()
    is_match = pd.Series(True, index=df.index)

    if group_filter is not None:
        is_match &= df["group"] == group_filter
    if block_filter is not None:
        is_match &= df["block"] == block_filter
    if ecp_filter is not None:
        is_match &= df["ecp_type"] == ecp_filter
    if search_value:
        # FR : En mode russe, la recherche porte aussi sur le nom russe.
        # RU : В русском режиме поиск охватывает и русское название.
        name_col = "name_ru" if lang == "ru" else "name"
        is_match &= df.apply(
            lambda row: search_value in row[name_col].lower() or search_value in row["symbol"].lower(),
            axis=1,
        )

    # FR : "customdata" transporte 20 champs par élément (indice 19 = nom russe),
    #      récupérés dans le callback de clic.
    # RU : "customdata" переносит 20 полей на элемент (индекс 19 = русское название).
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

    # FR : Dessin des cases. layer="below" est crucial : sans cela, les shapes
    #      s'affichent par-dessus les traces texte et masquent les symboles.
    #      scaleanchor="x" + scaleratio=1 sur l'axe y force des cases carrées.
    # RU : Отрисовка ячеек. layer="below" критически важен: без него shapes
    #      отображаются поверх текстовых трасс и скрывают символы элементов.
    #      scaleanchor="x" + scaleratio=1 на оси y обеспечивает квадратные ячейки.
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

    # FR : Trace invisible (marker transparent, size=2) : son seul rôle est de
    #      porter le texte du symbole centré et d'être la cible des événements
    #      clic/survol. textposition="middle center" centre le texte sur le
    #      marqueur, ce qui coïncide exactement avec le centre de la case.
    # RU : Невидимая трасса (прозрачный маркер, size=2): её единственная роль —
    #      нести текст символа по центру и быть целью событий клика/наведения.
    #      textposition="middle center" центрирует текст на маркере, что
    #      совпадает с центром ячейки.
    fig.add_trace(go.Scatter(
        x=df["col"],
        y=df["row"],
        mode="markers+text",
        marker=dict(size=2, color="rgba(0,0,0,0)", symbol="square"),
        text=df["symbol"],
        textposition="middle center",
        textfont=dict(
            color=["rgba(255,255,255,1)" if m else "rgba(255,255,255,0.18)" for m in is_match],
            size=11,
            family="Inter",
        ),
        customdata=customdata_cols,
        hovertemplate=hover,
        showlegend=False,
    ))

    # FR : Seconde trace pour les numéros atomiques en petit (Z) en haut à
    #      gauche de chaque case. Je décale de (-0.33, -0.33) en coordonnées
    #      de données pour rester dans la case. hoverinfo="skip" évite
    #      que cette trace déclenche des infobulles parasites.
    # RU : Вторая трасса для малых атомных номеров (Z) в верхнем левом углу
    #      каждой ячейки. Смещение (-0.33, -0.33) в координатах данных
    #      удерживает текст внутри ячейки. hoverinfo="skip" предотвращает
    #      появление лишних всплывающих подсказок от этой трассы.
    fig.add_trace(go.Scatter(
        x=df["col"] - 0.33,
        y=df["row"] - 0.33,
        mode="text",
        text=[str(int(n)) for n in df["atomic_number"]],
        textfont=dict(
            color=[f"rgba(255,255,255,{0.7 if m else 0.08})" for m in is_match],
            size=7,
            family="Inter",
        ),
        hoverinfo="skip",
        showlegend=False,
    ))

    for period in sorted(df[df["row"] <= 7]["period"].unique()):
        fig.add_annotation(
            x=0.3, y=period, xanchor="right",
            text=f"P{int(period)}",
            showarrow=False,
            font=dict(color="#eceff1", size=11),
        )
    fig.add_annotation(x=0.3, y=8, xanchor="right", text="6*", showarrow=False,
                       font=dict(color="#cfd8dc", size=10))
    fig.add_annotation(x=0.3, y=9, xanchor="right", text="7*", showarrow=False,
                       font=dict(color="#cfd8dc", size=10))

    fig.update_xaxes(
        title="",
        tickmode="array",
        tickvals=list(range(1, 19)),
        ticktext=[str(n) for n in range(1, 19)],
        range=[0.5, 18.5],
        showgrid=False, zeroline=False, showline=False,
        tickfont=dict(color="#cfd8dc", size=10),
        fixedrange=True,
    )
    fig.update_yaxes(
        title="",
        tickmode="array",
        tickvals=[1, 2, 3, 4, 5, 6, 7, 8, 9],
        ticktext=["1", "2", "3", "4", "5", "6", "7", "6*", "7*"],
        range=[9.5, 0.5],
        showgrid=False, zeroline=False, showline=False,
        tickfont=dict(color="#cfd8dc", size=10),
        scaleanchor="x", scaleratio=1,
        fixedrange=True,
    )

    fig.update_layout(
        plot_bgcolor="#102027",
        paper_bgcolor="#102027",
        margin=dict(l=20, r=20, t=15, b=25),
        hoverlabel=dict(bgcolor="#263238", font_size=12, font_family="Inter"),
        dragmode=False,
        showlegend=False,
        hoverdistance=40,
    )

    return fig


# FR : Callback réactif Dash : cette fonction est appelée automatiquement
#      chaque fois que l'un des quatre filtres change. Dash gère lui-même
#      la sérialisation JSON et le transport HTTP vers le navigateur.
#      Aucun état global n'est nécessaire : chaque appel reconstruit la
#      figure complète, ce qui est moins efficace qu'une mise à jour
#      partielle mais beaucoup plus simple à raisonner et à déboguer.
# RU : Реактивный callback Dash: эта функция вызывается автоматически при
#      изменении любого из четырёх фильтров. Dash самостоятельно управляет
#      JSON-сериализацией и HTTP-транспортом в браузер. Глобального состояния
#      не требуется: каждый вызов полностью перестраивает рисунок — это менее
#      эффективно, чем частичное обновление, но значительно проще в понимании
#      и отладке.
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


# FR : Callback de clic sur une case du tableau. clickData contient la
#      position et le customdata du point cliqué. Je déstructure les 19
#      champs par indices plutôt que par noms pour éviter une jointure :
#      l'ordre est fixé par la liste dans build_periodic_figure.
#      La fonction locale "section()" facttorise la création des blocs
#      HTML répétitifs — c'est l'équivalent d'un composant Dash réutilisable
#      sans passer par une classe.
# RU : Callback клика по ячейке таблицы. clickData содержит позицию и
#      customdata кликнутой точки. Я деструктурирую 19 полей по индексам,
#      а не по именам, чтобы избежать соединения: порядок фиксирован
#      списком в build_periodic_figure. Локальная функция "section()"
#      инкапсулирует создание повторяющихся HTML-блоков — это эквивалент
#      переиспользуемого компонента Dash без использования класса.
@app.callback(
    Output("element-details", "children"),
    Input("periodic-figure", "clickData"),
    Input("lang", "data"),
)
def display_element_details(click_data, lang):
    # FR : On utilise le state de la langue pour afficher les libellés et
    #      le nom de l'élément dans la langue sélectionnée.
    # RU : Состояние языка используется для отображения подписей и
    #      названия элемента на выбранном языке.
    t = LANG[lang or "fr"]

    if not click_data or not click_data.get("points"):
        return [html.P(t["click_hint"])]

    d = click_data["points"][0]["customdata"]
    # indices: 0=Z 1=sym 2=name(FR) 3=group 4=period 5=block 6=ecp 7=basis 8=pseudo
    #          9=alpha 10=ox 11=vol 12=ie1 13=ea 14=spin 15=vdw 16=func 17=disp 18=relat 19=name_ru

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

    ecp_val = t["ecp_values"].get(d[6], d[6])
    relat_val = t["relat_values"].get(d[18], d[18])
    disp_val = t["disp_values"].get(d[17], d[17])
    pseudo_val = t["pseudo_none"] if d[8] == "Aucun" else d[8]

    return [
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
        html.Div(className="bse-link", children=[
            html.A(
                t["bse_link"],
                href="https://www.basissetexchange.org/",
                target="_blank",
                className="bse-anchor",
            ),
        ]),
    ]


# FR : Callback de bascule de langue : détermine quelle langue est active
#      selon le bouton cliqué en dernier. ctx.triggered_id est disponible
#      depuis Dash 2.4 et évite de comparer des listes de triggered_prop_ids.
# RU : Callback переключения языка: определяет активный язык по последней
#      нажатой кнопке. ctx.triggered_id доступен с Dash 2.4 и позволяет
#      избежать сравнения списков triggered_prop_ids.
@app.callback(
    Output("lang", "data"),
    Input("btn-fr", "n_clicks"),
    Input("btn-ru", "n_clicks"),
    State("lang", "data"),
    prevent_initial_call=True,
)
def toggle_lang(n_fr, n_ru, current_lang):
    triggered = ctx.triggered_id
    if triggered == "btn-fr":
        return "fr"
    if triggered == "btn-ru":
        return "ru"
    return current_lang


# FR : Callback de mise à jour de l'interface : traduit tous les textes
#      statiques (titre, sous-titre, filtres, légende, pied de page) quand
#      la langue change. Un seul callback centralise toutes les sorties pour
#      éviter les dépendances circulaires.
# RU : Callback обновления интерфейса: переводит все статические тексты
#      (заголовок, подзаголовок, фильтры, легенда, подвал) при смене языка.
#      Один callback централизует все выходные данные во избежание
#      циклических зависимостей.
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
    Input("lang", "data"),
)
def update_ui_language(lang):
    t = LANG[lang or "fr"]
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
    fr_cls = "lang-btn active" if lang == "fr" else "lang-btn"
    ru_cls = "lang-btn active" if lang == "ru" else "lang-btn"
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
        fr_cls,
        ru_cls,
    )


if __name__ == "__main__":
    app.run_server(debug=True)

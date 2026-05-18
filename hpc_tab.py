"""
hpc_tab.py — Onglet générateur de scripts HPC (SLURM / PBS / SGE).
Вкладка генератора HPC-скриптов.
"""
from __future__ import annotations

from dash import html, dcc, Input, Output, State, callback
from hpc_generator import generate_script, list_schedulers


def create_hpc_layout() -> html.Div:
    schedulers = list_schedulers()
    return html.Div(className="tab-content-pad", children=[
        html.H2("Générateur de script HPC", id="hpc-title"),
        html.P(
            "Générez un script de soumission SLURM, PBS ou SGE pour lancer un calcul ORCA "
            "sur un cluster de calcul haute performance.",
            id="hpc-subtitle",
        ),
        html.Div(className="trend-controls-row", children=[
            html.Div([
                html.Label("Scheduler", id="hpc-sched-label"),
                dcc.RadioItems(
                    id="hpc-scheduler",
                    options=[{"label": s["label"], "value": s["value"]} for s in schedulers],
                    value="slurm",
                    labelStyle={"display": "inline-block", "marginRight": "12px"},
                ),
            ], className="cost-field"),
            html.Div([
                html.Label("Nom du job", id="hpc-name-label"),
                dcc.Input(id="hpc-jobname", value="orca_calc", type="text", className="cost-input"),
            ], className="cost-field"),
            html.Div([
                html.Label("Cœurs CPU", id="hpc-cores-label"),
                dcc.Input(id="hpc-cores", value=16, type="number", min=1, max=512, step=1,
                          className="cost-input"),
            ], className="cost-field"),
            html.Div([
                html.Label("RAM (Go)", id="hpc-mem-label"),
                dcc.Input(id="hpc-mem", value=64, type="number", min=1, max=2000, step=1,
                          className="cost-input"),
            ], className="cost-field"),
            html.Div([
                html.Label("Durée max (HH:MM:SS)", id="hpc-wall-label"),
                dcc.Input(id="hpc-walltime", value="24:00:00", type="text", className="cost-input"),
            ], className="cost-field"),
            html.Div([
                html.Label("Partition / queue", id="hpc-part-label"),
                dcc.Input(id="hpc-partition", value="compute", type="text", className="cost-input"),
            ], className="cost-field"),
            html.Div([
                html.Label("Module ORCA", id="hpc-mod-label"),
                dcc.Input(id="hpc-module", value="ORCA/5.0.4-gompi-2022a", type="text",
                          className="cost-input"),
            ], className="cost-field"),
            html.Div([
                html.Label("Fichier d'entrée (.inp)", id="hpc-inp-label"),
                dcc.Input(id="hpc-inputfile", value="molecule.inp", type="text",
                          className="cost-input"),
            ], className="cost-field"),
        ]),
        html.Button("Générer le script", id="hpc-btn", className="action-btn"),
        html.Div(id="hpc-result", style={"marginTop": "16px"}),
    ])


def register_callbacks(app=None):
    @callback(
        Output("hpc-title",    "children"),
        Output("hpc-subtitle", "children"),
        Output("hpc-sched-label",  "children"),
        Output("hpc-name-label",   "children"),
        Output("hpc-cores-label",  "children"),
        Output("hpc-mem-label",    "children"),
        Output("hpc-wall-label",   "children"),
        Output("hpc-part-label",   "children"),
        Output("hpc-mod-label",    "children"),
        Output("hpc-inp-label",    "children"),
        Input("lang", "data"),
    )
    def _lang(lang):
        lang = lang or "fr"
        if lang == "ru":
            return (
                "Генератор HPC-скрипта",
                "Создайте скрипт отправки SLURM, PBS или SGE для запуска ORCA на вычислительном кластере.",
                "Планировщик", "Имя задачи", "Ядра CPU", "ОЗУ (ГБ)",
                "Макс. время (ЧЧ:ММ:СС)", "Раздел / очередь", "Модуль ORCA", "Входной файл (.inp)",
            )
        return (
            "Générateur de script HPC",
            "Générez un script de soumission SLURM, PBS ou SGE pour lancer un calcul ORCA sur un cluster.",
            "Scheduler", "Nom du job", "Cœurs CPU", "RAM (Go)",
            "Durée max (HH:MM:SS)", "Partition / queue", "Module ORCA", "Fichier d'entrée (.inp)",
        )

    @callback(
        Output("hpc-result", "children"),
        Input("hpc-btn", "n_clicks"),
        State("hpc-scheduler",  "value"),
        State("hpc-jobname",    "value"),
        State("hpc-cores",      "value"),
        State("hpc-mem",        "value"),
        State("hpc-walltime",   "value"),
        State("hpc-partition",  "value"),
        State("hpc-module",     "value"),
        State("hpc-inputfile",  "value"),
        State("lang", "data"),
        prevent_initial_call=True,
    )
    def _generate(n_clicks, scheduler, job_name, cores, mem_gb, walltime,
                  partition, module_orca, input_file, lang):
        lang = lang or "fr"
        try:
            script = generate_script(
                scheduler=scheduler or "slurm",
                job_name=job_name or "orca_calc",
                n_cores=int(cores or 16),
                mem_gb=int(mem_gb or 64),
                walltime=walltime or "24:00:00",
                partition=partition or "compute",
                module_orca=module_orca or "ORCA/5.0.4",
                input_file=input_file or "molecule.inp",
            )
        except ValueError as e:
            return html.P(str(e), style={"color": "red"})

        ext_map = {"slurm": ".sh", "pbs": ".pbs", "sge": ".sge"}
        ext = ext_map.get(scheduler, ".sh")
        filename = f"{job_name or 'orca_calc'}{ext}"

        lbl = "Script généré" if lang == "fr" else "Сгенерированный скрипт"
        tip = ("Copiez ce script sur votre cluster, adaptez les chemins si nécessaire."
               if lang == "fr" else
               "Скопируйте скрипт на кластер и адаптируйте пути при необходимости.")

        return html.Div([
            html.Div(style={"display": "flex", "alignItems": "center", "gap": "12px",
                            "marginBottom": "8px"}, children=[
                html.Strong(f"{lbl} — {filename}"),
                dcc.Clipboard(
                    target_id="hpc-script-area",
                    title="Copier" if lang == "fr" else "Копировать",
                    style={"cursor": "pointer", "fontSize": "1.1em"},
                ),
            ]),
            html.Textarea(
                id="hpc-script-area",
                children=script,
                readOnly=True,
                style={
                    "width": "100%", "height": "420px", "fontFamily": "monospace",
                    "fontSize": "0.82em", "background": "#1a1a2e", "color": "#e0e0e0",
                    "border": "1px solid #444", "borderRadius": "4px", "padding": "10px",
                    "resize": "vertical",
                },
            ),
            html.P(tip, style={"fontSize": "0.82em", "color": "#aaa", "marginTop": "6px"}),
        ])

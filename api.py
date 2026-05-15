"""
api.py — Endpoints REST enregistrés sur le serveur Flask de Dash.
REST API endpoints registered on the Dash Flask server.
"""
from __future__ import annotations

from flask import jsonify, request, Response


def register_api_routes(server, elements_by_z: dict[int, dict]) -> None:
    """Register /api/v1/* routes on the Dash Flask server."""

    from recommendation_engine import recommend, list_methods, list_properties, get_nmr_isotopes

    # ── /api/v1/elements ────────────────────────────────────────────────────

    @server.route("/api/v1/elements")
    def api_elements():
        """Return a compact list of all 118 elements."""
        FIELDS = ["atomic_number", "symbol", "name", "name_ru", "atomic_mass",
                  "electronegativity", "atomic_radius", "group", "period", "block",
                  "category", "ecp_type", "basis_rec", "ie1", "ea", "spin_mult",
                  "vdw_radius", "polarisabilite"]
        data = [
            {f: el.get(f) for f in FIELDS}
            for el in elements_by_z.values()
        ]
        data.sort(key=lambda e: e["atomic_number"])
        return jsonify({"count": len(data), "elements": data})

    # ── /api/v1/elements/<z> ─────────────────────────────────────────────────

    @server.route("/api/v1/elements/<int:z>")
    def api_element(z: int):
        """Return all available data for element Z."""
        el = elements_by_z.get(z)
        if el is None:
            return jsonify({"error": f"Element Z={z} not found"}), 404
        # Exclude large nested dicts from JSON (orbital_info, nmr_isotopes already flat)
        payload = {k: v for k, v in el.items() if not isinstance(v, (list, dict)) or k in ("nmr_isotopes",)}
        return jsonify(payload)

    # ── /api/v1/recommend ────────────────────────────────────────────────────

    @server.route("/api/v1/recommend")
    def api_recommend():
        """
        Query params: z (int), method (str), prop (str), lang (fr|ru|en).
        Returns the full recommendation dict.
        """
        try:
            z      = int(request.args.get("z", 1))
            method = request.args.get("method", "dft_hybrid")
            prop   = request.args.get("prop",   "geometry")
            lang   = request.args.get("lang",   "fr")
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid query parameters"}), 400

        el = elements_by_z.get(z)
        if el is None:
            return jsonify({"error": f"Element Z={z} not found"}), 404

        block = el.get("block", "s")
        rec   = recommend(z, block, method, prop, lang if lang in ("fr", "ru") else "fr")
        # Remove large software list URLs for brevity — keep names
        rec_clean = dict(rec)
        rec_clean["software"] = [{"name": s["name"], "url": s["url"], "free": s["free"]}
                                  for s in rec.get("software", [])]
        rec_clean["method_info"]   = {k: v for k, v in rec.get("method_info", {}).items() if not k.startswith("_")}
        rec_clean["property_info"] = {k: v for k, v in rec.get("property_info", {}).items() if not k.startswith("_")}
        return jsonify({"z": z, "element": el["symbol"], "recommendation": rec_clean})

    # ── /api/v1/methods ──────────────────────────────────────────────────────

    @server.route("/api/v1/methods")
    def api_methods():
        lang = request.args.get("lang", "fr")
        return jsonify(list_methods(lang if lang in ("fr", "ru") else "fr"))

    # ── /api/v1/properties ──────────────────────────────────────────────────

    @server.route("/api/v1/properties")
    def api_properties():
        lang = request.args.get("lang", "fr")
        return jsonify(list_properties(lang if lang in ("fr", "ru") else "fr"))

    # ── /api/v1/nmr/<z> ─────────────────────────────────────────────────────

    @server.route("/api/v1/nmr/<int:z>")
    def api_nmr(z: int):
        """Return NMR-active isotopes for element Z."""
        return jsonify({"z": z, "isotopes": get_nmr_isotopes(z)})

    # ── /api/v1/input ────────────────────────────────────────────────────────

    @server.route("/api/v1/input")
    def api_input():
        """
        Generate an input file snippet.
        Query params: z, method, prop, software (orca|gaussian|pyscf), lang.
        Returns plain text.
        """
        from input_generator import generate_input
        try:
            z        = int(request.args.get("z", 1))
            method   = request.args.get("method",   "dft_hybrid")
            prop     = request.args.get("prop",     "geometry")
            software = request.args.get("software", "orca").lower()
            lang     = request.args.get("lang",     "fr")
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid query parameters"}), 400

        el = elements_by_z.get(z)
        if el is None:
            return jsonify({"error": f"Element Z={z} not found"}), 404

        block = el.get("block", "s")
        rec   = recommend(z, block, method, prop, lang)
        content = generate_input(software, el, method, prop,
                                 rec["basis"], rec["ecp"],
                                 rec["functional"], rec["dispersion"])
        return Response(content, mimetype="text/plain")

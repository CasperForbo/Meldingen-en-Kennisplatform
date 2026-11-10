from collections import Counter
from datetime import datetime

from flask import Blueprint, abort, redirect, render_template, request, url_for

if __package__ and "." in __package__:
    from ..models.database import delete_melding, get_melding, get_meldingen, save_melding, update_melding
else:
    from models.database import delete_melding, get_melding, get_meldingen, save_melding, update_melding

main = Blueprint("main", __name__)


@main.get("/")
def index():
    meldingen = get_meldingen()
    gesloten_statussen = {"opgelost", "gesloten"}
    open_count = sum(
        melding["status"].strip().lower() not in gesloten_statussen
        for melding in meldingen
    )
    categorie_counts = Counter(melding["categorie"] for melding in meldingen)
    return render_template(
        "dashboard.html",
        open_count=open_count,
        closed_count=len(meldingen) - open_count,
        categorie_counts=sorted(categorie_counts.items()),
        recente_meldingen=meldingen[:3],
    )

@main.get("/add")
def add():
    return render_template("add.html")

@main.get("/meldingen")
def meldingen():
    filters = {
        "categorie": request.args.get("categorie", "").strip(),
        "status": request.args.get("status", "").strip(),
        "prioriteit": request.args.get("prioriteit", "").strip(),
        "search": request.args.get("q", "").strip(),
    }
    meldingen = get_meldingen(**filters)
    return render_template("meldingen.html", meldingen=meldingen, filters=filters)


@main.route("/meldingen/<int:melding_id>", methods=["GET", "POST"])
def melding_detail(melding_id):
    melding = get_melding(melding_id)
    if melding is None:
        abort(404)

    if request.method == "POST":
        update_melding(
            melding_id=melding_id,
            probleem=request.form.get("probleem", "").strip(),
            beschrijving=request.form.get("beschrijving", "").strip(),
            categorie=request.form.get("categorie", "Lijn 1"),
            status=request.form.get("status", "Nieuw"),
            prioriteit=request.form.get("prioriteit", "Laag"),
            oplossing=request.form.get("oplossing", "").strip(),
        )
        return redirect(url_for("main.meldingen"))

    return render_template("melding_detail.html", melding=melding)


@main.post("/meldingen/<int:melding_id>/delete")
def melding_delete(melding_id):
    delete_melding(melding_id)
    return redirect(url_for("main.meldingen"))


@main.post("/add")
def add_melding():
    save_melding(
        probleem=request.form.get("probleem", "").strip(),
        beschrijving=request.form.get("beschrijving", "").strip(),
        categorie=request.form.get("categorie", "Lijn1"),
        status=request.form.get("status", "nieuw"),
        prioriteit=request.form.get("prioriteit", "laag"),
        oplossing=request.form.get("oplossing", "oplossing").strip(),
        datum=datetime.now()
    )
    return redirect(url_for("main.meldingen"))


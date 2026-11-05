from datetime import datetime

from flask import Blueprint, redirect, render_template, request, url_for

if __package__ and "." in __package__:
    from ..models.database import get_meldingen_by_categorie, save_melding
else:
    from models.database import get_meldingen_by_categorie, save_melding

main = Blueprint("main", __name__)


@main.get("/")
def index():
    return render_template("dashboard.html")

@main.get("/add")
def add():
    return render_template("add.html")

@main.get("/lijn1")
def lijn1():
    return render_category("Lijn1", "Lijn 1")


@main.get("/diepdruk")
def diepdruk():
    return render_category("diepdruk", "Diepdruk")


@main.get("/lijn23")
def lijn23():
    return render_category("lijn23", "Lijn 2/3")


@main.get("/multilijn")
def multilijn():
    return render_category("multilijn", "Multilijn")


@main.get("/infinity")
def infinity():
    return render_category("infinity", "Infinity")


def render_category(category, category_label):
    meldingen = get_meldingen_by_categorie(category)
    return render_template(
        "meldingen.html",
        meldingen=meldingen,
        category_label=category_label
    )


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
    return redirect(url_for("main.index"))


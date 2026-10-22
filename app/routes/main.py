from flask import Blueprint, redirect, render_template, request, url_for

if __package__ and "." in __package__:
    from ..models.database import save_melding
else:
    from models.database import save_melding

main = Blueprint("main", __name__)


@main.get("/")
def index():
    return render_template("dashboard.html")

@main.get("/add")
def add():
    return render_template("add.html")


@main.post("/add")
def add_melding():
    save_melding(
        probleem=request.form.get("probleem", "").strip(),
        beschrijving=request.form.get("beschrijving", "").strip(),
        status=request.form.get("status", "nieuw"),
        priority=request.form.get("priority", "laag"),
        category=request.form.get("category", "Lijn1"),
        oplossing=request.form.get("oplossing", "").strip(),
    )
    return redirect(url_for("main.index"))


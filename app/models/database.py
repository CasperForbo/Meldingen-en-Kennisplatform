import os
import re
from datetime import datetime

import pyodbc
from flask import current_app


def save_melding(probleem, beschrijving, categorie, status, prioriteit, oplossing, datum):
	database_config = current_app.config["database"]
	connection_string_env = database_config["connection_string_env"]
	connection_string = os.environ.get(connection_string_env) or database_config.get("connection_string")
	if not connection_string:
		raise RuntimeError(f"Configure a SQL Server connection string or set {connection_string_env}.")

	table = database_config["table"]
	if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)?", table):
		raise ValueError("The configured database table name is invalid.")

	connection = pyodbc.connect(connection_string)
	try:
		cursor = connection.cursor()
		cursor.execute(
			f"""
			INSERT INTO {table} (probleem, beschrijving, categorie, status, prioriteit, oplossing, datum)
			VALUES (?, ?, ?, ?, ?, ?, ?)
			""",
			probleem,
			beschrijving,
			categorie,
			status,
			prioriteit,
			oplossing,
			datum
		)
		connection.commit()
	except Exception:
		connection.rollback()
		raise
	finally:
		connection.close()


def get_meldingen_by_categorie(categorie):
	database_config = current_app.config["database"]
	connection_string_env = database_config["connection_string_env"]
	connection_string = os.environ.get(connection_string_env) or database_config.get("connection_string")
	if not connection_string:
		raise RuntimeError(f"Configure a SQL Server connection string or set {connection_string_env}.")

	table = database_config["table"]
	if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)?", table):
		raise ValueError("The configured database table name is invalid.")

	connection = pyodbc.connect(connection_string)
	try:
		cursor = connection.cursor()
		cursor.execute(
			f"""
			SELECT id, probleem, beschrijving, categorie, status, prioriteit, oplossing, datum
			FROM {table}
			WHERE categorie = ?
			ORDER BY datum DESC, id DESC
			""",
			categorie
		)
		columns = [column[0] for column in cursor.description]
		meldingen = [dict(zip(columns, row)) for row in cursor.fetchall()]
		for melding in meldingen:
			if isinstance(melding["datum"], str):
				melding["datum"] = datetime.fromisoformat(melding["datum"])
		return meldingen
	finally:
		connection.close()

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


def get_melding(melding_id):
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
			f"SELECT id, probleem, beschrijving, categorie, status, prioriteit, oplossing, datum FROM {table} WHERE id = ?",
			melding_id
		)
		row = cursor.fetchone()
		if row is None:
			return None
		columns = [column[0] for column in cursor.description]
		melding = dict(zip(columns, row))
		if isinstance(melding["datum"], str):
			melding["datum"] = datetime.fromisoformat(melding["datum"])
		return melding
	finally:
		connection.close()


def update_melding(melding_id, probleem, beschrijving, categorie, status, prioriteit, oplossing):
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
			UPDATE {table}
			SET probleem = ?, beschrijving = ?, categorie = ?, status = ?, prioriteit = ?, oplossing = ?
			WHERE id = ?
			""",
			probleem,
			beschrijving,
			categorie,
			status,
			prioriteit,
			oplossing,
			melding_id
		)
		connection.commit()
	except Exception:
		connection.rollback()
		raise
	finally:
		connection.close()


def delete_melding(melding_id):
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
		cursor.execute(f"DELETE FROM {table} WHERE id = ?", melding_id)
		connection.commit()
	except Exception:
		connection.rollback()
		raise
	finally:
		connection.close()


def get_meldingen(categorie="", status="", prioriteit="", search=""):
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
		conditions = []
		parameters = []
		for column, value in (("categorie", categorie), ("status", status), ("prioriteit", prioriteit)):
			if value:
				conditions.append(f"{column} = ?")
				parameters.append(value)
		if search:
			conditions.append("(probleem LIKE ? OR beschrijving LIKE ? OR oplossing LIKE ?)")
			search_pattern = f"%{search}%"
			parameters.extend((search_pattern, search_pattern, search_pattern))

		query = f"""
			SELECT id, probleem, beschrijving, categorie, status, prioriteit, oplossing, datum
			FROM {table}
		"""
		if conditions:
			query += " WHERE " + " AND ".join(conditions)
		query += " ORDER BY datum DESC, id DESC"
		cursor.execute(query, *parameters)
		columns = [column[0] for column in cursor.description]
		meldingen = [dict(zip(columns, row)) for row in cursor.fetchall()]
		for melding in meldingen:
			if isinstance(melding["datum"], str):
				melding["datum"] = datetime.fromisoformat(melding["datum"])
		return meldingen
	finally:
		connection.close()

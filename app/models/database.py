import os
import re

import pyodbc
from flask import current_app


def save_melding(probleem, beschrijving, status, priority, category, oplossing):
	database_config = current_app.config["database"]
	connection_string_env = database_config["connection_string_env"]
	connection_string = os.environ.get(connection_string_env)
	if not connection_string:
		raise RuntimeError(f"Set {connection_string_env} to connect to SQL Server.")

	table = database_config["table"]
	if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)?", table):
		raise ValueError("The configured database table name is invalid.")

	connection = pyodbc.connect(connection_string)
	try:
		cursor = connection.cursor()
		cursor.execute(
			f"""
			INSERT INTO {table} (probleem, beschrijving, status, priority, category, oplossing)
			VALUES (?, ?, ?, ?, ?, ?)
			""",
			probleem,
			beschrijving,
			status,
			priority,
			category,
			oplossing
		)
		connection.commit()
	except Exception:
		connection.rollback()
		raise
	finally:
		connection.close()

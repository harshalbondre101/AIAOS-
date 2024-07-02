from urllib.parse import urlparse

import click
import psycopg2
from flask import current_app, g


def get_db():
    """Connect to database using credentials from the environment
    and return the connection instance.
    """
    parser = urlparse(current_app.config["DATABASE"])
    # print(parser)

    conn_dict = {
        "database": "Restaurant",
        "user": "admin",
        "password": "Abhi#2003",
        "port": "10032",
        "host": "postgresql-174300-0.cloudclusters.net"
    }
    print(conn_dict)
    if "db" not in g:
        g.db = psycopg2.connect(**conn_dict)

        with g.db.cursor() as cur:
            # Set datestyle format
            cur.execute("""SET datestyle TO 'ISO, DMY'""")

    return g.db


def close_db(e=None):
    """Close the database"""
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    """Database initialization using database schema in schema.sql"""
    # print("schema")
    db = get_db()

    with db.cursor() as cur:
        with current_app.open_resource("schema.sql") as f:
            print(f)
            cur.execute(f.read().decode("utf8"))

    db.commit()


@click.command("init-db")
def init_db_command():
    """Command to use outside the web
    `flask --app run init-db`
    """
    init_db()
    click.echo("Initalized the database")


def init_app(app):
    # print('initializing')
    """Execute close_db when closing the app, also add init database command"""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

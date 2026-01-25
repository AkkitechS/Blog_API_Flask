import click
from flask.cli import with_appcontext
from app.seeders.category_seeder import seed_categories


@click.command("seed-categories")
@with_appcontext
def seed_categories_command():
    seed_categories()

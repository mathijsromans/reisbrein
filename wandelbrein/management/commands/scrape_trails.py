from django.core.management.base import BaseCommand

from wandelbrein import wandelbrein


class Command(BaseCommand):
    help = 'Scrapes nswandel.nl for hiking trails and adds them in the database'

    def handle(self, *args, **options):
        wandelbrein.scrape_and_create_trails(max_trails=5)

from django.core.management.base import BaseCommand

from wandelbrein import wandelbrein


class Command(BaseCommand):
    help = 'Delete all trails'

    def handle(self, *args, **options):
        wandelbrein.delete_trails()

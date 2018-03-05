from django.conf import settings
from django.core.management.base import BaseCommand

from experiment.views import send_all_experiments_to_portal


class Command(BaseCommand):
    help = 'Send all experiments that were scheduled to portal'

    def handle(self, *args, **options):
        print('Start of sending...')
        send_all_experiments_to_portal()
        print('End of sending.')

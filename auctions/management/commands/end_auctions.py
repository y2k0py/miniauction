from django.core.management.base import BaseCommand

from auctions.services import end_expired_auctions


class Command(BaseCommand):
    help = "Kończy wygasłe aukcje i wyznacza zwycięzców."

    def handle(self, *args, **options):
        count = end_expired_auctions()
        self.stdout.write(self.style.SUCCESS(f"Zakończono {count} aukcji."))

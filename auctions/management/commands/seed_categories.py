from django.core.management.base import BaseCommand

from auctions.models import Category


class Command(BaseCommand):
    help = "Tworzy domyślne kategorie aukcji."

    def handle(self, *args, **options):
        categories = ["Elektronika", "Książki", "Sport", "Dom i ogród", "Inne"]
        created = 0
        for name in categories:
            _, was_created = Category.objects.get_or_create(name=name)
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f"Utworzono {created} kategorii."))

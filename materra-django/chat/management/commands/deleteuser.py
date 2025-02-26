from chat.constants import DELETED_USER_DISPLAY_NAME
from chat.models import User

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = "Soft-Delete a user from the database"

    def add_arguments(self, parser):
        parser.add_argument("user_id", type=int)

    def handle(self, *args, **options):
        user_id = options['user_id']
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise CommandError('User "%s" does not exist' % user_id)

        user.display_name = DELETED_USER_DISPLAY_NAME
        user.is_deleted = True
        user.save()

        self.stdout.write(
            self.style.SUCCESS('Successfully marked user "%s" as deleted!' % user_id)
        )

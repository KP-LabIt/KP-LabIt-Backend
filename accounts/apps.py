from django.apps import AppConfig
from django.conf import settings
from django.db.models.signals import post_migrate


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):

        def configure_site(sender, **kwargs):
            from django.contrib.sites.models import Site

            # Frontend domain from settings or a sane default
            domain = getattr(settings, "FRONTEND_DOMAIN", "localhost:5173")
            site_name = getattr(settings, "SITE_NAME", "KP | GearHub")

            # Ensure site with ID=1 exists and has the right domain/name
            Site.objects.update_or_create(
                id=getattr(settings, "SITE_ID", 1),
                defaults={"domain": domain, "name": site_name},
            )

        # Connect the handler so it runs after migrations for this app
        post_migrate.connect(configure_site, sender=self)
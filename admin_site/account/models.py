from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db.models.signals import post_save

from system.models import Site

class UserProfile(models.Model):
    """BibOS Admin specific user profile."""
    # This is the user to which the profile belongs
    user = models.ForeignKey(User, unique=True, related_name='bibos_profile')

    SUPER_ADMIN = 0
    SITE_USER = 1
    SITE_ADMIN = 2
    type_choices = (
        (SUPER_ADMIN, _("Super Admin")),
        (SITE_USER, _("Site User")),
        (SITE_ADMIN, _("Site Admin"))
    )

    # The choices that can be used on the non-admin part of the website
    NON_ADMIN_CHOICES = (
        (SITE_USER, _("Site User")),
        (SITE_ADMIN, _("Site Admin"))
    )

    type = models.IntegerField(choices=type_choices, default=SITE_USER)
    site = models.ForeignKey(Site, null=True, blank=True)
    # TODO: Add more fields/user options as needed.
    # TODO: Make before_save integrity check that SITE_USER and 
    # SITE_ADMIN users MUST be associated with a site.
   
    def __unicode__(self):
        return self.user.username

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.type != UserProfile.SUPER_ADMIN and self.site is None:
            raise ValidationError(_(
                'Non-admin users MUST be attached to a site'
            ))
        #if self.type == UserProfile.SUPER_ADMIN and self.site is not None:
        #    raise ValidationError(_(
        #        'BibOS admins may not be attached to a site'
        #    ))

User.get_profile = lambda self: UserProfile.objects.get(user=self)

# Django does not automatically create profile objects for you. That is your responsibility. 
# A common way to do that is to attach a post-save signal handler to the User model, 
# and then create a profile whenever a new user is created.
def create_profile(sender, instance=None, **kwargs):
    if instance is None:
        return
    profile, created = UserProfile.objects.get_or_create(user=instance)


post_save.connect(create_profile, sender=User)
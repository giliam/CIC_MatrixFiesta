from django.dispatch import receiver

from django_cas_ng.signals import cas_user_authenticated

from matrix.models import ProfileUser

@receiver(cas_user_authenticated)
def create_cas_user(user, **kwargs):
    profile_user, created = ProfileUser.objects.get_or_create(user=user)

    if created:
        attribs = kwargs["attributes"]

        user.first_name = attribs.get('givenName')
        user.last_name = attribs.get('sn')
        user.email = attribs.get('mail')
        user.save()

        profile_user.firstname = attribs.get('givenName')
        profile_user.lastname = attribs.get('sn')
        profile_user.save()

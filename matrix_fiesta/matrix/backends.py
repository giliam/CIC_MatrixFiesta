from django_cas_ng.backends import CASBackend

class MatrixCASBackend(CASBackend):
    def user_can_authenticate(self, user):
        return not user is None

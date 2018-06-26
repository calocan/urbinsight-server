from rest_framework.authentication import SessionAuthentication, BasicAuthentication

class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
        Django Rest Framework ignores the CSRF Token on POST/PATCH and makes the user anonymous, causing
        the user to fail the CSRF check. I can't figure out why this happens, so I'm disabling CSRF here in the
        meantime. Grrr.
    """

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening
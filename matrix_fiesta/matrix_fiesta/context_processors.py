import os

if os.path.isfile('matrix_fiesta/parameters.py'):
    from matrix_fiesta import parameters
else:
    parameters = object

if hasattr(parameters, "DISCOURSE_URL"):
    DISCOURSE_URL = parameters.DISCOURSE_URL
else:
    DISCOURSE_URL = "#"

#définit quel élément de la navbar est actif selon l'application actuelle.
def activeNavbar(request):
    if request.resolver_match and request.resolver_match.url_name:
        requests_elements = request.resolver_match.url_name.split(".")
    else:
        return {}

    if len(requests_elements) <= 1:
        view_name = "homepage"
    else:
        view_name = requests_elements[1]
    return { 'nav_' + view_name + '_active': "active" }


def discourseUrl(request):
    return { 'DISCOURSE_URL': DISCOURSE_URL }
#définit quel élément de la navbar est actif selon l'application actuelle.
def activeNavbar(request):
    if request.resolver_match:
        requests_elements = request.resolver_match.url_name.split(".")
    else:
        return {}
    
    if len(requests_elements) <= 1:
        view_name = "homepage"
    else:
        view_name = requests_elements[1]
    return { 'nav_' + view_name + '_active': "active" }
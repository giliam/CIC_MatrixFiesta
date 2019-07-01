#définit quel élément de la navbar est actif selon l'application actuelle.
def activeNavbar(request):
    app = request.resolver_match.url_name.split(".")[0]
    return { 'nav_' + app + '_active': "active" }
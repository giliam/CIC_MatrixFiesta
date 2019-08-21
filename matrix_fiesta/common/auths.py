users_checks = {
    "Enseignants": {},
    "Élèves": {},
    "DE": {},
}

def check_is_student(user):
    if not user.id in users_checks["Élèves"].keys():
        users_checks["Élèves"][user.id] = user.groups.filter(name="Élèves").exists() 
    return users_checks["Élèves"][user.id]


def check_is_teacher(user):
    if not user.id in users_checks["Enseignants"].keys():
        users_checks["Enseignants"][user.id] = user.groups.filter(name="Enseignants").exists() 
    return users_checks["Enseignants"][user.id]


def check_is_de(user):
    if not user.id in users_checks["DE"].keys():
        users_checks["DE"][user.id] = user.groups.filter(name="DE").exists() 
    return users_checks["DE"][user.id]
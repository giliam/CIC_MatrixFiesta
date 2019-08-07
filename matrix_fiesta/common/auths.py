users_checks = {
    "Enseignants": {},
    "Élèves": {},
}

def check_is_student(user):
    if not user.id in users_checks["Élèves"].keys():
        users_checks["Élèves"][user.id] = user.groups.filter(name="Élèves").exists() 
    return users_checks["Élèves"][user.id]


def check_is_teacher(user):
    if not user.id in users_checks["Enseignants"].keys():
        users_checks["Enseignants"][user.id] = user.groups.filter(name="Enseignants").exists() 
    return users_checks["Enseignants"][user.id]
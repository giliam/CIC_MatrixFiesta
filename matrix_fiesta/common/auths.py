def check_is_student(user):
    return user.groups.filter(name="Élèves").exists() 


def check_is_teacher(user):
    return user.groups.filter(name="Enseignants").exists() 
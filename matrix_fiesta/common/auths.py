from enum import Enum

class GroupsNames(Enum):
    STUDENTS_LEVEL = "Élèves"
    TEACHERS_LEVEL = "Enseignants"
    DIRECTOR_LEVEL = "DE"

users_checks = {
    GroupsNames.STUDENTS_LEVEL: {},
    GroupsNames.TEACHERS_LEVEL: {},
    GroupsNames.DIRECTOR_LEVEL: {},
}

def check_is_student(user):
    if not user.id in users_checks[GroupsNames.STUDENTS_LEVEL].keys():
        users_checks[GroupsNames.STUDENTS_LEVEL][user.id] = user.groups.filter(name=GroupsNames.STUDENTS_LEVEL.value).exists() 
    return users_checks[GroupsNames.STUDENTS_LEVEL][user.id]


def check_is_teacher(user):
    if not user.id in users_checks[GroupsNames.TEACHERS_LEVEL].keys():
        users_checks[GroupsNames.TEACHERS_LEVEL][user.id] = user.groups.filter(name=GroupsNames.TEACHERS_LEVEL.value).exists() 
    return users_checks[GroupsNames.TEACHERS_LEVEL][user.id]


def check_is_de(user):
    if not user.id in users_checks[GroupsNames.DIRECTOR_LEVEL].keys():
        users_checks[GroupsNames.DIRECTOR_LEVEL][user.id] = user.groups.filter(name=GroupsNames.DIRECTOR_LEVEL.value).exists() 
    return users_checks[GroupsNames.DIRECTOR_LEVEL][user.id]
from enum import Enum

from django.utils.timezone import now


class GroupsNames(Enum):
    STUDENTS_LEVEL = "Élèves"
    TEACHERS_LEVEL = "Enseignants"
    DIRECTOR_LEVEL = "DE"


users_checks = {
    GroupsNames.STUDENTS_LEVEL: {},
    GroupsNames.TEACHERS_LEVEL: {},
    GroupsNames.DIRECTOR_LEVEL: {},
}


def check_is_(user, level):
    if not user.is_authenticated:
        return False

    # If the user test has not been stored yet
    if not user.id in users_checks[level].keys():
        users_checks[level][user.id] = (
            user.groups.filter(name=level.value).exists(),
            now()
        )
    # Or if the last login is too far away, refreshes the groups rights
    elif (now()-user.last_login).seconds > 600:
        users_checks[level][user.id] = (
            user.groups.filter(name=level.value).exists(),
            now()
        )

    # Returns the users checks
    return users_checks[level][user.id][0]


def check_is_student(user):
    return check_is_(user, GroupsNames.STUDENTS_LEVEL)


def check_is_teacher(user):
    return check_is_(user, GroupsNames.TEACHERS_LEVEL)


def check_is_de(user):
    return check_is_(user, GroupsNames.DIRECTOR_LEVEL)
# coding: utf-8

"""
    Comes from sametmax.com
    http://sametmax.com/quelques-outils-pour-gerer-les-cles-secretes-en-django/
    Handles secret key issue.
"""

import io
import os
import random
import string


def secret_key(size=50):
    pool = string.ascii_letters + string.digits + string.punctuation
    return "".join(random.SystemRandom().choice(pool) for i in range(size))

try:
    import pwd
except ImportError:
    pass

try:
    import grp
except ImportError:
    pass


def secret_key_from_file(
        file_path,
        create=True,
        size=50,
        file_perms=None, # unix uniquement
        file_user=None, # unix uniquement
        file_group=None # unix uniquement
    ):
    try:
        with io.open(file_path) as f:
            return f.read().strip()
    except IOError as e:
        if e.errno == 2 and create:
            with io.open(file_path, 'w') as f:
                key = secret_key(size)
                f.write(key)

            if any((file_perms, file_user, file_group)) and not pwd:
                raise ValueError('File chmod and chown are for Unix only')

            if file_user:
                os.chown(file_path, uid=pwd.getpwnam(file_user).pw_uid)

            if file_group:
                os.chown(file_path, gid=grp.getgrnam(file_group).gr_gid)

            if file_perms:
                os.chmod(file_path, int(str(file_perms), 8))

            return key

        raise
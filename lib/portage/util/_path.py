# Copyright 2013 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

import stat

from portage import os_unicode_fs
from portage.exception import PermissionDenied


def exists_raise_eaccess(path):
    try:
        os_unicode_fs.stat(path)
    except OSError as e:
        if e.errno == PermissionDenied.errno:
            raise PermissionDenied("stat('%s')" % path)
        return False
    else:
        return True


def isdir_raise_eaccess(path):
    try:
        st = os_unicode_fs.stat(path)
    except OSError as e:
        if e.errno == PermissionDenied.errno:
            raise PermissionDenied("stat('%s')" % path)
        return False
    else:
        return stat.S_ISDIR(st.st_mode)

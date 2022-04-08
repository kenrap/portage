# Copyright 1999-2012 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

from _emerge.CompositeTask import CompositeTask
from _emerge.EbuildPhase import EbuildPhase

import portage
from portage import os_unicode_fs
from portage.const import SUPPORTED_GENTOO_BINPKG_FORMATS
from portage.exception import InvalidBinaryPackageFormat


class EbuildBinpkg(CompositeTask):
    """
    This assumes that src_install() has successfully completed.
    """

    __slots__ = ("pkg", "settings") + ("_binpkg_tmpfile", "_binpkg_info")

    def _start(self):
        pkg = self.pkg
        root_config = pkg.root_config
        bintree = root_config.trees["bintree"]
        binpkg_format = self.settings.get(
            "BINPKG_FORMAT", SUPPORTED_GENTOO_BINPKG_FORMATS[0]
        )
        if binpkg_format == "xpak":
            binpkg_tmpfile = os_unicode_fs.path.join(
                bintree.pkgdir, pkg.cpv + ".tbz2." + str(portage.getpid())
            )
        elif binpkg_format == "gpkg":
            binpkg_tmpfile = os_unicode_fs.path.join(
                bintree.pkgdir, pkg.cpv + ".gpkg.tar." + str(portage.getpid())
            )
        else:
            raise InvalidBinaryPackageFormat(binpkg_format)
        bintree._ensure_dir(os_unicode_fs.path.dirname(binpkg_tmpfile))

        self._binpkg_tmpfile = binpkg_tmpfile
        self.settings["PORTAGE_BINPKG_TMPFILE"] = self._binpkg_tmpfile

        package_phase = EbuildPhase(
            background=self.background,
            phase="package",
            scheduler=self.scheduler,
            settings=self.settings,
        )

        self._start_task(package_phase, self._package_phase_exit)

    def _package_phase_exit(self, package_phase):

        self.settings.pop("PORTAGE_BINPKG_TMPFILE", None)
        if self._default_exit(package_phase) != os_unicode_fs.EX_OK:
            try:
                os_unicode_fs.unlink(self._binpkg_tmpfile)
            except OSError:
                pass
            self.wait()
            return

        pkg = self.pkg
        bintree = pkg.root_config.trees["bintree"]
        self._binpkg_info = bintree.inject(pkg.cpv, filename=self._binpkg_tmpfile)

        self._current_task = None
        self.returncode = os_unicode_fs.EX_OK
        self.wait()

    def get_binpkg_info(self):
        return self._binpkg_info

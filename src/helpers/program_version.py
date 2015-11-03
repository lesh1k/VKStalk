from __future__ import unicode_literals


def prettify_project_version(version):
    version = "| VKStalk ver. {} |".format(version)
    version = '\n' + '=' * \
        ((42 - len(version)) / 2) + version + \
        '=' * ((42 - len(version)) / 2) + '\n\n'
    return version

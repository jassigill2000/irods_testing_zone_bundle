# Library of common additional functions to be used in custom modules
#
# To use, copy to ansible's "module_utils" directory
#  e.g. /usr/local/lib/python2.7/dist-packages/ansible/module_utils
#  and add the following two lines to the bottom of the module
#
#  from ansible.module_utils.basic import *
#  from ansible.module_utils.local_ansible_utils_extension import *
#
# Provides the following functions:
#
#  get_distribution_version_major() -> string
#
#  get_irods_platform_string() -> string
#   distribution+major_version specific string (e.g. "Ubuntu_14")
#
#  install_os_packages(packages)
#   packages is a list of strings of package names (e.g. ["fuse", "git"])
#
#  install_os_packages_from_files(files)
#   files is a list of strings of filenames (e.g. ["irods-icat-4.1.4-64bit-centos6.rpm"]

import subprocess


def get_distribution_version_major():
    return get_distribution_version().split('.')[0]

def get_irods_platform_string():
    return get_distribution() + '_' + get_distribution_version_major()

def subprocess_get_output(*args, **kwargs):
    kwargs['stdout'] = subprocess.PIPE
    kwargs['stderr'] = subprocess.PIPE
    check_rc = False
    if 'check_rc' in kwargs:
        check_rc = kwargs['check_rc']
        del kwargs['check_rc']
    p = subprocess.Popen(*args, **kwargs)
    out, err = p.communicate()
    if check_rc:
        if p.returncode != 0:
            raise Exception('''subprocess_get_output() failed
args: {0}
kwargs: {1}
returncode: {2}
stdout: {3}
stderr: {4}
'''.format(args, kwargs, p.returncode, out, err))
    return p.returncode, out, err

def install_os_packages_apt(packages):
    subprocess_get_output(['sudo', 'apt-get', 'update'], check_rc=True)
    args = ['sudo', 'apt-get', 'install', '-y'] + packages
    subprocess_get_output(args, check_rc=True)

def install_os_packages_yum(packages):
    args = ['sudo', 'yum', 'install', '-y'] + packages
    subprocess_get_output(args, check_rc=True)

def install_os_packages_zypper(packages):
    args = ['sudo', 'zypper', '--non-interactive', 'install'] + packages
    subprocess_get_output(args, check_rc=True)

def install_os_packages(packages):
    dispatch_map = {
        'Ubuntu': install_os_packages_apt,
        'Centos': install_os_packages_yum,
        'Centos linux': install_os_packages_yum,
        'Opensuse ': install_os_packages_zypper,
    }

    try:
        dispatch_map[get_distribution()](packages)
    except KeyError:
        raise NotImplementedError('install_os_packages() for [{0}]'.format(get_distribution()))

def install_os_packages_from_files_apt(files):
    args = ['sudo', 'dpkg', '-i'] + files
    subprocess_get_output(args) # no check_rc, missing deps return code 1
    subprocess_get_output(['sudo', 'apt-get', 'update'], check_rc=True)
    subprocess_get_output(['sudo', 'apt-get', 'install', '-yf'], check_rc=True)

def install_os_packages_from_files_yum(files):
    args = ['sudo', 'yum', 'localinstall', '-y', '--nogpgcheck'] + files
    subprocess_get_output(args, check_rc=True)

def install_os_packages_from_files_zypper(files):
    install_os_packages_zypper(files)

def install_os_packages_from_files(files):
    dispatch_map = {
        'Ubuntu': install_os_packages_from_files_apt,
        'Centos': install_os_packages_from_files_yum,
        'Centos linux': install_os_packages_from_files_yum,
        'Opensuse ': install_os_packages_from_files_zypper,
    }

    try:
        dispatch_map[get_distribution()](files)
    except KeyError:
        raise NotImplementedError('install_os_packages_from_files() for [{0}]'.format(get_distribution()))
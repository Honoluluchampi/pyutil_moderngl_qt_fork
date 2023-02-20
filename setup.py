from setuptools import setup

def _requires_from_file(filename):
    return open(filename).read().splitlines()

setup(
    name="util_moderngl_qt",
    version="0.1.5",
    install_requires=_requires_from_file('requirements.txt')
)
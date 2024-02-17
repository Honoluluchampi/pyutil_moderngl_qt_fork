pip3 install build
rm -f -r util_moderngl_qt.egg-info/* dist/*
python3 -m build --sdist
python3 -m build --wheel
twine upload --repository pypi dist/*

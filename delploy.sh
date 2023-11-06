rm -f -r util_moderngl_qt.egg-info/* dist/*
python3 setup.py sdist
python3 setup.py bdist_wheel
twine upload --repository pypi dist/*

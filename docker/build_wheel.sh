set -exo pipefail

. /venv/bin/activate

python setup.py bdist_wheel
pip install dist/samsara-0.1-py2-none-any.whl

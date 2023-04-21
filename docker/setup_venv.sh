set -exo pipefail

virtualenv --system-site-packages /venv
. /venv/bin/activate

pip --no-cache-dir --disable-pip-version-check \
    install --upgrade pip setuptools

pip --no-python-version-warning \
    config set global.no_python_version_warning True
pip config set global.no_cache_dir True

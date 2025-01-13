from setuptools import setup, find_packages

setup(
    name="flacjacket",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'flask',
        'flask-sqlalchemy',
        'flask-migrate',
        'flask-jwt-extended',
        'flask-restx',
        'werkzeug',
        'psycopg2-binary',
        'python-magic',
        'structlog',
        'python-json-logger',
        'pytest'
    ]
)

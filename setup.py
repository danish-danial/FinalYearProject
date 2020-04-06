from setuptools import setup

setup (
    name = 'application',
    package = ['application'],
    include_package_data = True,
    install_requires = [
        'bootstrap-flask', 
        'flask',
        'flask-login',
        'flask-sqlalchemy', 
        'jupyter',
        'matplotlib', 
        'numpy',
        'pandas', 
        'pylint',
        'scikit-learn', 
        'seaborn',
    ]
)
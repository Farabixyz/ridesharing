from setuptools import setup, find_packages

setup(
    name="fuel_ordering_system",  # Name of your project
    version="1.0.0",              # Version number
    description="A Flask-based Fuel Ordering System with user roles",  # Short description
    author="Farabi Tanim",           # Replace with your name
    author_email="ftanim521@gmail.com",  # Replace with your email
    url="https://github.com/Farabixyz/Tankupnow",  # Project's GitHub URL
    packages=find_packages(),     # Automatically discover all packages in the project
    include_package_data=True,    # Include non-code files specified in MANIFEST.in
    install_requires=[
        "flask>=2.0.0",           # Flask for web framework
        "flask-sqlalchemy>=2.5.0",  # SQLAlchemy for database management
        "flask-wtf>=1.0.0",       # Flask-WTF for form handling
        "flask-login>=0.6.0",     # Flask-Login for user authentication
        "wtforms>=3.0.0",         # WTForms for form validation
        "email-validator"         # For email validation in forms
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Flask",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',  # Require Python version 3.7 or higher
    entry_points={
        "console_scripts": [
            "run-fuel-system=your_package.app:main",  # Entry point to run your app
        ]
    },
)

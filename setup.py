from setuptools import setup, find_packages
import os

version = "1.2"

setup(
    name="django-cookieless",
    version=version,
    description="Django cookie free sessions optional decorator",
    long_description=open("README.txt").read()
    + "\n"
    + open(os.path.join("docs", "HISTORY.txt")).read(),
    # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "License :: OSI Approved :: Apache Software License",
    ],
    keywords="Django, No cookies, cookieless",
    author="Ed Crewe",
    author_email="edmundcrewe@gmail.com",
    url="https://github.com/edcrewe/django-cookieless",
    license="Apache2",
    packages=find_packages(exclude=["ez_setup"]),
    # namespace_packages=['cookieless'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "setuptools",
        # -*- Extra requirements: -*-
        "cryptography",
    ],
    entry_points="""
      # -*- Entry points: -*-
      """,
)

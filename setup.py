from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='django-cookieless',
      version=version,
      description="Cookie free sessions and decorator",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='No cookies',
      author='Ed Crewe',
      author_email='edmundcrewe@gmail.com',
      url='http://edcrewe.com',
      license='Apache2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['cookieless'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )

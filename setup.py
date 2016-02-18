"""
setup.py
~~~~~~~~
Setup script to install news-dentist.

"""
from setuptools import setup

setup(name='news-dentist',
      version='0.1',
      description='Extract articles text from Google News',
      author='Jamie Bull',
      author_email='jamie.bull@oco-carbon.com',
      url='',
      packages=['surgery'],
      install_requires=[
          "beautifulsoup4>=4.4",
          "lxml>=3.5",
          "requests>=2.9",
          "flask>=0.10.1",
      ],
      )

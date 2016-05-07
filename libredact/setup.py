import os
import warnings

#from distutils.core import setup
from setuptools import setup


with open(os.path.join('libredact', '__init__.py')) as init_:
    for line in init_:
        if '__version__' in line:
            version = line.split('=')[-1].strip().replace('"','')
            break
    else:
        version = 'unknown'
        warnings.warn('Unable to find version, using "%s"' % version)
        input("Continue?")


setup(name='libredact',
      version=version,
      description='BitCurator Access Redaction Tools',
      author='BitCurator',
      author_email='bitcurator@gmail.com',
      maintainer = "BitCurator",
      maintainer_email = "bitcurator@gmail.com",
      url="https://github.com/bitcurator/bca-redtools",
      #packages=['bctools', ],
      #package_data={'bctools': ['font/*.ttf', 'font/*.txt']},

      py_modules = ['dfxml', 'fiwalk'],

      scripts = ['iredact.py'],

      classifiers = ['Development Status :: 2 - Pre-Alpha'
                     "Intended Audience :: Developers",
                     "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
                     "Programming Language :: Python",
                     'Programming Language :: Python :: 3',
                     'Programming Language :: Python :: 3.0'
                     "Programming Language :: Python :: 3.1",
                     "Programming Language :: Python :: 3.2",
                     "Operating System :: OS Independent",
                     "Topic :: Software Development :: Libraries :: Python Modules"],
      keywords="bitcurator")

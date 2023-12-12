from setuptools import setup, find_packages

setup(
    name='marc21',
    version='0.3.3',
    description='library to create bibliographic marc21 records',
    url='',
    author='John van der Vuurst',
    author_email='jwvdvuurst@gmail.com',
    license='',
    packages=find_packages(include=['marc21', 'marc21.*']),
    package_dir={'Package': 'marc21'},
    requires=[],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: European Union Public Licence 1.1 (EUPL 1.1)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.11',
        'Topic :: Other/Nonlisted Topic'
    ]
)
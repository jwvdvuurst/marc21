from setuptools import setup, find_packages

setup(
    name='marc21',
    version='0.5.0',
    description='library to create bibliographic MARC21 records',
    url='https://github.com/jwvdvuurst/marc21.git',
    author='John van der Vuurst',
    author_email='jwvdvuurst@gmail.com',
    license='EUPL-1.1',
    packages=find_packages(include=['marc21', 'marc21.*']),
    install_requires=[],
    python_requires='>=3.10',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: European Union Public Licence 1.1 (EUPL 1.1)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.11',
        'Topic :: Other/Nonlisted Topic'
    ]
)
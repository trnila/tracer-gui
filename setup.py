from setuptools import setup, find_packages

setup(
    name='tracergui',
    packages=find_packages(),
    entry_points={
        'console_scripts': ['tracergui = tracergui.app:main']
    }
)

from setuptools import setup

setup(
    name="EC2 snapshot script",
    author="Manokar",
    version="1.0",
    packages=['SS'],
    url="https://github.com/Harish5510/Snapshot",
    install_requires=[
        'click',
        'boto3'
    ],
    entry_points='''
        [console_scripts]
        shotty=SS.SS_Script:cli
    '''
)

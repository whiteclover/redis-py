from setuptools import setup 


with open('README.md') as f:
    long_description = f.read()

setup(
    name = "redispy",
    version = "0.1",
    license = 'MIT',
    description = "An Other Redis Client for Python",
    author = 'Thomas Huang',
    url = 'https://github.com/thomashuang/redis-py',
    packages = ['redispy', 'redispy.connection', 'redispy.profile'],
    install_requires = ['setuptools'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: Redis Client',
        ],
    long_description=long_description,
    platform='any'
)
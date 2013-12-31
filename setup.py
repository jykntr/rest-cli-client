from setuptools import setup, find_packages
import restcli

setup(
    name='restcli',
    version=restcli.__version__,
    packages=find_packages(exclude='test'),
    entry_points={
        'console_scripts': ['restcli = restcli.restcli:main']
    },
    install_requires=['requests>=2.0.0', 'Pygments>=1.6', 'colorama>=0.2.5'],
    package_data={
        'restcli': ['*.conf'],
    },

    author='jykntr',
    author_email='jykntr@gmail.com',
    description='Command line REST request tool',
    license='MIT',
    keywords='rest http',
    url='http://jykntr.github.io/rest-cli-client/',
    download_url='https://github.com/jykntr/rest-cli-client/releases/tag/v' + restcli.__version__
)

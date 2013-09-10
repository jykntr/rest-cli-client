from setuptools import setup, find_packages
setup(
    name = "restcli",
    version = "0.1",
    packages = find_packages(),
    entry_points = {
        'console_scripts': ['restcli = restcli.restcli:main']
    },
    install_requires = ['requests>=1.2.3','Pygments>=1.6'],

    package_data = {
        'restcli': ['*.conf'],
    },

    author_email = "jykntr@gmail.com",
    description = "Command line REST request tool",
    #license = "PSF",
    keywords = "rest http",
    url = "https://bitbucket.org/jayknitter/cli-rest-client",
)

from setuptools import setup, find_packages
setup(
    name="restcli",
    version="0.1",
    packages=find_packages(),
    entry_points={
        'console_scripts': ['restcli = restcli.restcli:main']
    },

    package_data={
        'restcli': ['*.conf'],
    },

    author_email="jykntr@gmail.com",
    description="Command line REST request tool",
    license="MIT",
    keywords="rest http",
    url="https://github.com/jykntr/rest-cli-client",
)

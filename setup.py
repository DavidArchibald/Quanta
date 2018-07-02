import setuptools
from Quanta import __version__

with open("README.md", "r") as f:
    long_description = f.read()

if __name__ == "__main__":
    setuptools.setup(
        name="Quanta",
        author="David Archibald",
        author_email="", # Left out so I don't get spammed
        version=__version__,
        description="A Discord Bot named Quanta",
        long_description=long_description,
        license="MIT",
        classifiers=["Development Status :: 2"], # pre-alpha
        url="https://github.com/DavidArchibald/Quanta",
        zip_safe=False,
        include_package_data=True,
        packages=setuptools.find_packages(),
        provides=setuptools.find_packages(
            include=["Quanta"],
            exclude=["test", "test.*", "*.test", "*.test.*"]
        ),
        setup_requires=[
            "wheel"
        ],
        install_requires=[
            #"discord.py>=1.0.0",
            "fuzzywuzzy==0.16.0",
            "python-Levenshtein==0.12.0",
            "Django==2.0.6"
        ],
        dependency_links=[
            "pip install -U git+https://github.com/Rapptz/discord.py@rewrite#egg=discord.py[voice]"
        ]
    )

from setuptools import find_packages, setup
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name="DiscordEconomy",
    version="1.3.5",
    description="Discord.py, other libs(hikari etc.), and forks(pycord, nextcord etc.) extension to create economy easily.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Nohet/DiscordEconomy",
    author="Nohet",
    author_email="igorczupryniak503@gmail.com",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    keywords="discord, discord extension, discord.py, economy, economy bot, discord economy, DiscordEconomy",
    packages=find_packages(),
    install_requires=["aiosqlite", "aiohttp"],
)

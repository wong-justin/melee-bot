import setuptools

setuptools.setup(
    name="livemelee",
    version="0.1.0",
    author="Justin Wong",
    author_email="jkwongfl@yahoo.com",
    description="An easier way to develop a SSBM bot. Built off libmelee.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/wong-justin/melee-bot",
    packages=setuptools.find_packages(),
    install_requires=[
        'melee',
    ],
    python_requires='>=3.7',
    keywords=['melee', 'smash bros', 'slippi'],
)

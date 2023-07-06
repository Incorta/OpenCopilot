"""Setup.py for the Open Copilot provider package."""

from setuptools import setup, find_packages


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='opencopilot',
    version='0.0.1',
    description='An AI-driven Copilot Agent designed to offer an efficient and controllable framework for software companies',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Incorta',
    author_email='devteam-python-libs@incorta.com',
    url="https://github.com/Incorta/OpenCopilot",
    packages=find_packages(),
    install_requires=[
        'openai~=0.27.6',
        'termcolor~=2.3.0',
        'jinja2~=3.1.2',
        'pydantic~=1.10.7',
        'utils~=1.0.1',
        'pytest~=7.3.1'


    ],
    python_requires='>=3.6',
)

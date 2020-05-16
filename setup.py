import pathlib
import re

import setuptools

ROOT = pathlib.Path(__file__).parent

with open(ROOT / "README.md", "r") as fh:
    long_description = fh.read()


with open(ROOT / "aioscheduler" / "__init__.py", encoding="utf-8") as f:
    match = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE)
    if match is None:
        raise RuntimeError("Could not parse version.")
    VERSION = match.group(1)

setuptools.setup(
    name="aioscheduler",
    version=VERSION,
    author="Jens Reidel",
    author_email="adrian@travitia.xyz",
    description="Scalable, high-performance AsyncIO task scheduler",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Gelbpunkt/aioscheduler",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)

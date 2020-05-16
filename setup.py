import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aioscheduler",
    version="1.0.0",
    author="Jens Reidel",
    author_email="adrian@travitia.xyz",
    description="Scalable, high-performance AsyncIO task scheduler",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Gelbpunkt/aioscheduler",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)

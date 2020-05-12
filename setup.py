import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tuimux-XLE", # Replace with your own username
    version="0.0.1",
    author="XLE",
    author_email="tca@xle.sh",
    description="A TUI menu for creating and selecting tmux sessions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tcaxle/tuimux",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: GNU/Linux",
    ],
    python_requires='>=3.8',
)

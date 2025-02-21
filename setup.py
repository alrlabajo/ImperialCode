import setuptools

setuptools.setup(
    name="imperialcode",
    version="0.0.1",
    author="automata",
    author_email="alrlabajo@gmail.com",
    description=("A Victorian era themed programming language based on C language"),
    long_description=("A Victorian era themed programming language based on C language"),
    long_description_content_type="text/markdown",
    url="https://github.com",
    project_urls={
        "Bug Tracker": "https://github.com",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=["imp_code", "imp_code.components", "imp_code.utils"],
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "ic = imp_code.cli:main",
        ]
    },
)

import setuptools

setuptools.setup(
    name="imperialcode",
    version="0.0.1",
    author="automata",
    author_email="automa@gmail.com",
    description=("An object-oriented programming language inspired by Python and C++"),
    long_description=("An object-oriented programming language inspired by Python and C++"),
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
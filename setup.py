import setuptools

setuptools.setup(
    name="SubtitleConverter",
    version="1.0.0",
    author="Bernard G. Tapiru, Jr.",
    description="JSON to Subtitle Converter",
    
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    
    # This creates the command-line tool!
    # 'subconvert' will be the command
    # 'cli:main' means: in the 'cli' module, run the 'main' function
    entry_points={
        "console_scripts": [
            "subconvert=subconverter.cli:main",
        ],
    },
    
    # Add dependencies here
    install_requires=[
        # 'PySide6' and 'tkinter' are GUI, not core.
        # The core library has no dependencies!
    ],
)

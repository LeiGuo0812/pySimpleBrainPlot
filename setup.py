import setuptools

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name="pySimpleBrainPlot",
    version="0.0.4",
    author="LeiGuo",
    author_email="",
    description="simpleBrainPlot is a small python package to create simple line-art brain plots, modified from matlab package Simple-Brain-Plot, https://github.com/dutchconnectomelab/Simple-Brain-Plot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LeiGuo0812/pySimpleBrainPlot",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=[
        'numpy',
        'matplotlib'
    ],
    package_data={'pySimpleBrainPlot': ['regionDescriptions.pkl', 'atlases/*.svg']},
)
from setuptools import setup, find_packages

print(find_packages())  # Add this line to debug

setup(
    name='custom_functions',
    version='0.1.3',
    packages=find_packages(),
    install_requires=[
        # List your runtime dependencies here
    ],
    extras_require={
        'tests': [
            'pytest',
        ],
    },
    url='https://github.com/lumeohq/custom-functions',
    author='Lumeo',
    author_email='support@lumeo.com',
    description='Sample Lumeo Custom Functions',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
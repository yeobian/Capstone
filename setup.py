from setuptools import find_packages, setup

setup(
    name='capstone_wardrobe',
    packages=find_packages(),
    version='0.1.0',
    description='Personal Wardrobe Intelligence Platform',
    author='Yeobi',
    license='MIT',
    install_requires=[
        'torch',
        'torchvision',
        'pandas',
        'numpy',
        'scikit-learn',
        'matplotlib',
        'pillow',
        'tqdm',
        'pyyaml'
    ],
)

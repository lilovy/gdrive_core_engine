from setuptools import setup, find_packages


with open('requirements.txt') as f:
    install_requires = f.read().strip().split('\n')

setup(
    name='gdrive_engine',
    version='0.0.3',
    packages=find_packages(),
    install_requires=install_requires,
    author='Lilovy',
    author_email='iv1hanz@gmail.com',
    description='api for making call to google drive',
    license='MIT',
    url='https://github.com/lilovy/gdrive_core_engine',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)

from setuptools import setup
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()
setup(name='converter_package',
      version='2.5',
      description='This converter library is able to transform the ACCORDION application model to K3s configuration files',
      author='Giannis Korontanis',
      author_email='gkorod2@gmail.com',
      license='MIT',
      packages=['converter_package'],
      long_description=long_description,
      long_description_content_type='text/markdown',
      install_requires=[
          'pyyaml==5.3.1', 'kafka==1.3.5', 'hurry.filesize==0.9', 'oyaml==1.0'
      ],
      zip_safe=False)

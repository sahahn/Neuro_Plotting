from setuptools import setup, find_packages

setup(name='Neuro_Plotting',
      version='0.21',
      description='Plotting helper tool',
      url='http://github.com/sahahn/Neuro_Plotting',
      author='Sage Hahn',
      author_email='sahahn@euvm.edu',
      license='MIT',
      packages=['Neuro_Plotting'],
      include_package_data=True,
      package_data={'Neuro_Plotting': ['data/*/*/*', 'data/*/*']},
      package_dir={'Neuro_Plotting': 'Neuro_Plotting'},

      install_requires=[
          'nibabel',
          'pandas',
          'nilearn',
          'numpy',
          'matplotlib'
      ],
      zip_safe=False)

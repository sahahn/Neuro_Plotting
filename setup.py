from setuptools import setup

setup(name='Neuro_Plotting',
      version='0.1',
      description='Plotting helper tool',
      url='http://github.com/sahahn/Neuro_Plotting',
      author='Sage Hahn',
      author_email='sahahn@euvm.edu',
      license='MIT',
      packages=['Neuro_Plotting'],
      install_requires=[
          'nibabel',
          'pandas',
          'nilearn',
          'numpy',
          'matplotlib'
      ],
      zip_safe=False)

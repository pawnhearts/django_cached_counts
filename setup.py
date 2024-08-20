import setuptools 

with open("README.md", "r") as fh: 
    long_description = fh.read() 

setuptools.setup( 
    long_description=long_description,
    long_description_content_type="text/markdown", 
    name='django_cached_counts',
    version='0.2.0',
    description='Caching count() in django models',
    python_requires='==3.*,>=3.8.0',
    author='pawnhearts',
    author_email='robotnaoborot@gmail.com',
    license='MIT',
    packages=['django_cached_counts'],
    package_dir={"": "."},
    package_data={},
    install_requires=['django==2.*,>=2.2.0'],



	#	 install_requires=[ 
	#	 "package1", 
	# "package2", 
	# ], 



	# classifiers like program is suitable for python3, just leave as it is. 
	classifiers=[ 
		"Programming Language :: Python :: 3", 
		"License :: OSI Approved :: MIT License", 
		"Operating System :: OS Independent", 
	], 
) 


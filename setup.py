from setuptools import setup, find_packages

setup(
    name='alan_robot',
    version='1.0.0',
    packages=find_packages(),
    # package_dir={'robot_control': ''},
    url='http://pabogdan.github.io/AlanProject',
    license='',
    author='Petrut Antoniu Bogdan',
    author_email='petrut.bogdan@student.manchester.ac.uk',
    description='Spiking neural network robot control system running on SpiNNaker',
    # Requirements
    dependency_links = ['https://github.com/nengo/nengo/tarball/23107fe#egg=nengo-2.0.0',
                        'https://github.com/pabogdan/nengo_spinnaker/tarball/master#=nengo_spinnaker-0.2.4'],

    install_requires=["nengo>=2.0.0, <3.0.0", "rig>=0.5.3, <1.0.0",
                      "bitarray>=0.8.1, <1.0.0", "nengo_spinnaker>=0.2.4"],
    classifiers=[
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",

        "Programming Language :: Python :: 2.7"
    ]
)

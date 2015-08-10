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
    install_requires=["nengo>=2.0.0, <3.0.0", "rig>=0.5.3, <1.0.0",
                      "bitarray>=0.8.1, <1.0.0", "nengo_spinnaker>=0.2.4"],
)

#Simulations

This folder contains larger pieces of functionality pertaining to controlling a physical robot __independent of the actual implementation__ of it.

I am simulating a __right arm__ just because that is my dominant arm.

Simulations needed to implement the final robot control system (in increasing order of complexity):

- [x] 1DOF (Degree of Freedom) Arm (can be generalized for head movement)
- [x] 2DOF Arm (can be generalized to eye movement)
- [x] 2DOF Arm (with finger movement) 
- [x] 3DOF Arm (with finger movement)(can be generalized to head + eye movement)
- [x] Action selection based on input (from Raspberry PI)
- [x] Action execution based on previously selected action
- [x] Computing rotating target position
- [x] Computing joint positions
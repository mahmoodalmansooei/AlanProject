@ECHO OFF
activate spinnaker_env && rig-power 192.168.240.0 on && rig-power 192.168.240.2 on && cd /d "C:\Users\Tove Kjellmark\Anaconda2\envs\spinnaker_env\alanproject"  && python furhatClass.py && PAUSE

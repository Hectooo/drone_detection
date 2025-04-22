# drone_detection

This Project is a demonstrator for a drone detection system that I made during an internship conducted in the French Aeronautical Company TDM in Mérignac (https://www.tdm-ing.com) at the beggining of the year 2024. Its initial purpose was to be presented in various occasion in the hope of attracting potential investors and implementing the system with professional standards.

The goal of this project was to prove the feasibility of an anti-drone protection system destined to be equipped on military ground vehicles, as drones (as demonstrated by the war in Ukraine) have become an essential part of modern warfare.

Hardware used in this project:
- NVIDIA Jetson AGX Orin 64GB card development kit ;
- E_CON e-CAM56_CUOAGX 2432x2048 camera (connected to the Jetson with an IPEX cable);
- ARDUCAM PTZ IMX477 camera ;
- FUJINON circular fisheye lens with m12 mount.

Once launched, the image recognition AI implemented on the Jetson card analyse in real time the video stream from the E_CON camera equipped with the fisheye lens in order to detect any drone in the area above the system. When it does, the system compute the angular coordinates (elevation and time angle from the camera) and forward them to the PTZ camera in order for it to point at the object, simulating in this way the presence of an automatic weapon destined to neutralize the threat.

For more information regarding the research process and implementation of this project, please check the documentation directory.

import math

# focal length of the fisheye lens (in mm)
F_LENGTH = 1.7
# pixel size of the camera sensor(in mm)
PXL_SIZE = 0.00274


# get the azimut of the object according to its (x,y) position on the image
# return value is expressed in degree between ]-180, 180]
def get_azimut(x, y, WIDTH, HEIGHT):
    centre_x = WIDTH / 2
    centre_y = HEIGHT / 2

    delta_x = x - centre_x
    delta_y = y - centre_y

    angle_rad = math.atan2(delta_x, delta_y)
    angle_deg = math.degrees(angle_rad)

    return angle_deg


# get the elevation of the object according to its (x,y) position on the image
# return value is expressed in degree between [90-FOV/2, 90]
def get_elevation(x, y, WIDTH, HEIGHT):
    centre_x = WIDTH / 2
    centre_y = HEIGHT / 2

    alpha = 1.015  # Approximate value for alpha based on FOV

    delta_x = x - centre_x
    delta_y = y - centre_y
    
    # distance of the pixel from the center
    dist = math.sqrt(delta_x**2 + delta_y**2) * PXL_SIZE

    angle_rad = alpha * (dist / F_LENGTH) # equidistant function
    angle_deg = 90 - math.degrees(angle_rad)
    
    return angle_deg


import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D

class RealTimeAnglePlotting:
    def __init__(self):
        self.angles = []
        self.fig, self.ax = self.initialize_plot()
        self.ani = FuncAnimation(self.fig, self.update, interval=50, blit=False) # update the graph every 50 ms

    def initialize_plot(self):
        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(111, projection='3d')
        ax.set_xlim([-1, 1])
        ax.set_ylim([1, -1]) # postive Y values are to be on the right side of the camera
        ax.set_zlim([-1, 1])
        ax.set_axis_off() # deactivate the grid for a better visibility
        
        ax.quiver(-1, 0, 0, 2, 0, 0, color='red', arrow_length_ratio=0.05)   # X axis is red because it represents the direction of the system
        ax.quiver(0, -1, 0, 0, 2, 0, color='black', arrow_length_ratio=0.05)
        ax.quiver(0, 0, -1, 0, 0, 2, color='black', arrow_length_ratio=0.05)
        
        return fig, ax

    def update_plot(self):
        self.ax.cla()  # Clear the previous plot
        # replicate what has been done in 'initialize_plot'
        self.ax.set_xlim([-1, 1])
        self.ax.set_ylim([1, -1])
        self.ax.set_zlim([-1, 1])
        self.ax.set_axis_off()
        
        self.ax.quiver(-1, 0, 0, 2, 0, 0, color='red', arrow_length_ratio=0.05)
        self.ax.quiver(0, -1, 0, 0, 2, 0, color='black', arrow_length_ratio=0.05)
        self.ax.quiver(0, 0, -1, 0, 0, 2, color='black', arrow_length_ratio=0.05)

        # for every angular coordinate (every detected object), compute its direction vector and plot it
        for angle_pair in self.angles:
            direction_vector = self.calculate_direction_vector(angle_pair)
            self.plot_line(direction_vector)

    def calculate_direction_vector(self, angles):
        elevation, azimuth = angles
        elevation_rad = np.radians(elevation)
        azimuth_rad = np.radians(azimuth)
        
        # Calculate direction vector components
        x = np.cos(elevation_rad) * np.cos(azimuth_rad)
        y = np.cos(elevation_rad) * np.sin(azimuth_rad)
        z = np.sin(elevation_rad)
        
        return np.array([x, y, z])

    def plot_line(self, direction_vector):
        origin = np.array([0, 0, 0])
        end_point = origin + direction_vector
        self.ax.quiver(origin[0], origin[1], origin[2], 
                       direction_vector[0], direction_vector[1], direction_vector[2],
                       length=1.0, normalize=True)

    def update(self, frame):
        self.update_plot()
        return self.ax.artists + self.ax.lines

    def set_angles(self, angles_list):
        self.angles = angles_list

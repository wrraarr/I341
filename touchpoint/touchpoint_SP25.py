import pygame
import time
import serial  # Make sure pyserial is installed for serial communication
import colorsys


# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Touch Points Visualization")
clock = pygame.time.Clock()


# Serial communication setup (update with correct port)
ser = serial.Serial('/dev/cu.usbmodem1401', 9600)


# TouchPoint class represents a touch sensor on the screen
class TouchPoint:
    def __init__(self, index, position, size):
        self.index = index
        self.position = position
        self.size = size
        self.is_active = False
        self.color = self.get_color_from_index(index)
        self.last_switch_time = time.time()

    def get_color_from_index(self, index):
        """Generate a unique color for each touch point."""
        rgb = colorsys.hsv_to_rgb(index / 12.0, 1.0, 1.0)
        return (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))

    def toggle(self):
        """Toggle the touch point's active state with a debounce delay."""
        current_time = time.time()
        if current_time - self.last_switch_time >= 0.2:  # 200ms debounce
            self.is_active = not self.is_active
            self.size = self.size * 2 if self.is_active else self.size / 2
            self.last_switch_time = current_time

    def render(self, screen):
        """Draw the touch point on the screen."""
        pygame.draw.rect(screen, self.color,
                         (self.position[0], self.position[1], int(self.size), int(self.size)))

# SensorBar class represents a sensor value displayed as a bar
class SensorBar:
    def __init__(self, label, color, x, y, is_dial=False):
        self.label = label
        self.color = color
        self.position = (x, y)
        self.values = []
        self.window_size = 10  # Smoothing window
        self.value = 0
        self.is_dial = is_dial

    def update(self, new_value):
        """Smooth sensor data by averaging the last few readings."""
        self.values.append(new_value)
        if len(self.values) > self.window_size:
            self.values.pop(0)
        self.value = sum(self.values) / len(self.values)

    def get_rainbow_color(self):
        """Convert sensor value to a rainbow color if it's a dial."""
        hue = (self.value / 1023.0) * 360
        rgb = colorsys.hsv_to_rgb(hue / 360, 1, 1)
        return (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))

    def draw(self, screen):
        """Draw the sensor bar on the screen."""
        bar_color = self.get_rainbow_color() if self.is_dial else self.color
        bar_width = (self.value / 1023) * WIDTH
        pygame.draw.rect(screen, bar_color, (self.position[0], self.position[1], bar_width, 30))

        font = pygame.font.Font(None, 24)
        text = font.render(f"{self.label}: {int(self.value)}", True, (255, 255, 255))
        screen.blit(text, (self.position[0], self.position[1] - 20))

# Define touch point positions
touchpoint_positions = {
    "Workbench 1": [(100, 150), (150, 150), (200, 150), (250, 150)],
    "Workbench 2": [(400, 150), (450, 150), (500, 150), (550, 150)],
    "3D Printer 1": [(300, 300), (350, 300)],
    "3D Printer 2": [(500, 300), (550, 300)]
}

# Create touch points
default_size = 20
touch_points = [
    TouchPoint(index, (x, y), default_size)
    for index, positions in enumerate(touchpoint_positions.values())
    for x, y in positions
]

def draw_labels():
    """Draw the group labels above the touchpoints."""
    font = pygame.font.Font(None, 28)
    for label, positions in touchpoint_positions.items():
        x, y = positions[0]
        text = font.render(label, True, (255, 255, 255))
        screen.blit(text, (x, y - 30))

# Create sensor bars
sensor_bars = [
    SensorBar("Distance", (255, 0, 0), 50, 400),
    SensorBar("Dial", (0, 255, 0), 50, 450, is_dial=True),
    SensorBar("Light", (0, 0, 255), 50, 500)
]

# Game loop
running = True
while running:
    screen.fill((0, 0, 0))  # Clear screen

    # Handle events (e.g., closing the window)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Read and process serial data from Arduino
    if ser.in_waiting:
        try:
            line = ser.readline().decode('utf-8').strip()
            data = list(map(int, line.split(',')))  # Convert all values to integers

            # Ensure correct data format before proceeding
            if len(data) < 5:
                raise ValueError("Incomplete data received")

            # Update touch points based on touch sensor data
            touch_index = data[3]  
            if 0 <= touch_index < len(touch_points):
                touch_points[touch_index].toggle()

            # Update sensor bars
            for i in range(3):
                sensor_bars[i].update(data[i])

            # Check for button press and adjust touch point color
            if data[4] == 0:  # Button is pressed
                dial_value = sensor_bars[1].value
                for touch_point in touch_points:
                    if touch_point.is_active:
                        touch_point.color = colorsys.hsv_to_rgb(dial_value / 1023, 1, 1)
                        touch_point.color = tuple(int(c * 255) for c in touch_point.color)
                        touch_point.toggle()

        except (ValueError, IndexError):
            print("Warning: Invalid or incomplete data received")

    # Render touch points
    for touch_point in touch_points:
        touch_point.render(screen)

    draw_labels()

    # Render sensor bars
    for bar in sensor_bars:
        bar.draw(screen)

    # Update display
    pygame.display.flip()
    clock.tick(60)

# Clean up
pygame.quit()
ser.close()




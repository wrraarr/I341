import pygame
import time
import serial  # Make sure pyserial is installed for serial communication
import colorsys


# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Touch Points Visualization")
clock = pygame.time.Clock()


#
# NO ARDUINO TEST CODE
#
# Lines needed for communication with arduino are commented out with -> ###


# Serial communication setup (update with correct port)
### ser = serial.Serial('/dev/cu.usbmodem1401', 9600)


# TouchPoint class represents a touch sensor on the screen
class TouchPoint:
    def __init__(self, index, position, size):
        self.index = index
        self.position = position
        self.size = size
        self.is_active = False
        self.color =  (128, 128, 128) #self.get_color_from_index(0)
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

    def interpolate_color(self, color1, color2):
        # Normalize self.value to a ratio between 0 and 1
        ratio = self.value / 1023
        # Ensure the ratio does not exceed bounds
        ratio = max(0, min(1, ratio))
        
        r = int(color1[0] + (color2[0] - color1[0]) * ratio)
        g = int(color1[1] + (color2[1] - color1[1]) * ratio)
        b = int(color1[2] + (color2[2] - color1[2]) * ratio)

        return (r, g, b)

    def interpolate_three_colors(self, color1, color2, color3):
        # Normalize self.value to a ratio between 0 and 2
        ratio = self.value / 1023 * 2
        # Ensure the ratio does not exceed bounds
        ratio = max(0, min(2, ratio))

        if ratio <= 1:
            # Interpolate between color1 and color2
            r = int(color1[0] + (color2[0] - color1[0]) * ratio)
            g = int(color1[1] + (color2[1] - color1[1]) * ratio)
            b = int(color1[2] + (color2[2] - color1[2]) * ratio)
        else:
            # Interpolate between color2 and color3
            ratio -= 1
            r = int(color2[0] + (color3[0] - color2[0]) * ratio)
            g = int(color2[1] + (color3[1] - color2[1]) * ratio)
            b = int(color2[2] + (color3[2] - color2[2]) * ratio)

        return (r, g, b)

    def draw(self, screen):
        """Draw the sensor bar on the screen."""
        color1 = (255, 0, 0)  # Red
        color2 = (128, 128, 128)  # grey
        color3 = (0, 0, 255) # blue
        self.color = self.interpolate_three_colors(color2,color3,color1) if self.is_dial else self.color
        #bar_color = self.get_rainbow_color() if self.is_dial else self.color
        bar_width = (self.value / 1023) * WIDTH / 2
        if self.is_dial:
            height = 30
        else:
            height = 10
        pygame.draw.rect(screen, self.color, (self.position[0], self.position[1], bar_width, height))

        font = pygame.font.SysFont("bentonsans", 24)
        text = font.render(f"{self.label}: {int(self.value)}", True, (255, 255, 255))
        screen.blit(text, (self.position[0], self.position[1] - 20))

touchpoint_positions = {
    # Arrange touchpoints for workbenches
    "Workbench 1": [(100, 209)],
    "Workbench 2": [(150, 259)],
    "Workbench 3": [(200, 309)],
    "Workbench 4": [(250, 200)],
    "Workbench 5": [(300, 250)],
    "Workbench 6": [(350, 300)],

    # Arrange touchpoints for 3D printers in a separate area
    "3D Printer 1": [(520, 200)],
    "3D Printer 2": [(650, 200)],
    "3D Printer 3": [(780, 200)],
    "3D Printer 4": [(520, 270)],
    "3D Printer 5": [(650, 270)],
    "3D Printer 6": [(780, 270)],
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
    font = pygame.font.SysFont("bentonsans", 18)
    for label, positions in touchpoint_positions.items():
        x, y = positions[0]
        text = font.render(label, True, (255, 255, 255))
        screen.blit(text, (x, y - 20))

# Create sensor bars
sensor_bars = [
    SensorBar("Distance", (0, 255, 0), 50, 650),
    SensorBar("Activity Level", (0, 255, 0), 50, 550, is_dial=True),
    SensorBar("Light", (255, 255, 0), 50, 700)
]


def draw_text_box(screen, x, y, width, height, text, font, text_color, border_color, border_thickness):
    # Define the text box area
    text_box_rect = pygame.Rect(x, y, width, height)
    
    # Draw the text box border
    pygame.draw.rect(screen, border_color, text_box_rect, border_thickness)
    
    # Prepare text wrapping
    words = text.split(' ')
    lines = []
    current_line = ''
    
    for word in words:
        # Add current word to the line
        test_line = current_line + word + ' '
        text_surface = font.render(test_line, True, text_color)
        text_width = text_surface.get_width()
        
        # Check if the line exceeds the text box width
        if text_width < width - 20:  # Add a buffer for padding
            current_line = test_line
        else:
            # Start a new line
            lines.append(current_line)
            current_line = word + ' '
    
    # Append the last line
    if current_line:
        lines.append(current_line)
    
    # Render the lines of text
    line_height = font.get_height()
    for i, line in enumerate(lines):
        text_surface = font.render(line, True, text_color)
        screen.blit(text_surface, (x + 10, y + 10 + i * line_height))

#
# NO ARDUINO FUNCTION
#
# Function to update CSV based on key inputs
def update_csv(key, line):
    # Split line string into a list of integers
    data = list(map(int, line.split(',')))

    # Modify values based on key pressed
    if key == pygame.K_1:  # If '1' key is pressed
        data[0] += 25  # Modify first value
    elif key == pygame.K_q:
        data[0] -= 25
    elif key == pygame.K_2:  # If '2' key is pressed
        data[1] += 25  # Modify second value
    elif key == pygame.K_w:
        data[1] -= 25
    elif key == pygame.K_4:  # If '3' key is pressed
        data[2] += 25  # Modify third value
    elif key == pygame.K_r:
        data[2] -= 25

    elif key == pygame.K_a:
        data[3] = 1
    elif key == pygame.K_b:
        data[3] = 2
    elif key == pygame.K_c:
        data[3] = 3
    elif key == pygame.K_d:
        data[3] = 4
    elif key == pygame.K_e:
        data[3] = 5
    elif key == pygame.K_f:
        data[3] = 6
    elif key == pygame.K_g:
        data[3] = 7
    elif key == pygame.K_h:
        data[3] = 8
    elif key == pygame.K_i:
        data[3] = 9
    elif key == pygame.K_j:
        data[3] = 10
    elif key == pygame.K_k:
        data[3] = 11
    elif key == pygame.K_l:
        data[3] = 12
    elif key == pygame.K_m:
        data[4] = 0

    # Join the updated list back into a CSV string
    updated_line = ','.join(map(str, data))
    return updated_line

#
# NO ARDUINO FUNCTION
#
# set the sensor line to default
def default_line(line):
    data = list(map(int, line.split(',')))
    data[3] = -1
    data[4] = 1

    if data[0] > 1023: 
        data[0] = 1023
    if data[1] > 1023: 
        data[1] = 1023
    if data[2] > 1023: 
        data[2] = 1023

    if data[0] < 0: 
        data[0] = 0
    if data[1] < 0: 
        data[1] = 0
    if data[2] < 0: 
        data[2] = 0    

    # Join the updated list back into a CSV string
    updated_line = ','.join(map(str, data))
    return updated_line

#
# NO ARDUINO VARIABLE
#
# Initial simulator sensor values
line = '100,200,300,-1,1'

# print(pygame.font.get_fonts())

# Game loop
running = True
while running:
    screen.fill((0, 0, 0))  # Clear screen

    # Handle events (e.g., closing the window)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        else:
    # Read and process serial data from Arduino
    ### ser.in_waiting:
        ### try:
            ### line = ser.readline().decode('utf-8').strip()

            #
            # NO ARDUINO PROCEDURE
            #
            if event.type == pygame.KEYDOWN:
                line = update_csv(event.key, line)
                print(line)
            #
            #
            #

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
                dial_value = sensor_bars[1].color
                for touch_point in touch_points:
                    if touch_point.is_active:
                        touch_point.color = dial_value#colorsys.hsv_to_rgb(dial_value / 1023, 1, 1)
                        #touch_point.color = tuple(int(c * 255) for c in touch_point.color)
                        touch_point.toggle()

        ### except (ValueError, IndexError):
        ###     print("Warning: Invalid or incomplete data received")

    #
    # NO ARDUINO
    #
    # Reset all buttons and capacitive pads to inactive
    line = default_line(line)
    #
    #
    #

    # Draw the text box using the function
    font = pygame.font.SysFont("bentonsans", 30)
    greeting_text = "Hello! Please tell us about the current Fab Lab use so we can keep it running smooth."
    how_to_text = "Use the touch pads to select each area that is currently active. Use the dial to indicate the level of activity."
    # Define colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    draw_text_box(
        screen=screen,
        x=600, 
        y=400, 
        width=350, 
        height=400, 
        font=font,
        text=how_to_text, 
        text_color=WHITE, 
        border_color=BLACK, 
        border_thickness=2
    )    
    font = pygame.font.SysFont("bentonsans", 34, bold=True)
    draw_text_box(
        screen=screen,
        x=70, 
        y=50, 
        width=800, 
        height=50, 
        font=font,
        text=greeting_text, 
        text_color=WHITE, 
        border_color=BLACK, 
        border_thickness=2
    ) 


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
### ser.close()




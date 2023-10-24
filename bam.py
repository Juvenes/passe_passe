import pygame
import io
from picamera2 import Picamera2
from PIL import Image

# Initialize pygame
pygame.init()

# Set the dimensions of the window
WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PiCamera2 Preview with Pygame")

# Initialize the camera
picam2 = Picamera2()
picam2.start()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Capture the image to a BytesIO stream
    stream = io.BytesIO()
    picam2.capture_file(stream, format='jpeg')
    stream.seek(0)
    
    # Convert the stream to a Pygame image
    image = Image.open(stream)
    image = pygame.image.fromstring(image.tobytes(), image.size, image.mode)
    
    # Display the image
    screen.blit(image, (0, 0))
    pygame.display.flip()

picam2.close()
pygame.quit()





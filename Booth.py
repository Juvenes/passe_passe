import pygame
import io
from picamera2 import Picamera2
import tempfile
from PIL import Image , ImageEnhance
import time
import qrcode
import os
import numpy as np
from datetime import datetime
import requests
from libcamera import controls ,Transform

def process_image(main_image, logo):
    # Load the main image and ensure it is in RGBA mode
    main_image = main_image.convert("RGBA")
    # Load the logo image and ensure it is in RGBA mode
    logo = logo.convert("RGBA")
    image_width, image_height = main_image.size
    logo_width, logo_height = logo.size
    x = image_width - logo_width
    y = image_height - logo_height
    # Assuming the logo size is already 50x50 as needed
    main_image.paste(logo,(x,y),logo)
    # Paste the logo onto the main image, using logo as the mask for transparency

    # Enhance sharpness of the main image
    sharpness_enhancer = ImageEnhance.Sharpness(main_image)
    enhanced_sharpness_image = sharpness_enhancer.enhance(1.2)  # Adjust the factor as needed
    # Since you wanted to use this image in Pygame, you need to convert the data

    return enhanced_sharpness_image

class Screen:
    def __init__(self, screen):
        self.screen = screen

    def draw(self):
        pass

    def handle_event(self, event):
        pass

class StartScreen(Screen):
    def __init__(self, screen):
        super().__init__(screen)
        print("HAHAHHAHAHHA")
        self.font = pygame.font.SysFont(None, 56)
        self.text = self.font.render("Take Image", True, (255, 255, 255))
        self.button_rect = self.text.get_rect(center=(screen_width/2, screen_height/2))

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.text, self.button_rect.topleft)
        pygame.display.flip()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.button_rect.collidepoint(event.pos):
            return PhotoScreen(self.screen)
        return self



class PhotoPreviewScreen(Screen):
    def __init__(self, screen, photo_path):
        super().__init__(screen)
        self.photo = Image.open(photo_path)
        self.font = pygame.font.SysFont(None, 48)
        self.screen.fill((0, 0, 0))
        # Define the buttons
        self.keep_button = pygame.Rect(screen_width/2 - 100, screen_height - 100, 200, 50)
        logo = Image.open("stamp1.png")
        self.photo = process_image(self.photo,logo)
        mode = self.photo.mode
        size = self.photo.size
        data = self.photo.tobytes()
    # Initialize Pygame and create a surface with the enhanced image
        self.photo_py = pygame.image.fromstring(data, size, mode)

    def draw(self):
        # Center the photo on the screen
        self.screen.blit(self.photo_py, (0,0))
        
        # Draw the buttons
        pygame.draw.rect(self.screen, (0, 255, 0), self.keep_button)
        
        keep_text = self.font.render("Finish", True, (255, 255, 255))
        
        self.screen.blit(keep_text, (self.keep_button.x + (self.keep_button.width - keep_text.get_width()) // 2, self.keep_button.y + (self.keep_button.height - keep_text.get_height()) // 2))
        
        pygame.display.flip()
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.keep_button.collidepoint(event.pos):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = f"saved_photos/final_{timestamp}.png"
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                self.photo.save(save_path)
                return StartScreen(self.screen)
        return self    
            
            

class PhotoScreen(Screen):
    def __init__(self, screen):
        super().__init__(screen)
        self.finished = False
        self.font_large = pygame.font.SysFont(None, 200)
        self.font_medium = pygame.font.SysFont(None, 50)
        self.picam2 = Picamera2()
        self.config = self.picam2.create_video_configuration(main={"size": (1024,600)},transform=Transform(hflip=True))
        self.picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous, "AfSpeed": controls.AfSpeedEnum.Fast})
        self.picam2.configure(self.config)
        self.picam2.start()
        self.start_time = None
        self.final = None
        
        # Define the "Ready" button properties
        self.ready_button_text = self.font_medium.render("Ready", True, (255, 255, 255))
        self.ready_button_rect = pygame.Rect(screen_width/2 - 100, screen_height - 100, 200, 50)

    def draw(self):
        self.screen.fill((0, 0, 0))
        # Capture the image to a BytesIO stream for live previe
        stream = io.BytesIO()
        self.picam2.capture_file(stream, format='jpeg')
        stream.seek(0)
        # Convert the stream to a Pygame image
        image = Image.open(stream)
        image = pygame.image.fromstring(image.tobytes(), image.size, image.mode)
        self.final = image
        image_width, image_height = image.get_size()
        x = (screen_width - image_width) // 2
        self.screen.blit(image, (x, 0))
        if not self.start_time:
            pygame.draw.rect(self.screen, (0, 128, 0), self.ready_button_rect)
            self.screen.blit(self.ready_button_text, (self.ready_button_rect.x + (self.ready_button_rect.width - self.ready_button_text.get_width()) // 2, self.ready_button_rect.y + (self.ready_button_rect.height - self.ready_button_text.get_height()) // 2))
        elapsed_time = time.time() - self.start_time if self.start_time else 0 
        if 2 <= elapsed_time < 3:
            countdown_text = self.font_large.render("3", True, (255, 0, 0))
            self.screen.blit(countdown_text, (screen_width/2 - countdown_text.get_width()/2, screen_height/2 - countdown_text.get_height()/2))
        elif 3 <= elapsed_time < 4:
            countdown_text = self.font_large.render("2", True, (255, 0, 0))
            self.screen.blit(countdown_text, (screen_width/2 - countdown_text.get_width()/2, screen_height/2 - countdown_text.get_height()/2))
        elif 4 <= elapsed_time < 5:
            countdown_text = self.font_large.render("1", True, (255, 0, 0))
            self.screen.blit(countdown_text, (screen_width/2 - countdown_text.get_width()/2, screen_height/2 - countdown_text.get_height()/2))
            self.final = image
        pygame.display.flip()  
    def update(self):
        elapsed_time = time.time() - self.start_time if self.start_time else 0 
        if elapsed_time >= 5:
            # Capture the photo and flash the screen in white
            self.picam2.stop()
            self.picam2.close()
            self.screen.fill((255, 255, 255))
            pygame.display.flip()
            pygame.image.save(self.final, 'output.png') 
            return PhotoPreviewScreen(self.screen,'output.png')
        return self
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.ready_button_rect.collidepoint(event.pos):
                pygame.draw.rect(self.screen, (0, 0, 0), self.ready_button_rect)
                self.screen.blit(self.ready_button_text, (self.ready_button_rect.x + (self.ready_button_rect.width - self.ready_button_text.get_width()) // 2, self.ready_button_rect.y + (self.ready_button_rect.height - self.ready_button_text.get_height()) // 2))
                self.start_time = time.time()
        return self.update()


pygame.init()

screen_width, screen_height = pygame.display.Info().current_w, pygame.display.Info().current_h
screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)

current_screen = StartScreen(screen)
running = True
while running:
    current_screen.draw()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        else:
            current_screen = current_screen.handle_event(event)
    if isinstance(current_screen, PhotoScreen):
        current_screen = current_screen.update()

pygame.quit()

import pygame
import io
from picamera2 import Picamera2
from PIL import Image
import time
import os
import numpy as np
import cv2
from libcamera import controls ,Transform


def process_image(pygame_image, logo_path):
    # Convert Pygame surface to OpenCV image
    cv_image = cv2.cvtColor(pygame.surfarray.array3d(pygame_image), cv2.COLOR_RGB2BGR)

    # Apply image enhancements here (if any)

    # Adjust brightness and contrast
    # Note: These values are examples and may need to be adjusted
    alpha = 1.5  # Contrast control
    beta = 50    # Brightness control
    adjusted = cv2.convertScaleAbs(cv_image, alpha=alpha, beta=beta)

    # Sharpen the image
    kernel = np.array([[0, -1, 0], [-1, 5,-1], [0, -1, 0]])
    sharpened = cv2.filter2D(adjusted, -1, kernel)

    # Load logo and add it to the bottom right corner
    logo = cv2.imread(logo_path, cv2.IMREAD_UNCHANGED)
    y_offset = cv_image.shape[0] - logo.shape[0]
    x_offset = cv_image.shape[1] - logo.shape[1]
    sharpened[y_offset:y_offset+logo.shape[0], x_offset:x_offset+logo.shape[1]] = logo

    return sharpened

os.system("v4l2-ctl --set-ctrl wide_dynamic_range=1 -d /dev/v4l-subdev0")
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
            return ChoiceScreen(self.screen)
        return self

class ChoiceScreen(Screen):
    def __init__(self, screen):
        super().__init__(screen)
        self.font = pygame.font.SysFont(None, 56)
        self.choices = ["Photo", "Gif", "Filtre"]
        self.buttons = {choice: self.font.render(choice, True, (255, 255, 255)) for choice in self.choices}

        spacing = screen_width // 16
        button_width = screen_width // 4
        self.button_rects = {
            choice: text.get_rect(center=((i + 1) * spacing + i * button_width + button_width / 2, screen_height / 2))
            for i, (choice, text) in enumerate(self.buttons.items())
        }

    def draw(self):
        self.screen.fill((0, 0, 0))
        for choice, text in self.buttons.items():
            self.screen.blit(text, self.button_rects[choice].topleft)
        pygame.display.flip()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for choice, rect in self.button_rects.items():
                if rect.collidepoint(event.pos):
                    return ChoiceDetailScreen(self.screen, choice)
        return self

class ChoiceDetailScreen(Screen):
    def __init__(self, screen, choice):
        super().__init__(screen)
        self.choice = choice
        self.font_large = pygame.font.SysFont(None, 72)
        self.font_small = pygame.font.SysFont(None, 48)

        # Title and explanatory text for each choice
        self.titles = {
            "Photo": "Take a Photo",
            "Gif": "Create a Gif from 2 secondes photos",
            "Filtre": "Take a Photo with filters"
        }
        self.explanations = {
            "Photo": "This option allows you to take a single photo.",
            "Gifs": "This option creates a short looping video.",
            "Filtre": "This option lets you send a text message."
        }

        # Rendered text surfaces
        self.title_text = self.font_large.render(self.titles[self.choice], True, (255, 255, 255))
        self.explanation_text = self.font_small.render(self.explanations[self.choice], True, (255, 255, 255))
        self.go_button_text = self.font_large.render("Go", True, (255, 255, 255))
        self.go_button_rect = self.go_button_text.get_rect(center=(screen_width/2, 3*screen_height/4))
        self.circle_radius = int(self.go_button_rect.width * 0.6)  # Adjust as needed

    def draw(self):
        self.screen.fill((0, 0, 0))

        # Draw borders
        pygame.draw.circle(self.screen, (255, 255, 255), self.go_button_rect.center, self.circle_radius, 2)

        # Draw text
        self.screen.blit(self.title_text, (screen_width/2 - self.title_text.get_width()/2, screen_height/8))
        self.screen.blit(self.explanation_text, (screen_width/2 - self.explanation_text.get_width()/2, screen_height/4))
        self.screen.blit(self.go_button_text, self.go_button_rect.topleft)

        pygame.display.flip()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.go_button_rect.collidepoint(event.pos):
                if self.choice == "Photo":
                    return PhotoScreen(self.screen)  # Transition to the PhotoScreen when "Photo" is selected
                # Add similar conditions for other choices if needed
                print(f"You chose {self.choice}!")
        return self
    

class PhotoPreviewScreen(Screen):
    def __init__(self, screen, photo_path):
        super().__init__(screen)
        self.photo = pygame.image.load(photo_path)
        self.font = pygame.font.SysFont(None, 48)
        self.screen.fill((0, 0, 0))
        # Define the buttons
        self.retry_button = pygame.Rect(50, screen_height/4, 150, 50)
        self.keep_button = pygame.Rect(50, screen_height/2, 150, 50)
        self.photo = process_image(self.photo, "stamp.png")  # Replace with your logo path


    def draw(self):
        # Center the photo on the screen
        x = (screen_width - self.photo.get_width()) // 2
        y = (screen_height - self.photo.get_height()) // 2
        self.screen.blit(self.photo, (x+100, y))
        
        # Draw the buttons
        pygame.draw.rect(self.screen, (255, 0, 0), self.retry_button)
        pygame.draw.rect(self.screen, (0, 255, 0), self.keep_button)
        
        retry_text = self.font.render("Retry", True, (255, 255, 255))
        keep_text = self.font.render("Keep-it", True, (255, 255, 255))
        
        self.screen.blit(retry_text, (self.retry_button.x + (self.retry_button.width - retry_text.get_width()) // 2, self.retry_button.y + (self.retry_button.height - retry_text.get_height()) // 2))
        self.screen.blit(keep_text, (self.keep_button.x + (self.keep_button.width - keep_text.get_width()) // 2, self.keep_button.y + (self.keep_button.height - keep_text.get_height()) // 2))
        
        pygame.display.flip()
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.retry_button.collidepoint(event.pos):
                # Return to the PhotoScreen to retake the photo
                return PhotoScreen(self.screen)
            elif self.keep_button.collidepoint(event.pos): # Replace with your logo path
                cv2.imwrite("path_to_save_final_image.png", self.p)  # Replace with your save path
                print("Photo saved!")
                return StartScreen(self.screen)
        return self


class PhotoScreen(Screen):
    def __init__(self, screen):
        super().__init__(screen)
        self.finished = False
        self.font_large = pygame.font.SysFont(None, 200)
        self.font_medium = pygame.font.SysFont(None, 50)
        self.picam2 = Picamera2()
        self.config = self.picam2.create_video_configuration(main={"size": (1280,720)},transform=Transform(hflip=True))
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

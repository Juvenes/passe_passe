import pygame
import io
from picamera2 import Picamera2
from PIL import Image
import time
from libcamera import controls





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
        self.choices = ["Photo", "Boomerang", "Message"]
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
            "Boomerang": "Create a Boomerang",
            "Message": "Send a Message"
        }
        self.explanations = {
            "Photo": "This option allows you to take a single photo.",
            "Boomerang": "This option creates a short looping video.",
            "Message": "This option lets you send a text message."
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

    def draw(self):
        # Center the photo on the screen
        x = (screen_width - self.photo.get_width()) // 2
        y = (screen_height - self.photo.get_height()) // 2
        self.screen.blit(self.photo, (x, y))
        
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
            elif self.keep_button.collidepoint(event.pos):
                # Transition to the next screen or action after keeping the photo
                # For now, we'll just print a message
                print("Photo saved!")
                # Return to the main screen or any other screen you'd like
                return StartScreen(self.screen)  # Replace with your main screen or desired screen
        return self


class PhotoScreen(Screen):
    def __init__(self, screen):
        super().__init__(screen)
        self.finished = False
        self.font_large = pygame.font.SysFont(None, 200)
        self.font_medium = pygame.font.SysFont(None, 50)
        self.picam2 = Picamera2()
        self.picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous, "AfSpeed": controls.AfSpeedEnum.Fast})
        self.picam2.start()
        self.stream = io.BytesIO()
        self.image =None
        self.start_time = None
        
        # Define the "Ready" button properties
        self.ready_button_text = self.font_medium.render("Ready", True, (255, 255, 255))
        self.ready_button_rect = pygame.Rect(screen_width/2 - 100, screen_height - 100, 200, 50)

    def draw(self):
        self.screen.fill((0, 0, 0))
        # Capture the image to a BytesIO stream for live preview

        self.picam2.capture_file(self.stream, format='jpeg')
        self.stream.seek(0)

        # Convert the stream to a Pygame image
        self.image = Image.open(self.stream)
        self.image = pygame.image.fromstring(self.image.tobytes(), self.image.size, self.image.mode)
        image_width, image_height = self.image.get_size()
        x = (screen_width - image_width) // 2
        pygame.draw.rect(self.screen, (0, 128, 0), self.ready_button_rect)
        self.screen.blit(self.ready_button_text, (self.ready_button_rect.x + (self.ready_button_rect.width - self.ready_button_text.get_width()) // 2, self.ready_button_rect.y + (self.ready_button_rect.height - self.ready_button_text.get_height()) // 2))
        self.screen.blit(self.image, (x, 0))
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
        pygame.display.flip()  
    def update(self):
        elapsed_time = time.time() - self.start_time if self.start_time else 0 
        if elapsed_time >= 5:
            # Capture the photo and flash the screen in white
            self.picam2.stop()
            self.picam2.close()
            self.stream.close()
            self.screen.fill((255, 255, 255))
            pygame.display.flip()
            pygame.image.save(self.image, 'output.png') 
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

pygame.quit()

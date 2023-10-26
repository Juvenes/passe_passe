import pygame
import io
from picamera2 import Picamera2
from PIL import Image
import time

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
            for choice, rect in self.go_button_rect.items():
                if rect.collidepoint(event.pos):
                    if choice == "Photo":
                        return PhotoScreen(self.screen)  # Transition to the PhotoScreen when "Photo" is selected
                    # Add similar conditions for other choices if needed
                    print(f"You chose {choice}!")
        return self
class PhotoScreen(Screen):
    def __init__(self, screen):
        super().__init__(screen)
        self.font_large = pygame.font.SysFont(None, 200)
        self.picam2 = Picamera2()
        self.picam2.start()
        self.start_time = None

    def draw(self):
        # Capture the image to a BytesIO stream for live preview
        stream = io.BytesIO()
        self.picam2.capture_file(stream, format='jpeg')
        stream.seek(0)
        
        # Convert the stream to a Pygame image
        image = Image.open(stream)
        image = pygame.image.fromstring(image.tobytes(), image.size, image.mode)
        
        # Display the live preview
        self.screen.blit(image, (0, 0))

        # Display countdown after waiting for 2 seconds
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
        elif elapsed_time >= 5:
            # Capture the photo and flash the screen in white
            self.picam2.capture_file("captured_photo.jpg", format='jpeg')
            self.screen.fill((255, 255, 255))

        pygame.display.flip()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.start_time = time.time()
        return self

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

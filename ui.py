"""
Holds the code and functions related to the User Interface for the Synthesizer.
"""

import pygame
from audio import AudioPlayer
from synth import Synth


class SynthUI:
    attack_input = 0.1
    decay_input = 0.1
    sustain_input = 0.7
    release_input = 0.2
    cutoff_input = 2000

    def __init__(self):
        self.rate = 44100
        self.width, self.height = 1200, 1000
        self.font = pygame.font.Font(None, 36)
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Simple Synth")

        self.synth = Synth(self.rate)
        self.audio_player = AudioPlayer()  # Create an instance of AudioPlayer

        self.frequency_input = ""
        self.duration_input = ""
        self.active_input = "frequency"

        self.slider_x = 50
        self.slider_y = 250
        self.slider_width = 300
        self.slider_height = 40
        self.lfo_slider_y = 300
        self.toggle_y = 370
        self.adsr_slider_y = 400  # Position for ADSR sliders

    def draw_input_boxes(self):
        self.screen.fill((0, 0, 0))
        pygame.draw.rect(self.screen, (255, 255, 255), (50, 50, 300, 40), 2)
        pygame.draw.rect(self.screen, (255, 255, 255), (50, 150, 300, 40), 2)
        pygame.draw.rect(self.screen, (255, 255, 255),
                         (self.slider_x, self.slider_y, self.slider_width, self.slider_height), 2)
        pygame.draw.rect(self.screen, (255, 255, 255),
                         (self.slider_x, self.lfo_slider_y, self.slider_width, self.slider_height),
                         2)

        frequency_text = self.font.render(f"Frequency: {self.frequency_input}", True,
                                          (255, 255, 255))
        duration_text = self.font.render(f"Duration: {self.duration_input}", True, (255, 255, 255))
        cutoff_text = self.font.render(f"Cutoff: {SynthUI.cutoff_input} Hz", True, (255, 255, 255))
        lfo_rate_text = self.font.render(f"LFO Rate: {self.synth.lfo_rate:.2f} Hz",
                                         True,
                                         (255, 255, 255))
        lfo_toggle_text = self.font.render(
            f"LFO: {'ON' if self.synth.lfo_enabled else 'OFF'}",
            True, (255, 255, 255))

        self.screen.blit(frequency_text, (60, 55))
        self.screen.blit(duration_text, (60, 155))
        self.screen.blit(cutoff_text, (60, 255))
        self.screen.blit(lfo_rate_text, (60, 305))
        self.screen.blit(lfo_toggle_text, (60, self.toggle_y))

        attack_text = self.font.render(f"Attack: {SynthUI.attack_input:.2f} s", True,
                                       (255, 255, 255))
        decay_text = self.font.render(f"Decay: {SynthUI.decay_input:.2f} s", True, (255, 255, 255))
        sustain_text = self.font.render(f"Sustain: {SynthUI.sustain_input:.2f}", True,
                                        (255, 255, 255))
        release_text = self.font.render(f"Release: {SynthUI.release_input:.2f} s", True,
                                        (255, 255, 255))

        self.screen.blit(attack_text, (60, self.adsr_slider_y))
        self.screen.blit(decay_text, (60, self.adsr_slider_y + 30))
        self.screen.blit(sustain_text, (60, self.adsr_slider_y + 60))
        self.screen.blit(release_text, (60, self.adsr_slider_y + 90))

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.frequency_input and self.duration_input:
                    frequency = float(self.frequency_input)
                    duration = float(self.duration_input)
                    sound_file = self.synth.generate_and_play_sound(
                        frequency, duration, SynthUI.cutoff_input
                    )
                    self.audio_player.play_sound(sound_file)
                else:
                    print("Please enter valid numbers for frequency and duration.")
            elif event.key == pygame.K_BACKSPACE:
                if self.active_input == "frequency" and self.frequency_input:
                    self.frequency_input = self.frequency_input[:-1]
                elif self.active_input == "duration" and self.duration_input:
                    self.duration_input = self.duration_input[:-1]
            elif event.key == pygame.K_TAB:  # Switch active input
                self.active_input = "duration" if self.active_input == "frequency" else "frequency"
            elif event.key == pygame.K_SPACE:  # Toggle LFO on/off
                self.synth.lfo_enabled = not self.synth.lfo_enabled  # Stop LFO thread
            else:
                if self.active_input == "frequency":
                    if event.unicode.isnumeric() or event.unicode in ['.', '']:
                        if len(self.frequency_input) < 10:
                            self.frequency_input += event.unicode
                elif self.active_input == "duration":
                    if event.unicode.isnumeric() or event.unicode in ['.', '']:
                        if len(self.duration_input) < 10:
                            self.duration_input += event.unicode
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            # Handle cutoff slider
            if (self.slider_x <= mouse_x <= self.slider_x + self.slider_width
                    and self.slider_y <= mouse_y <= self.slider_y + self.slider_height):
                SynthUI.cutoff_input = int((mouse_x - self.slider_x) / self.slider_width * 5000)
            # Handle LFO rate slider
            elif (self.slider_x <= mouse_x <= self.slider_x + self.slider_width
                  and self.lfo_slider_y <= mouse_y <= self.lfo_slider_y + self.slider_height):
                self.synth.lfo_rate = (mouse_x - self.slider_x) / self.slider_width * 10
            # Handle Attack slider
            elif (self.slider_x <= mouse_x <= self.slider_x + self.slider_width
                  and self.adsr_slider_y <= mouse_y <= self.adsr_slider_y + self.slider_height):
                SynthUI.attack_input = (
                                               mouse_x - self.slider_x) / self.slider_width * 2  # Max 2 seconds
                self.synth.attack = SynthUI.attack_input
            # Handle Decay slider
            elif (self.slider_x <= mouse_x <= self.slider_x + self.slider_width
                  and self.adsr_slider_y + 30 <= mouse_y <= self.adsr_slider_y + 30 + self.slider_height):
                SynthUI.decay_input = (
                                              mouse_x - self.slider_x) / self.slider_width * 2  # Max 2 seconds
                self.synth.decay = SynthUI.decay_input
            # Handle Sustain slider
            elif (self.slider_x <= mouse_x <= self.slider_x + self.slider_width
                  and self.adsr_slider_y + 60 <= mouse_y <= self.adsr_slider_y + 60 + self.slider_height):
                SynthUI.sustain_input = (
                                                mouse_x - self.slider_x) / self.slider_width  # Level 0 to 1
                self.synth.sustain = SynthUI.sustain_input
            # Handle Release slider
            elif (self.slider_x <= mouse_x <= self.slider_x + self.slider_width
                  and self.adsr_slider_y + 90 <= mouse_y <= self.adsr_slider_y + 90 + self.slider_height):
                SynthUI.release_input = (
                                                mouse_x - self.slider_x) / self.slider_width * 2  # Max 2 seconds
                self.synth.release = SynthUI.release_input

    def run(self):
        running = True
        while running:
            self.draw_input_boxes()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self.handle_input(event)

            pygame.display.flip()
            pygame.time.Clock().tick(30)

        self.synth.stop_lfo_thread()  # Ensure the thread is stopped on exit

import numpy as np
from scipy.signal import sawtooth, lfilter, butter
from scipy.io.wavfile import write
import threading
import time


class Synth:
    def __init__(self, rate=44100):
        self.rate = rate
        self.lfo_enabled = False
        self.lfo_rate = 1.0
        self.lfo_value = 0.0
        self.lfo_thread = None
        self.running = False

        # Envelope parameters
        self.attack = 0.1  # seconds
        self.decay = 0.1  # seconds
        self.sustain = 0.7  # level (0 to 1)
        self.release = 0.2  # seconds

    def low_pass_filter(self, signal, cutoff):
        nyquist = 0.5 * self.rate
        cutoff = np.clip(cutoff, 1, 5000)
        normal_cutoff = cutoff / nyquist
        coefficients = butter(1, normal_cutoff, btype='low', analog=False)
        b, a = coefficients[0], coefficients[1]
        return lfilter(b, a, signal)

    def generate_lfo_signal(self):
        while self.running:
            if self.lfo_enabled:
                t = time.time() % (1 / self.lfo_rate)
                self.lfo_value = 0.5 * (1 + sawtooth(2 * np.pi * self.lfo_rate * t))
            time.sleep(0.01)

    def start_lfo_thread(self):
        self.running = True
        self.lfo_thread = threading.Thread(target=self.generate_lfo_signal)
        self.lfo_thread.start()

    def stop_lfo_thread(self):
        self.running = False
        if self.lfo_thread is not None:
            self.lfo_thread.join()

    def generate_envelope(self, duration):
        # Calculate the number of samples for each stage
        attack_samples = int(self.attack * self.rate)
        decay_samples = int(self.decay * self.rate)
        sustain_samples = int((duration - self.attack - self.decay - self.release) * self.rate)
        release_samples = int(self.release * self.rate)

        # Ensure sustain_samples is not negative
        sustain_samples = max(0, sustain_samples)

        # Create the envelope
        total_samples = attack_samples + decay_samples + sustain_samples + release_samples
        envelope = np.zeros(int(duration * self.rate))

        # Attack
        for i in range(min(attack_samples, len(envelope))):
            envelope[i] = i / attack_samples

        # Decay
        for i in range(min(decay_samples, len(envelope) - attack_samples)):
            envelope[attack_samples + i] = 1 - (1 - self.sustain) * (i / decay_samples)

        # Sustain
        if sustain_samples > 0:
            envelope[
            attack_samples + decay_samples:attack_samples + decay_samples + sustain_samples] = self.sustain

        # Release
        for i in range(min(release_samples,
                           len(envelope) - (attack_samples + decay_samples + sustain_samples))):
            envelope[attack_samples + decay_samples + sustain_samples + i] = self.sustain * (
                        1 - (i / release_samples))

        return envelope

    def generate_and_play_sound(self, frequency, duration, cutoff):
        t = np.linspace(0, duration, int(self.rate * duration), endpoint=False)
        func = sawtooth(2 * np.pi * frequency * t)
        func = func / np.max(np.abs(func))

        if self.lfo_enabled:
            current_cutoff = self.lfo_value * 5000
        else:
            current_cutoff = cutoff

        filtered_func = self.low_pass_filter(func, current_cutoff)

        # Apply the envelope
        envelope = self.generate_envelope(duration)
        final_signal = filtered_func * envelope

        write('generated-audios/test.wav', self.rate, final_signal)
        return 'generated-audios/test.wav'

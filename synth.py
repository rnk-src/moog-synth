
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
                # LFO value between 0 and 1
            time.sleep(0.01)  # Update rate (10 ms)

    def start_lfo_thread(self):
        self.running = True
        self.lfo_thread = threading.Thread(target=self.generate_lfo_signal)
        self.lfo_thread.start()

    def stop_lfo_thread(self):
        self.running = False
        if self.lfo_thread is not None:
            self.lfo_thread.join()

    def generate_and_play_sound(self, frequency, duration, cutoff):
        t = np.linspace(0, duration, int(self.rate * duration), endpoint=False)
        func = sawtooth(2 * np.pi * frequency * t)
        func = func / np.max(np.abs(func))

        # Use LFO value to sweep through the cutoff range (0 to 5000 Hz)
        if self.lfo_enabled:
            current_cutoff = self.lfo_value * 5000  # Map LFO value to cutoff range
        else:
            current_cutoff = cutoff  # Default cutoff when LFO is off

        filtered_func = self.low_pass_filter(func, current_cutoff)

        write('generated-audios/test.wav', self.rate, filtered_func)
        return 'generated-audios/test.wav'

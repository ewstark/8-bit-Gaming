import math
import struct
import wave
import winsound
import random
import argparse

g_verbose = True
g_sample_rate = 16000

class AudioBuffer_8bit():
    def __init__(self):
        self.samples = []
    def raw(self):
        return self.samples
    def pad_silence(self, num_samples):
        self.samples += [0 for _ in range(num_samples)]
    def append_sample(self, sample):
        assert 0 <= sample <= 255
        self.samples.append(int(sample))
    def append(self, audio_buffer):
        self.samples += audio_buffer.raw()
    def length(self):
        return len(self.samples)
    def peaks(self):
        return (min(self.samples), max(self.samples))
    def save(self, filename):
        raw_samples = []
        for s in self.samples:
            raw_samples.append(struct.pack('B', s))
        with wave.open(filename, "w") as wr:
            wr.setnchannels(1)  # mono = 1 channel
            wr.setsampwidth(1)  # 1-byte = 8-bits per sample
            wr.setframerate(g_sample_rate)
            wr.writeframes(b''.join(raw_samples))

def make_tone (duration, freq, amp=1.0):
    audio_event = AudioBuffer_8bit()
    totalSamples = int(duration * g_sample_rate)
    theta_per_sample = 2 * math.pi / g_sample_rate
    sampleNumber = 0
    while sampleNumber < totalSamples:
        pct = sampleNumber / totalSamples
        a = amp
        if pct < 0.1:
            a *= pct / 0.1
        elif pct > 0.85:
            a *= (1.0 - pct) / 0.15
        theta = sampleNumber * theta_per_sample
        # sample = math.sin(theta * freq)
        sample = 0.7 * math.sin(theta * freq) + 0.3 * math.sin(theta * freq * 3)
        audio_event.append_sample(128 + 127.0 * a * sample)
        sampleNumber += 1
    return audio_event

def make_noise (duration, amp=1.0):
    audio_event = AudioBuffer_8bit()
    totalSamples = int(duration * g_sample_rate) - 2
    theta_per_sample = 2 * math.pi / g_sample_rate
    audio_event.append_sample(127)
    sampleNumber = 0
    while sampleNumber < totalSamples:
        audio_event.append_sample(127 + (amp * (random.randint(0, 254) - 127)))
        sampleNumber += 1
    audio_event.append_sample(127)
    return audio_event

def midi_to_freq (midi_note):
    return math.pow(2.0, ((float(midi_note) - 69.0) / 12.0)) * 440.0

def create_sample_file (filename):
    MIDI_C1 = 24
    MIDI_A1 = 33
    n = MIDI_C1
    f = midi_to_freq(n)
    audio_buffer = make_tone(0.2, f)
    if g_verbose:
        print(f"Tone @ {f:.1f} Hz")
    for _ in range(8):
        n += 12
        f = midi_to_freq(n)
        audio_buffer.append(make_tone(0.2, f))
        if g_verbose:
            print(f"Tone @ {f:.1f} Hz")
    n = MIDI_A1
    for octave in range(8):
        a = 0.2
        f1 = midi_to_freq(n)
        f2 = midi_to_freq(n+7)
        if g_verbose:
            print(f"Warble @ {f1:.1f} Hz - {f2:.1f} Hz")
        for _ in range(4):
            audio_buffer.append(make_tone(0.1, f1, a))
            audio_buffer.append(make_tone(0.1, f2, a))
            a = a * 0.5
        n += 12
    audio_buffer.append(make_noise(0.1, 0))
    audio_buffer.append(make_noise(1.0, 0.1))
    audio_buffer.append(make_noise(0.1, 0))
    if g_verbose:
        print(f"White noise, amp = 10%")
    audio_buffer.save(filename)
    if g_verbose:
        print(f"Saved to '{filename}'")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create an example 8-bit PCM audio file')
    parser.add_argument('samplerate', type=int, help='PCM sample rate')
    parser.add_argument('filename', type=str, help='name of wave file to create')
    parser.add_argument('-v', '--verbose', action="store_true", help='display extra runtime info')
    args = parser.parse_args()
    g_verbose = args.verbose
    g_sample_rate = args.samplerate

    create_sample_file(args.filename)

    winsound.PlaySound(args.filename, winsound.SND_FILENAME)

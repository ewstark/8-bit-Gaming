import math
import struct
import wave
import winsound
import random

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
    def save(self, _filename):
        raw_samples = []
        for s in self.samples:
            raw_samples.append(struct.pack('B', s))
        with wave.open("out.wav", "w") as wr:
            wr.setnchannels(1)  # mono = 1 channel
            wr.setsampwidth(1)  # 1-byte = 8-bits per sample
            wr.setframerate(g_sample_rate)
            wr.writeframes(b''.join(raw_samples))

def make_tone (duration, freq, amp=1.0):
    if g_verbose:
        print(f"Tone: {duration} {freq} {amp}")
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
        sample = math.sin(theta * freq)
        audio_event.append_sample(128 + 127.0 * a * sample)
        sampleNumber += 1
    return audio_event

def make_chord (duration, freqs, amps):
    if g_verbose:
        print(f"Chord: {duration} {freqs} {amps}")
    assert len(freqs) == len(amps)
    audio_event = AudioBuffer_8bit()
    totalSamples = int(duration * g_sample_rate)
    theta_per_sample = 2 * math.pi / g_sample_rate
    samples = []
    for n in range(len(freqs)):
        sampleNumber = 0
        while sampleNumber < totalSamples:
            pct = sampleNumber / totalSamples
            # amplitude envelope
            a = amps[n]
            if pct < 0.1:
                a *= (pct / 0.1)
            elif pct > 0.85:
                a *= ((1.0 - pct) / 0.15)
            # frequency content
            theta = sampleNumber * theta_per_sample
            sample = math.sin(theta * freqs[n])
            # append
            audio_event.append_sample(128 + 127.0 * a * sample)
            sampleNumber += 1
    return audio_event

def make_noise (duration, amp=1.0):
    if g_verbose:
        print(f"Noise: {duration} {amp}")
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

MIDI_C1 = 24
MIDI_A1 = 33

n = MIDI_C1
ev = make_tone(0.2, midi_to_freq(n))
for _ in range(7):
    n += 12
    ev.append(make_tone(0.2, midi_to_freq(n)))

n = MIDI_A1
for octave in range(8):
    a = 0.5
    for _ in range(4):
        ev.append(make_tone(0.08, midi_to_freq(n), a))
        ev.append(make_tone(0.08, midi_to_freq(n+7), a))
        a = a * 0.5
    n += 12

ev.append(make_noise(0.2, 0))
ev.append(make_noise(0.1, 0.1))
ev.append(make_noise(0.2, 0))
ev.append(make_noise(0.1, 1.0))
ev.append(make_noise(0.2, 0))
ev.append(make_noise(1.0, 0.2))
ev.append(make_noise(1.0, 0.05))
ev.append(make_noise(1.0, 0.005))

ev.save("out.wav")

winsound.PlaySound("out.wav", winsound.SND_FILENAME)

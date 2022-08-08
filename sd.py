import sounddevice as sd
import numpy as np
import sys
import sdl2
import sdl2.ext
import wavefile

outs = []

WIN_X = 800
WIN_Y = 600
FREQ_TOP = 440 * 4
FREQ_BOTTOM = 220

SAMPLE_RATE = 44100

CRUNCH_BASE = 0.5
CRUNCHINESS = {
    sdl2.SDLK_1: CRUNCH_BASE,
    sdl2.SDLK_2: CRUNCH_BASE / 10.,
    sdl2.SDLK_3: CRUNCH_BASE / 100.,
    sdl2.SDLK_4: CRUNCH_BASE / 500.,
    sdl2.SDLK_5: CRUNCH_BASE / 100000.,
}

WAVETABLE_SIZE = 1024
wavetable = np.sin(np.linspace(0, 2 * np.pi, WAVETABLE_SIZE))

current_freq = 440.
current_amplitude = 1.
current_crunch = CRUNCH_BASE / 100000.

def run():
    global current_freq, current_amplitude, current_crunch

    sdl2.ext.init()
    window = sdl2.ext.Window("The Pong Game", size=(WIN_X, WIN_Y))
    window.show()
    running = True
    while running:
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_MOUSEMOTION:
                x = event.motion.x
                y = event.motion.y
                current_freq = FREQ_BOTTOM + (y / WIN_Y) * (FREQ_TOP - FREQ_BOTTOM)
                current_amplitude = x / WIN_X
            elif event.type == sdl2.SDL_KEYDOWN:
                key = event.key.keysym.sym

                print(key)
                if CRUNCHINESS.get(key):
                    print('crunch', CRUNCHINESS[key])
                    current_crunch = CRUNCHINESS[key]
            elif event.type == sdl2.SDL_QUIT:
                print('quit')
                running = False
                break
        window.refresh()
    return 0


def callback(outdata, frames, time, status):
    t = time.outputBufferDacTime
    step_size = current_freq * WAVETABLE_SIZE
    dt = 1. / SAMPLE_RATE

    amplitude = (np.exp(current_amplitude) - 1) / np.e

    for i in range(len(outdata)):
        outval = wavetable[int(step_size * (t + dt * i)) % WAVETABLE_SIZE]
        outval = amplitude * int(outval / current_crunch) * current_crunch
        outdata[i] = outval

    outs.append(np.copy(outdata))

    if status:
        print('status', status)
    # outdata[:] = indata


try:
    with sd.OutputStream(device=sd.default.device,
                   samplerate=SAMPLE_RATE, blocksize=2048,
                   dtype=np.float32, latency='low',
                   channels=1, callback=callback):
        run()
    with wavefile.WaveWriter('out.wav', channels=1, samplerate=SAMPLE_RATE, format=wavefile.Format.WAV | wavefile.Format.FLOAT) as wav:
        all_ = np.reshape(np.vstack(outs), (1, -1))
        wav.write(all_)

except KeyboardInterrupt:
    sys.exit(0)
except Exception as e:
    raise e

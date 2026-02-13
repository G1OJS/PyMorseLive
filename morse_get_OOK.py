MAX_WPM = 35
MIN_WPM = 12
DOT_TOL_FACTS = (0.8, 1.2)
DASH_TOL_FACTS = (0.8, 1.6)
CHARSEP_THRESHOLD = 0.7
WORDSEP_THRESHOLD = 0.7
        
class TimingDecoder:

    def __init__(self, ax, spec):
        import threading
        self.ax = ax
        self.spec = spec
        self.key_is_down = False
        self.n_fbins = spec['pgrid'].shape[0]
        self.fbin = 0
        self.check_speed(1.2/16)
        self.ticker = False
        self.set_fbin(10)
        self.symbols = ""
        threading.Thread(target = self.get_symbols).start()
        threading.Thread(target = self.decoder).start()

    def set_fbin(self, fbin):
        if(fbin == self.fbin):
            return
        if(self.ticker):
            self.ticker.set_text(" " * 20)
        self.fbin = fbin
        self.ticker = self.ax.text(0, (0.5 + self.fbin) / self.n_fbins,'')
        self.ticker_text = []

    def check_element(self, dur):
        import numpy as np
        se = self.speed_elements
        if DOT_TOL_FACTS[0]*se['dot'] < dur < DOT_TOL_FACTS[1]*se['dot']:
            return '.'
        if DASH_TOL_FACTS[0]*se['dash'] < dur < DASH_TOL_FACTS[1]*se['dash']:
            return '-'
        return ''

    def check_speed(self, dd):
        if(dd < 1.2/MAX_WPM or dd > 3*1.2/MIN_WPM):
            return
        if(dd < 1.2/MIN_WPM):
            self.wpm = 1.2/dd
        else:
            self.wpm = 3*1.2/dd
        if(self.wpm > MAX_WPM): self.wpm = MAX_WPM
        if(self.wpm < MIN_WPM): self.wpm = MIN_WPM
        tu = 1.2/self.wpm
        self.speed_elements = {'dot':1*tu, 'dash':3*tu, 'charsep':3*tu, 'wordsep':7*tu}
            
    def get_symbols(self):
        import time
        t_key_down = False
        self.t_key_up = time.time()
        s = ""
        
        while(True):
            time.sleep(0.002)

            # hysteresis
            level = self.spec['pgrid'][self.fbin, self.spec['idx']]
            if not self.key_is_down and level > 0.6:
                self.key_is_down = True
            elif self.key_is_down and level < 0.3:
                self.key_is_down = False

            # key_down to key_up transition
            if t_key_down and not self.key_is_down:
                self.t_key_up = time.time()
                down_duration = self.t_key_up - t_key_down
                t_key_down = False
                self.check_speed(down_duration)
                s = s + self.check_element(down_duration)

            # watch key_up duration for inter-character and inter-word gaps
            if self.t_key_up:
                key_up_dur = time.time() - self.t_key_up
                if key_up_dur > CHARSEP_THRESHOLD * self.speed_elements['charsep']:
                    if(len(s)):
                        self.symbols = s
                        s = ""
                if key_up_dur > WORDSEP_THRESHOLD * self.speed_elements['wordsep']:
                    if(len(self.ticker_text)):
                        if(self.ticker_text[-1] != " "):
                            self.ticker_text.append(" ")

            # key_up to key_down transition
            if(self.t_key_up and self.key_is_down):
                t_key_down = time.time()
                self.t_key_up = False

    def decoder(self):
        import time
        
        MORSE = {
        ".-": "A",    "-...": "B",  "-.-.": "C",  "-..": "D",
        ".": "E",     "..-.": "F",  "--.": "G",   "....": "H",
        "..": "I",    ".---": "J",  "-.-": "K",   ".-..": "L",
        "--": "M",    "-.": "N",    "---": "O",   ".--.": "P",
        "--.-": "Q",  ".-.": "R",   "...": "S",   "-": "T",
        "..-": "U",   "...-": "V",  ".--": "W",   "-..-": "X",
        "-.--": "Y",  "--..": "Z",

        "-----": "0", ".----": "1", "..---": "2", "...--": "3",
        "....-": "4", ".....": "5", "-....": "6", "--...": "7",
        "---..": "8", "----.": "9"
        }

        while(True):
            time.sleep(0.2)
            
            # decode and print single character
            if len(self.symbols):
                ch = MORSE.get(self.symbols, "_")
                self.symbols = ""
                prevchars = ''.join(self.ticker_text).replace(' ','')[-2:]
                skip = False
                skip = skip or (prevchars == "EE" and ch == "E" or ch == "T")
                skip = skip or (prevchars == "TT" and ch == "T")
                if(not skip):
                    self.ticker_text.append(ch)
                    self.ticker_text = self.ticker_text[-20:]
                    self.ticker.set_text(f"{self.wpm:4.1f} {''.join(self.ticker_text)}")
            
def run():
    import matplotlib.pyplot as plt
    from audio import Audio_in
    import time
    import numpy as np
        
    fig, axs = plt.subplots(1,2, figsize = (8,8))
    audio = Audio_in(dur = 2, df = 50, dt = 0.01, fRng = [300, 900])
    spec = audio.specbuff
    spec_plot = axs[0].imshow(spec['pgrid'], origin = 'lower', aspect='auto', interpolation = 'none')
    axs[0].set_xticks([])
    axs[0].set_yticks([])
    axs[1].set_axis_off()

    decoders = []
    for i in range(spec['pgrid'].shape[0]):
        d = TimingDecoder(axs[1], spec)
        d.set_fbin(i)
        decoders.append(d)

    while True:
        time.sleep(0.01)
        idx = spec['idx']
        wf = spec['pgrid']
        display = np.hstack((wf[:, idx:], wf[:, :idx]))
        spec_plot.set_data(display)
        spec_plot.autoscale()
        plt.pause(0.03)

run()

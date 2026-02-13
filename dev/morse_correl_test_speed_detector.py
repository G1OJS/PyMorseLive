MAX_WPM = 40
MIN_WPM = 12
 
class CorrelDecoder:

    def __init__(self, ax, spec):
        import threading
        self.ax = ax
        self.spec = spec
        self.n_fbins = spec['pgrid'].shape[0]
        self.fbin = 0
        self.symbols = ""
        self.ticker = False
        self.set_fbin(0)
        self.gen_patterns()
        #threading.Thread(target = self.correl).start()
        #threading.Thread(target = self.decoder).start()

    def set_fbin(self, fbin):
        if(fbin == self.fbin):
            return
        if(self.ticker):
            self.ticker.set_text(" " * 20)
        self.fbin = fbin
        self.ticker = self.ax.text(0, (0.5 + self.fbin) / self.n_fbins,'')
        self.ticker_text = []

    def gen_patterns(self):
        import numpy as np
        dt = self.spec['dt']
        bpd0, bpdn = int(0.5+(1.2/MAX_WPM)/dt), int(0.5+(1.2/MIN_WPM)/dt)
        bitsperdit_rng = range(bpd0, bpdn)
        speeds = []
        self.patterns = np.zeros((len(bitsperdit_rng), 5*bpdn))
        for i, bpd in enumerate(bitsperdit_rng):
            pat = [(1/(i+1))*b for b in [1,-1,1,1,1] for i in range(bpd)]
            self.patterns[i,-len(pat):] = pat



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
                self.ticker_text.append(ch)
                self.ticker_text = self.ticker_text[-20:]
                self.ticker.set_text(f"{self.wpm:4.1f} {''.join(self.ticker_text)}")


def test():
    import matplotlib.pyplot as plt
    from audio import Audio_in
    import time
    import numpy as np
    fig, axs = plt.subplots(1,2, figsize = (8,8))
    audio = Audio_in(dur = 2, df = 50, dt = 0.005, fRng = [450, 530])
    spec = audio.specbuff
    d = CorrelDecoder(axs[1], spec)

    fig, ax = plt.subplots(figsize = (8,8))
    plt.ion()
    cplot = None
    correl = np.zeros((d.patterns.shape[0]))
    while True:
        time.sleep(0.05)
        idx = d.spec['idx']
        p = d.spec['pgrid']
        p = p/np.max(p)
        p = 2*p -1
        pgrid_cont = np.hstack((p[d.fbin, idx:], p[d.fbin, :idx]))
        correl = np.dot(d.patterns, pgrid_cont[-d.patterns.shape[1]:, None]).flatten()
        if cplot is None:
            cplot = ax.plot(correl)
            ax.set_ylim(-20,20)
        else:
            cplot[0].set_ydata(correl)
        plt.pause(0.05)
    
            
def run():
    import matplotlib.pyplot as plt
    from audio import Audio_in
    import time
    import numpy as np
        
    fig, axs = plt.subplots(1,2, figsize = (8,8))
    audio = Audio_in(dur = 2, df = 50, dt = 0.01, fRng = [450, 530])
    spec = audio.specbuff
    spec_plot = axs[0].imshow(spec['pgrid'], origin = 'lower', aspect='auto', interpolation = 'none')
    axs[0].set_xticks([])
    axs[0].set_yticks([])
    axs[1].set_axis_off()

    decoders = []
    for i in range(spec['pgrid'].shape[0]):
        d = CorrelDecoder(axs[1], spec)
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

#run()
test()

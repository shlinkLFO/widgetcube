import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import QTimer
import sounddevice as sd
from scipy.fft import fft

class AudioVisualizer(QWidget):
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.setGeometry(100, 100, 800, 200)
        self.setWindowTitle('Audio Spectrum Analyzer')
        
        # Audio setup
        self.sample_rate = 44100
        self.block_size = 2048
        self.audio_data = np.zeros(self.block_size)
        self.spectrum_data = np.zeros(self.block_size // 2)
        
        # Get default output device
        device_info = sd.query_devices()
        wasapi_devices = [idx for idx, device in enumerate(device_info) 
                         if 'WASAPI' in device['name'] and device['max_output_channels'] > 0]
        
        if not wasapi_devices:
            print("No WASAPI output devices found. Falling back to default input.")
            self.stream = sd.InputStream(
                channels=1,
                samplerate=self.sample_rate,
                blocksize=self.block_size,
                callback=self.audio_callback
            )
        else:
            device_id = wasapi_devices[0]
            device_info = sd.query_devices(device_id)
            channels = min(2, device_info['max_output_channels'])
            
            self.stream = sd.InputStream(
                device=device_id,
                channels=channels,
                samplerate=self.sample_rate,
                blocksize=self.block_size,
                callback=self.audio_callback,
                latency='low',
                dtype=np.float32,
                extra_settings={'wasapi_loopback': True}  # Enable WASAPI loopback
            )
        
        self.stream.start()
        
        # Update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(30)  # 30ms refresh rate
        
    def audio_callback(self, indata, frames, time, status):
        if status:
            print(status)
        # Get audio data and convert stereo to mono by averaging channels
        audio = np.mean(indata, axis=1)
        windowed = audio * np.hanning(len(audio))
        # Compute FFT and get magnitude spectrum
        spectrum = np.abs(fft(windowed))[:len(windowed)//2]
        # Convert to dB scale with some offset to avoid log(0)
        self.spectrum_data = 20 * np.log10(spectrum + 1e-10)
        
    def paintEvent(self, event):
        from PyQt5.QtGui import QPainter, QPen, QColor
        from PyQt5.QtCore import Qt
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Background
        painter.fillRect(self.rect(), Qt.black)
        
        width = self.width()
        height = self.height()
        
        # Draw frequency bands
        pen = QPen(Qt.green, 2)
        painter.setPen(pen)
        
        # Use logarithmic scaling for frequency bins
        num_bins = len(self.spectrum_data)
        max_db = np.max(self.spectrum_data)
        min_db = max_db - 60  # 60dB dynamic range
        
        for i in range(width):
            # Map x position to frequency bin using log scale
            freq_bin = int(np.exp(np.log(num_bins) * i / width))
            if freq_bin >= num_bins:
                freq_bin = num_bins - 1
                
            # Get magnitude at this frequency
            magnitude = self.spectrum_data[freq_bin]
            # Normalize magnitude to 0-1 range
            magnitude = (magnitude - min_db) / (max_db - min_db)
            magnitude = np.clip(magnitude, 0, 1)
            
            # Calculate bar height
            bar_height = int(magnitude * height)
            
            # Draw vertical bar
            color = QColor(
                int(255 * (1 - magnitude)),  # Red
                int(255 * magnitude),        # Green
                0                           # Blue
            )
            painter.setPen(QPen(color, 2))
            painter.drawLine(i, height, i, height - bar_height)
    
    def closeEvent(self, event):
        self.stream.stop()
        self.stream.close()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    viz = AudioVisualizer()
    viz.show()
    sys.exit(app.exec_())

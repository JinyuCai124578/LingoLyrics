import queue
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any, List, Optional

from record_system_audio import choose_speaker, load_audio_modules, speaker_loopback_microphone, write_wav


class SystemAudioRecorderApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("System Audio Recorder")
        self.root.geometry("560x320")
        self.root.minsize(520, 300)

        self.np: Any = None
        self.sc: Any = None
        self.speakers: List[Any] = []
        self.recording_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.ui_queue: "queue.Queue[tuple[str, Any]]" = queue.Queue()
        self.chunks: List[Any] = []
        self.started_at: Optional[float] = None

        default_output = Path.cwd() / "system_audio.wav"
        self.output_path = tk.StringVar(value=str(default_output))
        self.device_label = tk.StringVar()
        self.status_text = tk.StringVar(value="Ready")
        self.elapsed_text = tk.StringVar(value="00:00.0")
        self.level_value = tk.DoubleVar(value=0)

        self._build_ui()
        self._load_devices()
        self._poll_queue()

    def _build_ui(self) -> None:
        outer = ttk.Frame(self.root, padding=16)
        outer.pack(fill=tk.BOTH, expand=True)
        outer.columnconfigure(1, weight=1)

        ttk.Label(outer, text="Output device").grid(row=0, column=0, sticky="w", pady=(0, 8))
        self.device_combo = ttk.Combobox(
            outer,
            textvariable=self.device_label,
            state="readonly",
            values=[],
        )
        self.device_combo.grid(row=0, column=1, sticky="ew", padx=(12, 8), pady=(0, 8))
        ttk.Button(outer, text="Refresh", command=self._load_devices).grid(
            row=0, column=2, sticky="ew", pady=(0, 8)
        )

        ttk.Label(outer, text="Save as").grid(row=1, column=0, sticky="w", pady=(0, 8))
        self.output_entry = ttk.Entry(outer, textvariable=self.output_path)
        self.output_entry.grid(row=1, column=1, sticky="ew", padx=(12, 8), pady=(0, 8))
        self.choose_button = ttk.Button(outer, text="Browse", command=self._choose_output)
        self.choose_button.grid(row=1, column=2, sticky="ew", pady=(0, 8))

        controls = ttk.Frame(outer)
        controls.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(8, 12))
        controls.columnconfigure(0, weight=1)
        controls.columnconfigure(1, weight=1)

        self.start_button = ttk.Button(controls, text="Start recording", command=self._start_recording)
        self.start_button.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.stop_button = ttk.Button(controls, text="Stop and save", command=self._stop_recording, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, sticky="ew", padx=(6, 0))

        meter_frame = ttk.LabelFrame(outer, text="Input level")
        meter_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(4, 12))
        meter_frame.columnconfigure(0, weight=1)
        self.level_bar = ttk.Progressbar(
            meter_frame,
            variable=self.level_value,
            maximum=100,
            mode="determinate",
        )
        self.level_bar.grid(row=0, column=0, sticky="ew", padx=12, pady=12)

        info = ttk.Frame(outer)
        info.grid(row=4, column=0, columnspan=3, sticky="ew")
        info.columnconfigure(1, weight=1)
        ttk.Label(info, text="Elapsed").grid(row=0, column=0, sticky="w")
        ttk.Label(info, textvariable=self.elapsed_text).grid(row=0, column=1, sticky="w", padx=(12, 0))
        ttk.Label(info, textvariable=self.status_text).grid(row=1, column=0, columnspan=2, sticky="w", pady=(8, 0))

    def _load_devices(self) -> None:
        try:
            self.np, self.sc = load_audio_modules()
            self.speakers = self.sc.all_speakers()
        except SystemExit:
            messagebox.showerror(
                "Missing dependency",
                "Please install dependencies first:\n\npython -m pip install soundcard numpy",
            )
            self.status_text.set("Missing dependency: soundcard or numpy")
            return
        except Exception as exc:
            messagebox.showerror("Device error", str(exc))
            self.status_text.set("Could not load output devices")
            return

        labels = [f"{index}: {speaker.name}" for index, speaker in enumerate(self.speakers)]
        self.device_combo["values"] = labels

        if not labels:
            self.device_label.set("")
            self.status_text.set("No output devices found")
            return

        default_name = self.sc.default_speaker().name
        default_index = 0
        for index, speaker in enumerate(self.speakers):
            if speaker.name == default_name:
                default_index = index
                break

        self.device_combo.current(default_index)
        self.status_text.set("Ready")

    def _choose_output(self) -> None:
        selected = filedialog.asksaveasfilename(
            title="Save recording as",
            defaultextension=".wav",
            filetypes=[("WAV audio", "*.wav"), ("All files", "*.*")],
            initialfile=Path(self.output_path.get()).name,
        )
        if selected:
            self.output_path.set(selected)

    def _selected_device_index(self) -> Optional[int]:
        label = self.device_label.get()
        if not label:
            return None
        try:
            return int(label.split(":", 1)[0])
        except ValueError:
            return None

    def _start_recording(self) -> None:
        if self.recording_thread and self.recording_thread.is_alive():
            return

        output = Path(self.output_path.get()).expanduser()
        if not output.name:
            messagebox.showwarning("Output path", "Please choose an output file.")
            return

        if self.sc is None or not self.speakers:
            self._load_devices()
            if self.sc is None or not self.speakers:
                return

        self.chunks = []
        self.stop_event.clear()
        self.started_at = time.monotonic()
        self.level_value.set(0)
        self.status_text.set("Recording...")
        self.start_button.configure(state=tk.DISABLED)
        self.stop_button.configure(state=tk.NORMAL)
        self.choose_button.configure(state=tk.DISABLED)
        self.device_combo.configure(state=tk.DISABLED)

        self.recording_thread = threading.Thread(
            target=self._record_worker,
            args=(self._selected_device_index(), output),
            daemon=True,
        )
        self.recording_thread.start()

    def _stop_recording(self) -> None:
        if not self.recording_thread:
            return
        self.status_text.set("Stopping and saving...")
        self.stop_button.configure(state=tk.DISABLED)
        self.stop_event.set()

    def _record_worker(self, device_index: Optional[int], output: Path) -> None:
        samplerate = 48000
        chunk_frames = int(samplerate * 0.08)

        try:
            speaker = choose_speaker(self.sc, device_index)
            microphone = speaker_loopback_microphone(self.sc, speaker)

            with microphone.recorder(samplerate=samplerate) as recorder:
                while not self.stop_event.is_set():
                    audio = recorder.record(numframes=chunk_frames)
                    self.chunks.append(audio)
                    level = self._audio_level(audio)
                    elapsed = time.monotonic() - (self.started_at or time.monotonic())
                    self.ui_queue.put(("level", level))
                    self.ui_queue.put(("elapsed", elapsed))

            write_wav(self.np, output, self.chunks, samplerate)
            self.ui_queue.put(("saved", output.resolve()))
        except Exception as exc:
            self.ui_queue.put(("error", str(exc)))

    def _audio_level(self, audio: Any) -> float:
        if audio.size == 0:
            return 0.0
        rms = float(self.np.sqrt(self.np.mean(self.np.square(audio))))
        return min(100.0, rms * 320.0)

    def _poll_queue(self) -> None:
        try:
            while True:
                event, value = self.ui_queue.get_nowait()
                if event == "level":
                    self.level_value.set(value)
                elif event == "elapsed":
                    self.elapsed_text.set(self._format_elapsed(value))
                elif event == "saved":
                    self._finish_recording_ui(f"Saved: {value}")
                    messagebox.showinfo("Recording saved", f"Saved:\n{value}")
                elif event == "error":
                    self._finish_recording_ui("Recording failed")
                    messagebox.showerror("Recording failed", value)
        except queue.Empty:
            pass

        if self.recording_thread and not self.recording_thread.is_alive():
            self.recording_thread = None

        self.root.after(50, self._poll_queue)

    def _finish_recording_ui(self, status: str) -> None:
        self.status_text.set(status)
        self.start_button.configure(state=tk.NORMAL)
        self.stop_button.configure(state=tk.DISABLED)
        self.choose_button.configure(state=tk.NORMAL)
        self.device_combo.configure(state="readonly")
        self.level_value.set(0)

    @staticmethod
    def _format_elapsed(seconds: float) -> str:
        minutes = int(seconds // 60)
        remainder = seconds - minutes * 60
        return f"{minutes:02d}:{remainder:04.1f}"


def main() -> None:
    root = tk.Tk()
    app = SystemAudioRecorderApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: on_close(root, app))
    root.mainloop()


def on_close(root: tk.Tk, app: SystemAudioRecorderApp) -> None:
    if app.recording_thread and app.recording_thread.is_alive():
        if not messagebox.askyesno("Recording", "Stop recording and close?"):
            return
        app.stop_event.set()
        app.recording_thread.join(timeout=3)
    root.destroy()


if __name__ == "__main__":
    main()

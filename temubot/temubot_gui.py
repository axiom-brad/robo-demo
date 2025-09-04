#!/usr/bin/env python3
"""
This program creates a graphical user interface (GUI) in Python for a Linux environment.
It features three interactive sliders and buttons for serial communication.

Requirements:
- Python 3
- Tkinter (usually included with Python 3)
- pyserial library (install with 'sudo apt install python3-serial')
"""


import threading
import time
import tkinter as tk
from tkinter import messagebox

import serial


class SerialApp:
    """A GUI application for controlling and monitoring a serial device."""

    def __init__(self, root):
        self.root = root
        self.root.title("Motor Control & Serial Monitor")
        self.root.geometry("800x800")
        self.root.configure(bg="#2c3e50")

        # Serial Port Configuration
        self.serial_port = "/dev/ttyACM0"
        self.baud_rate = 9600
        self.ser = None
        self.stop_event = threading.Event()
        self.command_in_progress = False
        self.after_id = None

        self.setup_gui()
        self.setup_serial()

    def setup_gui(self):
        """Builds the main GUI layout with sliders, buttons, and a serial monitor."""
        main_frame = tk.Frame(self.root, bg="#34495e", padx=20, pady=20)
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        title_label = tk.Label(
            main_frame,
            text="Motor Angle Controller",
            font=("Helvetica", 24, "bold"),
            fg="#ecf0f1",
            bg="#34495e",
        )
        title_label.pack(pady=10)

        # Sliders for Motor Angles
        slider_frame = tk.Frame(main_frame, bg="#34495e")
        slider_frame.pack(pady=5)
        self.sliders = []
        for i in range(1, 4):
            label = tk.Label(
                slider_frame,
                text=f"Motor {i} Angle",
                font=("Helvetica", 14),
                fg="#ecf0f1",
                bg="#34495e",
            )
            label.pack(pady=2)
            slider = tk.Scale(
                slider_frame,
                from_=-720,
                to=720,
                orient=tk.HORIZONTAL,
                length=600,
                bg="#7f8c8d",
                fg="#2c3e50",
                troughcolor="#bdc3c7",
                font=("Helvetica", 12),
                highlightthickness=0,
                borderwidth=0,
                resolution=0.01,
            )
            slider.set(0.0)  # Set initial value to 0.0
            slider.pack(pady=5)
            self.sliders.append(slider)

        # Button Section
        button_frame = tk.Frame(main_frame, bg="#34495e")
        button_frame.pack(pady=10)

        # Ping and Reset Buttons Frame
        top_button_frame = tk.Frame(button_frame, bg="#34495e")
        top_button_frame.pack(pady=5, anchor=tk.W)

        # Ping Button
        ping_button = tk.Button(
            top_button_frame,
            text="Ping",
            font=("Helvetica", 14, "bold"),
            bg="#3498db",
            fg="#ecf0f1",
            activebackground="#2980b9",
            width=12,
            command=lambda: self.send_serial_command("ping\n"),
        )
        ping_button.pack(side=tk.LEFT, padx=5)

        # Reset Button
        reset_button = tk.Button(
            top_button_frame,
            text="Reset",
            font=("Helvetica", 14, "bold"),
            bg="#f1c40f",
            fg="#2c3e50",
            activebackground="#f39c12",
            width=12,
            command=self.reset_sliders,
        )
        reset_button.pack(side=tk.LEFT, padx=5)

        # Get Motor Angle Buttons Frame
        get_angle_frame = tk.Frame(button_frame, bg="#34495e")
        get_angle_frame.pack(pady=5, anchor=tk.W)

        get_angle1_button = tk.Button(
            get_angle_frame,
            text="Get Angle 1",
            font=("Helvetica", 14, "bold"),
            bg="#2ecc71",
            fg="#ecf0f1",
            activebackground="#27ae60",
            command=lambda: self.send_serial_command("get angle 1\n"),
        )
        get_angle1_button.pack(side=tk.LEFT, padx=5, pady=5)

        get_angle2_button = tk.Button(
            get_angle_frame,
            text="Get Angle 2",
            font=("Helvetica", 14, "bold"),
            bg="#2ecc71",
            fg="#ecf0f1",
            activebackground="#27ae60",
            command=lambda: self.send_serial_command("get angle 2\n"),
        )
        get_angle2_button.pack(side=tk.LEFT, padx=5, pady=5)

        get_angle3_button = tk.Button(
            get_angle_frame,
            text="Get Angle 3",
            font=("Helvetica", 14, "bold"),
            bg="#2ecc71",
            fg="#ecf0f1",
            activebackground="#27ae60",
            command=lambda: self.send_serial_command("get angle 3\n"),
        )
        get_angle3_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Move Motor Buttons Frame
        move_motor_frame = tk.Frame(button_frame, bg="#34495e")
        move_motor_frame.pack(pady=5, anchor=tk.W)

        move_motor1_button = tk.Button(
            move_motor_frame,
            text="Move Motor 1",
            font=("Helvetica", 14, "bold"),
            bg="#e74c3c",
            fg="#ecf0f1",
            activebackground="#c0392b",
            command=lambda: self.move_motor(1),
        )
        move_motor1_button.pack(side=tk.LEFT, padx=5, pady=5)

        move_motor2_button = tk.Button(
            move_motor_frame,
            text="Move Motor 2",
            font=("Helvetica", 14, "bold"),
            bg="#e74c3c",
            fg="#ecf0f1",
            activebackground="#c0392b",
            command=lambda: self.move_motor(2),
        )
        move_motor2_button.pack(side=tk.LEFT, padx=5, pady=5)

        move_motor3_button = tk.Button(
            move_motor_frame,
            text="Move Motor 3",
            font=("Helvetica", 14, "bold"),
            bg="#e74c3c",
            fg="#ecf0f1",
            activebackground="#c0392b",
            command=lambda: self.move_motor(3),
        )
        move_motor3_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Store all command buttons in a list for easy state management
        self.action_buttons = [
            ping_button,
            reset_button,
            get_angle1_button,
            get_angle2_button,
            get_angle3_button,
            move_motor1_button,
            move_motor2_button,
            move_motor3_button,
        ]

        # Serial Monitor Display
        display_frame = tk.Frame(main_frame, bg="#34495e")
        display_frame.pack(expand=True, fill="both")

        display_label = tk.Label(
            display_frame,
            text="Serial Monitor",
            font=("Helvetica", 14, "bold"),
            fg="#ecf0f1",
            bg="#34495e",
        )
        display_label.pack(pady=(0, 5))

        self.display_text = tk.Text(
            display_frame,
            height=15,
            bg="#2c3e50",
            fg="#ecf0f1",
            font=("Courier New", 12),
            wrap=tk.WORD,
            borderwidth=0,
            highlightthickness=0,
        )
        self.display_text.pack(expand=True, fill="both", padx=10, pady=10)
        self.display_text.insert(tk.END, "Waiting for serial connection...\n")
        self.display_text.config(state=tk.DISABLED)

    def reset_sliders(self):
        """Resets all motor sliders to a value of 0.0."""
        for slider in self.sliders:
            slider.set(0.0)
        self.append_to_display("All sliders have been reset to 0.0.")

    def setup_serial(self):
        """Initializes and opens the serial port, and starts the reader thread."""
        try:
            # The timeout is set to a low value to allow the thread to check the stop event
            self.ser = serial.Serial(self.serial_port, self.baud_rate, timeout=0.1)
            time.sleep(2)  # Give the connection time to establish
            self.append_to_display(
                f"Connected to {self.serial_port} at {self.baud_rate} baud.\n"
            )

            # Start a separate thread to continuously read data
            self.serial_reader_thread = threading.Thread(
                target=self.serial_reader, daemon=True
            )
            self.serial_reader_thread.start()
        except serial.SerialException as e:
            messagebox.showerror(
                "Serial Connection Error",
                f"Failed to connect to {self.serial_port}:\n{e}",
            )
            self.ser = None

    def append_to_display(self, message):
        """Safely appends a message to the text widget from any thread."""
        # Use root.after to pass the message to the main GUI thread
        self.root.after(0, self.insert_text, message)

    def insert_text(self, message):
        """Helper function to insert text into the display widget."""
        self.display_text.config(state=tk.NORMAL)
        self.display_text.insert(tk.END, message + "\n")
        self.display_text.see(tk.END)  # Auto-scroll to the bottom
        self.display_text.config(state=tk.DISABLED)

    def serial_reader(self):
        """A dedicated thread function to continuously read and display serial data."""
        while not self.stop_event.is_set():
            if self.ser and self.ser.is_open:
                try:
                    # Check if there is data available to read
                    if self.ser.in_waiting > 0:
                        line = self.ser.readline().decode("utf-8").strip()
                        if line:
                            self.append_to_display(f"Received: {line}")
                            # If a command was sent, handle the response
                            if self.command_in_progress:
                                self.root.after_idle(self.handle_serial_response)
                    else:
                        # Sleep for a short while to prevent a busy loop
                        time.sleep(0.01)
                except Exception as e:
                    self.append_to_display(f"Communication error: {e}")
                    self.stop_event.set()

    def send_serial_command(self, command):
        """Sends a command to the serial port in a thread to keep the GUI responsive."""
        if not self.command_in_progress:
            self.command_in_progress = True
            self.set_button_state(tk.DISABLED)
            # Set a 30-second timeout to re-enable buttons
            self.after_id = self.root.after(30000, self.handle_timeout)

            if self.ser and self.ser.is_open:
                threading.Thread(
                    target=self.send_command, args=(command,), daemon=True
                ).start()
            else:
                messagebox.showerror("Error", "Serial port is not connected.")
                self.handle_timeout()  # Re-enable buttons immediately if no connection

    def set_button_state(self, state):
        """Sets the state of all command-related buttons."""
        for button in self.action_buttons:
            button.config(state=state)

    def handle_timeout(self):
        """Called if a response is not received within the timeout period."""
        if self.command_in_progress:
            self.command_in_progress = False
            self.set_button_state(tk.NORMAL)
            self.append_to_display("Timeout occurred: No response received.")

    def send_command(self, command):
        """Sends a command and display it in the monitor."""
        try:
            self.append_to_display(f"Sending: {command.strip()}")
            self.ser.write(command.encode("utf-8"))
        except Exception as e:
            self.append_to_display(f"Communication error: {e}")
            self.root.after_idle(
                self.handle_timeout
            )  # Use after_idle to call on main thread

    def handle_serial_response(self):
        """Called when a serial response is received to re-enable buttons and cancel timeout."""
        if self.command_in_progress:
            if self.after_id:
                self.root.after_cancel(self.after_id)
                self.after_id = None
            self.command_in_progress = False
            self.set_button_state(tk.NORMAL)

    def move_motor(self, motor_number):
        """Gets the slider value for the specified motor and sends a move command."""
        # Get the floating point value of the corresponding slider
        angle = self.sliders[motor_number - 1].get()
        # Format the command string
        command = f"move motor {motor_number} absolute {angle}\n"
        # Send the command to the serial port
        self.send_serial_command(command)

    def on_closing(self):
        """Closes the serial port and stops the reader thread when the app is closed."""
        self.stop_event.set()  # Signal the reader thread to stop
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = SerialApp(root)
    # Set a callback for when the window is closed
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

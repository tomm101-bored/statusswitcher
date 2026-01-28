import asyncio
import aiohttp
import tkinter as tk
from tkinter import messagebox
import threading
import time
import random

class StatusCyclerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Status Cycler (User Token Version)")
        self.running = False

        tk.Label(master, text="User Token:").pack()
        self.token_entry = tk.Entry(master, width=60, show="*")
        self.token_entry.pack()

        tk.Label(master, text="Statuses (one per line):").pack()
        self.status_text = tk.Text(master, height=15, width=60)
        self.status_text.pack()

        tk.Label(master, text="Interval (seconds):").pack()
        self.interval_entry = tk.Entry(master, width=10)
        self.interval_entry.insert(0, "15")
        self.interval_entry.pack()

        self.start_button = tk.Button(master, text="Start", command=self.start_cycling)
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(master, text="Stop", command=self.stop_cycling, state=tk.DISABLED)
        self.stop_button.pack()

    def start_cycling(self):
        token = self.token_entry.get().strip()
        statuses = self.status_text.get("1.0", tk.END).strip().split("\n")

        try:
            interval = int(self.interval_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for interval.")
            return

        if not token or not statuses:
            messagebox.showerror("Error", "Please fill in all fields correctly.")
            return

        self.token = token
        self.statuses = statuses
        self.interval = interval
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        threading.Thread(target=lambda: asyncio.run(self.cycle_statuses()), daemon=True).start()

    def stop_cycling(self):
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        messagebox.showinfo("Stopped", "Status cycling stopped.")

    async def cycle_statuses(self):
        headers = {
            "Authorization": self.token,
            "Content-Type": "application/json"
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            index = 0
            while self.running:
                status = self.statuses[index]
                payload = {
                    "custom_status": {"text": status}
                }

                try:
                    async with session.patch("https://discord.com/api/v9/users/@me/settings", json=payload) as resp:
                        if resp.status != 200:
                            print(f"Failed to update status: {resp.status}")
                            messagebox.showerror("Error", f"Failed to update status: HTTP {resp.status}")
                            self.stop_cycling()
                            return
                except Exception as e:
                    print(f"Error: {e}")
                    messagebox.showerror("Error", f"Failed to connect:\n{e}")
                    self.stop_cycling()
                    return

                index = (index + 1) % len(self.statuses)
                await asyncio.sleep(self.interval)

# GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = StatusCyclerApp(root)
    root.mainloop()
from pathlib import Path
import tkinter as tk

class ProgramStatus:
    OUTPUT_PATH = Path(__file__).parent
    ASSETS_PATH = OUTPUT_PATH / Path("./gui/assets/frame0")

    def __init__(self):
        self.destroy = False
        self.status = 'Moving Cursor'

    def initialize_window(self):
        self.window = tk.Tk()

        self.window.geometry("325x76")
        self.window.configure(bg = "#FFFFFF")

        self.canvas = tk.Canvas(
            self.window,
            bg = "#FFFFFF",
            height = 76,
            width = 325,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )

        self.canvas.place(x = 0, y = 0)
        self.canvas.create_rectangle(
            0.0,
            0.0,
            325.0,
            76.0,
            fill="#D9D9D9",
            outline="")

        self.button_image_1 = tk.PhotoImage(
            file=self.relative_to_assets("button_1.png")
        )

        self.button_1 = tk.Button(
            image=self.button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.destroy_window(),
            relief="flat"
        )

        self.button_1.place(
            x=300.0,
            y=10.0,
            width=17.0,
            height=17.0
        )

        self.status_label = self.canvas.create_text(
            10.0,
            32.0,
            anchor="nw",
            text=self.status,
            fill="#000000",
            font=("Inter Bold", 32 * -1)
        )

        self.canvas.create_text(
            10.0,
            10.0,
            anchor="nw",
            text="Program Status",
            fill="#000000",
            font=("Inter", 12 * -1)
        )

        return self.window

    def destroy_window(self):
        self.destroy = True

    def change_status(self, status):
        self.canvas.itemconfigure(self.status_label, text=status)
        self.window.update()

    def relative_to_assets(self, path: str) -> Path:
        return self.ASSETS_PATH / Path(path)
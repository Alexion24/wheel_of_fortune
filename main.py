import time
import tkinter as tk
from PIL import Image, ImageDraw, ImageTk, ImageFont
import math
import random


class WheelOfFortune:
    # Constants
    CANVAS_SIZE = (500, 400)
    WHEEL_POSITION = (250, 200)
    WHEEL_RADIUS = 150
    INDICATOR_POSITION = (420, 220)
    COLORS = [
        "#FF5733",  # Ярко-оранжевый
        "#33FF57",  # Ярко-зеленый
        "#3357FF",  # Ярко-синий
        "#FF33A6",  # Ярко-розовый
        "#A633FF",  # Ярко-фиолетовый
        "#33FFF3",  # Ярко-бирюзовый
        "#FFA633",  # Ярко-коричневый
        "#F3FF33",  # Ярко-желтый
    ]
    SPIN_DURATION = 3000  # ms
    FULL_ROTATIONS = 5

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Колесо Фортуны")

        self.items = ["Пункт 1", "Пункт 2", "Пункт 3", "Пункт 4",
                      "Пункт 5", "Пункт 6", "Пункт 7", "Пункт 8"]
        self.angle = 0
        self.spinning = False
        self.animation_id = None

        self._setup_ui()
        self._create_wheel()
        self._create_indicator()

    def _setup_ui(self) -> None:
        """Initialize GUI components"""
        self.canvas = tk.Canvas(
            self.root,
            width=self.CANVAS_SIZE[0],
            height=self.CANVAS_SIZE[1]
        )
        self.canvas.pack()

        self.result_label = tk.Label(
            self.root,
            text="Нажмите кнопку, чтобы крутить колесо",
            font=("Arial", 16, "bold")
        )
        self.result_label.pack(pady=20)

        self.spin_button = tk.Button(
            self.root,
            text="Крутить колесо",
            command=self.spin_wheel,
            font=("Arial", 14, "bold")
        )
        self.spin_button.pack(pady=10)

    def _create_wheel(self) -> None:
        """Generate wheel image with sectors"""
        size = self.WHEEL_RADIUS * 2
        self.wheel_image = Image.new("RGBA", (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(self.wheel_image)

        num_items = len(self.items)
        angle_per_item = 360 / num_items

        for i, item in enumerate(self.items):
            # Draw sector
            start_angle = i * angle_per_item
            end_angle = (i + 1) * angle_per_item
            draw.pieslice(
                [0, 0, size, size],
                start_angle,
                end_angle,
                fill=self.COLORS[i % len(self.COLORS)],
                outline="black"
            )

            # Draw text
            text_angle = math.radians(start_angle + angle_per_item / 2)
            text_x = self.WHEEL_RADIUS + (self.WHEEL_RADIUS * 0.6) * math.cos(text_angle)
            text_y = self.WHEEL_RADIUS + (self.WHEEL_RADIUS * 0.6) * math.sin(text_angle)
            draw.text(
                (text_x, text_y),
                item,
                fill="black",
                font=self._get_font(),
                anchor="mm"
            )

        self.wheel_photo = ImageTk.PhotoImage(self.wheel_image)
        self.canvas.create_image(*self.WHEEL_POSITION, image=self.wheel_photo)

    def _create_indicator(self) -> None:
        """Create rotation indicator arrow"""
        indicator_size = (50, 50)
        self.indicator_image = Image.new("RGBA", indicator_size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(self.indicator_image)

        # Draw triangle arrow
        points = [
            (10, 25),
            (40, 15),
            (40, 35)
        ]
        draw.polygon(points, fill="red")

        self.indicator_photo = ImageTk.PhotoImage(self.indicator_image)
        self.canvas.create_image(*self.INDICATOR_POSITION, image=self.indicator_photo)

    def _get_font(self):
        """Get preferred font or fallback to default"""
        try:
            return ImageFont.truetype("arial.ttf", 16)
        except IOError:
            try:
                return ImageFont.truetype("DejaVuSans.ttf", 16)
            except IOError:
                return ImageFont.load_default()

    def spin_wheel(self) -> None:
        """Start wheel spinning animation"""
        if self.spinning:
            return

        self.spinning = True
        self.spin_button.config(state=tk.DISABLED)
        self.result_label.config(text="Колесо крутится...")

        # Calculate target rotation
        num_items = len(self.items)
        target_item = random.randint(0, num_items - 1)
        target_angle = (
                self.FULL_ROTATIONS * 360 +
                (target_item * 360 / num_items)
        )

        # Start animation
        self._animate_rotation(
            start_time=time.time(),
            target_angle=target_angle,
            duration=self.SPIN_DURATION
        )

    def _animate_rotation(
            self,
            start_time: float,
            target_angle: float,
            duration: float
    ) -> None:
        """Animate wheel using easing function"""
        progress = (time.time() - start_time) * 1000 / duration

        if progress >= 1:
            self._finalize_spin(target_angle)
            return

        # Cubic easing out
        eased_progress = 1 - math.pow(1 - progress, 3)
        current_angle = eased_progress * target_angle
        self.angle = current_angle % 360

        self._update_wheel()
        self.animation_id = self.root.after(
            16,
            lambda: self._animate_rotation(start_time, target_angle, duration)
        )

    def _finalize_spin(self, target_angle: float) -> None:
        """Finalize spin and show result"""
        self.angle = target_angle % 360
        self._update_wheel()

        num_items = len(self.items)
        angle_per_item = 360 / num_items
        result_index = int((360 - self.angle % 360) // angle_per_item) % num_items
        result = self.items[result_index]

        self.result_label.config(text=f"Результат: {result}")
        self.spin_button.config(state=tk.NORMAL)
        self.spinning = False

    def _update_wheel(self) -> None:
        """Update wheel display"""
        rotated_image = self.wheel_image.rotate(-self.angle, resample=Image.BICUBIC)
        self.wheel_photo = ImageTk.PhotoImage(rotated_image)
        self.canvas.create_image(*self.WHEEL_POSITION, image=self.wheel_photo)


if __name__ == "__main__":
    root = tk.Tk()
    app = WheelOfFortune(root)
    root.mainloop()
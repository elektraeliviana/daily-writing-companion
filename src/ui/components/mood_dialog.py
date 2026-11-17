"""
Mood Selection Modal Dialog.
Presented after saving a journal session to log the writer's emotional state.
"""

from typing import Optional, Callable
import customtkinter as ctk
from config.settings import MOOD_CHOICES


class MoodDialog(ctk.CTkToplevel):
    """Modal dialog prompting the user to choose their mood."""

    def __init__(self, parent, on_select: Callable[[Optional[str]], None]):
        super().__init__(parent)
        self.on_select = on_select
        self.selected_mood: Optional[str] = None

        self.title("How are you feeling?")
        self.geometry("420x360")
        self.resizable(False, False)

        # Center dialog relative to parent
        self.transient(parent)
        self.grab_set()

        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)

        # Title / Header
        title_label = ctk.CTkLabel(
            self,
            text="✨ Great writing session!",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        title_label.pack(pady=(25, 5))

        subtitle_label = ctk.CTkLabel(
            self,
            text="How are you feeling after writing?",
            font=ctk.CTkFont(size=13),
            text_color="gray",
        )
        subtitle_label.pack(pady=(0, 20))

        # Mood Buttons Container
        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=40)

        for mood in MOOD_CHOICES:
            btn = ctk.CTkButton(
                buttons_frame,
                text=mood,
                font=ctk.CTkFont(size=14),
                height=38,
                fg_color="#2b2b36",
                hover_color="#3e3e50",
                command=lambda m=mood: self._choose(m),
            )
            btn.pack(fill="x", pady=4)

        # Skip Button
        skip_btn = ctk.CTkButton(
            self,
            text="Skip for now",
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            text_color="gray",
            hover_color="#22222a",
            command=lambda: self._choose(None),
        )
        skip_btn.pack(pady=(15, 10))

    def _choose(self, mood: Optional[str]):
        self.selected_mood = mood
        self.grab_release()
        self.destroy()
        if self.on_select:
            self.on_select(mood)

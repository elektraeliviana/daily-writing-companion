"""
AI Writing Feedback Modal Dialog.
Displays constructive critique and reflection questions from Gemini AI.
"""

import customtkinter as ctk


class FeedbackDialog(ctk.CTkToplevel):
    """Modal dialog displaying AI writing feedback."""

    def __init__(self, parent, feedback_text: str):
        super().__init__(parent)
        self.title("✨ Gemini AI Writing Mentor")
        self.geometry("560x480")
        self.resizable(True, True)

        self.transient(parent)
        self.grab_set()

        self._build_ui(feedback_text)

    def _build_ui(self, feedback_text: str):
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=25, pady=(20, 10))

        title = ctk.CTkLabel(
            header_frame,
            text="AI Mentor Feedback",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            header_frame,
            text="Personalized reflection, strengths, and creative suggestions.",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        )
        subtitle.pack(anchor="w")

        # Scrollable Textbox with Feedback
        textbox = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(size=13),
            wrap="word",
            corner_radius=8,
        )
        textbox.pack(fill="both", expand=True, padx=25, pady=10)
        textbox.insert("1.0", feedback_text)
        textbox.configure(state="disabled")  # Read-only

        # Close Button
        close_btn = ctk.CTkButton(
            self,
            text="Got it, thanks!",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=38,
            command=self._close,
        )
        close_btn.pack(pady=(10, 20), padx=25, fill="x")

    def _close(self):
        self.grab_release()
        self.destroy()

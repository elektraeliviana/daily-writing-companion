"""
Entry Detail & Edit Modal Dialog.
Enables viewing full entries, modifying text, updating moods, or deleting entries safely.
"""

from typing import Optional, Callable
import customtkinter as ctk
from src.models.entry import Entry
from config.settings import MOOD_CHOICES


class EntryDetailDialog(ctk.CTkToplevel):
    """Modal dialog for viewing, editing, or deleting a specific journal entry."""

    def __init__(
        self,
        parent,
        entry: Entry,
        on_save: Callable[[int, str, Optional[str]], None],
        on_delete: Callable[[int], None],
    ):
        super().__init__(parent)
        self.entry = entry
        self.on_save = on_save
        self.on_delete = on_delete

        self.title(f"Entry: {entry.entry_date} - {entry.category_name.capitalize()}")
        self.geometry("640x580")
        self.minsize(500, 400)

        self.transient(parent)
        self.grab_set()

        self._build_ui()

    def _build_ui(self):
        # Header Info Frame
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 5))

        title_lbl = ctk.CTkLabel(
            header,
            text=f"📅 {self.entry.entry_date}  •  Category: {self.entry.category_name.capitalize()}",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        title_lbl.pack(anchor="w")

        # Prompt Display Card
        if self.entry.prompt_text:
            prompt_frame = ctk.CTkFrame(self, corner_radius=6, fg_color=("#e6e8eb", "#202028"))
            prompt_frame.pack(fill="x", padx=20, pady=8)
            prompt_lbl = ctk.CTkLabel(
                prompt_frame,
                text=f'Prompt: "{self.entry.prompt_text}"',
                font=ctk.CTkFont(size=12, slant="italic"),
                wraplength=580,
                justify="left",
            )
            prompt_lbl.pack(padx=12, pady=8, anchor="w")

        # Text Editor
        self.textbox = ctk.CTkTextbox(self, font=ctk.CTkFont(size=14), wrap="word", corner_radius=8)
        self.textbox.pack(fill="both", expand=True, padx=20, pady=5)
        self.textbox.insert("1.0", self.entry.content)
        self.textbox.bind("<KeyRelease>", self._update_live_stats)

        # Meta & Status Row (Live Word Count + Mood Dropdown)
        meta_row = ctk.CTkFrame(self, fg_color="transparent")
        meta_row.pack(fill="x", padx=20, pady=5)

        self.word_count_lbl = ctk.CTkLabel(
            meta_row,
            text=f"Words: {self.entry.word_count}  •  Duration: {self.entry.duration_seconds}s",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        )
        self.word_count_lbl.pack(side="left")

        # Mood Selector
        mood_options = ["(No Mood)"] + MOOD_CHOICES
        current_mood = self.entry.mood if self.entry.mood in MOOD_CHOICES else "(No Mood)"
        self.mood_var = ctk.StringVar(value=current_mood)

        mood_dropdown = ctk.CTkOptionMenu(
            meta_row,
            values=mood_options,
            variable=self.mood_var,
            width=140,
            height=28,
        )
        mood_dropdown.pack(side="right")

        # Actions Row (Delete, Cancel, Save)
        action_row = ctk.CTkFrame(self, fg_color="transparent")
        action_row.pack(fill="x", padx=20, pady=(10, 15))

        delete_btn = ctk.CTkButton(
            action_row,
            text="Delete Entry",
            fg_color="#8b1e1e",
            hover_color="#b22b2b",
            width=110,
            height=34,
            command=self._confirm_delete,
        )
        delete_btn.pack(side="left")

        save_btn = ctk.CTkButton(
            action_row,
            text="Save Changes",
            fg_color="#2b7a4b",
            hover_color="#36965d",
            width=120,
            height=34,
            command=self._save_changes,
        )
        save_btn.pack(side="right", padx=(10, 0))

        cancel_btn = ctk.CTkButton(
            action_row,
            text="Cancel",
            fg_color="transparent",
            text_color="gray",
            hover_color="#2a2a32",
            width=80,
            height=34,
            command=self._close,
        )
        cancel_btn.pack(side="right")

    def _update_live_stats(self, event=None):
        content = self.textbox.get("1.0", "end-1c").strip()
        words = len(content.split()) if content else 0
        self.word_count_lbl.configure(
            text=f"Words: {words}  •  Duration: {self.entry.duration_seconds}s"
        )

    def _save_changes(self):
        new_content = self.textbox.get("1.0", "end-1c").strip()
        if not new_content:
            return

        selected_mood = self.mood_var.get()
        mood_val = None if selected_mood == "(No Mood)" else selected_mood

        self.on_save(self.entry.id, new_content, mood_val)
        self._close()

    def _confirm_delete(self):
        # Confirmation dialog
        confirm_box = ctk.CTkToplevel(self)
        confirm_box.title("Confirm Delete")
        confirm_box.geometry("340x160")
        confirm_box.resizable(False, False)
        confirm_box.transient(self)
        confirm_box.grab_set()

        lbl = ctk.CTkLabel(
            confirm_box,
            text="Are you sure you want to delete this entry?\nThis action cannot be undone.",
            font=ctk.CTkFont(size=13),
            wraplength=300,
        )
        lbl.pack(pady=(20, 15))

        btn_row = ctk.CTkFrame(confirm_box, fg_color="transparent")
        btn_row.pack(fill="x", padx=30)

        def do_delete():
            confirm_box.grab_release()
            confirm_box.destroy()
            self.on_delete(self.entry.id)
            self._close()

        def cancel_delete():
            confirm_box.grab_release()
            confirm_box.destroy()

        ctk.CTkButton(
            btn_row,
            text="Yes, Delete",
            fg_color="#8b1e1e",
            hover_color="#b22b2b",
            width=110,
            command=do_delete,
        ).pack(side="left")

        ctk.CTkButton(
            btn_row,
            text="Cancel",
            fg_color="gray",
            width=90,
            command=cancel_delete,
        ).pack(side="right")

    def _close(self):
        self.grab_release()
        self.destroy()

"""
History & Search View: Browse, filter, search, view, edit, and delete past entries.
"""

from typing import Optional, Callable, List
import customtkinter as ctk

from src.models.entry import Entry
from src.repositories.entry_repository import EntryRepository
from src.ui.components.entry_dialog import EntryDetailDialog
from config.settings import MOOD_CHOICES


class HistoryView(ctk.CTkFrame):
    """View for searching and inspecting historical entries."""

    def __init__(
        self,
        parent,
        entry_repo: EntryRepository,
        on_data_changed: Optional[Callable[[], None]] = None,
    ):
        super().__init__(parent, fg_color="transparent")
        self.entry_repo = entry_repo
        self.on_data_changed = on_data_changed

        self._build_ui()
        self.refresh_entries()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)  # List expands

        # Title & Summary Row
        header_row = ctk.CTkFrame(self, fg_color="transparent")
        header_row.grid(row=0, column=0, sticky="ew", padx=25, pady=(20, 10))

        title = ctk.CTkLabel(
            header_row,
            text="Journal History & Search",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        title.pack(side="left")

        self.summary_badge = ctk.CTkLabel(
            header_row,
            text="0 entries",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        )
        self.summary_badge.pack(side="right")

        # Filters Row
        filter_bar = ctk.CTkFrame(self, corner_radius=8, fg_color=("#e6e8eb", "#1f1f28"))
        filter_bar.grid(row=1, column=0, sticky="ew", padx=25, pady=5)
        filter_bar.grid_columnconfigure(0, weight=1)

        # Keyword Search Entry
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(
            filter_bar,
            placeholder_text="🔍 Search by keyword...",
            textvariable=self.search_var,
            height=34,
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(12, 8), pady=8)
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_entries())

        # Category Filter Dropdown
        self.category_var = ctk.StringVar(value="All Categories")
        self.category_dropdown = ctk.CTkOptionMenu(
            filter_bar,
            values=["All Categories", "Journal", "Story", "Poem"],
            variable=self.category_var,
            command=lambda v: self.refresh_entries(),
            width=135,
            height=34,
        )
        self.category_dropdown.pack(side="left", padx=4, pady=8)

        # Mood Filter Dropdown
        mood_options = ["All Moods"] + MOOD_CHOICES
        self.mood_var = ctk.StringVar(value="All Moods")
        self.mood_dropdown = ctk.CTkOptionMenu(
            filter_bar,
            values=mood_options,
            variable=self.mood_var,
            command=lambda v: self.refresh_entries(),
            width=135,
            height=34,
        )
        self.mood_dropdown.pack(side="left", padx=(4, 12), pady=8)

        # Scrollable Cards Area
        self.scroll_frame = ctk.CTkScrollableFrame(self, corner_radius=8, fg_color="transparent")
        self.scroll_frame.grid(row=2, column=0, sticky="nsew", padx=25, pady=(10, 20))
        self.scroll_frame.grid_columnconfigure(0, weight=1)

    def refresh_entries(self):
        """Fetches filtered entries and repopulates the card list."""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        # Parse filters
        keyword = self.search_var.get().strip() or None

        cat_choice = self.category_var.get()
        category_name = None if cat_choice == "All Categories" else cat_choice.lower()

        mood_choice = self.mood_var.get()
        mood = None if mood_choice == "All Moods" else mood_choice

        entries = self.entry_repo.search(
            keyword=keyword,
            category_name=category_name,
            mood=mood,
        )

        total_words = sum(e.word_count for e in entries)
        self.summary_badge.configure(text=f"Showing {len(entries)} entries • {total_words} words")

        if not entries:
            empty_lbl = ctk.CTkLabel(
                self.scroll_frame,
                text="No writing entries found matching your criteria.\nTry clearing filters or write a new entry!",
                font=ctk.CTkFont(size=14),
                text_color="gray",
                justify="center",
            )
            empty_lbl.pack(pady=60)
            return

        for entry in entries:
            self._create_entry_card(entry)

    def _create_entry_card(self, entry: Entry):
        card = ctk.CTkFrame(
            self.scroll_frame,
            corner_radius=8,
            fg_color=("#f0f2f5", "#1e1e26"),
            border_width=1,
            border_color=("#d0d4db", "#2e2e3d"),
        )
        card.pack(fill="x", pady=5)
        card.grid_columnconfigure(1, weight=1)

        # Header of Card (Date, Category, Mood, Words)
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(12, 4))

        date_lbl = ctk.CTkLabel(
            header,
            text=f"📅 {entry.entry_date}",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        date_lbl.pack(side="left")

        cat_badge = ctk.CTkLabel(
            header,
            text=f"  {entry.category_name.upper()}  ",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=("#e2e8f0", "#2d3748"),
            corner_radius=4,
        )
        cat_badge.pack(side="left", padx=10)

        if entry.mood:
            mood_lbl = ctk.CTkLabel(
                header,
                text=entry.mood,
                font=ctk.CTkFont(size=12),
            )
            mood_lbl.pack(side="left")

        words_lbl = ctk.CTkLabel(
            header,
            text=f"{entry.word_count} words",
            font=ctk.CTkFont(size=12),
            text_color="#8ea0b5",
        )
        words_lbl.pack(side="right")

        # Prompt Snippet
        if entry.prompt_text:
            prompt_snip = entry.prompt_text[:90] + ("..." if len(entry.prompt_text) > 90 else "")
            p_lbl = ctk.CTkLabel(
                card,
                text=f'Prompt: "{prompt_snip}"',
                font=ctk.CTkFont(size=12, slant="italic"),
                text_color="#94a3b8",
                anchor="w",
            )
            p_lbl.pack(fill="x", padx=15, pady=(0, 4))

        # Content Preview Snippet
        text_preview = entry.content[:160] + ("..." if len(entry.content) > 160 else "")
        c_lbl = ctk.CTkLabel(
            card,
            text=text_preview,
            font=ctk.CTkFont(size=13),
            wraplength=620,
            justify="left",
            anchor="w",
        )
        c_lbl.pack(fill="x", padx=15, pady=(0, 10))

        # Click card to open modal detail
        view_btn = ctk.CTkButton(
            card,
            text="View / Edit Entry",
            font=ctk.CTkFont(size=11),
            width=110,
            height=26,
            fg_color="transparent",
            text_color="#3b82f6",
            hover_color=("#e2e8f0", "#272733"),
            command=lambda e=entry: self._open_entry_modal(e),
        )
        view_btn.pack(anchor="e", padx=15, pady=(0, 10))

    def _open_entry_modal(self, entry: Entry):
        EntryDetailDialog(
            parent=self,
            entry=entry,
            on_save=self._on_entry_updated,
            on_delete=self._on_entry_deleted,
        )

    def _on_entry_updated(self, entry_id: int, new_content: str, new_mood: Optional[str]):
        self.entry_repo.update_entry(entry_id=entry_id, content=new_content, mood=new_mood)
        self.refresh_entries()
        if self.on_data_changed:
            self.on_data_changed()

    def _on_entry_deleted(self, entry_id: int):
        self.entry_repo.delete_by_id(entry_id)
        self.refresh_entries()
        if self.on_data_changed:
            self.on_data_changed()

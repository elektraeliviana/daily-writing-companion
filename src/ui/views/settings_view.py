"""
Settings View: Configure daily word goals, Gemini API credentials, and app appearance.
"""

from pathlib import Path
from typing import Optional, Callable
import customtkinter as ctk

from src.services.goal_service import GoalService
from src.services.ai_service import AIService
from config.settings import BASE_DIR, GEMINI_API_KEY


class SettingsView(ctk.CTkFrame):
    """View for configuring application preferences."""

    def __init__(
        self,
        parent,
        goal_service: GoalService,
        ai_service: AIService,
        on_goal_changed: Optional[Callable[[], None]] = None,
    ):
        super().__init__(parent, fg_color="transparent")
        self.goal_service = goal_service
        self.ai_service = ai_service
        self.on_goal_changed = on_goal_changed

        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header Row
        header_row = ctk.CTkFrame(self, fg_color="transparent")
        header_row.grid(row=0, column=0, sticky="ew", padx=25, pady=(20, 10))

        title = ctk.CTkLabel(
            header_row,
            text="Application Settings",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        title.pack(side="left")

        # Scrollable Settings Container
        container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        container.grid(row=1, column=0, sticky="nsew", padx=25, pady=(5, 20))
        container.grid_columnconfigure(0, weight=1)

        # ----------------------------------------------------
        # 1. Daily Word Count Goal Section
        # ----------------------------------------------------
        goal_section = ctk.CTkFrame(container, corner_radius=10, fg_color=("#e6e8eb", "#1f1f28"))
        goal_section.pack(fill="x", pady=10)
        goal_section.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            goal_section,
            text="🎯 Daily Writing Goal",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", padx=20, pady=(15, 5))

        ctk.CTkLabel(
            goal_section,
            text="Set the number of words you aim to write each day.",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        ).pack(anchor="w", padx=20, pady=(0, 10))

        goal_controls = ctk.CTkFrame(goal_section, fg_color="transparent")
        goal_controls.pack(fill="x", padx=20, pady=(0, 15))

        current_goal = self.goal_service.get_daily_goal()
        self.goal_entry = ctk.CTkEntry(goal_controls, width=120, height=34)
        self.goal_entry.insert(0, str(current_goal))
        self.goal_entry.pack(side="left", padx=(0, 10))

        save_goal_btn = ctk.CTkButton(
            goal_controls,
            text="Update Goal",
            width=110,
            height=34,
            command=self._save_goal,
        )
        save_goal_btn.pack(side="left")

        self.goal_status_lbl = ctk.CTkLabel(goal_controls, text="", font=ctk.CTkFont(size=12))
        self.goal_status_lbl.pack(side="left", padx=15)

        # Quick Select Buttons
        quick_row = ctk.CTkFrame(goal_section, fg_color="transparent")
        quick_row.pack(fill="x", padx=20, pady=(0, 15))

        for target in [50, 100, 200, 500]:
            btn = ctk.CTkButton(
                quick_row,
                text=f"{target} words",
                width=80,
                height=26,
                fg_color=("#d0d4db", "#2e2e3d"),
                hover_color=("#bfc4cc", "#3d3d52"),
                text_color=("#1a1a1a", "#ffffff"),
                font=ctk.CTkFont(size=11),
                command=lambda t=target: self._quick_set_goal(t),
            )
            btn.pack(side="left", padx=(0, 8))

        # ----------------------------------------------------
        # 2. Gemini AI Writing Partner Section
        # ----------------------------------------------------
        ai_section = ctk.CTkFrame(container, corner_radius=10, fg_color=("#e6e8eb", "#1f1f28"))
        ai_section.pack(fill="x", pady=10)

        ctk.CTkLabel(
            ai_section,
            text="✨ Google Gemini AI Configuration",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", padx=20, pady=(15, 5))

        ctk.CTkLabel(
            ai_section,
            text="Powers AI prompt generation and constructive feedback. Saved securely in local .env file.",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        ).pack(anchor="w", padx=20, pady=(0, 10))

        ai_input_row = ctk.CTkFrame(ai_section, fg_color="transparent")
        ai_input_row.pack(fill="x", padx=20, pady=(0, 10))

        self.ai_key_entry = ctk.CTkEntry(
            ai_input_row,
            placeholder_text="Enter Gemini API Key (e.g. AIzaSy...)",
            show="*",
            height=34,
        )
        if self.ai_service.api_key:
            self.ai_key_entry.insert(0, self.ai_service.api_key)
        self.ai_key_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.show_key_var = ctk.BooleanVar(value=False)
        self.show_key_btn = ctk.CTkCheckBox(
            ai_input_row,
            text="Show",
            variable=self.show_key_var,
            command=self._toggle_show_key,
            width=60,
        )
        self.show_key_btn.pack(side="left", padx=(0, 10))

        ai_actions_row = ctk.CTkFrame(ai_section, fg_color="transparent")
        ai_actions_row.pack(fill="x", padx=20, pady=(0, 15))

        self.test_ai_btn = ctk.CTkButton(
            ai_actions_row,
            text="Test Connection",
            width=130,
            height=34,
            fg_color="#3b82f6",
            hover_color="#2563eb",
            command=self._test_ai_connection,
        )
        self.test_ai_btn.pack(side="left", padx=(0, 10))

        self.save_key_btn = ctk.CTkButton(
            ai_actions_row,
            text="Save API Key",
            width=120,
            height=34,
            fg_color="#10b981",
            hover_color="#059669",
            command=self._save_ai_key,
        )
        self.save_key_btn.pack(side="left")

        self.ai_status_lbl = ctk.CTkLabel(ai_section, text="", font=ctk.CTkFont(size=12))
        self.ai_status_lbl.pack(anchor="w", padx=20, pady=(0, 15))

        # ----------------------------------------------------
        # 3. Theme & Appearance Section
        # ----------------------------------------------------
        theme_section = ctk.CTkFrame(container, corner_radius=10, fg_color=("#e6e8eb", "#1f1f28"))
        theme_section.pack(fill="x", pady=10)

        ctk.CTkLabel(
            theme_section,
            text="🎨 Appearance & Theme",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", padx=20, pady=(15, 5))

        ctk.CTkLabel(
            theme_section,
            text="Customize the visual theme of Daily Writing Companion.",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        ).pack(anchor="w", padx=20, pady=(0, 10))

        theme_row = ctk.CTkFrame(theme_section, fg_color="transparent")
        theme_row.pack(fill="x", padx=20, pady=(0, 15))

        ctk.CTkLabel(theme_row, text="Color Theme:", font=ctk.CTkFont(size=13)).pack(side="left", padx=(0, 15))

        self.theme_dropdown = ctk.CTkOptionMenu(
            theme_row,
            values=["Dark", "Light", "System"],
            command=self._change_theme,
            width=130,
            height=32,
        )
        self.theme_dropdown.set("Dark")
        self.theme_dropdown.pack(side="left")

    def _toggle_show_key(self):
        show_char = "" if self.show_key_var.get() else "*"
        self.ai_key_entry.configure(show=show_char)

    def _quick_set_goal(self, target: int):
        self.goal_entry.delete(0, "end")
        self.goal_entry.insert(0, str(target))
        self._save_goal()

    def _save_goal(self):
        val_str = self.goal_entry.get().strip()
        try:
            val = int(val_str)
            if val <= 0:
                raise ValueError()
            self.goal_service.set_daily_goal(val)
            self.goal_status_lbl.configure(text=f"✓ Goal saved: {val} words/day", text_color="#10b981")
            if self.on_goal_changed:
                self.on_goal_changed()
        except ValueError:
            self.goal_status_lbl.configure(text="Please enter a valid positive number", text_color="#ef4444")

    def _test_ai_connection(self):
        key = self.ai_key_entry.get().strip()
        self.ai_service.set_api_key(key)

        self.test_ai_btn.configure(state="disabled", text="Testing...")
        self.update()

        success, msg = self.ai_service.test_connection()
        self.test_ai_btn.configure(state="normal", text="Test Connection")

        color = "#10b981" if success else "#ef4444"
        self.ai_status_lbl.configure(text=msg, text_color=color)

    def _save_ai_key(self):
        key = self.ai_key_entry.get().strip()
        self.ai_service.set_api_key(key)

        # Persist to .env file
        env_path = BASE_DIR / ".env"
        existing_lines = []
        if env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                existing_lines = f.readlines()

        new_lines = []
        found = False
        for line in existing_lines:
            if line.startswith("GEMINI_API_KEY="):
                new_lines.append(f"GEMINI_API_KEY={key}\n")
                found = True
            else:
                new_lines.append(line)

        if not found:
            new_lines.append(f"GEMINI_API_KEY={key}\n")

        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        self.ai_status_lbl.configure(text="✓ API Key saved to .env successfully!", text_color="#10b981")

    def _change_theme(self, choice: str):
        ctk.set_appearance_mode(choice.lower())

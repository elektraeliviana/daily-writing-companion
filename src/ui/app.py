"""
Main Application Shell for Daily Writing Companion.
Manages window layout, sidebar navigation, and coordinated view state.
"""

import customtkinter as ctk

from src.db.session import init_db, get_session
from src.repositories.entry_repository import EntryRepository
from src.repositories.category_repository import CategoryRepository
from src.repositories.prompt_repository import PromptRepository
from src.repositories.goal_repository import GoalRepository
from src.services.streak_service import StreakService
from src.services.goal_service import GoalService
from src.services.export_service import ExportService
from src.services.journal_service import JournalService
from src.services.ai_service import AIService

from src.ui.views.writing_view import WritingView
from src.ui.views.history_view import HistoryView
from src.ui.views.stats_view import StatsView
from src.ui.views.settings_view import SettingsView
from config.settings import APP_THEME


class WritingCompanionApp(ctk.CTk):
    """Main desktop application window."""

    def __init__(self):
        super().__init__()

        # Appearance configuration
        ctk.set_appearance_mode(APP_THEME)
        ctk.set_default_color_theme("blue")

        self.title("Daily Writing Companion")
        self.geometry("1060x700")
        self.minsize(920, 600)

        # Database and Services Initialization
        init_db()
        self.session = get_session()

        # Repositories
        self.category_repo = CategoryRepository(self.session)
        self.prompt_repo = PromptRepository(self.session)
        self.goal_repo = GoalRepository(self.session)
        self.entry_repo = EntryRepository(self.session)

        # Ensure seed data is present
        self.category_repo.seed_defaults()
        self.prompt_repo.seed_default_prompts()
        self.goal_repo.get_active_goal()

        # Services
        self.goal_service = GoalService(self.session)
        self.export_service = ExportService(self.session)
        self.journal_service = JournalService(self.session)
        self.ai_service = AIService()

        self._build_layout()
        self._select_view("write")

        # Cleanup on close
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _build_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ----------------------------------------------------
        # Left Sidebar Navigation
        # ----------------------------------------------------
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # App Brand Header
        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_frame.pack(fill="x", padx=20, pady=(25, 20))

        app_title = ctk.CTkLabel(
            brand_frame,
            text="✍️ Companion",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        app_title.pack(anchor="w")

        app_subtitle = ctk.CTkLabel(
            brand_frame,
            text="Daily Writing & Journal",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        )
        app_subtitle.pack(anchor="w")

        # Navigation Buttons
        self.nav_buttons = {}

        nav_items = [
            ("write", "✍️  Writing Space"),
            ("history", "📚  History & Search"),
            ("stats", "📊  Stats & Insights"),
            ("settings", "⚙️  Settings"),
        ]

        for view_key, label in nav_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=label,
                font=ctk.CTkFont(size=13, weight="bold"),
                anchor="w",
                height=42,
                corner_radius=8,
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("#e2e8f0", "#282834"),
                command=lambda k=view_key: self._select_view(k),
            )
            btn.pack(fill="x", padx=15, pady=4)
            self.nav_buttons[view_key] = btn

        # Sidebar Footer: Live Streak Indicator
        self.footer_frame = ctk.CTkFrame(self.sidebar, corner_radius=8, fg_color=("#e2e8f0", "#202028"))
        self.footer_frame.pack(side="bottom", fill="x", padx=15, pady=20)

        self.streak_badge_lbl = ctk.CTkLabel(
            self.footer_frame,
            text="🔥 Streak: 0 days",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#f59e0b",
        )
        self.streak_badge_lbl.pack(padx=10, pady=(10, 4))

        self.status_sub_lbl = ctk.CTkLabel(
            self.footer_frame,
            text="Keep the habit alive",
            font=ctk.CTkFont(size=10),
            text_color="gray",
        )
        self.status_sub_lbl.pack(padx=10, pady=(0, 10))

        # ----------------------------------------------------
        # Right Main Content Container
        # ----------------------------------------------------
        self.content_container = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_container.grid(row=0, column=1, sticky="nsew")
        self.content_container.grid_columnconfigure(0, weight=1)
        self.content_container.grid_rowconfigure(0, weight=1)

        # Initialize View Instances
        self.views = {
            "write": WritingView(
                self.content_container,
                journal_service=self.journal_service,
                prompt_repo=self.prompt_repo,
                goal_repo=self.goal_repo,
                ai_service=self.ai_service,
                on_entry_saved=self._on_data_updated,
            ),
            "history": HistoryView(
                self.content_container,
                entry_repo=self.entry_repo,
                on_data_changed=self._on_data_updated,
            ),
            "stats": StatsView(
                self.content_container,
                journal_service=self.journal_service,
                export_service=self.export_service,
            ),
            "settings": SettingsView(
                self.content_container,
                goal_service=self.goal_service,
                ai_service=self.ai_service,
                on_goal_changed=self._on_data_updated,
            ),
        }

        self._refresh_sidebar_streak()

    def _select_view(self, view_key: str):
        """Swaps the active view and highlights corresponding navigation button."""
        for k, btn in self.nav_buttons.items():
            if k == view_key:
                btn.configure(fg_color=("#3b82f6", "#2563eb"), text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color=("gray10", "gray90"))

        for k, view in self.views.items():
            if k == view_key:
                view.grid(row=0, column=0, sticky="nsew")
            else:
                view.grid_forget()

        # Specific refreshes when switching to view
        if view_key == "history":
            self.views["history"].refresh_entries()
        elif view_key == "stats":
            self.views["stats"].refresh_stats()

    def _refresh_sidebar_streak(self):
        dates = self.entry_repo.get_all_dates()
        current, _, written_today = StreakService.calculate_streaks(dates)
        self.streak_badge_lbl.configure(text=f"🔥 Streak: {current} day{'s' if current != 1 else ''}")
        if written_today:
            self.status_sub_lbl.configure(text="✓ Written today!", text_color="#10b981")
        else:
            self.status_sub_lbl.configure(text="Write today to continue", text_color="gray")

    def _on_data_updated(self):
        """Callback invoked when entries are added, edited, deleted, or goals change."""
        self._refresh_sidebar_streak()
        # Update goal progress in writing view
        current_words = len(self.views["write"].editor.get("1.0", "end-1c").strip().split())
        self.views["write"]._update_progress_display(current_words)

    def _on_closing(self):
        if self.session:
            self.session.close()
        self.destroy()

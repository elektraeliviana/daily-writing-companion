"""
Stats & Insights Dashboard View: Visual streaks, goal completion, and analytics.
"""

from pathlib import Path
from typing import Optional, Callable
import customtkinter as ctk

from src.services.journal_service import JournalService
from src.services.export_service import ExportService
from config.settings import BASE_DIR


class StatsView(ctk.CTkFrame):
    """Dashboard view for streaks, writing metrics, and mood trends."""

    def __init__(
        self,
        parent,
        journal_service: JournalService,
        export_service: ExportService,
        on_request_write: Optional[Callable[[], None]] = None,
    ):
        super().__init__(parent, fg_color="transparent")
        self.journal_service = journal_service
        self.export_service = export_service
        self.on_request_write = on_request_write

        self._build_ui()
        self.refresh_stats()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header Row
        header_row = ctk.CTkFrame(self, fg_color="transparent")
        header_row.grid(row=0, column=0, sticky="ew", padx=25, pady=(20, 10))

        title = ctk.CTkLabel(
            header_row,
            text="Writing Stats & Insights",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        title.pack(side="left")

        # Export Button
        export_btn = ctk.CTkButton(
            header_row,
            text="📄 Export to .txt",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=130,
            height=32,
            fg_color="#334155",
            hover_color="#475569",
            command=self._export_journal,
        )
        export_btn.pack(side="right")

        # Scrollable Content Area
        self.scroll_content = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_content.grid(row=1, column=0, sticky="nsew", padx=25, pady=(5, 20))
        self.scroll_content.grid_columnconfigure((0, 1), weight=1)

        # 1. Streak & Goal Top Cards Row
        self.streak_card = ctk.CTkFrame(self.scroll_content, corner_radius=10, fg_color=("#e6e8eb", "#1f1f28"))
        self.streak_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)

        self.goal_card = ctk.CTkFrame(self.scroll_content, corner_radius=10, fg_color=("#e6e8eb", "#1f1f28"))
        self.goal_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=10)

        # 2. Key Metrics Row
        self.metrics_frame = ctk.CTkFrame(self.scroll_content, corner_radius=10, fg_color=("#e6e8eb", "#1f1f28"))
        self.metrics_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=10)
        self.metrics_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # 3. Category & Mood Breakdown Row
        self.cat_frame = ctk.CTkFrame(self.scroll_content, corner_radius=10, fg_color=("#e6e8eb", "#1f1f28"))
        self.cat_frame.grid(row=2, column=0, sticky="nsew", padx=(0, 10), pady=10)

        self.mood_frame = ctk.CTkFrame(self.scroll_content, corner_radius=10, fg_color=("#e6e8eb", "#1f1f28"))
        self.mood_frame.grid(row=2, column=1, sticky="nsew", padx=(10, 0), pady=10)

    def refresh_stats(self):
        """Fetches fresh data and updates all dashboard widgets."""
        summary = self.journal_service.get_dashboard_summary()

        current_streak = summary["current_streak"]
        longest_streak = summary["longest_streak"]
        written_today = summary["written_today"]
        today_progress = summary["today_progress"]
        stats = summary["stats"]

        self._render_streak_card(current_streak, longest_streak, written_today)
        self._render_goal_card(today_progress)
        self._render_metrics_row(stats)
        self._render_categories(stats.get("category_breakdown", {}))
        self._render_moods(stats.get("mood_breakdown", {}))

    def _render_streak_card(self, current: int, longest: int, written_today: bool):
        for w in self.streak_card.winfo_children():
            w.destroy()

        title = ctk.CTkLabel(
            self.streak_card,
            text="🔥 Writing Streak",
            font=ctk.CTkFont(size=15, weight="bold"),
        )
        title.pack(anchor="w", padx=18, pady=(15, 5))

        streak_val = ctk.CTkLabel(
            self.streak_card,
            text=f"{current} Day{'s' if current != 1 else ''}",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#f59e0b",
        )
        streak_val.pack(anchor="w", padx=18)

        status_text = "✨ You have written today!" if written_today else "⏳ Write today to keep your streak!"
        status_color = "#10b981" if written_today else "#94a3b8"

        status_lbl = ctk.CTkLabel(
            self.streak_card,
            text=status_text,
            font=ctk.CTkFont(size=12),
            text_color=status_color,
        )
        status_lbl.pack(anchor="w", padx=18, pady=(2, 8))

        best_lbl = ctk.CTkLabel(
            self.streak_card,
            text=f"All-time longest streak: {longest} day{'s' if longest != 1 else ''}",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        )
        best_lbl.pack(anchor="w", padx=18, pady=(0, 15))

    def _render_goal_card(self, progress: dict):
        for w in self.goal_card.winfo_children():
            w.destroy()

        title = ctk.CTkLabel(
            self.goal_card,
            text="🎯 Today's Word Goal",
            font=ctk.CTkFont(size=15, weight="bold"),
        )
        title.pack(anchor="w", padx=18, pady=(15, 5))

        words = progress.get("words_today", 0)
        goal = progress.get("goal", 200)
        pct = progress.get("percentage", 0.0)

        val = ctk.CTkLabel(
            self.goal_card,
            text=f"{words} / {goal} words",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#10b981" if progress.get("is_reached") else "#3b82f6",
        )
        val.pack(anchor="w", padx=18)

        p_bar = ctk.CTkProgressBar(self.goal_card, height=10, corner_radius=5)
        p_bar.set(min(1.0, words / goal if goal > 0 else 1.0))
        p_bar.configure(progress_color="#10b981" if progress.get("is_reached") else "#3b82f6")
        p_bar.pack(fill="x", padx=18, pady=8)

        desc = (
            "🎉 Goal achieved for today!"
            if progress.get("is_reached")
            else f"{progress.get('remaining', 0)} more words needed today."
        )
        desc_lbl = ctk.CTkLabel(
            self.goal_card,
            text=f"{desc} ({pct}%)",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        )
        desc_lbl.pack(anchor="w", padx=18, pady=(0, 15))

    def _render_metrics_row(self, stats: dict):
        for w in self.metrics_frame.winfo_children():
            w.destroy()

        metrics = [
            ("Total Entries", str(stats.get("total_entries", 0))),
            ("Total Words", f"{stats.get('total_words', 0):,}"),
            ("Average Words/Entry", str(stats.get("average_words", 0))),
        ]

        for col, (label, val) in enumerate(metrics):
            box = ctk.CTkFrame(self.metrics_frame, fg_color="transparent")
            box.grid(row=0, column=col, padx=15, pady=15)

            v_lbl = ctk.CTkLabel(
                box, text=val, font=ctk.CTkFont(size=22, weight="bold"), text_color="#6366f1"
            )
            v_lbl.pack()

            l_lbl = ctk.CTkLabel(box, text=label, font=ctk.CTkFont(size=12), text_color="gray")
            l_lbl.pack()

    def _render_categories(self, cat_data: dict):
        for w in self.cat_frame.winfo_children():
            w.destroy()

        ctk.CTkLabel(
            self.cat_frame,
            text="📚 Writing by Category",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(anchor="w", padx=18, pady=(15, 10))

        if not cat_data:
            ctk.CTkLabel(self.cat_frame, text="No entries yet.", font=ctk.CTkFont(size=12), text_color="gray").pack(
                padx=18, pady=10
            )
            return

        total_entries = sum(item["count"] for item in cat_data.values())

        for cat_name, info in cat_data.items():
            row = ctk.CTkFrame(self.cat_frame, fg_color="transparent")
            row.pack(fill="x", padx=18, pady=4)

            name_lbl = ctk.CTkLabel(
                row,
                text=cat_name.capitalize(),
                font=ctk.CTkFont(size=13, weight="bold"),
                width=80,
                anchor="w",
            )
            name_lbl.pack(side="left")

            count_pct = (info["count"] / total_entries) if total_entries > 0 else 0
            bar = ctk.CTkProgressBar(row, height=8, corner_radius=4)
            bar.set(count_pct)
            bar.pack(side="left", fill="x", expand=True, padx=10)

            stats_lbl = ctk.CTkLabel(
                row,
                text=f"{info['count']} ({info['words']}w)",
                font=ctk.CTkFont(size=12),
                text_color="gray",
                width=70,
                anchor="e",
            )
            stats_lbl.pack(side="right")

        # Bottom padding
        ctk.CTkLabel(self.cat_frame, text="", height=5).pack()

    def _render_moods(self, mood_data: dict):
        for w in self.mood_frame.winfo_children():
            w.destroy()

        ctk.CTkLabel(
            self.mood_frame,
            text="🎭 Mood Breakdown",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(anchor="w", padx=18, pady=(15, 10))

        if not mood_data:
            ctk.CTkLabel(
                self.mood_frame,
                text="Rate your mood after writing to see trends here!",
                font=ctk.CTkFont(size=12),
                text_color="gray",
            ).pack(padx=18, pady=10)
            return

        total_moods = sum(mood_data.values())

        for mood, count in mood_data.items():
            row = ctk.CTkFrame(self.mood_frame, fg_color="transparent")
            row.pack(fill="x", padx=18, pady=4)

            name_lbl = ctk.CTkLabel(
                row,
                text=mood,
                font=ctk.CTkFont(size=13),
                width=120,
                anchor="w",
            )
            name_lbl.pack(side="left")

            pct = (count / total_moods) if total_moods > 0 else 0
            bar = ctk.CTkProgressBar(row, height=8, corner_radius=4)
            bar.set(pct)
            bar.pack(side="left", fill="x", expand=True, padx=10)

            count_lbl = ctk.CTkLabel(
                row,
                text=f"{count}",
                font=ctk.CTkFont(size=12),
                text_color="gray",
                width=30,
                anchor="e",
            )
            count_lbl.pack(side="right")

        ctk.CTkLabel(self.mood_frame, text="", height=5).pack()

    def _export_journal(self):
        try:
            exported_file = self.export_service.export_to_text(BASE_DIR)
            # Show popup
            alert = ctk.CTkToplevel(self)
            alert.title("Export Successful")
            alert.geometry("450x180")
            alert.transient(self)
            alert.grab_set()

            ctk.CTkLabel(
                alert,
                text="🎉 Journal Exported Successfully!",
                font=ctk.CTkFont(size=16, weight="bold"),
            ).pack(pady=(25, 8))

            ctk.CTkLabel(
                alert,
                text=f"Saved to:\n{exported_file.name}",
                font=ctk.CTkFont(size=12),
                text_color="gray",
            ).pack(pady=5)

            ctk.CTkButton(
                alert,
                text="Close",
                width=100,
                command=lambda: (alert.grab_release(), alert.destroy()),
            ).pack(pady=(10, 0))

        except Exception as e:
            print(f"Export error: {e}")

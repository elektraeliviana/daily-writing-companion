"""
Writing Space View: The core creative writing canvas.
Includes dynamic prompts, live word counting, progress tracking, timer, and AI assistance.
"""

from datetime import datetime, date
from typing import Optional, Callable
import customtkinter as ctk

from src.repositories.prompt_repository import PromptRepository
from src.repositories.goal_repository import GoalRepository
from src.services.journal_service import JournalService
from src.services.ai_service import AIService
from src.ui.components.mood_dialog import MoodDialog
from src.ui.components.feedback_dialog import FeedbackDialog


class WritingView(ctk.CTkFrame):
    """Writing Space canvas view."""

    def __init__(
        self,
        parent,
        journal_service: JournalService,
        prompt_repo: PromptRepository,
        goal_repo: GoalRepository,
        ai_service: AIService,
        on_entry_saved: Optional[Callable[[], None]] = None,
    ):
        super().__init__(parent, fg_color="transparent")
        self.journal_service = journal_service
        self.prompt_repo = prompt_repo
        self.goal_repo = goal_repo
        self.ai_service = ai_service
        self.on_entry_saved = on_entry_saved

        # State
        self.current_category = "journal"
        self.current_prompt_text = ""
        self.session_start_time: Optional[datetime] = None
        self.timer_seconds = 0
        self.timer_running = False
        self._timer_after_id = None

        self._build_ui()
        self._load_initial_prompt()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)  # Editor expands

        # Top Control Row (Category Selector + AI Action)
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.grid(row=0, column=0, sticky="ew", padx=25, pady=(20, 10))

        cat_lbl = ctk.CTkLabel(top_bar, text="Writing Mode:", font=ctk.CTkFont(size=13, weight="bold"))
        cat_lbl.pack(side="left", padx=(0, 10))

        self.category_seg = ctk.CTkSegmentedButton(
            top_bar,
            values=["Journal", "Story", "Poem", "Surprise Me"],
            command=self._on_category_changed,
        )
        self.category_seg.set("Journal")
        self.category_seg.pack(side="left")

        # Timer Indicator
        self.timer_lbl = ctk.CTkLabel(
            top_bar,
            text="⏱️ 00:00",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#8ea0b5",
        )
        self.timer_lbl.pack(side="right", padx=(10, 0))

        # Prompt Card
        self.prompt_card = ctk.CTkFrame(self, corner_radius=10, fg_color=("#e6e8eb", "#1f1f28"))
        self.prompt_card.grid(row=1, column=0, sticky="ew", padx=25, pady=5)
        self.prompt_card.grid_columnconfigure(0, weight=1)

        self.prompt_lbl = ctk.CTkLabel(
            self.prompt_card,
            text="Loading prompt...",
            font=ctk.CTkFont(size=14, slant="italic"),
            wraplength=650,
            justify="left",
        )
        self.prompt_lbl.grid(row=0, column=0, sticky="w", padx=20, pady=(15, 10))

        # Prompt Button Actions Row
        prompt_actions = ctk.CTkFrame(self.prompt_card, fg_color="transparent")
        prompt_actions.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 12))

        self.new_prompt_btn = ctk.CTkButton(
            prompt_actions,
            text="🎲 New Prompt",
            font=ctk.CTkFont(size=12),
            width=110,
            height=28,
            fg_color=("#d0d4db", "#2e2e3d"),
            hover_color=("#bfc4cc", "#3d3d52"),
            text_color=("#1a1a1a", "#ffffff"),
            command=self._next_prompt,
        )
        self.new_prompt_btn.pack(side="left", padx=(0, 10))

        self.ai_prompt_btn = ctk.CTkButton(
            prompt_actions,
            text="✨ Ask Gemini Prompt",
            font=ctk.CTkFont(size=12),
            width=140,
            height=28,
            fg_color="#4f46e5",
            hover_color="#4338ca",
            command=self._generate_ai_prompt,
        )
        self.ai_prompt_btn.pack(side="left")

        # Text Editor Area
        self.editor = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(size=15),
            wrap="word",
            corner_radius=10,
            undo=True,
        )
        self.editor.grid(row=2, column=0, sticky="nsew", padx=25, pady=10)
        self.editor.bind("<KeyRelease>", self._on_text_changed)

        # Bottom Bar: Goal Progress & Actions
        bottom_bar = ctk.CTkFrame(self, fg_color="transparent")
        bottom_bar.grid(row=3, column=0, sticky="ew", padx=25, pady=(5, 20))
        bottom_bar.grid_columnconfigure(0, weight=1)

        # Progress Stats
        progress_info = ctk.CTkFrame(bottom_bar, fg_color="transparent")
        progress_info.grid(row=0, column=0, sticky="ew")

        self.word_count_lbl = ctk.CTkLabel(
            progress_info,
            text="0 / 200 words (0%)",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self.word_count_lbl.pack(side="left", pady=(0, 5))

        self.progress_bar = ctk.CTkProgressBar(progress_info, height=10, corner_radius=5)
        self.progress_bar.set(0.0)
        self.progress_bar.pack(fill="x", pady=(0, 10))

        # Bottom Buttons Row
        action_buttons = ctk.CTkFrame(bottom_bar, fg_color="transparent")
        action_buttons.grid(row=1, column=0, sticky="ew")

        self.feedback_btn = ctk.CTkButton(
            action_buttons,
            text="✨ AI Writing Mentor",
            font=ctk.CTkFont(size=13),
            width=150,
            height=36,
            fg_color="#3b82f6",
            hover_color="#2563eb",
            command=self._request_ai_feedback,
        )
        self.feedback_btn.pack(side="left")

        self.status_banner = ctk.CTkLabel(
            action_buttons,
            text="",
            font=ctk.CTkFont(size=12, slant="italic"),
            text_color="#10b981",
        )
        self.status_banner.pack(side="left", padx=15)

        self.save_btn = ctk.CTkButton(
            action_buttons,
            text="💾 Save Entry",
            font=ctk.CTkFont(size=13, weight="bold"),
            width=130,
            height=36,
            fg_color="#10b981",
            hover_color="#059669",
            command=self._initiate_save,
        )
        self.save_btn.pack(side="right")

    def _start_timer_if_needed(self):
        if not self.timer_running:
            self.timer_running = True
            self.session_start_time = datetime.now()
            self._tick_timer()

    def _tick_timer(self):
        if self.timer_running:
            self.timer_seconds += 1
            mins, secs = divmod(self.timer_seconds, 60)
            self.timer_lbl.configure(text=f"⏱️ {mins:02d}:{secs:02d}")
            self._timer_after_id = self.after(1000, self._tick_timer)

    def _stop_timer(self):
        self.timer_running = False
        if self._timer_after_id:
            self.after_cancel(self._timer_after_id)
            self._timer_after_id = None

    def _reset_timer(self):
        self._stop_timer()
        self.timer_seconds = 0
        self.timer_lbl.configure(text="⏱️ 00:00")

    def _on_category_changed(self, choice: str):
        mapping = {"Journal": "journal", "Story": "story", "Poem": "poem"}
        if choice in mapping:
            self.current_category = mapping[choice]
        else:
            import random
            self.current_category = random.choice(["journal", "story", "poem"])
        self._next_prompt()

    def _load_initial_prompt(self):
        self._next_prompt()
        self._update_progress_display(0)

    def _next_prompt(self):
        prompt_obj = self.prompt_repo.get_random_prompt(self.current_category)
        if prompt_obj:
            self.current_prompt_text = prompt_obj.content
        else:
            self.current_prompt_text = "What is on your mind today? Let words flow freely."
        self.prompt_lbl.configure(text=f'"{self.current_prompt_text}"')

    def _generate_ai_prompt(self):
        self.ai_prompt_btn.configure(state="disabled", text="Generating...")
        self.update()

        success, result = self.ai_service.generate_prompt(category=self.current_category)
        self.ai_prompt_btn.configure(state="normal", text="✨ Ask Gemini Prompt")

        if success:
            self.current_prompt_text = result
            self.prompt_lbl.configure(text=f'"{self.current_prompt_text}"')
            # Save generated prompt to database
            self.prompt_repo.add_prompt(
                category_name=self.current_category, content=result, is_ai_generated=True
            )
        else:
            self._show_temp_status(f"Notice: {result}", is_error=True)

    def _on_text_changed(self, event=None):
        self._start_timer_if_needed()
        text = self.editor.get("1.0", "end-1c").strip()
        words = len(text.split()) if text else 0
        self._update_progress_display(words)

    def _update_progress_display(self, words: int):
        goal = self.goal_repo.get_active_goal()
        pct = min(1.0, words / goal) if goal > 0 else 1.0
        pct_int = int(pct * 100)

        self.word_count_lbl.configure(text=f"{words} / {goal} words ({pct_int}%)")
        self.progress_bar.set(pct)

        # Highlight in emerald green if goal reached!
        if words >= goal and goal > 0:
            self.word_count_lbl.configure(text_color="#10b981")
            self.progress_bar.configure(progress_color="#10b981")
        else:
            self.word_count_lbl.configure(text_color=("black", "white"))
            self.progress_bar.configure(progress_color="#3b82f6")

    def _request_ai_feedback(self):
        text = self.editor.get("1.0", "end-1c").strip()
        if not text or len(text.split()) < 3:
            self._show_temp_status("Please write at least a few sentences first!", is_error=True)
            return

        self.feedback_btn.configure(state="disabled", text="Analyzing...")
        self.update()

        success, feedback = self.ai_service.get_writing_feedback(
            text=text,
            category=self.current_category,
            prompt_used=self.current_prompt_text,
        )
        self.feedback_btn.configure(state="normal", text="✨ AI Writing Mentor")

        if success:
            FeedbackDialog(self, feedback)
        else:
            self._show_temp_status(feedback, is_error=True)

    def _initiate_save(self):
        text = self.editor.get("1.0", "end-1c").strip()
        if not text:
            self._show_temp_status("Nothing to save! Write something first.", is_error=True)
            return

        self._stop_timer()

        # Open post-writing mood rating dialog
        MoodDialog(self, on_select=self._complete_save)

    def _complete_save(self, selected_mood: Optional[str]):
        text = self.editor.get("1.0", "end-1c").strip()
        if not text:
            return

        duration = max(self.timer_seconds, 1)

        # Save entry via JournalService
        entry = self.journal_service.save_new_entry(
            content=text,
            prompt_text=self.current_prompt_text,
            category_name=self.current_category,
            duration_seconds=duration,
            mood=selected_mood,
            entry_date=date.today(),
        )

        # Clear editor and reset state
        self.editor.delete("1.0", "end")
        self._reset_timer()
        self._update_progress_display(0)
        self._next_prompt()

        mood_str = f" with mood {selected_mood}" if selected_mood else ""
        self._show_temp_status(f"🎉 Saved {entry.word_count} words{mood_str}!")

        if self.on_entry_saved:
            self.on_entry_saved()

    def _show_temp_status(self, msg: str, is_error: bool = False):
        color = "#ef4444" if is_error else "#10b981"
        self.status_banner.configure(text=msg, text_color=color)
        self.after(5000, lambda: self.status_banner.configure(text=""))

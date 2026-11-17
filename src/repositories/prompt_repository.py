"""
Prompt Repository for managing static and AI prompts.
"""

import random
from typing import Optional, List
from sqlalchemy.orm import Session
from src.models.prompt import Prompt
from src.repositories.base_repository import BaseRepository
from src.repositories.category_repository import CategoryRepository
from config.settings import DEFAULT_PROMPTS


class PromptRepository(BaseRepository[Prompt]):
    """Data access layer for writing prompts."""

    def __init__(self, session: Session):
        super().__init__(Prompt, session)
        self.category_repo = CategoryRepository(session)

    def get_by_category(self, category_name: str) -> List[Prompt]:
        """Get all prompts under a given category."""
        category = self.category_repo.get_by_name(category_name)
        if not category:
            return []
        return self.session.query(Prompt).filter(Prompt.category_id == category.id).all()

    def get_random_prompt(self, category_name: Optional[str] = None) -> Optional[Prompt]:
        """Fetch a random prompt, optionally filtered by category."""
        query = self.session.query(Prompt)
        if category_name:
            cat = self.category_repo.get_by_name(category_name)
            if cat:
                query = query.filter(Prompt.category_id == cat.id)

        prompts = query.all()
        return random.choice(prompts) if prompts else None

    def add_prompt(self, category_name: str, content: str, is_ai_generated: bool = False) -> Prompt:
        """Add a new prompt linked to a category."""
        category = self.category_repo.get_or_create(category_name)
        prompt = Prompt(
            category_id=category.id,
            content=content.strip(),
            is_ai_generated=is_ai_generated,
        )
        self.add(prompt)
        self.session.commit()
        return prompt

    def seed_default_prompts(self) -> int:
        """Seeds curated prompts from settings if not already present."""
        seeded_count = 0
        for category_name, prompts_list in DEFAULT_PROMPTS.items():
            category = self.category_repo.get_or_create(category_name)
            existing_contents = {
                p.content for p in self.session.query(Prompt).filter(Prompt.category_id == category.id).all()
            }
            for prompt_text in prompts_list:
                if prompt_text not in existing_contents:
                    prompt = Prompt(
                        category_id=category.id,
                        content=prompt_text,
                        is_ai_generated=False,
                    )
                    self.add(prompt)
                    seeded_count += 1
        self.session.commit()
        return seeded_count

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

REQUIRED_PROMPT_SECTIONS = [
    "Rolle",
    "Scope",
    "Inputs",
    "Output-Schema",
    "Harte Regeln",
    "Bewertungslogik",
    "Eskalationslogik",
    "Beispiele fuer Findings",
    "Beispiele fuer insufficient evidence",
    "Verbot von freiem Weltwissen",
    "Pflicht zur Seiten-/Chunk-/Zitat-Evidenz",
    "Denke konservativ",
]


class PromptTemplateNotFoundError(Exception):
    pass


class PromptTemplateValidationError(Exception):
    pass


@dataclass(frozen=True)
class PromptTemplate:
    file_name: str
    prompt_version: str
    version: str
    path: Path
    content: str


class PromptTemplateLoader:
    def __init__(self, *, prompts_dir: Path | None = None) -> None:
        self.prompts_dir = prompts_dir or Path(__file__).resolve().parent / "prompts"

    def load(self, template_name: str) -> PromptTemplate:
        file_name = template_name if template_name.endswith(".md") else f"{template_name}.md"
        path = self.prompts_dir / file_name
        if not path.exists():
            raise PromptTemplateNotFoundError(f"Prompt template not found: {path}")

        content = path.read_text(encoding="utf-8")
        missing_sections = [
            section for section in REQUIRED_PROMPT_SECTIONS if f"## {section}" not in content
        ]
        if missing_sections:
            raise PromptTemplateValidationError(
                f"Prompt template {file_name} is missing sections: {', '.join(missing_sections)}"
            )

        prompt_version = file_name.removesuffix(".md")
        return PromptTemplate(
            file_name=file_name,
            prompt_version=prompt_version,
            version=_extract_version(prompt_version),
            path=path,
            content=content,
        )


def _extract_version(prompt_version: str) -> str:
    match = re.search(r"_v(\d+)$", prompt_version)
    if match is None:
        raise PromptTemplateValidationError(
            f"Prompt template version suffix missing in {prompt_version}"
        )
    return f"v{match.group(1)}"

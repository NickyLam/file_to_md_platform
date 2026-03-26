from dataclasses import dataclass, field


@dataclass(frozen=True)
class ConversionResult:
    markdown: str
    warnings: tuple[str, ...] = ()
    artifacts: dict[str, bytes] = field(default_factory=dict)

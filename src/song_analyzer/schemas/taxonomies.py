"""Allowed taxonomy/standardized variable values, used by the Song Analyzer schemas and prompts."""

THEME_FAMILIES = [
    "love_relationships",
    "loss_grief",
    "connection_belonging",
    "loneliness_isolation",
    "identity_self_discovery",
    "conflict_struggle",
    "healing_recovery",
    "hope_resilience",
    "freedom_autonomy",
    "change_transition",
    "memory_nostalgia",
    "mortality_spirituality",
    "social_commentary",
]

EMOTION_FAMILIES = [
    "joy",
    "sadness",
    "anger",
    "fear_anxiety",
    "love_connection",
    "loneliness_isolation",
    "hope_empowerment",
    "calm_acceptance",
    "shame_guilt",
    "nostalgia_longing",
    "confusion_ambivalence",
    "disgust_rejection",
]

THEME_ROLES = [
    "primary",
    "secondary",
]

EMOTION_ROLES = [
    "primary",
    "secondary",
]

ARC_MOVEMENTS = [
    "positive_shift",
    "negative_shift",
    "stable_positive",
    "stable_negative",
    "mixed",
    "cyclical",
    "ambiguous",
]

AGENCY_LEVELS = [
    "low",
    "medium",
    "high",
    "mixed",
    "ambiguous",
]

RESOLUTION_STATES = [
    "resolved",
    "partially_resolved",
    "unresolved",
    "ambiguous",
]

CONFIDENCE_LEVELS = [
    "low",
    "medium",
    "high",
]

UNCERTAINTY_FIELDS = [
    "themes",
    "emotions",
    "emotional_arc",
    "agency_level",
    "resolution_state",
]
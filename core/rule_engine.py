"""
Rule Engine — Loads regulatory rules from YAML config.
Single source of truth for all validators.
"""
import yaml
import os
from pathlib import Path


class RuleEngine:
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "rules.yaml"
        with open(config_path, "r") as f:
            self._rules = yaml.safe_load(f)

    @property
    def required_fields(self) -> list:
        return self._rules["schema"]["required_fields"]

    @property
    def field_types(self) -> dict:
        return self._rules["schema"]["field_types"]

    @property
    def thresholds(self) -> dict:
        return self._rules["thresholds"]

    @property
    def patterns(self) -> dict:
        return self._rules["patterns"]

    @property
    def cross_field_rules(self) -> list:
        return self._rules["cross_field"]

    @property
    def anomaly_config(self) -> dict:
        return self._rules["anomaly_detection"]

    def get_threshold(self, field: str) -> dict:
        return self._rules["thresholds"].get(field, None)
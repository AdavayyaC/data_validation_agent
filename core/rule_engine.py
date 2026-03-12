"""
Rule Engine — Single source of truth for all validation rules.
Loaded from rules.yaml — no hardcoded thresholds anywhere.
"""
import yaml
from pathlib import Path


class RuleEngine:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "rules.yaml"
        with open(config_path, "r") as f:
            self._rules = yaml.safe_load(f)

    @property
    def required_fields(self): return self._rules["schema"]["required_fields"]
    @property
    def field_types(self): return self._rules["schema"]["field_types"]
    @property
    def thresholds(self): return self._rules["thresholds"]
    @property
    def patterns(self): return self._rules["patterns"]
    @property
    def cross_field_rules(self): return self._rules["cross_field"]
    @property
    def anomaly_config(self): return self._rules["anomaly_detection"]
    @property
    def integrity_config(self): return self._rules["integrity"]
    @property
    def escalation_rules(self): return self._rules["escalation"]["rules"]
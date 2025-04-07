import re
import time
import html
import json
import logging
import statistics
from typing import Dict, List, Tuple, Optional, Union, Any, Set
from datetime import datetime
from functools import wraps
from collections import defaultdict
from enum import Enum
from threading import Lock

############################################
# Constants
############################################
APP_VERSION = "4.0.2"
DICTIONARY_VERSIONS = {
    "politeness": "1.2.0",
    "cooperative": "1.1.0",
    "concerning_verbs": "1.3.0",
    "power_assertions": "1.2.0",
    "positive_words": "1.0.0",
    "concerning_patterns": "1.1.0",
    "negation_phrases": "1.0.0",
    "positive_context": "1.1.0",
    "profanity": "1.2.0",
    "cross_language_profanity": "1.0.0",
    "emoji": "1.1.0",
    "language_detectors": "1.0.0"
}

# Constants for trigger categories
class TriggerCategory(str, Enum):
    POLITENESS = "politeness"
    COOPERATIVE = "cooperative"
    POSITIVE = "positive"
    CONCERN = "concern"
    NEGATED_CONCERN = "negated_concern"
    PROFANITY = "profanity"
    COLORFUL_PROFANITY = "colorful_profanity"
    POWER_ASSERTION = "power_assertion"
    CONCERNING_PATTERN = "concerning_pattern"
    QUESTION_MARK = "question_mark"
    POSITIVE_EMOJI = "positive_emoji"
    NEGATIVE_EMOJI = "negative_emoji"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    SARCASM_DETECTED = "sarcasm_detected"
    SYNONYM = "synonym"
    OTHER = "other"
    CONTEXT_MODIFIES = "context_modifies"

############################################
# Logging configuration
############################################
logger = logging.getLogger("solon_intent_checker")
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

############################################
# User Context Management
############################################
class UserContextManager:
    """Manages user-specific context, including message history and warnings."""

    def __init__(self, max_history=20, score_history_length=5, context_expiration_seconds=3600):
        self.user_contexts = {}
        self.max_history = max_history
        self.score_history_length = score_history_length
        self.context_expiration_seconds = context_expiration_seconds
        self.lock = Lock()  # Ensures thread-safe access to user contexts

    def get_context(self, user_id: str) -> Dict[str, Any]:
        """Retrieves or creates a user context."""
        now = datetime.now()
        with self.lock:  # Thread-safe context retrieval and updating
            if user_id not in self.user_contexts or self._is_context_expired(self.user_contexts[user_id], now):
                self.user_contexts[user_id] = {
                    "message_history": [],
                    "warning_count": 0,
                    "last_scores": [],
                    "created_at": now.isoformat(),
                    "feature_usage": defaultdict(int)
                }
        return self.user_contexts[user_id]

    def update_context(self, user_id: str, message: str, result: Dict):
        """Updates the user context with new message and result data."""
        context = self.get_context(user_id)
        with self.lock:  # Thread-safe context update
            context["message_history"].append(message)
            context["message_history"] = context["message_history"][-self.max_history:]
            context["last_scores"].append(result["score"])
            context["last_scores"] = context["last_scores"][-self.score_history_length:]
            if not result["is_respectful"]:
                context["warning_count"] += 1
            for trigger, _ in result["triggers"]:
                feature = trigger.split(":")[0] if ":" in trigger else trigger
                context["feature_usage"][feature] += 1

    def _is_context_expired(self, context: Dict[str, Any], now: datetime) -> bool:
        """Checks if the user context has expired."""
        created_at_str = context.get("created_at")
        if not created_at_str:
            return True
        created_at = datetime.fromisoformat(created_at_str)
        return (now - created_at).total_seconds() > self.context_expiration_seconds

    def clear_expired_contexts(self):
        """Removes expired user contexts."""
        now = datetime.now()
        with self.lock:  # Thread-safe removal of expired contexts
            self.user_contexts = {
                user_id: context
                for user_id, context in self.user_contexts.items()
                if not self._is_context_expired(context, now)
            }

############################################
# Performance Metrics
############################################
class PerformanceMetrics:
    """Collects and reports performance statistics."""

    def __init__(self):
        self.total_calls = 0
        self.processing_times = []
        self.processing_times_by_feature = defaultdict(list)
        self.error_count = 0
        self.lock = Lock()

    def reset(self):
        """Resets all metrics."""
        with self.lock:  # Thread-safe reset
            self.total_calls = 0
            self.processing_times = []
            self.processing_times_by_feature.clear()
            self.error_count = 0

    def add_processing_time(self, duration: float, feature_name: Optional[str] = None):
        """Adds a processing time measurement."""
        with self.lock:  # Thread-safe addition
            self.processing_times.append(duration)
            if feature_name:
                self.processing_times_by_feature[feature_name].append(duration)

    def increment_error_count(self):
        """Increments the error count."""
        with self.lock:  # Thread-safe increment
            self.error_count += 1

    def get_stats(self) -> Dict[str, Any]:
        """Calculates and returns performance statistics."""
        with self.lock:  # Thread-safe stats calculation
            stats = {
                "total_calls": self.total_calls,
                "error_count": self.error_count,
            }
            times = self.processing_times
            if times:
                stats.update({
                    "avg_processing_time_ms": round(statistics.mean(times) * 1000, 2),
                    "median_processing_time_ms": round(statistics.median(times) * 1000, 2),
                    "max_processing_time_ms": round(max(times) * 1000, 2),
                    "min_processing_time_ms": round(min(times) * 1000, 2),
                    "stdev_processing_time_ms": round(statistics.stdev(times) * 1000, 2) if len(times) > 1 else 0.0
                })

            if self.total_calls > 0:
                stats["error_rate"] = round((self.error_count / self.total_calls) * 100, 2)
            else:
                stats["error_rate"] = 0.0

            feature_timing = {}
            for feature, times in self.processing_times_by_feature.items():
                if times:
                    feature_timing[feature] = {
                        "avg_ms": round(statistics.mean(times) * 1000, 2),
                        "calls": len(times),
                        "total_ms": round(sum(times) * 1000, 2)
                    }
            stats["feature_timing"] = feature_timing
            return stats

############################################
# Telemetry
############################################
class TelemetryManager:
    """Handles collection and logging of anonymized telemetry data."""

    def __init__(self, enabled: bool = False):
        self.enabled = enabled
        self.consented_users = set()
        self.lock = Lock()

    def enable(self):
        """Enables telemetry collection."""
        with self.lock:  # Thread-safe enable
            self.enabled = True

    def disable(self):
        """Disables telemetry collection."""
        with self.lock:  # Thread-safe disable
            self.enabled = False

    def add_consent(self, user_id: str):
        """Adds a user to the set of those who have consented."""
        with self.lock:  # Thread-safe addition
            self.consented_users.add(user_id)

    def remove_consent(self, user_id: str):
        """Removes a user from the set of those who have consented."""
        with self.lock:  # Thread-safe removal
            self.consented_users.discard(user_id)

    def should_collect(self, user_id: Optional[str] = None) -> bool:
        """Determines if telemetry data should be collected for the given user."""
        with self.lock:  # Thread-safe check
            return self.enabled and (user_id is None or user_id in self.consented_users)

    def log(self, message_length: int, result: Dict, culture: str, user_id: Optional[str] = None):
        """Logs anonymized telemetry data."""
        if not self.should_collect(user_id):
            return

        telemetry_data = {
            "timestamp": datetime.now().isoformat(),
            "message_length": message_length,
            "culture": culture,
            "is_respectful": result["is_respectful"],
            "score_range": round(result["score"] * 2) / 2,
            "confidence": round(result["confidence"] * 10) / 10,
            "feature_count": len(result["triggers"]),
            "processing_time_ms": round(result["metadata"].get("processing_time", 0) * 1000, 2),
            "language": result["metadata"].get("language", "unknown"),
        }
        logger.info(f"Telemetry: {json.dumps(telemetry_data)}")

# Replaced global instances with private members of the IntentChecker class
class IntentChecker:
    """
    Solon Intent Checker: A comprehensive system for evaluating message intent.
    """

    def __init__(
        self,
        user_id: Optional[str] = None,
        culture: str = "general",
        positive_threshold: float = 0.5,
        negative_threshold: float = -0.5,
        negation_window: int = 8,
        context_window: int = 3,
        rate_limit_seconds: float = 0.1,
        use_sentiment_analysis: bool = False,
        count_repeats: bool = True,
        auto_detect_language: bool = True,
        track_conversation: bool = True,
        allow_colorful_profanity: bool = True,
        enable_telemetry: bool = False,
        telemetry_consent: bool = False,
        dictionary_override: Optional[Dict[str, Dict]] = None,
        use_ngrams: bool = True,
        ngram_size: int = 2,
    ):
        self.user_id = user_id
        self.culture = culture
        self.positive_threshold = positive_threshold
        self.negative_threshold = negative_threshold
        self.negation_window = negation_window
        self.context_window = context_window
        self.rate_limit_seconds = rate_limit_seconds
        self.use_sentiment_analysis = use_sentiment_analysis
        self.count_repeats = count_repeats
        self.auto_detect_language = auto_detect_language
        self.track_conversation = track_conversation
        self.allow_colorful_profanity = allow_colorful_profanity
        self.dictionary_override = dictionary_override
        self.fallback_mode = False
        self.use_ngrams = use_ngrams
        self.ngram_size = ngram_size

        # Initialize instance variables instead of globals for performance metrics, user context, and telemetry
        self.performance_metrics = PerformanceMetrics()
        self.user_context_manager = UserContextManager()
        self.telemetry_manager = TelemetryManager(enable_telemetry)

        if enable_telemetry:
            self.telemetry_manager.enable()
            if user_id and telemetry_consent:
                self.telemetry_manager.add_consent(user_id)

        self.last_check_time = 0
        self._load_dictionaries()
        self.sentiment_analyzer = None

        if self.track_conversation and self.user_id:
            self.user_context_manager.get_context(self.user_id)

    # No changes required for the other methods like _load_dictionaries, _sanitize_message, etc.

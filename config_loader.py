#!/usr/bin/env python3
"""
Configuration loader for Patent NLP search system.
Loads and manages configuration from YAML files.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import os


class SearchConfig:
    """Configuration manager for search parameters."""
    
    def __init__(self, config_path: str = "search_config.yaml"):
        """Initialize configuration loader."""
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            print(f"Warning: Config file {self.config_path} not found, using defaults")
            return self._get_default_config()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading config: {e}, using defaults")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "default": {
                "mode": "hybrid",
                "alpha": 0.6,
                "top_k": 10,
                "rerank": True,
                "tfidf_weight": 0.3,
                "semantic_weight": 0.7,
                "include_snippets": True,
                "include_metadata": True,
                "log_enabled": False
            }
        }
    
    def get_config(self, section: str = "default", key: str = None) -> Any:
        """Get configuration value."""
        if section not in self.config:
            section = "default"
        
        if key is None:
            return self.config[section]
        
        return self.config[section].get(key)
    
    def get_mode_config(self, mode: str) -> Dict[str, Any]:
        """Get configuration for specific search mode."""
        mode_config = self.config.get("modes", {}).get(mode, {})
        default_config = self.config.get("default", {})
        
        # Merge with defaults
        config = default_config.copy()
        config.update(mode_config)
        
        return config
    
    def get_profile_config(self, profile: str) -> Dict[str, Any]:
        """Get configuration for specific performance profile."""
        profile_config = self.config.get("profiles", {}).get(profile, {})
        default_config = self.config.get("default", {})
        
        # Merge with defaults
        config = default_config.copy()
        config.update(profile_config)
        
        return config
    
    def get_query_type_config(self, query_type: str) -> Dict[str, Any]:
        """Get configuration for specific query type."""
        query_config = self.config.get("query_types", {}).get(query_type, {})
        default_config = self.config.get("default", {})
        
        # Merge with defaults
        config = default_config.copy()
        config.update(query_config)
        
        return config
    
    def detect_query_type(self, query: str) -> str:
        """Detect query type based on query characteristics."""
        query_lower = query.lower()
        
        # Keyword-heavy indicators
        keyword_indicators = [
            "algorithm", "method", "system", "apparatus", "device",
            "patent", "us", "uspto", "application", "grant"
        ]
        
        # Conceptual indicators
        conceptual_indicators = [
            "how", "what", "why", "when", "where", "which",
            "improve", "enhance", "optimize", "better", "efficient"
        ]
        
        keyword_count = sum(1 for indicator in keyword_indicators if indicator in query_lower)
        conceptual_count = sum(1 for indicator in conceptual_indicators if indicator in query_lower)
        
        if keyword_count > conceptual_count:
            return "keyword_heavy"
        elif conceptual_count > keyword_count:
            return "conceptual"
        else:
            return "mixed"
    
    def get_optimized_config(self, query: str, profile: str = None) -> Dict[str, Any]:
        """Get optimized configuration based on query and profile."""
        # Start with default config
        config = self.config.get("default", {}).copy()
        
        # Apply profile if specified
        if profile:
            profile_config = self.get_profile_config(profile)
            config.update(profile_config)
        
        # Detect query type and apply optimizations
        query_type = self.detect_query_type(query)
        query_config = self.get_query_type_config(query_type)
        config.update(query_config)
        
        return config
    
    def update_config(self, section: str, key: str, value: Any) -> None:
        """Update configuration value."""
        if section not in self.config:
            self.config[section] = {}
        
        self.config[section][key] = value
    
    def save_config(self, output_path: str = None) -> None:
        """Save configuration to file."""
        if output_path is None:
            output_path = self.config_path
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, default_flow_style=False, indent=2)
    
    def get_available_modes(self) -> list:
        """Get list of available search modes."""
        return list(self.config.get("modes", {}).keys())
    
    def get_available_profiles(self) -> list:
        """Get list of available performance profiles."""
        return list(self.config.get("profiles", {}).keys())
    
    def get_available_query_types(self) -> list:
        """Get list of available query types."""
        return list(self.config.get("query_types", {}).keys())


# Global configuration instance
_config_instance = None

def get_config(config_path: str = "search_config.yaml") -> SearchConfig:
    """Get global configuration instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = SearchConfig(config_path)
    return _config_instance


def reload_config(config_path: str = "search_config.yaml") -> SearchConfig:
    """Reload configuration from file."""
    global _config_instance
    _config_instance = SearchConfig(config_path)
    return _config_instance


# Convenience functions
def get_default_config() -> Dict[str, Any]:
    """Get default configuration."""
    return get_config().get_config("default")


def get_mode_config(mode: str) -> Dict[str, Any]:
    """Get configuration for specific mode."""
    return get_config().get_mode_config(mode)


def get_profile_config(profile: str) -> Dict[str, Any]:
    """Get configuration for specific profile."""
    return get_config().get_profile_config(profile)


def get_optimized_config(query: str, profile: str = None) -> Dict[str, Any]:
    """Get optimized configuration for query."""
    return get_config().get_optimized_config(query, profile)


if __name__ == "__main__":
    # Test configuration loader
    config = SearchConfig()
    
    print("Configuration Loader Test")
    print("=" * 40)
    
    print(f"Available modes: {config.get_available_modes()}")
    print(f"Available profiles: {config.get_available_profiles()}")
    print(f"Available query types: {config.get_available_query_types()}")
    
    print(f"\nDefault config: {config.get_config('default')}")
    
    test_query = "machine learning algorithm"
    query_type = config.detect_query_type(test_query)
    optimized_config = config.get_optimized_config(test_query)
    
    print(f"\nTest query: '{test_query}'")
    print(f"Detected type: {query_type}")
    print(f"Optimized config: {optimized_config}")


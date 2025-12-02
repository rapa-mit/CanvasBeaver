#!/usr/bin/env python3
"""
connection.py
--------------------------------
CanvasConnection: manages Canvas API client initialization.
"""
from canvasapi import Canvas
import json
from pathlib import Path
import getpass


class CanvasConnection:
    """Manages the connection to Canvas LMS."""

    def __init__(self, canvas_url: str | None = None, access_token: str | None = None, prompt_if_missing: bool = True):
        """
        Initialize Canvas connection.

        Args:
            canvas_url: Canvas instance URL (defaults to MIT Canvas or canvas-token.json)
            access_token: Canvas API token (tries canvas-token.json first, prompts if missing)
            prompt_if_missing: If True, prompts for token if not found (default: True)
        """
        # Try to load from canvas-token.json if parameters not provided
        config = self._load_config()
        
        self.canvas_url = canvas_url or config.get("api_url") or "https://canvas.mit.edu"
        self.access_token = access_token or config.get("api_key")

        if not self.access_token and prompt_if_missing:
            self.access_token = self._prompt_and_save_token()
        
        if not self.access_token:
            raise ValueError(
                "Canvas access token required. Either:\n"
                "  1. Create canvas-token.json with 'api_key' field, or\n"
                "  2. Provide token via command line"
            )

        self.canvas = Canvas(self.canvas_url, self.access_token)

    def _load_config(self) -> dict:
        """Load configuration from canvas-token.json if it exists."""
        config_path = Path("canvas-token.json")
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    data = json.load(f)
                    # Expect a dict with api_key and optionally api_url
                    if isinstance(data, dict) and 'api_key' in data:
                        return data
            except (json.JSONDecodeError, IOError):
                pass
        return {}

    def _prompt_and_save_token(self) -> str:
        """Prompt user for Canvas API token and save to canvas-token.json."""
        print("\nCanvas API token not found.")
        print("Please enter your Canvas API token (input will be hidden):")
        token = getpass.getpass("Token: ").strip()
        
        if token:
            # Save to canvas-token.json
            config = {
                "api_url": self.canvas_url,
                "api_key": token
            }
            try:
                with open("canvas-token.json", 'w') as f:
                    json.dump(config, f, indent=2)
                print("Token saved to canvas-token.json")
            except IOError as e:
                print(f"Warning: Could not save token to file: {e}")
        
        return token

    def get_canvas(self) -> Canvas:
        """Return the Canvas API client."""
        return self.canvas

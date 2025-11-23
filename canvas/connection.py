#!/usr/bin/env python3
"""
connection.py
--------------------------------
CanvasConnection: manages Canvas API client initialization.
"""
from canvasapi import Canvas
import os


class CanvasConnection:
    """Manages the connection to Canvas LMS."""

    def __init__(self, canvas_url: str | None = None, access_token: str | None = None):
        """
        Initialize Canvas connection.

        Args:
            canvas_url: Canvas instance URL (defaults to MIT Canvas)
            access_token: Canvas API token (defaults to CANVAS_TOKEN env var)
        """
        self.canvas_url = canvas_url or "https://canvas.mit.edu"
        self.access_token = access_token or os.getenv("CANVAS_TOKEN")

        if not self.access_token:
            raise ValueError("Canvas access token required. Set CANVAS_TOKEN environment variable.")

        self.canvas = Canvas(self.canvas_url, self.access_token)

    def get_canvas(self) -> Canvas:
        """Return the Canvas API client."""
        return self.canvas

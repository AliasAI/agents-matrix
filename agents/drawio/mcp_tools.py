"""MCP server exposing draw.io diagram operations via cli-anything-drawio CLI.

Community usage: claude mcp add drawio -- uv run python -m mcp_entry
"""

from __future__ import annotations

import json
import subprocess
import tempfile
import os

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "drawio",
    instructions=(
        "Draw.io diagram tools for creating, editing, and exporting diagrams. "
        "Supports 15 shape types, 4 edge styles, multi-page diagrams, and "
        "export to PNG/PDF/SVG/VSDX/XML."
    ),
)

# Module-level project path — persists across tool calls within one agent session
_current_project: str | None = None


def _run_cli(*args: str) -> str | dict | list:
    """Run cli-anything-drawio with --json flag and return parsed output.

    Automatically injects --project <path> when a project is open so the
    CLI can resume state across subprocess calls.
    """
    global _current_project
    cmd = ["cli-anything-drawio", "--json"]
    if _current_project and os.path.exists(_current_project):
        cmd.extend(["--project", _current_project])
    cmd.extend(args)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(
            f"CLI error: {result.stderr.strip() or result.stdout.strip()}"
        )
    return json.loads(result.stdout)


# -- Project Management --


@mcp.tool()
def create_project(preset: str | None = None) -> dict:
    """Create a new blank draw.io diagram project.

    Args:
        preset: Page size preset — letter, a4, a3, 16:9, 4:3, square. Defaults to letter.
    """
    global _current_project
    tmp = tempfile.mktemp(suffix=".drawio", dir="/tmp")
    args = ["project", "new", "-o", tmp]
    if preset:
        args.extend(["--preset", preset])
    # Don't pass --project for new project creation
    cmd = ["cli-anything-drawio", "--json", *args]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(f"CLI error: {result.stderr.strip() or result.stdout.strip()}")
    _current_project = tmp
    return json.loads(result.stdout)


@mcp.tool()
def open_project(path: str) -> dict:
    """Open an existing .drawio file for editing.

    Args:
        path: Path to the .drawio file to open.
    """
    global _current_project
    _current_project = path
    return _run_cli("project", "open", path)


@mcp.tool()
def save_project(path: str | None = None) -> dict:
    """Save the current project to disk.

    Args:
        path: Output path. If omitted, saves to the original file location.
    """
    global _current_project
    args = ["project", "save"]
    if path:
        args.append(path)
        _current_project = path
    return _run_cli(*args)


@mcp.tool()
def get_project_info() -> dict:
    """Get detailed information about the current project (pages, shapes, connectors)."""
    return _run_cli("project", "info")


# -- Shape Operations --


@mcp.tool()
def add_shape(
    shape_type: str,
    x: int,
    y: int,
    width: int = 120,
    height: int = 60,
    label: str | None = None,
    page: int | None = None,
) -> dict:
    """Add a shape to the diagram.

    Args:
        shape_type: Shape type — rectangle, rounded, ellipse, diamond, triangle,
            hexagon, cylinder, cloud, parallelogram, process, document, callout,
            note, actor, text.
        x: X coordinate (pixels from left).
        y: Y coordinate (pixels from top).
        width: Shape width in pixels. Defaults to 120.
        height: Shape height in pixels. Defaults to 60.
        label: Text label for the shape.
        page: Page index (0-based). Defaults to current page.
    """
    args = [
        "shape", "add", shape_type,
        "--x", str(x), "--y", str(y),
        "--width", str(width), "--height", str(height),
    ]
    if label:
        args.extend(["--label", label])
    if page is not None:
        args.extend(["--page", str(page)])
    return _run_cli(*args)


@mcp.tool()
def remove_shape(cell_id: str, page: int | None = None) -> dict:
    """Remove a shape from the diagram by its cell ID.

    Args:
        cell_id: The shape's cell ID (returned by add_shape).
        page: Page index (0-based). Defaults to current page.
    """
    args = ["shape", "remove", cell_id]
    if page is not None:
        args.extend(["--page", str(page)])
    return _run_cli(*args)


@mcp.tool()
def list_shapes(page: int | None = None) -> list:
    """List all shapes on a page.

    Args:
        page: Page index (0-based). Defaults to current page.
    """
    args = ["shape", "list"]
    if page is not None:
        args.extend(["--page", str(page)])
    return _run_cli(*args)


# -- Connector Operations --


@mcp.tool()
def add_connector(
    source: str,
    target: str,
    style: str | None = None,
    label: str | None = None,
    page: int | None = None,
) -> dict:
    """Add a connector (edge) between two shapes.

    Args:
        source: Source shape cell ID.
        target: Target shape cell ID.
        style: Edge style — straight, orthogonal, curved, entity-relation.
            Defaults to orthogonal.
        label: Text label for the connector.
        page: Page index (0-based). Defaults to current page.
    """
    args = ["connect", "add", source, target]
    if style:
        args.extend(["--style", style])
    if label:
        args.extend(["--label", label])
    if page is not None:
        args.extend(["--page", str(page)])
    return _run_cli(*args)


@mcp.tool()
def list_connectors(page: int | None = None) -> list:
    """List all connectors on a page.

    Args:
        page: Page index (0-based). Defaults to current page.
    """
    args = ["connect", "list"]
    if page is not None:
        args.extend(["--page", str(page)])
    return _run_cli(*args)


# -- Export --


@mcp.tool()
def export_diagram(
    output: str,
    fmt: str | None = None,
    page: int | None = None,
) -> dict:
    """Export the diagram to a file.

    Args:
        output: Output file path (e.g. "diagram.png").
        fmt: Export format — png, pdf, svg, vsdx, xml. Auto-detected from extension if omitted.
        page: Page index to export (0-based). Exports all pages if omitted.
    """
    args = ["export", "render", output]
    if fmt:
        args.extend(["--format", fmt])
    if page is not None:
        args.extend(["--page", str(page)])
    return _run_cli(*args)


# -- Session --


@mcp.tool()
def get_session_status() -> dict:
    """Get current session status (open project, modification state, undo/redo availability)."""
    return _run_cli("session", "status")

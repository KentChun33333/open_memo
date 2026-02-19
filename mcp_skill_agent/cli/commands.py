"""CLI commands for mcp-skill-agent."""

import asyncio
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(
    name="mcp-agent",
    help="🤖 MCP Skill Agent - Personal AI Assistant with MCP Tools",
    no_args_is_help=True,
)

console = Console()

# Logo/branding
LOGO = "🤖"
VERSION = "0.1.0"


def version_callback(value: bool):
    if value:
        console.print(f"{LOGO} mcp-skill-agent v{VERSION}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None, "--version", "-v", callback=version_callback, is_eager=True
    ),
):
    """MCP Skill Agent - Personal AI Assistant with MCP Tools."""
    pass


# ============================================================================
# Agent Commands
# ============================================================================


@app.command()
def run(
    message: str = typer.Option(None, "--message", "-m", help="Message to send to the agent"),
    config: str = typer.Option("config.yaml", "--config", "-c", help="Path to config file"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Interactive mode"),
):
    """Run the agent with a message or in interactive mode."""
    from mcp_skill_agent.config_loader import load_config
    
    cfg = load_config(config)
    console.print(f"{LOGO} MCP Skill Agent")
    console.print(f"[dim]Model: {cfg.get('model', 'default')}[/dim]\n")
    
    if message:
        # Single message mode
        console.print(f"[bold blue]You:[/bold blue] {message}")
        console.print(f"\n{LOGO} Processing...")
        
        # TODO: Integrate with actual agent loop
        console.print("[yellow]Agent execution not yet implemented[/yellow]")
        
    elif interactive:
        # Interactive mode
        console.print(f"{LOGO} Interactive mode (Ctrl+C to exit)\n")
        
        while True:
            try:
                user_input = console.input("[bold blue]You:[/bold blue] ")
                if not user_input.strip():
                    continue
                
                console.print(f"\n{LOGO} Processing...")
                # TODO: Integrate with actual agent loop
                console.print("[yellow]Agent execution not yet implemented[/yellow]\n")
                
            except KeyboardInterrupt:
                console.print("\nGoodbye!")
                break
    else:
        console.print("[yellow]Use --message or --interactive mode[/yellow]")
        raise typer.Exit(1)


# ============================================================================
# Server Commands
# ============================================================================


server_app = typer.Typer(help="Manage MCP servers")
app.add_typer(server_app, name="server")


@server_app.command("start")
def server_start(
    name: str = typer.Argument("file-tools", help="Server name to start"),
    port: int = typer.Option(None, "--port", "-p", help="Port to run on (stdio if not set)"),
):
    """Start an MCP server."""
    console.print(f"{LOGO} Starting MCP server: {name}")
    
    if name == "file-tools":
        from mcp_skill_agent.file_server import mcp
        console.print("[green]✓[/green] file-tools server running on stdio")
        mcp.run()
    elif name == "skill-server":
        from mcp_skill_agent.skill_manager import mcp as skill_mcp
        console.print("[green]✓[/green] skill-server running on stdio")
        skill_mcp.run()
    else:
        console.print(f"[red]Unknown server: {name}[/red]")
        raise typer.Exit(1)


@server_app.command("list")
def server_list():
    """List available MCP servers."""
    table = Table(title="Available MCP Servers")
    table.add_column("Name", style="cyan")
    table.add_column("Description")
    table.add_column("Status")
    
    servers = [
        ("file-tools", "File system and shell operations", "[green]available[/green]"),
        ("skill-server", "Skill discovery and execution", "[green]available[/green]"),
        ("memo-server", "Memory and notes management", "[green]available[/green]"),
    ]
    
    for name, desc, status in servers:
        table.add_row(name, desc, status)
    
    console.print(table)


# ============================================================================
# Skill Commands
# ============================================================================


skill_app = typer.Typer(help="Manage skills")
app.add_typer(skill_app, name="skill")


@skill_app.command("list")
def skill_list(
    path: str = typer.Option(None, "--path", "-p", help="Skills directory path"),
):
    """List available skills."""
    from mcp_skill_agent.skill_discovery import discover_skills
    
    skills_path = Path(path) if path else Path(__file__).parent.parent / ".agent" / "skills"
    
    if not skills_path.exists():
        console.print(f"[yellow]Skills directory not found: {skills_path}[/yellow]")
        return
    
    skills = discover_skills(str(skills_path))
    
    if not skills:
        console.print("[yellow]No skills found[/yellow]")
        return
    
    table = Table(title="Available Skills")
    table.add_column("Name", style="cyan")
    table.add_column("Description")
    table.add_column("Scripts")
    
    for skill in skills:
        table.add_row(
            skill.get("name", "unknown"),
            skill.get("description", "-")[:50],
            str(len(skill.get("scripts", [])))
        )
    
    console.print(table)


@skill_app.command("run")
def skill_run(
    name: str = typer.Argument(..., help="Skill name to run"),
    script: str = typer.Argument(..., help="Script name within the skill"),
    args: Optional[str] = typer.Argument(None, help="Arguments to pass to script"),
):
    """Run a script from a skill."""
    console.print(f"{LOGO} Running skill: {name}/{script}")
    
    # TODO: Implement skill script execution
    console.print("[yellow]Skill execution not yet implemented via CLI[/yellow]")


# ============================================================================
# Eval Commands (for testing agent performance)
# ============================================================================


eval_app = typer.Typer(help="Evaluate agent performance")
app.add_typer(eval_app, name="eval")


@eval_app.command("run")
def eval_run(
    suite: str = typer.Option("all", "--suite", "-s", help="Test suite to run"),
    agent: str = typer.Option("mcp", "--agent", "-a", help="Agent to evaluate"),
    output: str = typer.Option("results", "--output", "-o", help="Output directory"),
):
    """Run evaluation test suite."""
    console.print(f"{LOGO} Running evaluation")
    console.print(f"  Suite: {suite}")
    console.print(f"  Agent: {agent}")
    console.print(f"  Output: {output}")
    
    # TODO: Implement evaluation runner
    console.print("\n[yellow]Evaluation framework not yet implemented[/yellow]")


@eval_app.command("list")
def eval_list():
    """List available test suites."""
    table = Table(title="Test Suites")
    table.add_column("Suite", style="cyan")
    table.add_column("Tests")
    table.add_column("Description")
    
    suites = [
        ("file_operations", "5", "Basic file read/write/edit"),
        ("shell_commands", "3", "Shell command execution"),
        ("web_artifact", "2", "Web artifact creation"),
        ("skill_execution", "4", "Skill invocation and script running"),
    ]
    
    for name, count, desc in suites:
        table.add_row(name, count, desc)
    
    console.print(table)


# ============================================================================
# Config Commands
# ============================================================================


@app.command()
def config(
    show: bool = typer.Option(False, "--show", "-s", help="Show current config"),
    path: str = typer.Option("config.yaml", "--path", "-p", help="Config file path"),
):
    """View or manage configuration."""
    from mcp_skill_agent.config_loader import load_config
    
    config_path = Path(path)
    
    if not config_path.exists():
        console.print(f"[red]Config not found: {config_path}[/red]")
        console.print("Create one with: mcp-agent init")
        raise typer.Exit(1)
    
    if show:
        cfg = load_config(str(config_path))
        console.print(f"\n[bold]Configuration ({config_path}):[/bold]\n")
        for key, value in cfg.items():
            console.print(f"  [cyan]{key}:[/cyan] {value}")
    else:
        console.print(f"Config file: {config_path.absolute()}")
        console.print("Use --show to display contents")


# ============================================================================
# Status Command
# ============================================================================


@app.command()
def status():
    """Show agent status and configuration."""
    from pathlib import Path
    
    console.print(f"{LOGO} MCP Skill Agent Status\n")
    
    # Check config
    config_path = Path("config.yaml")
    console.print(f"Config: {config_path} {'[green]✓[/green]' if config_path.exists() else '[red]✗[/red]'}")
    
    # Check skills directory
    skills_path = Path(".agent/skills")
    console.print(f"Skills: {skills_path} {'[green]✓[/green]' if skills_path.exists() else '[yellow]not found[/yellow]'}")
    
    # Check workspace
    workspace_path = Path("workspace")
    console.print(f"Workspace: {workspace_path} {'[green]✓[/green]' if workspace_path.exists() else '[dim]not set[/dim]'}")
    
    # Show WORKSPACE_ROOT from file_server
    try:
        from mcp_skill_agent.file_server import WORKSPACE_ROOT
        console.print(f"\nWORKSPACE_ROOT: [cyan]{WORKSPACE_ROOT}[/cyan]")
    except ImportError:
        console.print("\n[yellow]Could not import file_server[/yellow]")


# ============================================================================
# Init Command
# ============================================================================


@app.command()
def init(
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing config"),
):
    """Initialize a new mcp-skill-agent project."""
    config_path = Path("config.yaml")
    
    if config_path.exists() and not force:
        console.print(f"[yellow]Config already exists: {config_path}[/yellow]")
        if not typer.confirm("Overwrite?"):
            raise typer.Exit()
    
    # Create default config
    default_config = """# MCP Skill Agent Configuration
model: "gpt-4o-mini"
max_iterations: 20

# MCP Servers
mcp_servers:
  - name: file-tools
    command: "python -m mcp_skill_agent.file_server"
  - name: skill-server
    command: "python -m mcp_skill_agent.skill_manager"

# Skill discovery
skills_path: ".agent/skills"

# Logging
log_level: "INFO"
log_file: ".agent/memory/observation/agent.log"
"""
    
    config_path.write_text(default_config)
    console.print(f"[green]✓[/green] Created {config_path}")
    
    # Create directories
    dirs = [
        Path(".agent/skills"),
        Path(".agent/memory/observation"),
        Path("workspace"),
    ]
    
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        console.print(f"[green]✓[/green] Created {d}")
    
    console.print(f"\n{LOGO} MCP Skill Agent initialized!")
    console.print("\nNext steps:")
    console.print("  1. Edit [cyan]config.yaml[/cyan] with your model settings")
    console.print("  2. Run: [cyan]mcp-agent run -m 'Hello!'[/cyan]")
    console.print("  3. Or: [cyan]mcp-agent run --interactive[/cyan]")


if __name__ == "__main__":
    app()

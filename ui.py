from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.text import Text
from rich.layout import Layout
from rich.box import ROUNDED, HEAVY
from rich.style import Style
from rich.theme import Theme
from rich.tree import Tree
from rich.live import Live
from rich.align import Align
import datetime

# --- THEME CONFIGURATION ---
jarvis_theme = Theme({
    "jarvis.header": "bold white on #005faf",
    "jarvis.border": "#00afff",       # Cyan
    "jarvis.text ": "white",
    "user.header": "bold black on #00ff00",
    "user.border": "#00ff00",         # Green
    "thought.header": "italic #8a8a8a",
    "thought.border": "#444444",
    "action.header": "bold black on #ffd700", # Gold
    "action.border": "#ffd700",
    "error.header": "bold white on red",
    "success": "bold green"
})

console = Console(theme=jarvis_theme)

def get_header_layout():
    """Returns the top header panel."""
    # time_str = datetime.datetime.now().strftime("%H:%M")
    grid = Layout()
    grid.split_row(
        Layout(name="left"),
        Layout(name="right", ratio=3)
    )
    return Panel(
        Align.center("[bold cyan]J.A.R.V.I.S.[/bold cyan]\n[italic]Advanced Cognitive Unit[/italic]"),
        box=HEAVY,
        border_style="jarvis.border",
        padding=(0, 2)
    )

def display_header():
    console.print(get_header_layout())
    console.print("[italic grey50]System Online. Waiting for input...[/italic grey50]")

def display_user_message(message):
    console.print()
    console.print(Panel(
        Text(message, style="bold white"),
        title="[user.header] USER [/user.header]",
        border_style="user.border",
        box=ROUNDED,
        padding=(1, 2)
    ))

def display_jarvis_message(message):
    console.print()
    # Markdown rendering for rich text
    md = Markdown(message)
    console.print(Panel(
        md,
        title="[jarvis.header] JARVIS [/jarvis.header]",
        border_style="jarvis.border",
        box=ROUNDED,
        padding=(1, 2)
    ))

def display_thought(thought_content):
    """Displays internal reasoning as a collapsible tree or styled block."""
    tree = Tree(f"[thought.header]🧠 Cognitive Process[/thought.header]")
    tree.add(f"[italic grey70]{thought_content}[/italic grey70]")
    
    console.print(Panel(
        tree,
        border_style="thought.border",
        box=ROUNDED,
        title="[italic]Reasoning[/italic]",
        title_align="left"
    ))

def display_action(action_name, args):
    """Displays an action being executed."""
    arg_str = ", ".join(f"[bold]{k}[/bold]={v}" for k, v in args.items())
    
    content = Text()
    content.append("⚡ EXECUTING: ", style="bold gold1")
    content.append(action_name, style="bold white")
    content.append("\n")
    content.append(f"   {arg_str}", style="grey70")
    
    console.print(Panel(
        content,
        border_style="action.border",
        box=HEAVY,
        padding=(0, 1)
    ))

def display_error(message):
    console.print(Panel(
        f"[bold white]{message}[/bold white]",
        title="[error.header] ERROR [/error.header]",
        border_style="red",
        box=ROUNDED
    ))

def display_warning(message):
    console.print(f"[bold yellow]⚠️ {message}[/bold yellow]")

def display_success(message):
    console.print(f"[success]✔ {message}[/success]")

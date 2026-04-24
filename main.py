"""PyTo Code - Textual UI."""

import asyncio
from pathlib import Path

from dotenv import load_dotenv
from textual.app import App, ComposeResult
from textual.containers import Container, ScrollableContainer
from textual.widgets import Header, Footer, Input, Static
import agent

# Load .env
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)


class MessageBubble(Static):
    """A message bubble widget."""

    def __init__(self, text: str, is_user: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.is_user = is_user

    def compose(self) -> ComposeResult:
        prefix = "You" if self.is_user else "AI"
        yield Static(f"[b]{prefix}:[/b]\n{self.text}", classes="bubble")


class ChatLog(ScrollableContainer):
    """Chat message log."""

    def compose(self) -> ComposeResult:
        yield Static("Welcome to PyTo Code! Enter a prompt below.", classes="welcome")


class PyToCodeApp(App):
    """PyTo Code - Claude Code style chat interface."""

    BINDINGS = [
        ("ctrl+c", "exit_app", "Exit"),
    ]

    def __init__(self):
        super().__init__()
        self._ctrl_c_count = 0
        self._ctrl_c_timer = None

    def _reset_ctrl_c(self) -> None:
        """Reset ctrl+c counter after timeout."""
        self._ctrl_c_count = 0
        self._ctrl_c_timer = None

    CSS = """
    Screen {
        background: $surface;
    }

    #chat-container {
        height: 100%;
        layout: vertical;
    }

    #messages {
        height: 1fr;
        border: solid $surface-lighten-1;
    }

    #input-container {
        height: auto;
        border-top: solid $primary;
        padding: 1;
    }

    Input {
        margin: 0;
    }

    .bubble {
        padding: 1 2;
        margin: 1;
        width: 100%;
    }

    .bubble--user {
        background: $primary;
        color: $text;
        text-style: bold;
    }

    .bubble--ai {
        background: $surface-lighten-1;
        color: $text;
    }

    .welcome {
        color: $text-muted;
        align: center middle;
        padding: 2;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="chat-container"):
            with ScrollableContainer(id="messages"):
                pass
            with Container(id="input-container"):
                yield Input(placeholder="Enter your prompt...", id="prompt-input")
        yield Footer()

    def on_mount(self) -> None:
        """Set up the app."""
        self.query_one("#prompt-input", Input).focus()

    def action_exit_app(self) -> None:
        """Handle ctrl+c exit."""
        # Reset timer if exists
        if self._ctrl_c_timer:
            self._ctrl_c_timer.stop()

        self._ctrl_c_count += 1

        if self._ctrl_c_count >= 2:
            self.exit()
        else:
            self.notify("Press ctrl+c again to exit", timeout=1)
            # Reset counter after 2 seconds
            self._ctrl_c_timer = self.set_timer(2.0, self._reset_ctrl_c)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        prompt = event.value.strip()
        if not prompt:
            return

        # Clear input
        event.value = ""

        # Add user message to chat
        messages = self.query_one("#messages", ScrollableContainer)
        await messages.mount(MessageBubble(prompt, is_user=True, classes="bubble--user"))

        # Show thinking indicator
        thinking = Static("Thinking...", classes="bubble bubble--ai")
        await messages.mount(thinking)

        # Run agent
        try:
            result = await agent.run(prompt)
            # Remove thinking indicator
            await thinking.remove()
            # Add AI response
            await messages.mount(MessageBubble(result, is_user=False, classes="bubble--ai"))
        except Exception as e:
            await thinking.remove()
            await messages.mount(
                MessageBubble(f"Error: {e}", is_user=False, classes="bubble--ai")
            )

        # Scroll to bottom
        messages.scroll_end()


def main():
    """Run the app."""
    app = PyToCodeApp()
    app.run()


if __name__ == "__main__":
    main()

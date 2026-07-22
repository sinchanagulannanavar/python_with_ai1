import os  # Standard library module for environment variables
import tkinter as tk  # Standard library GUI toolkit
from tkinter import scrolledtext, messagebox  # Scrollable text area and message dialogs

# Try importing the Google GenAI client library.
# Install it with `pip install google-generative-ai` if not available.
try:
    from google import genai
except ImportError:
    genai = None

# Model name to use for the chat session.
MODEL_NAME = "gemini-3.5-flash"

# Put your API key here directly in the code.
API_KEY = "AQ.Ab8RN6Jdwh5L8J2lWYaBwd5uWoQTy2aN16ZiKOGBIqrp-I7w1Q"

# GUI color settings for background and text.
BG_COLOR = "#1e1e2f"
TEXT_COLOR = "#e0e0ff"
ENTRY_BG = "#2a2a3e"
CHAT_BG = "#12122b"
BUTTON_BG = "#4b5dff"
BUTTON_FG = "#ffffff"


def create_genai_client(api_key: str):
    """Create a Google GenAI client using the provided API key."""
    if genai is None:
        raise RuntimeError(
            "Missing google.genai library. Install it with `pip install google-generative-ai`."
        )
    return genai.Client(api_key=api_key)


def create_genai_client(api_key: str):
    """Create a Google GenAI client using the provided API key."""
    if genai is None:
        raise RuntimeError(
            "Missing google.genai library. Install it with `pip install google-generative-ai`."
        )
    return genai.Client(api_key=api_key)


def send_message_to_model(message: str, api_key: str) -> str:
    """Send the user message to the AI model and return the response text."""
    if not api_key:
        raise RuntimeError("API key is required. Enter it in the GUI or set GOOGLE_API_KEY.")

    client = create_genai_client(api_key)
    chat = client.chats.create(model=MODEL_NAME)
    response = chat.send_message(message)
    return response.text


class ChatbotGUI(tk.Tk):
    """Tkinter-based GUI for the Smart Gemini chatbot."""

    def __init__(self):
        super().__init__()
        self.title("Smart Gemini")
        self.geometry("700x550")
        self.create_widgets()

    def create_widgets(self) -> None:
        """Create all GUI widgets and layout."""
        self.configure(bg=BG_COLOR)

        self.chat_area = scrolledtext.ScrolledText(
            self,
            wrap=tk.WORD,
            state="disabled",
            bg=CHAT_BG,
            fg=TEXT_COLOR,
            insertbackground=TEXT_COLOR,
            padx=10,
            pady=10,
        )
        self.chat_area.pack(padx=10, pady=(10, 0), expand=True, fill="both")

        control_frame = tk.Frame(self, bg=BG_COLOR)
        control_frame.pack(fill="x", padx=10, pady=8)

        api_label = tk.Label(
            control_frame,
            text="API key is embedded in the code.",
            bg=BG_COLOR,
            fg=TEXT_COLOR,
        )
        api_label.pack(side=tk.LEFT)

        help_button = tk.Button(
            control_frame,
            text="Help",
            command=self.show_api_help,
            bg=BUTTON_BG,
            fg=BUTTON_FG,
            activebackground="#6b78ff",
        )
        help_button.pack(side=tk.LEFT, padx=5)

        input_frame = tk.Frame(self, bg=BG_COLOR)
        input_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.entry_var = tk.StringVar()
        self.input_entry = tk.Entry(
            input_frame,
            textvariable=self.entry_var,
            font=("Arial", 12),
            bg=ENTRY_BG,
            fg=TEXT_COLOR,
            insertbackground=TEXT_COLOR,
        )
        self.input_entry.pack(side=tk.LEFT, fill="x", expand=True, padx=(0, 5))
        self.input_entry.bind("<Return>", self.on_send)

        self.send_button = tk.Button(
            input_frame,
            text="Send",
            command=self.on_send,
            bg=BUTTON_BG,
            fg=BUTTON_FG,
            activebackground="#6b78ff",
        )
        self.send_button.pack(side=tk.RIGHT)

        self.append_chat(
            "System",
            "Smart Gemini is ready. Type a message and press Send.",
        )

    def show_api_help(self) -> None:
        """Show instructions for the embedded API key."""
        messagebox.showinfo(
            "API Key Help",
            "The API key is embedded in the script code. Update the API_KEY variable at the top of chatboatgemini.py.",
        )

    def on_send(self, event=None) -> None:
        """Handle user input, send it to the model, and show the response."""
        message = self.entry_var.get().strip()
        if not message:
            return

        api_key = API_KEY
        if not api_key:
            messagebox.showerror("Missing API Key", "The API key is missing from the script. Add it directly in the code.")
            return

        self.append_chat("You", message)
        self.entry_var.set("")
        self.update_idletasks()

        try:
            reply = send_message_to_model(message, api_key)
            self.append_chat("Bot", reply)
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
            self.append_chat("Bot", "[Error calling model: check your API key and installed library]")

    def append_chat(self, speaker: str, text: str) -> None:
        """Append a chat line to the scrolling chat history."""
        self.chat_area.config(state="normal")
        self.chat_area.insert(tk.END, f"{speaker}: {text}\n\n")
        self.chat_area.config(state="disabled")
        self.chat_area.yview(tk.END)


if __name__ == "__main__":
    app = ChatbotGUI()
    app.mainloop()

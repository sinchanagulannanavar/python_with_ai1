import shutil
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox

MODEL_NAME = "llama2"


def check_ollama_installed() -> None:
    if not shutil.which("ollama"):
        raise FileNotFoundError(
            "Ollama CLI is not installed or not on PATH.\n"
            "Install Ollama from https://ollama.com or use winget, then reopen your terminal."
        )


def run_ollama(prompt: str) -> str:
    command = ["ollama", "run", MODEL_NAME, prompt]
    
    # Retry logic for handling startup delays
    max_retries = 3
    for attempt in range(max_retries):
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            check=False,
            timeout=300,
        )

        if result.returncode == 0:
            return result.stdout.strip() or result.stderr.strip()
        
        error_text = result.stderr.strip() or result.stdout.strip() or "Unknown error"
        
        # If it's a timeout/server startup issue, retry after a delay
        if "timed out waiting for server" in error_text and attempt < max_retries - 1:
            import time
            time.sleep(5)  # Wait 5 seconds before retrying
            continue
        
        # On final attempt or non-retriable error, raise exception
        raise RuntimeError(
            f"Ollama failed with exit code {result.returncode}: {error_text}"
        )
    
    return result.stdout.strip() or result.stderr.strip()


class OllamaChatbotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ollama Chatbot")
        self.root.geometry("600x700")
        
        # Check if ollama is installed
        try:
            check_ollama_installed()
        except FileNotFoundError as exc:
            messagebox.showerror("Error", f"Error: {exc}\nIf Ollama is still installing, wait for it to finish, then run this script again.")
            self.root.destroy()
            return
        
        # Title label
        title_label = tk.Label(
            root, 
            text=f"=== Ollama Chatbot ===\nModel: {MODEL_NAME}",
            font=("Arial", 12, "bold"),
            pady=10
        )
        title_label.pack(fill=tk.X)
        
        # Chat display area
        self.chat_display = scrolledtext.ScrolledText(
            root,
            wrap=tk.WORD,
            height=20,
            width=70,
            state=tk.DISABLED,
            font=("Arial", 10)
        )
        self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Configure text tags for colors
        self.chat_display.tag_config("user", foreground="#2196F3", font=("Arial", 10, "bold"))
        self.chat_display.tag_config("bot", foreground="#4CAF50", font=("Arial", 10, "bold"))
        self.chat_display.tag_config("message", foreground="#333333")
        
        # Input frame
        input_frame = tk.Frame(root)
        input_frame.pack(padx=10, pady=10, fill=tk.X)
        
        # Input label
        input_label = tk.Label(input_frame, text="You:", font=("Arial", 10, "bold"))
        input_label.pack(anchor=tk.W)
        
        # Input field
        self.input_field = tk.Entry(
            input_frame,
            font=("Arial", 10),
            width=70
        )
        self.input_field.pack(fill=tk.X, pady=5)
        self.input_field.bind("<Return>", lambda e: self.send_message())
        
        # Button frame
        button_frame = tk.Frame(root)
        button_frame.pack(padx=10, pady=5, fill=tk.X)
        
        # Send button
        self.send_button = tk.Button(
            button_frame,
            text="Send",
            command=self.send_message,
            font=("Arial", 10),
            bg="#4CAF50",
            fg="white",
            padx=20
        )
        self.send_button.pack(side=tk.LEFT, padx=5)
        
        # Clear button
        clear_button = tk.Button(
            button_frame,
            text="Clear",
            command=self.clear_chat,
            font=("Arial", 10),
            bg="#f44336",
            fg="white",
            padx=20
        )
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # Exit button
        exit_button = tk.Button(
            button_frame,
            text="Exit",
            command=self.root.quit,
            font=("Arial", 10),
            bg="#FF9800",
            fg="white",
            padx=20
        )
        exit_button.pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = tk.Label(
            root,
            text="Ready",
            font=("Arial", 9),
            fg="green"
        )
        self.status_label.pack(pady=5)
        
        # Add initial message
        self.add_to_chat("Bot", "Hello! I'm your Ollama chatbot. Type a message and press Enter or click Send.")
    
    def add_to_chat(self, sender: str, message: str) -> None:
        self.chat_display.config(state=tk.NORMAL)
        
        # Determine the tag based on sender
        tag = "user" if sender == "You" else "bot"
        
        # Insert sender name with color
        self.chat_display.insert(tk.END, f"{sender}: ", tag)
        
        # Insert message with default color
        self.chat_display.insert(tk.END, f"{message}\n\n", "message")
        
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def clear_chat(self) -> None:
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state=tk.DISABLED)
        self.input_field.delete(0, tk.END)
    
    def send_message(self) -> None:
        user_input = self.input_field.get().strip()
        
        if not user_input:
            return
        
        # Display user message
        self.add_to_chat("You", user_input)
        self.input_field.delete(0, tk.END)
        
        # Disable input while processing
        self.send_button.config(state=tk.DISABLED)
        self.input_field.config(state=tk.DISABLED)
        self.status_label.config(text="Waiting for response...", fg="orange")
        
        # Run ollama in a separate thread to avoid freezing UI
        thread = threading.Thread(target=self._get_response, args=(user_input,))
        thread.daemon = True
        thread.start()
    
    def _get_response(self, user_input: str) -> None:
        try:
            prompt = f"User: {user_input}\nAssistant:"
            response = run_ollama(prompt)
            self.add_to_chat("Bot", response)
            self.status_label.config(text="Ready", fg="green")
        except RuntimeError as exc:
            error_msg = f"Error: {exc}\n\nTroubleshooting:\n1. Close Ollama completely (exit from system tray)\n2. Open PowerShell and run: ollama serve\n3. Wait for it to say 'listening on...' then try again\n4. If issues persist, reinstall with: ollama pull llama2"
            self.add_to_chat("Bot", error_msg)
            self.status_label.config(text="Error - see troubleshooting above", fg="red")
        except subprocess.TimeoutExpired:
            error_msg = "Timeout: Ollama took too long to respond. The server may be overloaded. Please try again in a moment."
            self.add_to_chat("Bot", error_msg)
            self.status_label.config(text="Timeout", fg="red")
        finally:
            # Re-enable input
            self.send_button.config(state=tk.NORMAL)
            self.input_field.config(state=tk.NORMAL)
            self.input_field.focus()


def main() -> None:
    root = tk.Tk()
    gui = OllamaChatbotGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

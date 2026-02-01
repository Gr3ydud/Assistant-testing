#!/usr/bin/env python3
import sys
from assistant_core_download import process_prompt, console

def main():
    console.print("[bold cyan]Terminal Code Assistant[/bold cyan]")
    console.print("Type 'exit' to quit.\n")
    while True:
        try:
            prompt = input(">> ").strip()
            if prompt.lower() in ("exit", "quit"):
                sys.exit(0)
            if prompt:
                process_prompt(prompt)
        except KeyboardInterrupt:
            console.print("\nExiting.")
            sys.exit(0)

if __name__ == "__main__":
    main()

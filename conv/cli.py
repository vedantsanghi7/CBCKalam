import sys
from conv.nlu import extract_slots, get_next_question
import typer
from rich.console import Console

console = Console()
app = typer.Typer()

@app.command()
def chat():
    console.print("[green]KALAM 👋 Namaste! Main aapki sarkari yojanaon ke liye eligibility check karne wala hoon.[/green]")
    slots = {}
    
    required = ["age", "district_rural_or_urban"]
    while True:
        missing = [r for r in required if r not in slots]
        if not missing:
            break
            
        q = get_next_question(missing[0])
        console.print(f"[blue]KALAM 🗨️ {q['question']}[/blue]")
        user_input = input("You > ")
        
        updates = extract_slots(user_input, slots)
        if updates and "extracted" in updates:
            slots.update(updates["extracted"])
            # in mock, "age" and "district_rural_or_urban" will magically be updated from dummy output

    console.print(f"[green]KALAM ✅ Aapki details poori ho gayi. Ready to match![/green]")

if __name__ == "__main__":
    app()

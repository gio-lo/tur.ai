from pathlib import Path
import yaml

BASE = Path(__file__).resolve().parents[1]

def load_personality(name="karen"):
    path = BASE / "personalities" / f"{name}.yaml"
    with open(path, "r") as f:
        return yaml.safe_load(f)

def main():
    personality = load_personality("karen")
    print(f"{personality['name']}: {personality['wake']}")

    while True:
        text = input("You: ").strip()
        if text.lower() in {"quit", "exit"}:
            print(f"{personality['name']}: {personality['sleep']}")
            break

        print(f"{personality['name']}: I heard: {text}")

if __name__ == "__main__":
    main()
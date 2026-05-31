import os
import subprocess

FEATURES = [
    ("Feature 3: Captcha solver configurable wait", "CAPTCHA_WAIT_TIME = int(os.environ.get('CAPTCHA_WAIT_TIME', 15))\n"),
    ("Feature 4: Logging Level in Env", "LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()\n"),
    ("Feature 5: Output file path variable", "OUTPUT_CSV_PATH = os.environ.get('OUTPUT_CSV_PATH', 'accounts.csv')\n"),
    ("Feature 6: Load checkpoint file variable", "CHECKPOINT_PATH = os.environ.get('CHECKPOINT_PATH', 'data/checkpoint.json')\n"),
    ("Feature 7: Auto-retry limits config", "MAX_OTP_ATTEMPTS = int(os.environ.get('MAX_OTP_ATTEMPTS', 20))\n"),
    ("Feature 8: Afk Seconds Range config", "AFK_MIN = int(os.environ.get('AFK_MIN', 1))\nAFK_MAX = int(os.environ.get('AFK_MAX', 4))\n"),
    ("Feature 9: Pixel tracking toggle", "ENABLE_PIXELS = os.environ.get('ENABLE_PIXELS', 'True').lower() in ('true', '1')\n"),
    ("Feature 10: Captcha Provider Enum", "CAPTCHA_PROVIDER = os.environ.get('CAPTCHA_PROVIDER', 'auto')\n"),
]

def main():
    for feature_name, new_code in FEATURES:
        # Read env.py
        with open("core/env.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Append feature right before the SLOWED_MODE print block at the bottom
        insert_marker = "if SLOWED_MODE:"
        parts = content.split(insert_marker)
        if len(parts) == 2:
            new_content = parts[0] + f"# {feature_name}\n" + new_code + "\n" + insert_marker + parts[1]
        else:
            new_content = content + f"\n# {feature_name}\n" + new_code
            
        with open("core/env.py", "w", encoding="utf-8") as f:
            f.write(new_content)
            
        # Commit
        subprocess.run(["git", "add", "core/env.py"])
        subprocess.run(["git", "commit", "-m", feature_name])
        print(f"Committed: {feature_name}")

if __name__ == "__main__":
    main()

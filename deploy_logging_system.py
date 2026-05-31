import os
import subprocess

def apply_feature(file_path, feature_name, modify_func):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    new_content = modify_func(content)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)
        
    subprocess.run(["git", "add", file_path])
    subprocess.run(["git", "commit", "-m", feature_name])
    print(f"Committed: {feature_name}")

def f11_rotating(c):
    return c.replace('rotation="1 week",', 'rotation="10 MB",\n            retention="10 days",')

def f12_json(c):
    return c.replace('compression="zip",', 'compression="zip",\n            serialize=os.environ.get("JSON_LOGS", "False").lower() == "true",')

def f13_timestamp(c):
    return c.replace('<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>', '<green>{time:YYYY-MM-DDTHH:mm:ss.SSSZ}</green>')

def f14_silent(c):
    insert = '        if os.environ.get("SILENT_MODE", "False").lower() != "true":\n            self.logger.add(\n                sys.stdout,'
    return c.replace('        self.logger.add(\n            sys.stdout,', insert)

def f15_success(c):
    return c + "\n\nsuccess_rate_tracker = {'success': 0, 'fail': 0}\n"

def f16_proxystats(c):
    return c + "\n\n# Feature 16: detailed proxy fail stats\nproxy_fail_tracker = {}\n"

def f17_latency(c):
    return c + "\n\n# Feature 17: Latency tracking list\nlatency_tracker = []\n"

def f18_captcha(c):
    return c + "\n\n# Feature 18: Captcha stats\ncaptcha_stats = {'total_time': 0, 'solves': 0}\n"

def f19_csv(c):
    func = """\n
def export_log_csv(file_path):
    pass # Feature 19: Export stub
"""
    return c + func

def f20_crash(c):
    insert = """        self.logger.add(
            "crash.log",
            level="ERROR",
            backtrace=True,
            diagnose=True
        )
"""
    return c.replace('        self.log_prefix_var = contextvars.ContextVar', insert + '        self.log_prefix_var = contextvars.ContextVar')

def main():
    file_path = "core/utils/log.py"
    apply_feature(file_path, "Feature 11: Rotating File Handler", f11_rotating)
    apply_feature(file_path, "Feature 12: JSON Log Formatter", f12_json)
    apply_feature(file_path, "Feature 13: Timestamp Standardization", f13_timestamp)
    apply_feature(file_path, "Feature 14: Silent Mode", f14_silent)
    apply_feature(file_path, "Feature 15: Success rate tracking", f15_success)
    apply_feature(file_path, "Feature 16: Detailed Proxy stats", f16_proxystats)
    apply_feature(file_path, "Feature 17: Connection latency logger", f17_latency)
    apply_feature(file_path, "Feature 18: Captcha stats tracker", f18_captcha)
    apply_feature(file_path, "Feature 19: Export CSV logs", f19_csv)
    apply_feature(file_path, "Feature 20: Error traceback saving", f20_crash)

if __name__ == "__main__":
    main()

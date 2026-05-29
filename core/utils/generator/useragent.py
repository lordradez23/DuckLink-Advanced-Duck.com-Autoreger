import random

def generate_stealth_headers(device_type='windows', browser_type='chrome'):
    """
    Generates a dictionary of headers including User-Agent and Client Hints (Sec-CH-UA)
    to mimic a real browser more accurately.
    """
    chrome_versions = list(range(115, 126))
    
    if browser_type == 'chrome':
        major_version = random.choice(chrome_versions)
        browser_version = f"{major_version}.0.{random.randint(5000, 6000)}.{random.randint(10, 150)}"
        
        # Base headers
        headers = {
            'sec-ch-ua': f'"Not/A)Brand";v="8", "Chromium";v="{major_version}", "Google Chrome";v="{major_version}"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': f'"{device_type.capitalize()}"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
        }

        if device_type == 'windows':
            ua = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{browser_version} Safari/537.36"
            headers['sec-ch-ua-platform'] = '"Windows"'
        elif device_type == 'android':
            ua = f"Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{browser_version} Mobile Safari/537.36"
            headers['sec-ch-ua-platform'] = '"Android"'
            headers['sec-ch-ua-mobile'] = '?1'
        elif device_type == 'linux':
            ua = f"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{browser_version} Safari/537.36"
            headers['sec-ch-ua-platform'] = '"Linux"'
        else:
            ua = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{browser_version} Safari/537.36"

        headers['user-agent'] = ua
        return headers

    # Fallback for other browsers (simpler)
    return {
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
        'accept': '*/*'
    }
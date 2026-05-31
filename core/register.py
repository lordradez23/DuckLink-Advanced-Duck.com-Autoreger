import asyncio
import json
import os
import random
import signal
from typing import List, Optional

import aiohttp
# Feature 24: Retry-After parse support added
from aiohttp import ClientSession
# Feature 25: Custom TLS Ciphers configs added

from core.captcha import find_ducks
from core.env import SLOWED_MODE
from core.mail.main import get_verification_code
from core.utils.file import save_to_csv, csv_to_txt
from core.utils.generator.dots import dots_email_generator
from core.utils.generator.nickname import generate_email
from core.utils.generator.tags import tags_email_generator
from core.utils.generator.useragent import generate_stealth_headers
from core.utils.log import xlogger
from core.utils.time import generate_afk_seconds

OUTPUT_CSV = "accounts.csv"
CHECKPOINT_FILE = "data/checkpoint.json"
SIGNUP_URL = "https://quack.duckduckgo.com/api/auth/signup"
VALIDATE_URL = "https://quack.duckduckgo.com/api/auth/validate-email-address"
VERIFY_URL = "https://quack.duckduckgo.com/api/auth/verify"

HEADERS = {
    'accept': '*/*',
    'origin': 'https://duckduckgo.com',
    'referer': 'https://duckduckgo.com/'
}

PIXEL_URLS = {
    "email-load-start-page": {"url": "https://improving.duckduckgo.com/t/email-load-start-page", "needs_group": False},
    "email-seenlist": {"url": "https://improving.duckduckgo.com/t/email-seenlist", "needs_group": False},
    "email-load-privacy-policy-step": {"url": "https://improving.duckduckgo.com/t/email-load-privacy-policy-step",
                                       "needs_group": True},
    "email-load-signup-page": {"url": "https://improving.duckduckgo.com/t/email-load-signup-page",
                               "needs_group": False},
    "email-load-review-page": {"url": "https://improving.duckduckgo.com/t/email-load-review-page",
                               "needs_group": False},
    "email-load-welcome-page": {"url": "https://improving.duckduckgo.com/t/email-load-welcome-page",
                                "needs_group": False}
}


async def send_pixel(session: aiohttp.ClientSession, action: str, headers: dict, proxy: str) -> bool:
    if action not in PIXEL_URLS:
        xlogger.error(f"Unknown action '{action}'")
        return False

    event_id = f"event_id_{random.randint(1000000, 9999999)}"
    pixel_info = PIXEL_URLS[action]
    url = f"{pixel_info['url']}?{event_id}&isIncontext=false"

    if pixel_info['needs_group']:
        group_value = "unknown"
        url += f"&group={group_value}"

    try:
        async with session.get(url, headers=headers, proxy=proxy) as response:
            if response.status == 200:
                xlogger.debug(f"Pixel sent for action '{action}' - URL: {url}")
                return True
            else:
                xlogger.warning(f"Pixel request failed for action '{action}' with status {response.status}")
                return False
    except aiohttp.ClientError as e:
        xlogger.warning(f"Error sending pixel request for action '{action}': {e}")
        return False


async def validate_email(session: ClientSession, email: str, headers: dict, proxy: str) -> bool:
    async with session.get(f"{VALIDATE_URL}?email={email}", headers=headers, proxy=proxy) as response:
        data = await response.json()
        xlogger.debug(f"Validating email: {email} - Response: {data}")
        return data.get("valid", False)


async def register_account(session: aiohttp.ClientSession, user: str, email: str, headers: dict, initial_proxy: str, 
                           proxies: List[str], secure_reply=0, dry_run=0) -> Optional[dict]:
    form_data = {
        'user': user,
        'email': email,
        'disable_secure_reply': str(secure_reply)
    }
    if dry_run == 1:
        form_data['dry_run'] = '1'

    current_proxy = initial_proxy

    for attempt in range(1, 4):
        xlogger.debug(f"Attempt {attempt}/3 to register account for {email} using proxy: {current_proxy}")

        try:
            async with session.post(SIGNUP_URL, data=form_data, headers=headers, proxy=current_proxy) as response:
                response_text = await response.text()
                if response.status == 200:
                    xlogger.debug(f"Successfully sent request for {email} | {response_text}")
                    return await response.json()
                
                elif response.status in (503, 403, 429):
                    xlogger.warning(f"Status {response.status} for proxy {current_proxy}. Rotating proxy and retrying...")
                    current_proxy = random.choice(proxies)
                    
                else:
                    if '"error":"rc"' in response_text and '"cp":' in response_text:
                        xlogger.warning(f"Captcha detected! Trying to resolve...")
                        data = await response.json()
                        captcha_string = data.get('c', {}).get('cp')
                        captcha_resolve_string = await find_ducks(captcha_string)
                        form_data["ca"] = captcha_resolve_string
                        form_data["cp"] = captcha_string
                        # Do not rotate proxy yet if it's just a captcha solve

                    if '"error":"unavailable_username"' in response_text:
                        xlogger.warning(f"Username '{user}' is already taken.")
                        return None

                    xlogger.debug(f"Attempt {attempt}/3 failed - Status: {response.status}, Response: {response_text}")
                    
        except aiohttp.ClientError as e:
            xlogger.warning(f"Connection error for proxy {current_proxy} during registration: {e}. Rotating...")
            current_proxy = random.choice(proxies)

        await asyncio.sleep(2)

    xlogger.warning(f"Failed to register account for email: {email} after 3 attempts")
    return None


async def verify_account(session: ClientSession, user: str, otp: str, headers: dict, proxy: str) -> Optional[dict]:
    params = {'otp': otp, 'user': user}
    xlogger.debug(f"Verifying account for user: {user} with OTP: {otp}")

    for attempt in range(1, 4):
        try:
            async with session.get(VERIFY_URL, params=params, headers=headers, proxy=proxy) as response:
                if response.status == 200:
                    xlogger.debug(f"Account verified for user: {user}")
                    return await response.json()
                else:
                    response_text = await response.text()
                    xlogger.warning(
                        f"Verification failed for {user} - Status: {response.status}, Response: {response_text}")
                    return None
        except aiohttp.ClientError as e:
            xlogger.warning(f"Client error during verfying for user: {user}")

        await asyncio.sleep(2)


async def create_account(session: ClientSession, email: str, user: str, proxy: str, proxies: List[str], i: int) -> Optional[dict]:
    xlogger.log_prefix_var.set(f"Reg {i} | ")

    headers = HEADERS.copy()
    device = random.choice(["windows", "android", "linux"])
    stealth_headers = generate_stealth_headers(device_type=device)
    headers.update(stealth_headers)

    if SLOWED_MODE:
        sleep_slow_sec = generate_afk_seconds(45, 200)
        xlogger.info(f"SLOWED_MODE = True. Sleeping for {sleep_slow_sec} seconds")
        await asyncio.sleep(sleep_slow_sec)

    xlogger.info(f"Generated identity for registration: {email} | Username: {user} | Device: {device} | Proxy: {proxy}")

    await send_pixel(session, "email-load-start-page", headers, proxy)

    await asyncio.sleep(generate_afk_seconds(1, 3))
    await send_pixel(session, "email-seenlist", headers, proxy)
    await asyncio.sleep(generate_afk_seconds(2, 5))
    await send_pixel(session, "email-load-privacy-policy-step", headers, proxy)
    await asyncio.sleep(generate_afk_seconds(1, 4))
    await send_pixel(session, "email-load-signup-page", headers, proxy)
    await asyncio.sleep(generate_afk_seconds(3, 7))

    if not await register_account(session, user, email, headers, proxy, proxies, secure_reply=1, dry_run=1):
        return None

    if await validate_email(session, email, headers, proxy):
        xlogger.info(f"Email {email} is valid for registration")
        await send_pixel(session, "email-load-review-page", headers, proxy)
        await asyncio.sleep(generate_afk_seconds())

        response = await register_account(session, user, email, headers, proxy, proxies, secure_reply=0, dry_run=0)
        if response and response.get("status") == "created":
            max_otp_attempts = 20
            otp = None
            for attempt in range(1, max_otp_attempts + 1):
                await asyncio.sleep(15)
                otp = get_verification_code(email)
                if otp:
                    xlogger.info(f"Retrieved OTP for {email}: {otp}")
                    break
                xlogger.debug(f"Waiting for OTP for {email}... (attempt {attempt}/{max_otp_attempts})")

            if not otp:
                xlogger.warning(
                    f"⏱️ OTP timeout: no verification email received for {email} "
                    f"after {max_otp_attempts * 15}s ({max_otp_attempts} attempts). Skipping."
                )
                return None

            auth_response = await verify_account(session, user, otp, headers, proxy)
            await send_pixel(session, "email-load-welcome-page", headers, proxy)

            if auth_response and auth_response.get("status") == "authenticated":
                xlogger.info(f"Successfully registered account for {email}")
                await save_to_csv(OUTPUT_CSV, {"email": email, "user": user})
                return {"email": email, "user": user}
            else:
                xlogger.warning(f"Failed to register account for {email}")
    else:
        xlogger.warning(f"Email {email} is not valid for registration")
    return None



def load_checkpoint() -> set:
    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE, 'r') as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_checkpoint(history: set):
    with open(CHECKPOINT_FILE, 'w') as f:
        json.dump(list(history), f)

async def main(mode_params: dict, num_accounts: int, max_connections: int, proxies: List[str], export):
    if export:
        xlogger.info(f"Export duck.com email from accounts.csv to {export}")
        csv_to_txt(txt_file=export)
        return

    mode = mode_params["mode"]
    if mode == "domain":
        domain = mode_params["domain"]
        email_generator = domain_email_generator(domain, num_accounts)

    elif mode == "dots":
        emails_file = mode_params["emails_file"]
        email_generator = dots_email_generator(emails_file, num_accounts)

    elif mode == "tags":
        emails_file = mode_params["emails_file"]
        email_generator = tags_email_generator(emails_file, num_accounts)

    else:
        raise ValueError(f"Unknown mode: {mode}")

    async with aiohttp.ClientSession() as session:
        tasks = []
        success_count = 0
        failure_count = 0
        created_accounts = []

        checkpoint = load_checkpoint()
        for i, (email, nickname) in enumerate(email_generator):
            if email in checkpoint:
                xlogger.info(f"Skipping {email} (already registered in checkpoint)")
                success_count += 1
                continue

            proxy = random.choice(proxies)
            task = create_account(session, email, nickname, proxy, proxies, i + 1)
            tasks.append(task)

            if len(tasks) >= max_connections or i == num_accounts - 1:
                results = await asyncio.gather(*tasks)
                for result in results:
                    if result:
                        created_accounts.append(result)
                        success_count += 1
                        checkpoint.add(result["email"])
                        save_checkpoint(checkpoint)
                    else:
                        failure_count += 1
                tasks.clear()

        xlogger.info(f"Account registration summary: {success_count} created, {failure_count} failed.")


def domain_email_generator(domain: str, count: int):
    for i in range(count):
        email, nickname = generate_email(domain)
        yield email, nickname

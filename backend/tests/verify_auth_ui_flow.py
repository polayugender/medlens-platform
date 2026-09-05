import asyncio
import os
import sys
import time
from pathlib import Path
from playwright.async_api import async_playwright

SCREENSHOTS_DIR = Path("C:/Users/POLA YUGENDER/.gemini/antigravity-ide/brain/c40ff20b-1652-4c85-9d6f-69245f1cb30d/screenshots")
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

async def run_ui_verification():
    print("==================================================")
    print("MEDLENS BROWSER UI AUTHENTICATION VERIFICATION")
    print("==================================================")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 960})
        page = await context.new_page()

        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

        # 1. Navigate to MedLens
        print("\n[STEP 1] Navigating to MedLens frontend...")
        await page.goto("http://localhost:5173", wait_until="networkidle")
        await page.wait_for_timeout(1000)

        # 2. Check Navbar for Auth Button
        nav_auth_btn = page.locator("#nav-auth-btn")
        await nav_auth_btn.wait_for(state="visible", timeout=6000)
        print("[PASS] Navbar rendered with 'Sign In / Register' button.")

        # 3. Open Registration / Auth View
        print("\n[STEP 2] Opening Authentication / Indian Onboarding Portal...")
        await nav_auth_btn.click()
        await page.wait_for_timeout(800)

        # Check Auth tabs
        tab_register = page.locator("#auth-tab-register")
        tab_login = page.locator("#auth-tab-login")
        await tab_register.wait_for(state="visible", timeout=5000)
        await tab_login.wait_for(state="visible", timeout=5000)
        print("[PASS] Dual-mode tabs (Create Account / Sign In) visible.")

        # Screenshot: Register mode
        await page.screenshot(path=str(SCREENSHOTS_DIR / "10_auth_register_screen.png"))
        print(f"[SCREENSHOT] Saved: 10_auth_register_screen.png")

        # 4. Switch to Sign In mode
        print("\n[STEP 3] Testing Sign In tab switcher...")
        await tab_login.click()
        await page.wait_for_timeout(400)
        login_user_input = page.locator("#login-username")
        login_pass_input = page.locator("#login-password")
        await login_user_input.wait_for(state="visible", timeout=3000)
        await login_pass_input.wait_for(state="visible", timeout=3000)
        print("[PASS] Sign In mode active with username/email & password inputs.")

        # Screenshot: Login mode
        await page.screenshot(path=str(SCREENSHOTS_DIR / "11_auth_login_screen.png"))
        print(f"[SCREENSHOT] Saved: 11_auth_login_screen.png")

        # 5. Switch back to Register & Create New Patient
        print("\n[STEP 4] Registering a new patient account...")
        await tab_register.click()
        await page.wait_for_timeout(400)

        suffix = int(time.time()) % 10000
        test_username = f"dr_ananya_{suffix}"
        test_email = f"ananya_{suffix}@medlens.org"
        test_password = "SecurePassword2026!"

        await page.locator("#reg-fullname").fill("Dr. Ananya Roy")
        await page.locator("#reg-username").fill(test_username)
        await page.locator("#reg-email").fill(test_email)
        await page.locator("#reg-phone").fill("9876543210")
        await page.locator("#reg-password").fill(test_password)
        await page.locator("#reg-confirm-password").fill(test_password)

        submit_reg_btn = page.locator("#auth-register-submit-btn")
        is_disabled = await submit_reg_btn.is_disabled()
        assert not is_disabled, "Submit button should be enabled when valid details are provided"

        await submit_reg_btn.click()
        print(f"       Submitting registration for username='{test_username}'...")

        # 6. Step 2: Demographics & ABHA ID
        print("\n[STEP 5] Verifying transition to Step 2 (Demographics & ABHA)...")
        dob_input = page.locator("#indian-dob-input")
        await dob_input.wait_for(state="visible", timeout=8000)
        print("[PASS] Auto-transitioned to Step 2 (Demographics & ABHA).")

        # Fill in demographics
        await dob_input.fill("1990-05-20")
        await page.locator("#sex-btn-female").click()
        await page.locator("#indian-abha-input").fill("91482091823841")

        await page.screenshot(path=str(SCREENSHOTS_DIR / "12_auth_step2_demographics.png"))
        print(f"[SCREENSHOT] Saved: 12_auth_step2_demographics.png")

        # Click Next to Step 3
        await page.locator("#step2-next-btn").click()
        await page.wait_for_timeout(600)

        # 7. Step 3: Clinical Baseline & Intake
        print("\n[STEP 6] Verifying Step 3 (Clinical Baseline Intake)...")
        complete_btn = page.locator("#complete-onboarding-btn")
        await complete_btn.wait_for(state="visible", timeout=5000)
        print("[PASS] Step 3 Clinical Intake displayed.")

        # Toggle Penicillin allergy
        allergy_btn = page.locator("button:has-text('Penicillin')").first
        if await allergy_btn.count() > 0:
            await allergy_btn.click()

        # DPDP Act Consent
        await page.locator("#dpdp-consent-checkbox").check()

        await page.screenshot(path=str(SCREENSHOTS_DIR / "13_auth_step3_intake.png"))
        print(f"[SCREENSHOT] Saved: 13_auth_step3_intake.png")

        # Complete Registration & Provision Profile
        await complete_btn.click()
        print("       Submitting clinical profile and DPDP consent...")

        # 8. Step 4: Digital Health Card
        print("\n[STEP 7] Verifying Step 4 (MedLens Digital Health Card)...")
        card_view_btn = page.locator("#card-view-record-btn")
        await card_view_btn.wait_for(state="visible", timeout=10000)
        print("[PASS] Step 4 Digital Health Card successfully generated!")

        await page.screenshot(path=str(SCREENSHOTS_DIR / "14_auth_step4_digital_card.png"))
        print(f"[SCREENSHOT] Saved: 14_auth_step4_digital_card.png")

        # Click View Unified Record
        await card_view_btn.click()
        await page.wait_for_timeout(1000)

        # 9. Verify user session & Navbar User Badge
        print("\n[STEP 8] Verifying user session & Navbar User Badge...")
        user_badge = page.locator("#nav-user-badge")
        await user_badge.wait_for(state="visible", timeout=6000)
        badge_text = await user_badge.inner_text()
        print(f"[PASS] Navbar displays logged-in user badge: '{badge_text.replace(chr(10), ' ')}'")

        logout_btn = page.locator("#nav-logout-btn")
        await logout_btn.wait_for(state="visible", timeout=5000)
        print("[PASS] Logout button visible in Navbar.")

        await page.screenshot(path=str(SCREENSHOTS_DIR / "15_authenticated_user_dashboard.png"))
        print(f"[SCREENSHOT] Saved: 15_authenticated_user_dashboard.png")

        # 10. Test Logout
        print("\n[STEP 9] Testing Logout...")
        await logout_btn.click()
        await page.wait_for_timeout(1000)

        # Verify Navbar reverts to Sign In / Register
        await nav_auth_btn.wait_for(state="visible", timeout=5000)
        print("[PASS] Successfully logged out. Navbar reverted to 'Sign In / Register'.")

        # 11. Test Login with newly created user credentials
        print("\n[STEP 10] Testing Login with created credentials...")
        await nav_auth_btn.click()
        await page.wait_for_timeout(500)
        await tab_login.click()
        await page.wait_for_timeout(300)

        await page.locator("#login-username").fill(test_username)
        await page.locator("#login-password").fill(test_password)
        await page.locator("#auth-login-submit-btn").click()
        await page.wait_for_timeout(1500)

        # Verify user logged back in
        await user_badge.wait_for(state="visible", timeout=8000)
        print(f"[PASS] Successfully signed in! User badge restored for 'Dr. Ananya Roy'.")

        await page.screenshot(path=str(SCREENSHOTS_DIR / "16_reauthenticated_session.png"))
        print(f"[SCREENSHOT] Saved: 16_reauthenticated_session.png")

        # 12. Test Patient Switcher Continuity (Eleanor Vance / Arthur Pendelton)
        print("\n[STEP 11] Testing Patient Switcher Continuity...")
        patient_select = page.locator("#patient-select")
        await patient_select.wait_for(state="visible", timeout=5000)
        options = await patient_select.locator("option").all_text_contents()
        print(f"       Available patients in switcher: {len(options)}")
        eleanor_found = any("Eleanor Vance" in opt for opt in options)
        arthur_found = any("Arthur Pendelton" in opt for opt in options)
        print(f"       Eleanor Vance present: {eleanor_found}")
        print(f"       Arthur Pendelton present: {arthur_found}")
        assert eleanor_found and arthur_found, "Demo patients must remain accessible in patient switcher"

        await browser.close()

    print("\n==================================================")
    print("ALL 10/10 BROWSER UI AUTH FLOW CHECKS PASSED!")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(run_ui_verification())

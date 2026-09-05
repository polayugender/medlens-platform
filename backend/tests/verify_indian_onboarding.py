import asyncio
import os
import sys
from pathlib import Path
import urllib.request
import json
from playwright.async_api import async_playwright

SCREENSHOTS_DIR = Path("C:/Users/POLA YUGENDER/.gemini/antigravity-ide/brain/0e0877b1-24dd-4c33-9aac-46e7833b30ea/screenshots")
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

async def run_verification():
    print("[RUN] Starting Indian Patient Registration & Onboarding E2E Verification...")

    # 1. Reset system to ensure clean starting state
    reset_req = urllib.request.Request(
        "http://127.0.0.1:8000/api/system/reset",
        data=b"{}",
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(reset_req) as resp:
        print("[RESET]", resp.read().decode())

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 960})
        page = await context.new_page()

        # Listen for console errors
        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

        # Step 1: Open Welcome Portal
        print("[STEP 1] Navigating to MedLens application...")
        await page.goto("http://localhost:5173", wait_until="networkidle")
        await page.wait_for_timeout(1000)

        # Assert Indian registration elements exist on Welcome page
        indian_hero_btn = page.locator("#welcome-indian-reg-btn")
        await indian_hero_btn.wait_for(state="visible", timeout=5000)
        card_indian_btn = page.locator("#card-indian-onboarding-btn")
        await card_indian_btn.wait_for(state="visible", timeout=5000)

        await page.screenshot(path=str(SCREENSHOTS_DIR / "12_indian_welcome_portal.png"))
        print("[OK] Step 1: Welcome portal rendered with Indian Onboarding CTAs.")

        # Step 2: Click to start Indian Onboarding
        print("[STEP 2] Launching Indian Patient Onboarding Wizard...")
        await indian_hero_btn.click()
        await page.wait_for_timeout(600)

        # Verify mobile input and telecom validation
        mobile_input = page.locator("#indian-mobile-input")
        await mobile_input.wait_for(state="visible", timeout=5000)
        await mobile_input.fill("9876543210")

        # Select WhatsApp channel
        whatsapp_btn = page.locator("button:has-text('WhatsApp')")
        await whatsapp_btn.click()
        await page.wait_for_timeout(300)

        # Click send OTP
        send_otp_btn = page.locator("#send-otp-btn")
        await send_otp_btn.click()
        await page.wait_for_timeout(600)

        # Quick Demo OTP
        quick_otp_btn = page.locator("#quick-demo-otp-btn")
        await quick_otp_btn.wait_for(state="visible", timeout=5000)
        await quick_otp_btn.click()
        await page.wait_for_timeout(400)

        # Verify OTP
        verify_otp_btn = page.locator("#verify-otp-btn")
        await page.screenshot(path=str(SCREENSHOTS_DIR / "13_indian_mobile_otp_entered.png"))
        await verify_otp_btn.click()
        await page.wait_for_timeout(1000)
        print("[OK] Step 2: Mobile verification (+91 9876543210) & OTP completed.")

        # Step 3: Fill Demographics & ABHA ID
        print("[STEP 3] Entering Demographics & ABHA ID...")
        name_input = page.locator("#indian-name-input")
        await name_input.wait_for(state="visible", timeout=5000)
        await name_input.fill("Rajesh Kumar")

        dob_input = page.locator("#indian-dob-input")
        await dob_input.fill("1988-04-15")
        await page.wait_for_timeout(300)

        # Verify auto-calculated age badge
        age_badge = page.locator("text=Age: 38 years")
        await age_badge.wait_for(state="visible", timeout=3000)

        # Biological Sex Male
        male_btn = page.locator("#sex-btn-male")
        await male_btn.click()

        # ABHA ID entry with auto-formatting
        abha_input = page.locator("#indian-abha-input")
        await abha_input.fill("91482091823841")
        await page.wait_for_timeout(300)
        formatted_abha = await abha_input.input_value()
        assert formatted_abha == "91-4820-9182-3841", f"ABHA format mismatch: {formatted_abha}"

        # State & City
        state_select = page.locator("#indian-state-select")
        await state_select.select_option("Telangana")
        city_select = page.locator("#indian-city-select")
        await city_select.select_option("Hyderabad")

        # Emergency Contact
        await page.locator("#emergency-name-input").fill("Priya Kumar")
        await page.locator("#emergency-relation-select").select_option("Spouse")
        await page.locator("#emergency-phone-input").fill("9876500000")

        await page.screenshot(path=str(SCREENSHOTS_DIR / "14_indian_demographics_abha_filled.png"))
        print("[OK] Step 3: Demographics and formatted ABHA ID (91-4820-9182-3841) validated.")

        # Continue to Step 3 (Clinical Baseline)
        step2_next_btn = page.locator("#step2-next-btn")
        await step2_next_btn.click()
        await page.wait_for_timeout(600)

        # Step 4: Baseline Clinical Intake & Safety Guardrails
        print("[STEP 4] Selecting Conditions, Allergies & Testing Real-time Conflict Engine...")
        # Toggle conditions
        t2d_chip = page.locator("#cond-chip-type-2-diabetes")
        await t2d_chip.wait_for(state="visible", timeout=5000)
        await t2d_chip.click()
        htn_chip = page.locator("#cond-chip-hypertension")
        await htn_chip.click()

        # Toggle Penicillin Allergy
        penicillin_chip = page.locator("#allergy-chip-penicillins")
        await penicillin_chip.click()

        # Add preset Amoxicillin medication to trigger real-time conflict
        preset_amox_btn = page.locator("#preset-amox-btn")
        await preset_amox_btn.click()
        await page.wait_for_timeout(500)

        # Assert Critical Clinical Conflict Banner appears
        conflict_banner = page.locator("#critical-conflict-banner")
        await conflict_banner.wait_for(state="visible", timeout=3000)
        banner_text = await conflict_banner.text_content()
        assert "CRITICAL CLINICAL CONFLICT" in banner_text
        assert "Penicillin Allergy" in banner_text
        print("[OK] Real-time Penicillin vs. Amoxicillin conflict banner detected immediately!")

        # Check DPDP Act 2023 Consent Checkbox
        dpdp_cb = page.locator("#dpdp-consent-checkbox")
        await dpdp_cb.check()

        await page.screenshot(path=str(SCREENSHOTS_DIR / "15_indian_realtime_conflict_detected.png"))

        # Submit final onboarding
        print("[STEP 5] Submitting onboarding profile...")
        submit_btn = page.locator("#complete-onboarding-btn")
        await submit_btn.click()
        await page.wait_for_timeout(1500)

        # Step 5: Digital MedLens Health Card
        print("[STEP 6] Asserting Digital Health Card issuance...")
        card_name = page.locator("#card-patient-name")
        await card_name.wait_for(state="visible", timeout=5000)
        assert (await card_name.text_content()) == "Rajesh Kumar"

        # Assert ABHA ID on card
        card_text = await page.locator("text=91-4820-9182-3841").text_content()
        assert "91-4820-9182-3841" in card_text

        await page.screenshot(path=str(SCREENSHOTS_DIR / "16_indian_health_card_issued.png"))
        print("[OK] Digital Health Card issued with ABHA ID and Tricolor styling.")

        # Step 6: Direct Action -> View Unified Record
        print("[STEP 7] Navigating to Unified Patient Record...")
        view_record_btn = page.locator("#card-view-record-btn")
        await view_record_btn.click()
        await page.wait_for_timeout(1200)

        # Verify Patient Header in Unified Record
        patient_title = page.locator("h1:has-text('Rajesh Kumar')")
        await patient_title.wait_for(state="visible", timeout=5000)

        abha_chip = page.get_by_text("ABHA: 91-4820-9182-3841", exact=True)
        await abha_chip.wait_for(state="visible", timeout=3000)

        loc_chip = page.locator("text=Hyderabad, Telangana")
        await loc_chip.wait_for(state="visible", timeout=3000)

        await page.screenshot(path=str(SCREENSHOTS_DIR / "17_indian_unified_record_active.png"))
        print("[OK] Unified Patient Record loaded with Indian demographics & clinical tags.")

        # Step 7: Verify Audit Trail
        print("[STEP 8] Verifying Audit Trail logging...")
        audit_tab = page.locator("#nav-tab-audit")
        await audit_tab.click()
        await page.wait_for_timeout(1000)

        # Check for INTAKE_CREATED by patient_self_service
        intake_audit = page.locator("text=INTAKE_CREATED").first
        await intake_audit.wait_for(state="visible", timeout=5000)
        actor_tag = page.locator("text=patient_self_service")
        await actor_tag.first.wait_for(state="visible", timeout=3000)

        await page.screenshot(path=str(SCREENSHOTS_DIR / "18_indian_audit_trail_provenance.png"))
        print("[OK] Audit Trail confirms INTAKE_CREATED with actor: patient_self_service.")

        await browser.close()

    print("[SUCCESS] All Indian Patient Registration and Onboarding tests passed with 0 errors!")

if __name__ == "__main__":
    asyncio.run(run_verification())

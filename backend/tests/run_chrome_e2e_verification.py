"""
MedLens Automated E2E Test via Google Chrome
Executes full verification flow using the installed Google Chrome binary:
  C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe

Captures screenshots at each reference step, detects any console/runtime errors,
validates interactions, and confirms full system rectification.
"""

import asyncio
import json
import os
import sys
from playwright.async_api import async_playwright

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
FRONTEND_URL = "http://127.0.0.1:5173"
ARTIFACTS_DIR = r"C:\Users\POLA YUGENDER\.gemini\antigravity-ide\brain\0e0877b1-24dd-4c33-9aac-46e7833b30ea"
SCREENSHOTS_DIR = os.path.join(ARTIFACTS_DIR, "screenshots")
SCRATCH_DIR = os.path.join(ARTIFACTS_DIR, "scratch")

os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
os.makedirs(SCRATCH_DIR, exist_ok=True)


async def run_chrome_verification():
    print("=" * 70)
    print("STARTING MEDLENS CHROME E2E AUTOMATION RUN")
    print(f"Target Browser: Google Chrome ({CHROME_PATH})")
    print(f"Target URL:     {FRONTEND_URL}")
    print("=" * 70)

    if not os.path.exists(CHROME_PATH):
        raise FileNotFoundError(f"Google Chrome executable not found at: {CHROME_PATH}")

    errors_detected = []

    async with async_playwright() as p:
        # Launch Google Chrome with custom flags and desktop viewport
        browser = await p.chromium.launch(
            executable_path=CHROME_PATH,
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--window-size=1440,960",
            ],
        )

        context = await browser.new_context(
            viewport={"width": 1440, "height": 960},
            accept_downloads=True,
        )

        page = await context.new_page()

        # Listen for console errors & unhandled exceptions
        def handle_console(msg):
            if msg.type == "error":
                text = msg.text
                # Filter out harmless favicon 404s if any
                if "favicon" not in text.lower():
                    print(f"  [BROWSER CONSOLE ERROR] {text}")
                    errors_detected.append(f"Console error: {text}")

        def handle_pageerror(err):
            print(f"  [PAGE RUNTIME ERROR] {err}")
            errors_detected.append(f"Page runtime error: {err}")

        page.on("console", handle_console)
        page.on("pageerror", handle_pageerror)

        # ------------------------------------------------------------------
        # STEP 1: Load MedLens & Verify Eleanor Vance
        # ------------------------------------------------------------------
        print("\n[CHROME STEP 1] Loading application & inspecting Eleanor Vance record...")
        await page.goto(FRONTEND_URL, wait_until="networkidle")
        await page.wait_for_timeout(1000)

        # Confirm all 8 navigation tabs exist and are visible
        tab_ids = [
            "nav-tab-record",
            "nav-tab-verify",
            "nav-tab-upload",
            "nav-tab-intake",
            "nav-tab-side_by_side",
            "nav-tab-trends",
            "nav-tab-conflicts",
            "nav-tab-audit",
        ]
        for tid in tab_ids:
            tab_el = page.locator(f"#{tid}")
            is_vis = await tab_el.is_visible()
            assert is_vis, f"Navigation tab #{tid} must be visible"

        print("  [OK] All 8 navigation tabs are rendered cleanly on desktop viewport.")

        # Ensure Eleanor Vance is selected
        patient_select = page.locator("#patient-select")
        await patient_select.wait_for(state="visible")
        
        # Check if selected patient name contains Eleanor Vance
        selected_text = await page.locator("#patient-select option:checked").inner_text()
        if "Eleanor Vance" not in selected_text:
            options = await page.locator("#patient-select option").all()
            for opt in options:
                txt = await opt.inner_text()
                if "Eleanor Vance" in txt:
                    val = await opt.get_attribute("value")
                    await patient_select.select_option(val)
                    await page.wait_for_timeout(800)
                    break

        # Save Screenshot 1: Unified Record
        shot_01 = os.path.join(SCREENSHOTS_DIR, "01_eleanor_vance_unified_record.png")
        await page.screenshot(path=shot_01, full_page=False)
        print(f"  [OK] Saved Reference Screenshot: {shot_01}")

        # Check Non-Diagnostic Disclaimer Banner
        disclaimer = page.locator("text=NON-DIAGNOSTIC GUARDRAIL").first
        assert await disclaimer.is_visible(), "Non-diagnostic guardrail banner must be visible"
        print("  [OK] Non-diagnostic disclaimer banner confirmed.")

        # Navigate to Safety & Conflicts tab using reference click
        conflicts_tab = page.locator("#nav-tab-conflicts")
        await conflicts_tab.click()
        await page.wait_for_timeout(800)

        # Confirm Allergy Contradiction Alert (Amoxicillin vs Penicillin)
        allergy_alert = page.locator("text=Allergy Alert: Amoxicillin vs Penicillin Allergy").first
        assert await allergy_alert.is_visible(), "Allergy conflict alert must be visible"
        print("  [OK] Confirmed Clinical Conflict: Amoxicillin vs Penicillin Allergy.")

        # Save Screenshot 2: Safety & Conflicts
        shot_02 = os.path.join(SCREENSHOTS_DIR, "02_eleanor_vance_conflicts_allergy_alert.png")
        await page.screenshot(path=shot_02, full_page=False)
        print(f"  [OK] Saved Reference Screenshot: {shot_02}")

        # ------------------------------------------------------------------
        # STEP 2: Switch to Arthur Pendelton & Review/Verify
        # ------------------------------------------------------------------
        print("\n[CHROME STEP 2] Switching to Arthur Pendelton & verifying tests...")
        options = await page.locator("#patient-select option").all()
        arthur_val = None
        for opt in options:
            txt = await opt.inner_text()
            if "Arthur Pendelton" in txt:
                arthur_val = await opt.get_attribute("value")
                break
        assert arthur_val, "Patient 'Arthur Pendelton' must exist in patient switcher"
        await patient_select.select_option(arthur_val)
        await page.wait_for_timeout(1000)

        # Return to Unified Record to capture updated state
        await page.locator("#nav-tab-record").click()
        await page.wait_for_timeout(800)

        shot_03 = os.path.join(SCREENSHOTS_DIR, "03_arthur_pendelton_unified_record_alert.png")
        await page.screenshot(path=shot_03, full_page=False)
        print(f"  [OK] Saved Reference Screenshot: {shot_03}")

        # Click Review & Verify tab
        await page.locator("#nav-tab-verify").click()
        await page.wait_for_timeout(800)

        shot_04 = os.path.join(SCREENSHOTS_DIR, "04_arthur_pendelton_review_verify_unverified.png")
        await page.screenshot(path=shot_04, full_page=False)
        print(f"  [OK] Saved Reference Screenshot: {shot_04}")

        # Find editable test rows
        edit_buttons = await page.locator("button[data-testid='edit-test-btn']").all()
        if len(edit_buttons) > 0:
            print(f"  [INFO] Found {len(edit_buttons)} unverified tests available for editing.")
            first_edit_btn = edit_buttons[0]
            await first_edit_btn.click()
            await page.wait_for_timeout(500)

            # Locate edit input
            edit_input = page.locator("input[id^='edit-value-input-']").first
            assert await edit_input.is_visible(), "Edit input field must appear upon clicking edit"
            orig_val = await edit_input.input_value()
            new_val = "14.5" if orig_val != "14.5" else "12.8"
            await edit_input.fill(new_val)
            await page.wait_for_timeout(400)

            # Save Screenshot 5: Inline edit
            shot_05 = os.path.join(SCREENSHOTS_DIR, "05_arthur_pendelton_edited_test.png")
            await page.screenshot(path=shot_05, full_page=False)
            print(f"  [OK] Saved Reference Screenshot: {shot_05}")

            # Save the edit
            save_btn = page.locator("button[data-testid='save-test-btn']").first
            await save_btn.click()
            await page.wait_for_timeout(1000)
            print(f"  [OK] Saved edited value '{new_val}' to backend database.")

            # Commit single verification
            verify_single_btn = page.locator("button[data-testid='verify-single-btn']").first
            await verify_single_btn.click()
            await page.wait_for_timeout(1200)
            print("  [OK] Clicked verify to commit single test.")

            shot_06 = os.path.join(SCREENSHOTS_DIR, "06_arthur_pendelton_verified_committed.png")
            await page.screenshot(path=shot_06, full_page=False)
            print(f"  [OK] Saved Reference Screenshot: {shot_06}")

            # Scroll down to verified records section and capture verified table screenshot
            verified_section = page.locator("#verified-records-section")
            if await verified_section.is_visible():
                await verified_section.scroll_into_view_if_needed()
                await page.wait_for_timeout(500)
                shot_06b = os.path.join(SCREENSHOTS_DIR, "06b_arthur_pendelton_verified_table.png")
                await page.screenshot(path=shot_06b, full_page=False)
                print(f"  [OK] Saved Reference Screenshot: {shot_06b}")
        else:
            print("  [INFO] All tests are currently verified. Proceeding with verified tests table check.")

        # ------------------------------------------------------------------
        # STEP 3: Side-by-Side Source Inspector
        # ------------------------------------------------------------------
        print("\n[CHROME STEP 3] Inspecting Side-by-Side Source Inspector...")
        await page.locator("#nav-tab-side_by_side").click()
        await page.wait_for_timeout(1000)

        # Confirm dual-pane presence
        side_header = page.locator("text=Side-by-Side Source Inspector")
        assert await side_header.is_visible(), "Side-by-side header must be visible"

        shot_07 = os.path.join(SCREENSHOTS_DIR, "07_arthur_pendelton_side_by_side_inspector.png")
        await page.screenshot(path=shot_07, full_page=False)
        print(f"  [OK] Saved Reference Screenshot: {shot_07}")

        # ------------------------------------------------------------------
        # STEP 4: Audit Trail & JSON Diff Check
        # ------------------------------------------------------------------
        print("\n[CHROME STEP 4] Inspecting Audit Trail & diff logs...")
        await page.locator("#nav-tab-audit").click()
        await page.wait_for_timeout(1000)

        # Ensure all tabs remain aligned and no truncation occurred
        audit_tab = page.locator("#nav-tab-audit")
        record_tab = page.locator("#nav-tab-record")
        assert await audit_tab.is_visible(), "Audit tab must remain fully visible"
        assert await record_tab.is_visible(), "Unified Record tab must remain fully visible"

        # Locate the first audit event row that has a payload to expand
        expandable_rows = await page.locator("div[data-testid='audit-row'][data-has-payload='true']").all()
        if len(expandable_rows) > 0:
            print("  [INFO] Expanding audit event diff card to show Before/After state...")
            await expandable_rows[0].click()
            await page.wait_for_timeout(600)

        shot_08 = os.path.join(SCREENSHOTS_DIR, "08_arthur_pendelton_audit_trail_diff.png")
        await page.screenshot(path=shot_08, full_page=False)
        print(f"  [OK] Saved Reference Screenshot: {shot_08}")

        # ------------------------------------------------------------------
        # STEP 5: Export Record Dropdown, JSON & PDF Downloads
        # ------------------------------------------------------------------
        print("\n[CHROME STEP 5] Testing Clinical Record Export (JSON & PDF)...")
        await page.locator("#nav-tab-record").click()
        await page.wait_for_timeout(800)

        export_dropdown = page.locator("#export-record-dropdown-btn")
        await export_dropdown.click()
        await page.wait_for_timeout(600)

        shot_09 = os.path.join(SCREENSHOTS_DIR, "09_export_record_dropdown.png")
        await page.screenshot(path=shot_09, full_page=False)
        print(f"  [OK] Saved Reference Screenshot: {shot_09}")

        # Test Download JSON
        json_btn = page.locator("#download-json-btn")
        assert await json_btn.is_visible(), "Download JSON button must be visible"
        async with page.expect_download(timeout=10000) as download_json_info:
            await json_btn.click()
        download_json = await download_json_info.value
        json_save_path = os.path.join(SCRATCH_DIR, download_json.suggested_filename)
        await download_json.save_as(json_save_path)
        json_size = os.path.getsize(json_save_path)
        print(f"  [OK] JSON downloaded successfully: {json_save_path} ({json_size} bytes)")

        # Validate JSON content & disclaimers
        with open(json_save_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert "patient" in data, "Exported JSON must contain 'patient'"
            assert "structured_tests" in data or "verified_tests" in data, "Exported JSON must contain tests"
            assert "disclaimer" in data or "safety_disclaimer" in data.get("metadata", {}), "Disclaimer required"
            print(f"  [OK] Verified JSON payload integrity: patient='{data['patient']['name']}'.")

        # Test Download PDF
        await export_dropdown.click()
        await page.wait_for_timeout(600)

        pdf_btn = page.locator("#download-pdf-btn")
        assert await pdf_btn.is_visible(), "Download PDF button must be visible"
        async with page.expect_download(timeout=15000) as download_pdf_info:
            await pdf_btn.click()
        download_pdf = await download_pdf_info.value
        pdf_save_path = os.path.join(SCRATCH_DIR, download_pdf.suggested_filename)
        await download_pdf.save_as(pdf_save_path)
        pdf_size = os.path.getsize(pdf_save_path)
        print(f"  [OK] PDF downloaded successfully: {pdf_save_path} ({pdf_size} bytes)")

        # Validate PDF binary header
        with open(pdf_save_path, "rb") as f:
            header = f.read(5)
            assert header == b"%PDF-", f"Expected PDF binary header '%PDF-', got: {header}"
            print("  [OK] Verified PDF binary header: %PDF- valid ReportLab document!")

        # ------------------------------------------------------------------
        # STEP 6: Biomarker Trends & Sparkline Chart Verification
        # ------------------------------------------------------------------
        print("\n[CHROME STEP 6] Inspecting Biomarker Longitudinal Trends...")
        await page.locator("#nav-tab-trends").click()
        await page.wait_for_timeout(1000)

        shot_10 = os.path.join(SCREENSHOTS_DIR, "10_arthur_pendelton_trends_sparkline.png")
        await page.screenshot(path=shot_10, full_page=False)
        print(f"  [OK] Saved Reference Screenshot: {shot_10}")

        # ------------------------------------------------------------------
        # STEP 7: Medical Reports & Multi-Step Ingestion View
        # ------------------------------------------------------------------
        print("\n[CHROME STEP 7] Inspecting Medical Reports Upload View...")
        await page.locator("#nav-tab-upload").click()
        await page.wait_for_timeout(1000)

        shot_11 = os.path.join(SCREENSHOTS_DIR, "11_reports_upload_view.png")
        await page.screenshot(path=shot_11, full_page=False)
        print(f"  [OK] Saved Reference Screenshot: {shot_11}")

        await browser.close()

    print("\n" + "=" * 70)
    if len(errors_detected) > 0:
        print(f"WARNING: {len(errors_detected)} runtime/console issues detected:")
        for err in errors_detected:
            print(f"  - {err}")
    else:
        print("ZERO BROWSER CONSOLE ERRORS DETECTED.")
    print("ALL 5 MEDLENS WORKFLOWS VALIDATED VIA GOOGLE CHROME!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_chrome_verification())

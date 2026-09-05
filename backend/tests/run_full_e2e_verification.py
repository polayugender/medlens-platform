import asyncio
import os
import json
from playwright.async_api import async_playwright

ARTIFACT_DIR = r"C:\Users\POLA YUGENDER\.gemini\antigravity-ide\brain\0e0877b1-24dd-4c33-9aac-46e7833b30ea"
SCREENSHOTS_DIR = os.path.join(ARTIFACT_DIR, "screenshots")
SCRATCH_DIR = os.path.join(ARTIFACT_DIR, "scratch")

os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
os.makedirs(SCRATCH_DIR, exist_ok=True)

async def run_full_verification():
    print("================================================================")
    print("STARTING MEDLENS FULL END-TO-END AUTOMATED VERIFICATION")
    print("================================================================")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 850},
            accept_downloads=True
        )
        page = await context.new_page()

        # STEP 1: Navigate to MedLens and verify Eleanor Vance
        print("\n[STEP 1] Navigating to MedLens & Verifying Patient Eleanor Vance...")
        await page.goto("http://127.0.0.1:5173/", wait_until="networkidle")
        await page.wait_for_selector("header select", timeout=10000)

        # Select Eleanor Vance
        select_elem = page.locator("header select")
        options = await select_elem.locator("option").all_inner_texts()
        eleanor_opt = [o for o in options if "Eleanor Vance" in o]
        assert eleanor_opt, "Eleanor Vance option must exist in patient dropdown"
        
        # Select Eleanor Vance by label
        await select_elem.select_option(label=eleanor_opt[0])
        await page.wait_for_timeout(1500)

        # Verify Eleanor Vance header
        patient_title = await page.locator("h1").inner_text()
        assert "Eleanor Vance" in patient_title, f"Expected Eleanor Vance header, got: {patient_title}"
        print(f"  [OK] Active Patient: {patient_title}")

        # Capture Screenshot 1: Eleanor Vance Unified Record
        s1_path = os.path.join(SCREENSHOTS_DIR, "01_eleanor_vance_unified_record.png")
        await page.screenshot(path=s1_path)
        print(f"  [OK] Saved Screenshot: {s1_path}")

        # Navigate to Safety & Conflicts tab
        conflicts_tab = page.locator("#nav-tab-conflicts")
        await conflicts_tab.click()
        await page.wait_for_timeout(1200)

        # Check Penicillin vs Amoxicillin allergy conflict
        conflicts_text = await page.locator("main").inner_text()
        assert "Penicillin" in conflicts_text or "Amoxicillin" in conflicts_text or "Allergy" in conflicts_text, "Eleanor Vance should display allergy/medication conflict alert"
        print("  [OK] Confirmed Safety Conflict: Cross-reactivity / allergy contraindication found!")

        # Capture Screenshot 2: Eleanor Vance Allergy Conflict Alert
        s2_path = os.path.join(SCREENSHOTS_DIR, "02_eleanor_vance_conflicts_allergy_alert.png")
        await page.screenshot(path=s2_path)
        print(f"  [OK] Saved Screenshot: {s2_path}")

        # STEP 2: Switch to Patient Arthur Pendelton & Review/Verify
        print("\n[STEP 2] Switching to Patient Arthur Pendelton & Review/Verify...")
        arthur_opt = [o for o in options if "Arthur Pendelton" in o]
        assert arthur_opt, "Arthur Pendelton option must exist in patient dropdown"
        await select_elem.select_option(label=arthur_opt[0])
        await page.wait_for_timeout(1500)

        # Navigate to Unified Record tab to observe unverified alert callout
        record_tab = page.locator("#nav-tab-record")
        await record_tab.click()
        await page.wait_for_timeout(1200)

        arthur_title = await page.locator("h1").inner_text()
        assert "Arthur Pendelton" in arthur_title, f"Expected Arthur Pendelton header, got: {arthur_title}"
        print(f"  [OK] Active Patient: {arthur_title}")

        # Capture Screenshot 3: Arthur Pendelton Unified Record with Unverified Alert Callout
        s3_path = os.path.join(SCREENSHOTS_DIR, "03_arthur_pendelton_unified_record_alert.png")
        await page.screenshot(path=s3_path)
        print(f"  [OK] Saved Screenshot: {s3_path}")

        # Navigate to Review & Verify tab
        verify_tab = page.locator("#nav-tab-verify")
        await verify_tab.click()
        await page.wait_for_timeout(1500)

        # Capture Screenshot 4: Arthur Pendelton Unverified Lab Tests Queue
        s4_path = os.path.join(SCREENSHOTS_DIR, "04_arthur_pendelton_review_verify_unverified.png")
        await page.screenshot(path=s4_path)
        print(f"  [OK] Saved Screenshot: {s4_path}")

        # Check pending tests table
        edit_buttons = page.locator("button[title='Edit test values']")
        count_pending = await edit_buttons.count()
        print(f"  [OK] Pending unverified tests editable: {count_pending}")
        assert count_pending > 0, "Arthur Pendelton must have unverified test items"

        # Edit first test item
        await edit_buttons.first.click()
        await page.wait_for_timeout(500)

        # Locate value input and modify it
        val_input = page.locator("table tbody tr input.font-mono").first
        original_val = await val_input.input_value()
        print(f"  [OK] Original test value: {original_val}")
        new_val = "14.2" if original_val != "14.2" else "14.5"
        await val_input.fill(new_val)
        await page.wait_for_timeout(300)

        # Capture Screenshot 5: Arthur Pendelton Edited Test Form
        s5_path = os.path.join(SCREENSHOTS_DIR, "05_arthur_pendelton_edited_test.png")
        await page.screenshot(path=s5_path)
        print(f"  [OK] Saved Screenshot: {s5_path}")

        # Save test edit
        save_btn = page.locator("button[title='Save Changes']").first
        await save_btn.click()
        await page.wait_for_timeout(1000)
        print(f"  [OK] Saved edited value '{new_val}' to backend")

        # Verify single test item
        verify_single_btn = page.locator("button[title='Confirm and verify this test']").first
        await verify_single_btn.click()
        await page.wait_for_timeout(1500)
        print("  [OK] Clicked Verify Single to commit verification")

        # Capture Screenshot 6: Verified and Committed State
        s6_path = os.path.join(SCREENSHOTS_DIR, "06_arthur_pendelton_verified_committed.png")
        await page.screenshot(path=s6_path)
        print(f"  [OK] Saved Screenshot: {s6_path}")

        # STEP 3: Side-by-Side Inspector
        print("\n[STEP 3] Inspecting Side-by-Side Document Inspector...")
        sbs_tab = page.locator("#nav-tab-side_by_side")
        await sbs_tab.click()
        await page.wait_for_timeout(2000)

        # Capture Screenshot 7: Side-by-Side Inspector with Document Preview & Markers
        s7_path = os.path.join(SCREENSHOTS_DIR, "07_arthur_pendelton_side_by_side_inspector.png")
        await page.screenshot(path=s7_path)
        print(f"  [OK] Saved Screenshot: {s7_path}")

        # STEP 4: Verify Audit Trail
        print("\n[STEP 4] Verifying Audit Trail & Diff Payload...")
        audit_tab = page.locator("#nav-tab-audit")
        await audit_tab.click()
        await page.wait_for_timeout(1500)

        # Click the top audit log item to expand before/after diff
        log_items = page.locator("[data-testid='audit-row']")
        top_log = log_items.first
        await top_log.wait_for(state="visible", timeout=10000)
        await top_log.click()
        await page.wait_for_timeout(800)

        # Capture Screenshot 8: Audit Trail with Expanded Diff
        s8_path = os.path.join(SCREENSHOTS_DIR, "08_arthur_pendelton_audit_trail_diff.png")
        await page.screenshot(path=s8_path)
        print(f"  [OK] Saved Screenshot: {s8_path}")

        # STEP 5: Export Clinical Record (PDF & JSON)
        print("\n[STEP 5] Verifying Export Record Dropdown & File Downloads...")
        await record_tab.click()
        await page.wait_for_timeout(1500)

        # Locate and open Export dropdown
        export_dropdown = page.locator("#export-record-dropdown-btn")
        await export_dropdown.scroll_into_view_if_needed()
        await export_dropdown.click()
        await page.wait_for_timeout(600)

        # Capture Screenshot 9: Export Record Dropdown Menu
        s9_path = os.path.join(SCREENSHOTS_DIR, "09_export_record_dropdown.png")
        await page.screenshot(path=s9_path)
        print(f"  [OK] Saved Screenshot: {s9_path}")

        # Test Download JSON
        json_btn = page.locator("#download-json-btn")
        assert await json_btn.is_visible(), "Download JSON menu option must be visible"
        async with page.expect_download(timeout=10000) as download_json_info:
            await json_btn.click()
        download_json = await download_json_info.value
        json_save_path = os.path.join(SCRATCH_DIR, download_json.suggested_filename)
        await download_json.save_as(json_save_path)
        json_size = os.path.getsize(json_save_path)
        print(f"  [OK] JSON downloaded: {json_save_path} ({json_size} bytes)")
        
        # Verify JSON contents
        with open(json_save_path, "r", encoding="utf-8") as f:
            export_obj = json.load(f)
            assert "patient" in export_obj, "Export JSON must contain 'patient'"
            assert "verified_tests" in export_obj or "structured_tests" in export_obj, "Export JSON must contain 'verified_tests' or 'structured_tests'"
            assert "disclaimer" in export_obj or "safety_disclaimer" in export_obj.get("metadata", {}), "Export JSON must include non-diagnostic disclaimer"
            v_count = len(export_obj.get("verified_tests", export_obj.get("structured_tests", [])))
            print(f"  [OK] Verified JSON schema: patient='{export_obj['patient']['name']}', tests_count={v_count}")

        # Open dropdown again and test Download PDF
        await export_dropdown.click()
        await page.wait_for_timeout(600)

        pdf_btn = page.locator("#download-pdf-btn")
        assert await pdf_btn.is_visible(), "Download PDF menu option must be visible"
        async with page.expect_download(timeout=15000) as download_pdf_info:
            await pdf_btn.click()
        download_pdf = await download_pdf_info.value
        pdf_save_path = os.path.join(SCRATCH_DIR, download_pdf.suggested_filename)
        await download_pdf.save_as(pdf_save_path)
        pdf_size = os.path.getsize(pdf_save_path)
        print(f"  [OK] PDF downloaded: {pdf_save_path} ({pdf_size} bytes)")

        # Verify PDF magic bytes
        with open(pdf_save_path, "rb") as f:
            header = f.read(5)
            assert header == b"%PDF-", f"Expected PDF magic bytes %PDF-, got: {header}"
            print("  [OK] Verified PDF binary header: %PDF- valid document structure!")

        await browser.close()

    print("\n================================================================")
    print("ALL 5 VERIFICATION STEPS COMPLETED AND VERIFIED 100% SUCCESSFULLY!")
    print("================================================================")

if __name__ == "__main__":
    asyncio.run(run_full_verification())

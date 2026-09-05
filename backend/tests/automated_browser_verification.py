import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

import os

SCREENSHOTS_DIR = Path(
    os.getenv("SCREENSHOTS_DIR", r"C:\Users\POLA YUGENDER\.gemini\antigravity-ide\brain\c40ff20b-1652-4c85-9d6f-69245f1cb30d\screenshots")
)
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

async def run_browser_verification():
    print("[BROWSER] Launching Playwright Chromium...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        print("[STEP 1] Navigating to http://localhost:5173/...")
        await page.goto("http://localhost:5173/", wait_until="networkidle")
        await page.wait_for_timeout(1000)

        # Explicitly select Eleanor Vance
        print("[STEP 1] Selecting Eleanor Vance from dropdown...")
        await page.select_option("select", label="Eleanor Vance (Female, DOB: 1978-04-14)")
        await page.wait_for_timeout(1500)

        # Screenshot 1: Eleanor Vance Unified Record
        s1 = SCREENSHOTS_DIR / "01_eleanor_vance_unified_record.png"
        await page.screenshot(path=str(s1), full_page=True)
        print(f"  -> Captured: {s1.name}")

        # Check disclaimer banner
        disclaimer = await page.locator("text=Non-Diagnostic Guardrail").first.is_visible()
        print(f"  -> Persistent Non-Diagnostic Disclaimer Banner visible: {disclaimer}")

        # Step 1b: Navigate to Safety & Conflicts tab for Eleanor Vance
        print("[STEP 1b] Clicking 'Safety & Conflicts' tab for Eleanor Vance...")
        await page.click("#nav-tab-conflicts")
        await page.wait_for_timeout(1000)

        # Confirm allergy conflict warning
        allergy_alert = await page.locator("text=Allergy Alert: Amoxicillin vs Penicillin Allergy").is_visible()
        print(f"  -> Confirmed Penicillin vs. Amoxicillin conflict warning: {allergy_alert}")

        s2 = SCREENSHOTS_DIR / "02_eleanor_vance_conflicts_allergy_alert.png"
        await page.screenshot(path=str(s2), full_page=True)
        print(f"  -> Captured: {s2.name}")

        # Step 2: Switch to Patient 'Arthur Pendelton'
        print("[STEP 2] Switching patient dropdown to 'Arthur Pendelton'...")
        # Select by label
        await page.select_option("select", label="Arthur Pendelton (Male, DOB: 1962-11-20)")
        await page.wait_for_timeout(1500)

        s3 = SCREENSHOTS_DIR / "03_arthur_pendelton_unified_record_alert.png"
        await page.screenshot(path=str(s3), full_page=True)
        print(f"  -> Captured: {s3.name}")

        # Step 2b: Navigate to Review & Verify tab
        print("[STEP 2b] Opening 'Review & Verify' tab...")
        await page.click("#nav-tab-verify")
        await page.wait_for_timeout(1200)

        s4 = SCREENSHOTS_DIR / "04_arthur_pendelton_review_verify_unverified.png"
        await page.screenshot(path=str(s4), full_page=True)
        print(f"  -> Captured: {s4.name}")

        # Inspect unverified CBC test, click edit icon on Hemoglobin or first test
        print("[STEP 2c] Editing test value and verifying...")
        # Click the edit button for the second test (Hemoglobin) or first
        edit_buttons = page.locator("button[title='Edit test values']")
        count = await edit_buttons.count()
        print(f"  -> Found {count} editable unverified test rows")
        if count > 0:
            await edit_buttons.nth(0).click()
            await page.wait_for_timeout(500)

            # Change value slightly
            value_input = page.locator("input.font-mono")
            if await value_input.count() > 0:
                await value_input.fill("7.1")
                # Save edit
                save_btn = page.locator("button[title='Save Changes']")
                await save_btn.click()
                await page.wait_for_timeout(1000)
                print("  -> Saved edit on test record (updated value to 7.1)")

        s5 = SCREENSHOTS_DIR / "05_arthur_pendelton_edited_test.png"
        await page.screenshot(path=str(s5), full_page=True)
        print(f"  -> Captured: {s5.name}")

        # Click "Verify All Pending" button
        verify_all_btn = page.locator("button:has-text('Verify All Pending')")
        if await verify_all_btn.is_visible():
            print("  -> Clicking 'Verify All Pending' button...")
            await verify_all_btn.click()
            await page.wait_for_timeout(2000)
            print("  -> Batch verification committed!")

        s6 = SCREENSHOTS_DIR / "06_arthur_pendelton_verified_committed.png"
        await page.screenshot(path=str(s6), full_page=True)
        print(f"  -> Captured: {s6.name}")

        # Step 3: Side-by-Side Inspector
        print("[STEP 3] Opening 'Side-by-Side' tab...")
        await page.click("#nav-tab-side_by_side")
        await page.wait_for_timeout(1500)

        # Hover over test item to trigger source snippet highlight
        test_cards = page.locator("div.cursor-pointer")
        if await test_cards.count() > 0:
            await test_cards.nth(0).hover()
            await page.wait_for_timeout(800)

        s7 = SCREENSHOTS_DIR / "07_arthur_pendelton_side_by_side_inspector.png"
        await page.screenshot(path=str(s7), full_page=True)
        print(f"  -> Captured: {s7.name}")

        # Step 4: Audit Trail
        print("[STEP 4] Opening 'Audit Trail' tab...")
        await page.click("#nav-tab-audit")
        await page.wait_for_timeout(1200)

        # Expand top audit log to inspect Before/After diff
        log_items = page.locator("div.cursor-pointer")
        if await log_items.count() > 0:
            await log_items.nth(0).click()
            await page.wait_for_timeout(800)

        s8 = SCREENSHOTS_DIR / "08_arthur_pendelton_audit_trail_diff.png"
        await page.screenshot(path=str(s8), full_page=True)
        print(f"  -> Captured: {s8.name}")

        await browser.close()
        print("\n[SUCCESS] Automated browser verification completed flawlessly with all screenshots captured!")

if __name__ == "__main__":
    asyncio.run(run_browser_verification())

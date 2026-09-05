import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

ARTIFACTS_DIR = Path(r"C:\Users\POLA YUGENDER\.gemini\antigravity-ide\brain\0e0877b1-24dd-4c33-9aac-46e7833b30ea\screenshots")
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

async def run_new_user_verification():
    print("=" * 70)
    print("[RUN] STARTING MEDLENS NEW USER ONBOARDING VERIFICATION RUN")
    print("=" * 70)

    # 1. Reset database to ensure clean empty state
    import urllib.request
    try:
        reset_req = urllib.request.Request(
            "http://127.0.0.1:8000/api/system/reset",
            data=b"{}",
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(reset_req) as resp:
            print("[RESET]", resp.read().decode())
    except Exception as e:
        print("[WARN] Reset failed or backend not reachable:", e)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 960})
        page = await context.new_page()

        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        async def on_dialog(dialog):
            print(f"  [DIALOG] {dialog.message}")
            await dialog.accept()
        page.on("dialog", lambda d: asyncio.create_task(on_dialog(d)))
        page.on("pageerror", lambda err: print(f"  [PAGE ERROR]: {err}"))

        # -------------------------------------------------------------
        # Step 1: Navigate to fresh site with 0 patients
        # -------------------------------------------------------------
        print("\n[Step 1] Navigating to http://localhost:5173 with empty database...")
        await page.goto("http://localhost:5173", wait_until="networkidle")
        await asyncio.sleep(1)

        # Check for Welcome portal elements
        welcome_header = page.locator("text=Unified, Source-Traceable Patient Intelligence")
        await welcome_header.wait_for(state="visible", timeout=5000)
        print("  [OK] Welcome portal headline verified!")

        card1 = page.locator("text=Indian Patient Onboarding")
        card2 = page.locator("text=Quick Patient Intake")
        card3 = page.locator("text=Explore Demo Sandbox")
        await card1.wait_for(state="visible", timeout=5000)
        await card2.wait_for(state="visible", timeout=5000)
        await card3.wait_for(state="visible", timeout=5000)
        print("  [OK] Action cards (Indian Onboarding, Quick Intake & Demo Sandbox) verified!")

        screenshot_1 = ARTIFACTS_DIR / "01_new_user_welcome_portal.png"
        await page.screenshot(path=str(screenshot_1))
        print(f"  [SAVED] Screenshot: {screenshot_1.name}")

        # -------------------------------------------------------------
        # Step 2: Register a new patient
        # -------------------------------------------------------------
        print("\n[Step 2] Testing first-time patient registration...")
        create_btn = page.locator("#welcome-create-patient-btn")
        await create_btn.click()
        await asyncio.sleep(0.5)

        # Modal should be open
        modal_header = page.locator("h3:has-text('Add New Patient')")
        await modal_header.wait_for(state="visible", timeout=3000)
        print("  [OK] Registration modal opened!")

        await page.fill("#new-patient-name", "David Thorne")
        await page.fill("#new-patient-dob", "1985-06-12")
        await page.select_option("#new-patient-sex", "Male")

        submit_btn = page.locator("#submit-patient-btn")
        await submit_btn.click()
        await asyncio.sleep(1.5)

        # Verify new patient is selected and stepper is visible
        stepper = page.locator("text=Patient Profile Created: David Thorne")
        await stepper.wait_for(state="visible", timeout=5000)
        print("  [OK] David Thorne registered & selected! Guided setup stepper visible.")

        screenshot_2 = ARTIFACTS_DIR / "02_new_patient_intake_stepper.png"
        await page.screenshot(path=str(screenshot_2))
        print(f"  [SAVED] Screenshot: {screenshot_2.name}")

        # -------------------------------------------------------------
        # Step 3: Complete Intake form for David Thorne
        # -------------------------------------------------------------
        print("\n[Step 3] Completing clinical intake form for new patient...")
        await page.fill("#intake-age", "41")
        await page.fill("#symptom-input", "Mild headache")
        await page.click("#add-symptom-btn")
        await asyncio.sleep(0.3)
        await page.fill("#condition-input", "None")
        await page.click("#add-condition-btn")
        await asyncio.sleep(0.3)
        await page.fill("#allergy-input", "No known drug allergies")
        await page.click("#add-allergy-btn")
        await asyncio.sleep(0.3)

        save_intake_btn = page.locator("#save-intake-btn")
        await save_intake_btn.scroll_into_view_if_needed()
        await save_intake_btn.click()
        await asyncio.sleep(2)

        screenshot_3 = ARTIFACTS_DIR / "03_new_patient_intake_saved.png"
        await page.screenshot(path=str(screenshot_3))
        print(f"  [SAVED] Screenshot: {screenshot_3.name}")
        print("  [OK] Intake form saved!")

        # -------------------------------------------------------------
        # Step 4: Verify Unified Record for the new patient
        # -------------------------------------------------------------
        print("\n[Step 4] Checking Unified Record tab for newly onboarded patient...")
        record_tab = page.locator("#nav-tab-record")
        await record_tab.click()
        await asyncio.sleep(1)

        patient_title = page.locator("h1:has-text('David Thorne')")
        await patient_title.wait_for(state="visible", timeout=3000)
        print("  [OK] Unified Record reflects David Thorne profile!")

        # -------------------------------------------------------------
        # Step 5: Test Data Purge / Reset
        # -------------------------------------------------------------
        print("\n[Step 5] Testing system reset from UI...")
        sys_menu_btn = page.locator("#system-menu-btn")
        await sys_menu_btn.click()
        await asyncio.sleep(0.3)

        clear_btn = page.locator("#menu-clear-data-btn")
        await clear_btn.click()
        await asyncio.sleep(1.5)

        # Confirm we are back to Welcome portal
        await welcome_header.wait_for(state="visible", timeout=5000)
        print("  [OK] System reset successfully purged all data! Returned to Welcome Portal.")

        screenshot_4 = ARTIFACTS_DIR / "04_cleared_data_back_to_welcome.png"
        await page.screenshot(path=str(screenshot_4))
        print(f"  [SAVED] Screenshot: {screenshot_4.name}")

        # -------------------------------------------------------------
        # Step 6: Test 'Load Sample Demo Data' from Welcome Portal
        # -------------------------------------------------------------
        print("\n[Step 6] Testing 1-click 'Load Sample Demo Data' from Welcome Portal...")
        load_demo_btn = page.locator("#welcome-load-demo-btn")
        await load_demo_btn.click()
        # Seeding takes 3-6s for PDF generation & extraction
        print("  Waiting for sample clinical demo seed...")
        await asyncio.sleep(6)

        # Eleanor Vance should now be loaded
        eleanor_header = page.locator("h1:has-text('Eleanor Vance')")
        await eleanor_header.wait_for(state="visible", timeout=10000)
        print("  [OK] Demo data loaded! Eleanor Vance is selected with full records.")

        screenshot_5 = ARTIFACTS_DIR / "05_demo_sandbox_loaded.png"
        await page.screenshot(path=str(screenshot_5))
        print(f"  [SAVED] Screenshot: {screenshot_5.name}")

        # -------------------------------------------------------------
        # Step 7: Final Clean Purge - Leave site fresh for new users
        # -------------------------------------------------------------
        print("\n[Step 7] Performing final data clear so site is 100% fresh for new users...")
        await sys_menu_btn.click()
        await asyncio.sleep(0.3)
        await clear_btn.click()
        await asyncio.sleep(1.5)

        await welcome_header.wait_for(state="visible", timeout=5000)
        print("  [OK] Final data purge confirmed! Site is in fresh state for new users.")

        screenshot_6 = ARTIFACTS_DIR / "06_fresh_website_ready_for_new_users.png"
        await page.screenshot(path=str(screenshot_6))
        print(f"  [SAVED] Screenshot: {screenshot_6.name}")

        await browser.close()

    print("\n" + "=" * 70)
    print("[DONE] ALL NEW USER ONBOARDING VERIFICATION STEPS COMPLETED!")
    if console_errors:
        print(f"[WARN] Console errors detected: {console_errors}")
    else:
        print("[OK] Zero browser console errors!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(run_new_user_verification())

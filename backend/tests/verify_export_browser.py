import asyncio
from playwright.async_api import async_playwright
import os

async def verify_export_ui():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        
        # Navigate to frontend
        await page.goto("http://127.0.0.1:5173/", wait_until="networkidle")
        await page.wait_for_timeout(1000)

        # If on welcome portal, load demo
        demo_btn = page.locator("#welcome-load-demo-btn")
        if await demo_btn.is_visible():
            await demo_btn.click()
            await page.wait_for_timeout(2000)

        # Select Eleanor Vance from dropdown if available
        select = page.locator("#patient-select")
        if await select.is_visible():
            try:
                await page.select_option("#patient-select", label="Eleanor Vance (Female, DOB: 1978-04-14)")
            except Exception:
                pass
        await page.wait_for_timeout(1000)

        # Check export button
        export_btn = page.locator("#export-record-dropdown-btn")
        await export_btn.wait_for(state="visible", timeout=15000)
        await export_btn.scroll_into_view_if_needed()
        await export_btn.click()
        await page.wait_for_timeout(500)

        # Confirm dropdown options are visible
        pdf_btn = page.locator("#download-pdf-btn")
        json_btn = page.locator("#download-json-btn")
        
        assert await pdf_btn.is_visible(), "Download PDF button should be visible"
        assert await json_btn.is_visible(), "Download JSON button should be visible"
        
        # Save screenshot
        screenshots_dir = os.getenv("SCREENSHOTS_DIR", r"C:\Users\POLA YUGENDER\.gemini\antigravity-ide\brain\c40ff20b-1652-4c85-9d6f-69245f1cb30d\screenshots")
        scratch_dir = os.getenv("SCRATCH_DIR", r"C:\Users\POLA YUGENDER\.gemini\antigravity-ide\brain\c40ff20b-1652-4c85-9d6f-69245f1cb30d\scratch")
        os.makedirs(screenshots_dir, exist_ok=True)
        os.makedirs(scratch_dir, exist_ok=True)
        screenshot_path = os.path.join(screenshots_dir, "09_export_record_dropdown.png")
        await page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to: {screenshot_path}")
        
        # Test download click with download event listener
        async with page.expect_download(timeout=10000) as download_info:
            await json_btn.click()
        download = await download_info.value
        download_json_path = os.path.join(scratch_dir, download.suggested_filename)
        await download.save_as(download_json_path)
        print(f"JSON downloaded successfully: {download_json_path}, size: {os.path.getsize(download_json_path)} bytes")

        # Open dropdown again and test PDF download
        await export_btn.click()
        await page.wait_for_timeout(500)
        async with page.expect_download(timeout=10000) as download_pdf_info:
            await pdf_btn.click()
        download_pdf = await download_pdf_info.value
        download_pdf_path = os.path.join(scratch_dir, download_pdf.suggested_filename)
        await download_pdf.save_as(download_pdf_path)
        print(f"PDF downloaded successfully: {download_pdf_path}, size: {os.path.getsize(download_pdf_path)} bytes")

        await browser.close()
        print("ALL VERIFICATIONS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(verify_export_ui())

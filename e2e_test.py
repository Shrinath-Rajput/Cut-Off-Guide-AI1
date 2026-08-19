import asyncio
from playwright.async_api import async_playwright
import time

async def test_e2e():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        page.on("console", lambda msg: print(f"Browser console: {msg.text}"))
        page.on("pageerror", lambda err: print(f"Browser pageerror: {err}"))
        page.on("requestfailed", lambda req: print(f"Browser request failed: {req.url} - {req.failure}"))

        def log_step(step, status="PASS"):
            print(f"[E2E] {step}: {status}")

        try:
            # 1. Navigation
            await page.goto("http://localhost:5173/")
            await page.wait_for_selector("text=Start Your Journey")
            log_step("Navigate to Welcome Page")

            # 2. Go to Login
            await page.click("text=Start Your Journey")
            await page.wait_for_selector("text=Let's get you started")
            log_step("Navigate to Login Page")

            # 3. Authenticate (Phone)
            await page.fill("input[type='tel']", "9999999999")
            # We intercept the API response to get the dev_otp!
            async with page.expect_response("**/api/auth/send-otp") as response_info:
                await page.click("button:has-text('Send OTP')")
            
            resp = await response_info.value
            data = await resp.json()
            if "dev_otp" in data:
                otp = data["dev_otp"]
                log_step(f"Intercepted dev_otp: {otp}")
            else:
                raise Exception("dev_otp not found in response")

            # Enter OTP
            for i, digit in enumerate(str(otp)):
                await page.fill(f".stitch-otp-group input:nth-child({i+1})", digit)
            
            await page.click("text=Verify OTP")
            
            # Wait for successful login (navigates to /home or /onboarding)
            await page.wait_for_url("**/onboarding*")
            log_step("Authentication & OTP Verification")

            # 4. Onboarding
            await page.fill("#fullName", "E2E Test User")
            await page.fill("#email", "e2e@example.com")
            
            # Click category General
            await page.click("span.category-text:has-text('General')")
            
            await page.click("text=Continue to Academic Details")

            await page.fill("#examScore", "98.5")
            await page.fill("#preferredBranch", "Computer Science")
            await page.click("text=Continue to Preferences")

            await page.fill("#preferredLocation", "Mumbai")
            await page.fill("#budgetRange", "10-15 LPA")
            await page.click("text=Continue to Prediction")

            await page.click("button:has-text('Complete Onboarding')")
            
            # Wait for navigation to /home
            try:
                await page.wait_for_url("**/home*")
                log_step("Navigate to Home via Onboarding")
            except Exception as e:
                await page.screenshot(path="debug_onboarding_timeout.png")
                raise e
            
            # 6. View Profile Check
            await page.click("button[aria-label='Profile']")
            await page.wait_for_selector("input[name='name']")
            
            name_val = await page.input_value("input[name='name']")
            if name_val != "E2E Test User":
                raise Exception(f"Profile name mismatch: {name_val}")
            
            log_step("Profile Verification")

            # Edit Profile
            await page.click("text=Edit Profile")
            await page.fill("input[name='name']", "E2E Edited User")
            await page.click("text=Save Changes")
            await page.wait_for_selector("text=Profile updated successfully!")
            log_step("Profile Update")

            # 6. Colleges
            await page.click("a[href='/colleges']")
            await page.wait_for_selector("input[placeholder='Search colleges, courses or locations...']")
            
            await page.fill("input[placeholder='Search colleges, courses or locations...']", "Stanford")
            # Wait for Stanford to appear
            await page.wait_for_selector("h3:has-text('Stanford')")
            log_step("College Search")

            # 7. College Save
            await page.click("button.bookmark-button")
            log_step("College Save")

            # 8. Predictor (Cutoff)
            await page.click("a[href='/cutoff']")
            await page.wait_for_selector("input[name='percentile']")
            
            # Verify prefilled
            # Use a short loop or wait to handle async prepopulation
            for _ in range(10):
                perc_val = await page.input_value("input[name='percentile']")
                if perc_val == "98.5":
                    break
                import asyncio
                await asyncio.sleep(0.5)
            else:
                raise Exception(f"Predictor prefill mismatch: {perc_val}")
            log_step("Predictor Prefill")

            # Submit predict
            await page.click("button[type='submit']")
            await page.wait_for_selector("text=Prediction result")
            log_step("Prediction Result")

            # 9. Saved Colleges
            await page.click("a[href='/saved']")
            await page.wait_for_selector("h2:has-text('Stanford')")
            
            # Remove saved
            await page.click("button.bookmark-button")
            log_step("Saved Colleges & Remove")

            # 10. Logout
            await page.click("button[aria-label='Profile']")
            await page.wait_for_selector("button:has-text('Log Out')")
            await page.click("button:has-text('Log Out')")
            await page.wait_for_url("**/welcome*")
            log_step("Logout")

            print("[E2E] SUCCESS: ALL TESTS PASSED!")

        except Exception as e:
            print(f"[E2E] FAILED: {e}")
            import traceback
            traceback.print_exc()

        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_e2e())

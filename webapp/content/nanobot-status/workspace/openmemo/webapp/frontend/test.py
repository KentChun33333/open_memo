from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    # Capture console logs and failed requests
    page.on("console", lambda msg: print(f"Console: {msg.text}"))
    page.on("requestfailed", lambda req: print(f"Failed Request: {req.url} - {req.failure}"))
    page.on("response", lambda res: print(f"Response {res.status}: {res.url}") if res.status >= 400 else None)
    
    print("Testing CLOUD...")
    page.goto('https://kentchiu-memo-662008816033.asia-southeast1.run.app/blogs/nanobot_consciousness')
    page.wait_for_load_state('networkidle')

    browser.close()

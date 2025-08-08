import base64
import os
from datetime import datetime
from pathlib import Path

import requests
from cairosvg import svg2png
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from webdriver_manager.chrome import ChromeDriverManager

# Set up Chrome options for headless browsing in container
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-extensions")
options.add_argument("--disable-plugins")
# Keep images enabled to be safe when reading the SVG src

# Initialize the driver with automatic ChromeDriver management
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    print("Loading Worldle page...")
    # Navigate to the page
    driver.get("https://worldle.teuteuf.fr")

    # Wait for the page to load and the image to appear
    print("Waiting for country shape image to load...")
    wait = WebDriverWait(driver, 15)
    img = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "img[alt='country to guess']"))
    )

    # Get the src attribute
    src = img.get_attribute("src")
    print(f"Country shape image URL: {src}")

    # Prepare output directory
    output_dir = Path(os.environ.get("OUTPUT_DIR", "/app/output"))
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    svg_path = output_dir / f"worldle_{timestamp}.svg"
    png_path = output_dir / f"worldle_{timestamp}.png"

    # Fetch or decode the SVG
    if src.startswith("data:image/svg+xml;base64,"):
        b64_data = src.split(",", 1)[1]
        svg_bytes = base64.b64decode(b64_data)
    else:
        # Download content; if PNG/JPEG, still save alongside
        resp = requests.get(src, timeout=20)
        resp.raise_for_status()
        content_type = resp.headers.get("Content-Type", "")
        if "svg" in content_type or src.endswith(".svg"):
            svg_bytes = resp.content
        else:
            # If it's already a raster image, just save and optionally upload
            with open(png_path, "wb") as f:
                f.write(resp.content)
            print(f"Saved raster image to {png_path}")

            # Proceed to Slack upload if configured
            slack_token = os.environ.get("SLACK_BOT_TOKEN")
            slack_channel = os.environ.get("SLACK_CHANNEL")
            if slack_token and slack_channel:
                client = WebClient(token=slack_token)
                try:
                    client.files_upload_v2(
                        channel=slack_channel,
                        file=str(png_path),
                        title=f"Worldle {timestamp}",
                        filename=png_path.name,
                        initial_comment="Het Worldle land van vandaag: https://worldle.teuteuf.fr",
                    )
                    print("Uploaded raster image to Slack")
                except SlackApiError as e:
                    print(
                        f"Slack upload failed: {e.response['error'] if hasattr(e, 'response') else e}"
                    )
            else:
                print(
                    "SLACK_BOT_TOKEN or SLACK_CHANNEL not set; skipping Slack upload."
                )
            # Exit early since we handled raster path; driver will be closed in finally
            raise SystemExit(0)

    # Save SVG
    with open(svg_path, "wb") as f:
        f.write(svg_bytes)
    print(f"Saved SVG to {svg_path}")

    # Convert to PNG with white background
    svg2png(
        bytestring=svg_bytes,
        write_to=str(png_path),
        output_width=1024,
        output_height=1024,
        background_color="white",
    )
    print(f"Converted to PNG at {png_path}")

    # Upload to Slack if configured
    slack_token = os.environ.get("SLACK_BOT_TOKEN")
    slack_channel = os.environ.get("SLACK_CHANNEL")
    if slack_token and slack_channel:
        client = WebClient(token=slack_token)
        try:
            client.files_upload_v2(
                channel=slack_channel,
                file=str(png_path),
                title=f"Worldle {timestamp}",
                filename=png_path.name,
                initial_comment="Het Worldle land van vandaag: https://worldle.teuteuf.fr",
            )
            print("Uploaded PNG to Slack")
        except SlackApiError as e:
            print(
                f"Slack upload failed: {e.response['error'] if hasattr(e, 'response') else e}"
            )
    else:
        print("SLACK_BOT_TOKEN or SLACK_CHANNEL not set; skipping Slack upload.")

except Exception as e:
    print(f"Error: {e}")
    # Print page source for debugging
    print("Page source:")
    print(driver.page_source[:1000])  # First 1000 chars

finally:
    driver.quit()

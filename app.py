from flask import Flask, render_template, request
from playwright.sync_api import sync_playwright
import json
import os
import time
import re
from collections import Counter

app = Flask(__name__)

def extract_emojis(text):
    if not text: return []
    return re.findall(r'[^\w\s,.:!?-]', text)

def scrape_instagram(target_user):
    data = {
        'posts': [],
        'followers': "0",
        'top_hashtags': [],
        'top_emojis': []
    }
    
    with sync_playwright() as p:
        # headless=False para que veas qué está bloqueando al bot
        browser = p.chromium.launch(headless=False, slow_mo=100)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 1000}
        )

        if os.path.exists('cookies.json'):
            with open('cookies.json', 'r') as f:
                cookies = json.load(f)
                for cookie in cookies:
                    if cookie.get('sameSite') not in ["Strict", "Lax", "None"]:
                        cookie['sameSite'] = 'Lax'
                    if 'id' in cookie: del cookie['id']
                context.add_cookies(cookies)
        
        page = context.new_page()
        
        try:
            print(f"Navegando al perfil de @{target_user}...")
            page.goto(f"https://www.instagram.com/{target_user}/", wait_until="load", timeout=60000)
            time.sleep(5)

            # 1. CERRAR POP-UPS (Si aparecen y bloquean la vista)
            try:
                # Intenta cerrar "Ahora no" en avisos de notificaciones o login
                if page.get_by_role("button", name="Ahora no").is_visible():
                    page.get_by_role("button", name="Ahora no").click()
                    print("Pop-up cerrado.")
            except: pass

            # 2. Seguidores
            try:
                f_element = page.get_by_text("seguidores").first
                data['followers'] = f_element.inner_text().split(" ")[0]
            except: data['followers'] = "N/A"

            # 3. Scroll y espera de carga
            page.mouse.wheel(0, 1000)
            time.sleep(4)

            # 4. Extracción de Publicaciones con manejo de errores interno
            post_links = page.locator("a[href*='/p/'], a[href*='/reels/']").all()
            print(f"Elementos detectados: {len(post_links)}")

            all_hashtags = []
            all_emojis = []

            for link in post_links:
                if len(data['posts']) >= 10: break

                try:
                    # Esperamos máximo 3 segundos por cada imagen para no trabar el bot
                    img = link.locator("img").first
                    img.wait_for(state="attached", timeout=3000)
                    
                    img_url = img.get_attribute("src")
                    if img_url:
                        caption = img.get_attribute("alt") or ""
                        all_hashtags.extend(re.findall(r"#\w+", caption))
                        all_emojis.extend(extract_emojis(caption))

                        data['posts'].append({
                            'img_url': img_url,
                            'url': "https://www.instagram.com" + link.get_attribute("href"),
                            'caption': caption[:70] + "..."
                        })
                except Exception as post_err:
                    print(f"Saltando un post por error de carga: {post_err}")
                    continue # Si un post falla, sigue con el siguiente
            
            # 5. Estadísticas
            data['top_hashtags'] = [tag for tag, _ in Counter(all_hashtags).most_common(5)]
            data['top_emojis'] = [em for em, _ in Counter(all_emojis).most_common(6)]

        except Exception as e:
            print(f"Error general: {e}")
            page.screenshot(path="error_fatal.png")
        finally:
            browser.close()
            
    return data

@app.route('/', methods=['GET', 'POST'])
def index():
    res = None
    if request.method == 'POST':
        user = request.form.get('username').replace('@', '').strip()
        res = scrape_instagram(user)
    return render_template('index.html', data=res)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
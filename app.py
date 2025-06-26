from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests
import time
import os
from PIL import Image
from io import BytesIO

# MODEL_URL = "https://api-inference.huggingface.co/models/CompVis/stable-diffusion-v1-4"
# MODEL_NAME = "Stable Diffusion v1.4"
MODEL_URL = "https://image.pollinations.ai/prompt/"
MODEL_NAME = "Pollinations AI"

# Token artık gerekmiyor - Pollinations.ai tamamen ücretsiz

def generate_ai_image(prompt):
    print(f"🎨 Model: {MODEL_NAME}")
    print(f"📝 Prompt: '{prompt}'")
    print(f"🔍 Size: 1024x1024")
    print("⏳ Görsel oluşturuluyor...")
    
    start_time = time.time()
    
    try:
        # Pollinations.ai için URL encode edilmiş prompt
        import urllib.parse
        encoded_prompt = urllib.parse.quote(prompt)
        
        # Pollinations.ai parametreleri ile tam URL
        full_url = f"{MODEL_URL}{encoded_prompt}?width=1024&height=1024&model=flux&enhance=true"
        
        # Basit GET request
        response = requests.get(full_url, timeout=30)
        
        if response.status_code == 200:
            # Generated images klasörünü kontrol et ve oluştur
            generated_dir = os.path.join('static', 'images', 'generated')
            if not os.path.exists(generated_dir):
                os.makedirs(generated_dir)
            
            # Görsel dosyasını kaydet
            image = Image.open(BytesIO(response.content))
            timestamp = int(time.time())
            filename = f"generated_{timestamp}.png"
            filepath = os.path.join(generated_dir, filename)
            image.save(filepath)
            
            end_time = time.time()
            generation_time = end_time - start_time
                        
            print(f"✅ Görsel kaydedildi: {filepath}")
            print(f"🕒 Süre: {generation_time:.2f} saniye")
            
            # Frontend için relative path
            relative_path = f"images/generated/{filename}"
            return relative_path, True, f"Image generated successfully in {generation_time:.2f} seconds"
            
        else:
            error_msg = f"API Error: {response.status_code}"
            print(f"❌ Hata: {response.status_code}")
            if response.text:
                print(f"Detay: {response.text}")
            return None, False, error_msg
            
    except requests.exceptions.Timeout:
        error_msg = "Request timeout. Please try again."
        print("❌ Zaman aşımı! Lütfen tekrar deneyin.")
        return None, False, error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"❌ Beklenmeyen hata: {e}")
        return None, False, error_msg

app = Flask(__name__)

# Ana sayfa - tek sayfa tasarım
@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')

# AI Image Generator handler
@app.route('/generate-image', methods=['POST'])
def generate_image():
    try:
        # Form verilerini al
        prompt = request.form.get('prompt')
        
        # Validation
        if not prompt or not prompt.strip():
            return jsonify({
                'success': False,
                'message': 'Please provide a valid prompt.'
            }), 400 
        # Görsel oluştur (token gereksiz)
        image_path, success, message = generate_ai_image(prompt.strip())
        
        if success:
            response = {
                'success': True,
                'message': message,
                'prompt': prompt,
                'size': '1024x1024',
                'image_url': url_for('static', filename=image_path)
            }
            return jsonify(response)
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 500
            
    except Exception as e:
        print(f"❌ Error in generate_image route: {e}")
        return jsonify({
            'success': False,
            'message': 'An unexpected error occurred. Please try again.'
        }), 500

# Contact form handler
@app.route('/contact-form', methods=['POST'])
def contact_form():
    if request.method == 'POST':
        # Form verilerini işle
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        
        # Form verilerini console'a yazdır (geliştirme amaçlı)
        print(f"📧 İletişim Formu Gönderildi:")
        print(f"👤 İsim: {name}")
        print(f"📧 Email: {email}")
        print(f"📞 Telefon: {phone}")
        print(f"💬 Mesaj: {message}")
        
        return jsonify({
            'success': True,
            'message': 'Your message has been sent successfully! We will get back to you soon.'
        })

# 404 Error Handler
@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('index'))

# 500 Error Handler
@app.errorhandler(500)
def internal_server_error(e):
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
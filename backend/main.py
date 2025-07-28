from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import sqlite3
import uuid
import random
from datetime import datetime
import os
from typing import Optional

app = FastAPI(title="Dubai Tatil Çekilişi API")

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Veritabanı bağlantısı
DATABASE = "test.db"

def init_db():
    """Veritabanını başlat"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Kullanıcılar tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Çekilişler tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_draws (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            card_index INTEGER,
            result TEXT,
            prize_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Form gönderimleri tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS form_submissions (
            id TEXT PRIMARY KEY,
            user_draw_id TEXT,
            full_name TEXT,
            email TEXT,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_draw_id) REFERENCES user_draws (id)
        )
    ''')
    
    # Dubai tatil ödülü sayacı tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dubai_prize_counter (
            id INTEGER PRIMARY KEY,
            count INTEGER DEFAULT 0,
            max_count INTEGER DEFAULT 100000,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Sayaç tablosunu başlat
    cursor.execute('''
        INSERT OR IGNORE INTO dubai_prize_counter (id, count, max_count, is_active)
        VALUES (1, 0, 100000, 1)
    ''')
    
    conn.commit()
    conn.close()

# Veritabanını başlat
init_db()

# Pydantic modelleri
class CreateUserRequest(BaseModel):
    user_id: str

class PlayRequest(BaseModel):
    user_id: str
    selected_card_index: int

class FormSubmissionRequest(BaseModel):
    user_draw_id: str
    full_name: str
    email: str
    phone: str

# Dubai tatil ödülü sayacını kontrol et
def check_dubai_prize_limit():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT count, max_count, is_active FROM dubai_prize_counter WHERE id = 1")
    result = cursor.fetchone()
    conn.close()
    
    if result:
        count, max_count, is_active = result
        return count, max_count, is_active
    return 0, 100000, True

# Dubai tatil ödülü sayacını artır
def increment_dubai_prize_count():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("UPDATE dubai_prize_counter SET count = count + 1 WHERE id = 1")
    conn.commit()
    conn.close()

# Oyunu durdur
def stop_game():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("UPDATE dubai_prize_counter SET is_active = 0 WHERE id = 1")
    conn.commit()
    conn.close()

@app.post("/create-user")
async def create_user(request: CreateUserRequest):
    """Yeni kullanıcı oluştur"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (id) VALUES (?)", (request.user_id,))
        conn.commit()
        conn.close()
        return {"success": True, "user_id": request.user_id}
    except sqlite3.IntegrityError:
        return {"success": True, "user_id": request.user_id}  # Kullanıcı zaten var
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/play")
async def play_game(request: PlayRequest):
    """Kart çekme oyunu"""
    try:
        # Dubai tatil ödülü limitini kontrol et
        count, max_count, is_active = check_dubai_prize_limit()
        
        if not is_active:
            return {"result": "game_stopped", "message": "Oyun durduruldu. Dubai tatil ödülü 100.000 kişiye ulaştı!"}
        
        # Kullanıcının daha önce oynayıp oynamadığını kontrol et
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM user_draws WHERE user_id = ?", (request.user_id,))
        user_attempts = cursor.fetchone()[0]
        conn.close()
        
        # 3 kere oynamışsa oyun biter
        if user_attempts >= 3:
            return {"result": "max_attempts", "message": "Maksimum oynama hakkınız doldu!"}
        
        # Sabit kart içerikleri
        card_contents = [
            "tekrar_dene",  # Kart 0
            "tekrar_dene",  # Kart 1  
            "tekrar_dene",  # Kart 2
            "dubai_tatil",  # Kart 3
            "samsung_tab",  # Kart 4
            "airpods_4",    # Kart 5
            "tekrar_dene",  # Kart 6
            "tekrar_dene",  # Kart 7
            "tekrar_dene"   # Kart 8
        ]
        
        # Seçilen kartın içeriğini al
        selected_card_content = card_contents[request.selected_card_index]
        
        if selected_card_content == "tekrar_dene":
            # Tekrar dene
            user_draw_id = str(uuid.uuid4())
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO user_draws (id, user_id, card_index, result, prize_type) VALUES (?, ?, ?, ?, ?)",
                (user_draw_id, request.user_id, request.selected_card_index, "retry", "tekrar_dene")
            )
            conn.commit()
            conn.close()
            
            return {
                "result": "retry",
                "user_draw_id": user_draw_id,
                "message": "Tekrar deneyin!"
            }
        else:
            # Ödül kazandı
            if selected_card_content == "dubai_tatil":
                # Dubai tatil ödülü limitini kontrol et
                if count >= max_count:
                    # Limit dolmuşsa oyunu durdur
                    stop_game()
                    return {"result": "game_stopped", "message": "Dubai tatil ödülü 100.000 kişiye ulaştı! Oyun sona erdi."}
                
                # Dubai tatil ödülü sayacını artır
                increment_dubai_prize_count()
                prize_message = "Tebrikler! Dubai tatil ödülünü kazandınız!"
            elif selected_card_content == "samsung_tab":
                prize_message = "Tebrikler! Samsung Tab 10 ödülünü kazandınız!"
            elif selected_card_content == "airpods_4":
                prize_message = "Tebrikler! AirPods 4 ödülünü kazandınız!"
            else:
                prize_message = "Tebrikler! Ödül kazandınız!"
            
            # Ödül ver
            user_draw_id = str(uuid.uuid4())
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO user_draws (id, user_id, card_index, result, prize_type) VALUES (?, ?, ?, ?, ?)",
                (user_draw_id, request.user_id, request.selected_card_index, "prize", selected_card_content)
            )
            conn.commit()
            conn.close()
            
            return {
                "result": "prize",
                "user_draw_id": user_draw_id,
                "prize_type": selected_card_content,
                "message": prize_message
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/submit-form")
async def submit_form(request: FormSubmissionRequest):
    """Form gönderimi"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # user_draw_id'nin geçerli olup olmadığını kontrol et
        cursor.execute("SELECT result FROM user_draws WHERE id = ?", (request.user_draw_id,))
        draw = cursor.fetchone()
        
        if not draw:
            raise HTTPException(status_code=404, detail="Geçersiz user_draw_id")
        
        if draw[0] != "prize":
            raise HTTPException(status_code=400, detail="Bu çekiliş ödül değil")
        
        # Formu kaydet
        form_id = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO form_submissions (id, user_draw_id, full_name, email, phone) VALUES (?, ?, ?, ?, ?)",
            (form_id, request.user_draw_id, request.full_name, request.email, request.phone)
        )
        conn.commit()
        conn.close()
        
        return {"success": True, "message": "Form başarıyla gönderildi!"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/forms")
async def admin_forms(
    kontrol_paneli: str,
    username: str,
    password: str
):
    """Admin paneli - form listesi"""
    # Basit authentication (gerçek projede daha güvenli olmalı)
    if kontrol_paneli != "supergizli1234" or username != "bugrakrmrcn" or password != "123789Green":
        raise HTTPException(status_code=401, detail="Yetkisiz erişim")
    
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Form gönderimlerini ve ödül bilgilerini getir
        cursor.execute('''
            SELECT 
                fs.full_name,
                fs.email,
                fs.phone,
                ud.prize_type,
                fs.created_at
            FROM form_submissions fs
            JOIN user_draws ud ON fs.user_draw_id = ud.id
            ORDER BY fs.created_at DESC
        ''')
        
        forms = cursor.fetchall()
        conn.close()
        
        # HTML tablosu oluştur
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Dubai Tatil Çekilişi - Admin Paneli</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #ff6b35; color: white; }
                tr:nth-child(even) { background-color: #f2f2f2; }
                .stats { background: #ff8c42; color: white; padding: 10px; margin-bottom: 20px; border-radius: 5px; }
            </style>
        </head>
        <body>
            <h1>Dubai Tatil Çekilişi - Admin Paneli</h1>
        """
        
        # İstatistikler
        count, max_count, is_active = check_dubai_prize_limit()
        html_content += f"""
        <div class="stats">
            <h3>İstatistikler:</h3>
            <p>Dubai Tatil Ödülü Kazananlar: {count} / {max_count}</p>
            <p>Oyun Durumu: {'Aktif' if is_active else 'Durduruldu'}</p>
        </div>
        """
        
        html_content += """
            <table>
                <tr>
                    <th>Ad Soyad</th>
                    <th>E-posta</th>
                    <th>Telefon</th>
                    <th>Ödül Türü</th>
                    <th>Tarih</th>
                </tr>
        """
        
        for form in forms:
            html_content += f"""
                <tr>
                    <td>{form[0]}</td>
                    <td>{form[1]}</td>
                    <td>{form[2]}</td>
                    <td>{form[3]}</td>
                    <td>{form[4]}</td>
                </tr>
            """
        
        html_content += """
            </table>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """Oyun istatistikleri"""
    try:
        count, max_count, is_active = check_dubai_prize_limit()
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Toplam kullanıcı sayısı
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        # Toplam çekiliş sayısı
        cursor.execute("SELECT COUNT(*) FROM user_draws")
        total_draws = cursor.fetchone()[0]
        
        # Ödül kazananlar
        cursor.execute("SELECT COUNT(*) FROM user_draws WHERE result = 'prize'")
        total_prizes = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "dubai_prize_count": count,
            "dubai_prize_max": max_count,
            "game_active": is_active,
            "total_users": total_users,
            "total_draws": total_draws,
            "total_prizes": total_prizes
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
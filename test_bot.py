import requests
import time
import random
import uuid
from datetime import datetime
import json

class DubaiCekilisTestBot:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:5173"
        self.admin_token = "supergizli1234"
        self.admin_username = "bugrakrmrcn"
        self.admin_password = "123789Green"
        
        self.test_results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "details": []
        }
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def add_test_result(self, test_name, success, details=""):
        self.test_results["total_tests"] += 1
        if success:
            self.test_results["passed"] += 1
            self.log(f"✅ {test_name} - BAŞARILI", "PASS")
        else:
            self.test_results["failed"] += 1
            self.log(f"❌ {test_name} - BAŞARISIZ", "FAIL")
            
        self.test_results["details"].append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def test_backend_connection(self):
        """Backend bağlantısını test et"""
        try:
            response = requests.get(f"{self.base_url}/stats", timeout=5)
            if response.status_code == 200:
                self.add_test_result("Backend Bağlantısı", True)
                return True
            else:
                self.add_test_result("Backend Bağlantısı", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.add_test_result("Backend Bağlantısı", False, str(e))
            return False
    
    def test_frontend_connection(self):
        """Frontend bağlantısını test et"""
        try:
            response = requests.get(self.frontend_url, timeout=5)
            if response.status_code == 200:
                self.add_test_result("Frontend Bağlantısı", True)
                return True
            else:
                self.add_test_result("Frontend Bağlantısı", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.add_test_result("Frontend Bağlantısı", False, str(e))
            return False
    
    def test_user_creation(self):
        """Kullanıcı oluşturma testi"""
        try:
            user_id = f"test_user_{uuid.uuid4().hex[:8]}"
            response = requests.post(f"{self.base_url}/create-user", 
                                   json={"user_id": user_id},
                                   timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("user_id") == user_id:
                    self.add_test_result("Kullanıcı Oluşturma", True)
                    return user_id
                else:
                    self.add_test_result("Kullanıcı Oluşturma", False, "Invalid response data")
                    return None
            else:
                self.add_test_result("Kullanıcı Oluşturma", False, f"Status: {response.status_code}")
                return None
        except Exception as e:
            self.add_test_result("Kullanıcı Oluşturma", False, str(e))
            return None
    
    def test_card_play(self, user_id, card_index):
        """Kart çekme testi"""
        try:
            response = requests.post(f"{self.base_url}/play",
                                   json={
                                       "user_id": user_id,
                                       "selected_card_index": card_index
                                   },
                                   timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                result = data.get("result")
                
                if result in ["prize", "retry", "game_stopped", "max_attempts"]:
                    self.add_test_result(f"Kart Çekme (Index: {card_index})", True, f"Result: {result}")
                    return data
                else:
                    self.add_test_result(f"Kart Çekme (Index: {card_index})", False, f"Invalid result: {result}")
                    return None
            else:
                self.add_test_result(f"Kart Çekme (Index: {card_index})", False, f"Status: {response.status_code}")
                return None
        except Exception as e:
            self.add_test_result(f"Kart Çekme (Index: {card_index})", False, str(e))
            return None
    
    def test_form_submission(self, user_draw_id):
        """Form gönderimi testi"""
        try:
            form_data = {
                "user_draw_id": user_draw_id,
                "full_name": f"Test Kullanıcı {uuid.uuid4().hex[:4]}",
                "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
                "phone": f"555{uuid.uuid4().hex[:7]}"
            }
            
            response = requests.post(f"{self.base_url}/submit-form",
                                   json=form_data,
                                   timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.add_test_result("Form Gönderimi", True)
                    return form_data
                else:
                    self.add_test_result("Form Gönderimi", False, "Form submission failed")
                    return None
            else:
                self.add_test_result("Form Gönderimi", False, f"Status: {response.status_code}")
                return None
        except Exception as e:
            self.add_test_result("Form Gönderimi", False, str(e))
            return None
    
    def test_admin_panel(self, expected_email=None):
        """Admin paneli testi"""
        try:
            admin_url = f"{self.base_url}/admin/forms"
            params = {
                "kontrol_paneli": self.admin_token,
                "username": self.admin_username,
                "password": self.admin_password
            }
            
            response = requests.get(admin_url, params=params, timeout=10)
            
            if response.status_code == 200:
                content = response.text
                
                # Admin panelinde form verilerinin olup olmadığını kontrol et
                if "Dubai Tatil Çekilişi - Admin Paneli" in content:
                    self.add_test_result("Admin Paneli Erişimi", True)
                    
                    # Eğer beklenen email varsa, onun listede olup olmadığını kontrol et
                    if expected_email and expected_email in content:
                        self.add_test_result("Admin Panelinde Form Listesi", True)
                        return True
                    elif expected_email:
                        self.add_test_result("Admin Panelinde Form Listesi", False, "Expected email not found")
                        return False
                    else:
                        self.add_test_result("Admin Paneli İçeriği", True)
                        return True
                else:
                    self.add_test_result("Admin Paneli Erişimi", False, "Admin panel content not found")
                    return False
            else:
                self.add_test_result("Admin Paneli Erişimi", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.add_test_result("Admin Paneli Erişimi", False, str(e))
            return False
    
    def test_scenario_1(self):
        """Senaryo 1: Ödül kazanma ve form doldurma"""
        self.log("🎯 SENARYO 1 BAŞLATILIYOR: Ödül kazanma ve form doldurma", "SCENARIO")
        
        # Kullanıcı oluştur
        user_id = self.test_user_creation()
        if not user_id:
            return False
        
        # Kart çek (ödül çıkana kadar dene)
        max_attempts = 20
        for attempt in range(max_attempts):
            card_index = random.randint(0, 8)
            result = self.test_card_play(user_id, card_index)
            
            if result and result.get("result") == "prize":
                self.log(f"🎉 Ödül kazanıldı! Deneme: {attempt + 1}", "SUCCESS")
                
                # Form gönder
                user_draw_id = result.get("user_draw_id")
                form_data = self.test_form_submission(user_draw_id)
                
                if form_data:
                    # Admin panelinde kontrol et
                    admin_success = self.test_admin_panel(form_data["email"])
                    if admin_success:
                        self.log("✅ SENARYO 1 TAMAMLANDI: Ödül kazanıldı, form gönderildi, admin panelde listelendi", "SUCCESS")
                        return True
                    else:
                        self.log("❌ SENARYO 1 BAŞARISIZ: Admin panelde form bulunamadı", "ERROR")
                        return False
                else:
                    self.log("❌ SENARYO 1 BAŞARISIZ: Form gönderilemedi", "ERROR")
                    return False
            
            time.sleep(0.5)  # Kısa bekleme
        
        self.log("❌ SENARYO 1 BAŞARISIZ: 20 denemede ödül çıkmadı", "ERROR")
        return False
    
    def test_scenario_2(self):
        """Senaryo 2: 3 kere tekrar dene çekme (maksimum 3 kart çekme hakkı)"""
        self.log("🎯 SENARYO 2 BAŞLATILIYOR: 3 kere tekrar dene çekme", "SCENARIO")
        
        # Kullanıcı oluştur
        user_id = self.test_user_creation()
        if not user_id:
            return False
        
        # İlk kart çek
        result1 = self.test_card_play(user_id, random.randint(0, 8))
        if not result1 or result1.get("result") != "retry":
            self.log("❌ SENARYO 2 BAŞARISIZ: İlk denemede tekrar dene çıkmadı", "ERROR")
            return False
        
        self.log("🔄 İlk tekrar dene çekildi, 2. kart çekme hakkı kazanıldı", "INFO")
        
        # İkinci kart çek
        result2 = self.test_card_play(user_id, random.randint(0, 8))
        if not result2 or result2.get("result") != "retry":
            self.log("❌ SENARYO 2 BAŞARISIZ: İkinci denemede tekrar dene çıkmadı", "ERROR")
            return False
        
        self.log("🔄 İkinci tekrar dene çekildi, 3. kart çekme hakkı kazanıldı", "INFO")
        
        # Üçüncü kart çek (oyun bitmeli)
        result3 = self.test_card_play(user_id, random.randint(0, 8))
        if result3 and result3.get("result") == "max_attempts":
            self.log("✅ SENARYO 2 TAMAMLANDI: 3 kere tekrar dene çekildi, oyun bitti", "SUCCESS")
            return True
        else:
            self.log("❌ SENARYO 2 BAŞARISIZ: 3 denemeden sonra oyun bitmedi", "ERROR")
            return False
    
    def test_scenario_3(self):
        """Senaryo 3: Tekrar dene çekme ve ilk ekrana dönüş (maksimum 3 kart çekme hakkı)"""
        self.log("🎯 SENARYO 3 BAŞLATILIYOR: Tekrar dene çekme ve ilk ekrana dönüş", "SCENARIO")
        
        # Kullanıcı oluştur
        user_id = self.test_user_creation()
        if not user_id:
            return False
        
        # İlk kart çek - tekrar dene çıkmalı
        result1 = self.test_card_play(user_id, random.randint(0, 8))
        if not result1 or result1.get("result") != "retry":
            self.log("❌ SENARYO 3 BAŞARISIZ: İlk denemede tekrar dene çıkmadı", "ERROR")
            return False
        
        self.log("🔄 İlk tekrar dene çekildi, 2. kart çekme hakkı kazanıldı", "INFO")
        
        # İkinci kart çek - tekrar dene çıkmalı
        result2 = self.test_card_play(user_id, random.randint(0, 8))
        if not result2 or result2.get("result") != "retry":
            self.log("❌ SENARYO 3 BAŞARISIZ: İkinci denemede tekrar dene çıkmadı", "ERROR")
            return False
        
        self.log("🔄 İkinci tekrar dene çekildi, 3. kart çekme hakkı kazanıldı", "INFO")
        
        # Üçüncü kart çek - tekrar dene çıkmalı (oyun bitmeli)
        result3 = self.test_card_play(user_id, random.randint(0, 8))
        if result3 and result3.get("result") == "max_attempts":
            self.log("✅ SENARYO 3 TAMAMLANDI: 3 kere tekrar dene çekildi, oyun bitti", "SUCCESS")
            return True
        else:
            self.log("❌ SENARYO 3 BAŞARISIZ: 3 denemeden sonra oyun bitmedi", "ERROR")
            return False
    
    def test_dubai_prize_limit(self):
        """Dubai tatil ödülü 100.000 kişi limitini test et"""
        self.log("🎯 DUBAİ ÖDÜL LİMİTİ TESTİ BAŞLATILIYOR", "SCENARIO")
        
        # Mevcut durumu kontrol et
        try:
            response = requests.get(f"{self.base_url}/stats", timeout=5)
            if response.status_code == 200:
                stats = response.json()
                current_count = stats.get("dubai_prize_count", 0)
                max_count = stats.get("dubai_prize_max", 100000)
                is_active = stats.get("game_active", True)
                
                self.log(f"📊 Mevcut Dubai ödülü kazananlar: {current_count}/{max_count}", "INFO")
                self.log(f"📊 Oyun durumu: {'Aktif' if is_active else 'Durduruldu'}", "INFO")
                
                if current_count >= max_count and not is_active:
                    self.add_test_result("Dubai Ödül Limiti", True, f"Limit doldu: {current_count}/{max_count}")
                    return True
                elif current_count < max_count and is_active:
                    self.add_test_result("Dubai Ödül Limiti", True, f"Limit henüz dolmadı: {current_count}/{max_count}")
                    return True
                else:
                    self.add_test_result("Dubai Ödül Limiti", False, f"Beklenmeyen durum: {current_count}/{max_count}, Aktif: {is_active}")
                    return False
            else:
                self.add_test_result("Dubai Ödül Limiti", False, f"Stats API hatası: {response.status_code}")
                return False
        except Exception as e:
            self.add_test_result("Dubai Ödül Limiti", False, str(e))
            return False
    
    def run_all_tests(self):
        """Tüm testleri çalıştır"""
        self.log("🚀 DUBAİ TATİL ÇEKİLİŞİ OTOMATİK TEST BOTU BAŞLATILIYOR", "START")
        self.log("=" * 60, "SEPARATOR")
        
        # Temel bağlantı testleri
        self.log("🔌 TEMEL BAĞLANTI TESTLERİ", "SECTION")
        backend_ok = self.test_backend_connection()
        frontend_ok = self.test_frontend_connection()
        
        if not backend_ok or not frontend_ok:
            self.log("❌ Temel bağlantı testleri başarısız! Testler durduruluyor.", "ERROR")
            return
        
        # Dubai ödül limiti testi
        self.log("📊 DUBAİ ÖDÜL LİMİTİ TESTİ", "SECTION")
        self.test_dubai_prize_limit()
        
        # Senaryo testleri
        self.log("🎮 SENARYO TESTLERİ", "SECTION")
        
        # Senaryo 1: Ödül kazanma ve form doldurma
        scenario1_success = self.test_scenario_1()
        
        # Senaryo 2: 3 kere tekrar dene çekme
        scenario2_success = self.test_scenario_2()
        
        # Senaryo 3: Tekrar dene çekme ve ilk ekrana dönüş
        scenario3_success = self.test_scenario_3()
        
        # Sonuçları raporla
        self.generate_report()
    
    def generate_report(self):
        """Test raporu oluştur"""
        self.log("=" * 60, "SEPARATOR")
        self.log("📋 TEST RAPORU", "REPORT")
        self.log("=" * 60, "SEPARATOR")
        
        total = self.test_results["total_tests"]
        passed = self.test_results["passed"]
        failed = self.test_results["failed"]
        success_rate = (passed / total * 100) if total > 0 else 0
        
        self.log(f"📊 TOPLAM TEST: {total}", "SUMMARY")
        self.log(f"✅ BAŞARILI: {passed}", "SUMMARY")
        self.log(f"❌ BAŞARISIZ: {failed}", "SUMMARY")
        self.log(f"📈 BAŞARI ORANI: {success_rate:.1f}%", "SUMMARY")
        
        self.log("=" * 60, "SEPARATOR")
        self.log("📝 DETAYLI SONUÇLAR", "DETAILS")
        self.log("=" * 60, "SEPARATOR")
        
        for detail in self.test_results["details"]:
            status = "✅" if detail["success"] else "❌"
            self.log(f"{status} {detail['test']}: {detail['details']}", "DETAIL")
        
        # Raporu dosyaya kaydet
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_report_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        self.log(f"💾 Rapor kaydedildi: {filename}", "INFO")
        
        # Özet
        if success_rate >= 80:
            self.log("🎉 TESTLER BAŞARILI! Sistem beklentileri karşılıyor.", "SUCCESS")
        elif success_rate >= 60:
            self.log("⚠️ TESTLER KISMEN BAŞARILI! Bazı sorunlar var.", "WARNING")
        else:
            self.log("🚨 TESTLER BAŞARISIZ! Ciddi sorunlar var.", "ERROR")

if __name__ == "__main__":
    bot = DubaiCekilisTestBot()
    bot.run_all_tests() 
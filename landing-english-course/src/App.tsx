import React, { useState, useEffect } from 'react';
import './App.css';

interface Card {
  id: number;
  name: string;
  image: string;
  isRevealed: boolean;
  isSelected: boolean;
}

interface GameState {
  cards: Card[];
  userAttempts: number;
  maxAttempts: number;
  gamePhase: 'playing' | 'form' | 'gameOver' | 'gameStopped';
  selectedCard: Card | null;
  userDrawId: string | null;
}

function App() {
  const [gameState, setGameState] = useState<GameState>({
    cards: [
      { id: 1, name: 'Kart 1 - Tekrar Dene', image: '/card-back.svg', isRevealed: false, isSelected: false },
      { id: 2, name: 'Kart 2 - Tekrar Dene', image: '/card-back.svg', isRevealed: false, isSelected: false },
      { id: 3, name: 'Kart 3 - Tekrar Dene', image: '/card-back.svg', isRevealed: false, isSelected: false },
      { id: 4, name: 'Kart 4 - Dubai Tatili', image: '/card-back.svg', isRevealed: false, isSelected: false },
      { id: 5, name: 'Kart 5 - Samsung Tab 10', image: '/card-back.svg', isRevealed: false, isSelected: false },
      { id: 6, name: 'Kart 6 - AirPods 4', image: '/card-back.svg', isRevealed: false, isSelected: false },
      { id: 7, name: 'Kart 7 - Tekrar Dene', image: '/card-back.svg', isRevealed: false, isSelected: false },
      { id: 8, name: 'Kart 8 - Tekrar Dene', image: '/card-back.svg', isRevealed: false, isSelected: false },
      { id: 9, name: 'Kart 9 - Tekrar Dene', image: '/card-back.svg', isRevealed: false, isSelected: false },
    ],
    userAttempts: 0,
    maxAttempts: 3,
    gamePhase: 'playing',
    selectedCard: null,
    userDrawId: null
  });

  const [userId, setUserId] = useState<string>('');

  // Kullanıcı oluştur
  useEffect(() => {
    const createUser = async () => {
      try {
        console.log('Kullanıcı oluşturuluyor...');
        const user_id = generateUserId();
        console.log('Generated User ID:', user_id);
        
        const response = await fetch('http://localhost:8000/create-user', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ user_id: user_id }),
        });
        
        console.log('Create user response:', response.status);
        
        if (response.ok) {
          const data = await response.json();
          console.log('User created:', data);
          setUserId(data.user_id);
        } else {
          console.error('User creation failed:', response.status);
        }
      } catch (error) {
        console.error('Kullanıcı oluşturulamadı:', error);
      }
    };

    createUser();
  }, []);

  const generateUserId = () => {
    return 'user_' + Math.random().toString(36).substr(2, 9);
  };

  const handleCardClick = async (cardIndex: number) => {
    console.log('Kart tıklandı:', cardIndex);
    console.log('Oyun durumu:', gameState.gamePhase);
    console.log('User ID:', userId);
    
    if (gameState.gamePhase !== 'playing') {
      console.log('Oyun aktif değil!');
      return;
    }

    try {
      console.log('API çağrısı yapılıyor...');
      const response = await fetch('http://localhost:8000/play', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          selected_card_index: cardIndex
        }),
      });

      console.log('API yanıtı:', response.status);
      const data = await response.json();
      console.log('API data:', data);

      if (data.result === 'prize') {
        // Ödül çıktı
        setGameState(prev => ({
          ...prev,
          gamePhase: 'form',
          userDrawId: data.user_draw_id,
          selectedCard: prev.cards[cardIndex]
        }));
      } else if (data.result === 'game_stopped') {
        // Oyun durduruldu
        setGameState(prev => ({
          ...prev,
          gamePhase: 'gameStopped'
        }));
      } else if (data.result === 'retry') {
        // Tekrar dene
        setGameState(prev => ({
          ...prev,
          userAttempts: prev.userAttempts + 1,
          cards: prev.cards.map((card, index) => 
            index === cardIndex ? { ...card, isRevealed: true, isSelected: true } : card
          )
        }));

        // 3 kere tekrar dene çektiyse oyun biter
        if (gameState.userAttempts + 1 >= gameState.maxAttempts) {
          setTimeout(() => {
            setGameState(prev => ({ ...prev, gamePhase: 'gameOver' }));
          }, 2000);
        } else {
          // İlk ekrana dön
          setTimeout(() => {
            setGameState(prev => ({
              ...prev,
              cards: prev.cards.map(card => ({ ...card, isRevealed: false, isSelected: false }))
            }));
          }, 2000);
        }
      }
    } catch (error) {
      console.error('Kart çekme hatası:', error);
    }
  };

  const resetGame = () => {
    setGameState({
      cards: [
        { id: 1, name: 'Kart 1 - Tekrar Dene', image: '/card-back.svg', isRevealed: false, isSelected: false },
        { id: 2, name: 'Kart 2 - Tekrar Dene', image: '/card-back.svg', isRevealed: false, isSelected: false },
        { id: 3, name: 'Kart 3 - Tekrar Dene', image: '/card-back.svg', isRevealed: false, isSelected: false },
        { id: 4, name: 'Kart 4 - Dubai Tatili', image: '/card-back.svg', isRevealed: false, isSelected: false },
        { id: 5, name: 'Kart 5 - Samsung Tab 10', image: '/card-back.svg', isRevealed: false, isSelected: false },
        { id: 6, name: 'Kart 6 - AirPods 4', image: '/card-back.svg', isRevealed: false, isSelected: false },
        { id: 7, name: 'Kart 7 - Tekrar Dene', image: '/card-back.svg', isRevealed: false, isSelected: false },
        { id: 8, name: 'Kart 8 - Tekrar Dene', image: '/card-back.svg', isRevealed: false, isSelected: false },
        { id: 9, name: 'Kart 9 - Tekrar Dene', image: '/card-back.svg', isRevealed: false, isSelected: false },
      ],
      userAttempts: 0,
      maxAttempts: 3,
      gamePhase: 'playing',
      selectedCard: null,
      userDrawId: null
    });
  };

  if (gameState.gamePhase === 'form') {
    return <FormScreen userDrawId={gameState.userDrawId!} onBack={resetGame} />;
  }

  if (gameState.gamePhase === 'gameOver') {
    return <GameOverScreen onRestart={resetGame} />;
  }

  if (gameState.gamePhase === 'gameStopped') {
    return <GameStoppedScreen />;
  }

  return (
    <div className="app">
      <div className="header">
        <h1>Dubai Tatil Çekilişi</h1>
        <div className="attempts">
          Kalan Deneme: {gameState.maxAttempts - gameState.userAttempts}
        </div>
      </div>

      <div className="game-container">
        <div className="cards-grid">
          {gameState.cards.map((card, index) => (
            <div
              key={card.id}
              className={`card ${card.isRevealed ? 'revealed' : ''} ${card.isSelected ? 'selected' : ''}`}
              onClick={() => handleCardClick(index)}
            >
              <div className="card-inner">
                <div className="card-front">
                  <img src="/card-back.svg" alt="Kart Arka" />
                </div>
                <div className="card-back">
                  {card.isSelected && (
                    <div className="card-result">
                      {gameState.userAttempts < gameState.maxAttempts ? 'Tekrar Dene!' : 'Oyun Bitti!'}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="instructions">
          <p>Bir kart seçin ve şansınızı deneyin!</p>
          <p>Dubai tatil ödülünü kazanma şansınız var!</p>
        </div>
      </div>
    </div>
  );
}

// Form Ekranı Bileşeni
function FormScreen({ userDrawId, onBack }: { userDrawId: string; onBack: () => void }) {
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    phone: ''
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const response = await fetch('http://localhost:8000/submit-form', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_draw_id: userDrawId,
          ...formData
        }),
      });

      if (response.ok) {
        alert('Tebrikler! Form başarıyla gönderildi.');
        onBack();
      } else {
        alert('Form gönderilirken hata oluştu.');
      }
    } catch (error) {
      console.error('Form gönderme hatası:', error);
      alert('Form gönderilirken hata oluştu.');
    }
  };

  return (
    <div className="form-screen">
      <div className="form-container">
        <h2>Tebrikler! Ödül Kazandınız!</h2>
        <p>Bilgilerinizi doldurun ve çekilişe katılın.</p>
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Ad Soyad:</label>
            <input
              type="text"
              value={formData.full_name}
              onChange={(e) => setFormData(prev => ({ ...prev, full_name: e.target.value }))}
              required
            />
          </div>
          
          <div className="form-group">
            <label>E-posta:</label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
              required
            />
          </div>
          
          <div className="form-group">
            <label>Telefon:</label>
            <input
              type="tel"
              value={formData.phone}
              onChange={(e) => setFormData(prev => ({ ...prev, phone: e.target.value }))}
              required
            />
          </div>
          
          <button type="submit" className="submit-btn">Gönder</button>
        </form>
      </div>
    </div>
  );
}

// Oyun Bitti Ekranı
function GameOverScreen({ onRestart }: { onRestart: () => void }) {
  return (
    <div className="game-over-screen">
      <div className="game-over-container">
        <h2>Oyun Bitti!</h2>
        <p>3 kere "Tekrar Dene" kartı çektiniz.</p>
        <p>Daha fazla oynama hakkınız kalmadı.</p>
        <button onClick={onRestart} className="restart-btn">Yeni Oyun</button>
      </div>
    </div>
  );
}

// Oyun Durduruldu Ekranı
function GameStoppedScreen() {
  return (
    <div className="game-over-screen">
      <div className="game-over-container">
        <h2>Oyun Durduruldu!</h2>
        <p>Dubai tatil ödülü 100.000 kişiye ulaştı!</p>
        <p>Çekiliş sona erdi. Teşekkürler!</p>
      </div>
    </div>
  );
}

export default App; 
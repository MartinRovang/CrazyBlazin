import React, { useEffect, useState } from 'react';
import axios from 'axios';
import Lottery from './Lottery';  // No curly braces for default export


function App() {
  const [user, setUser] = useState(null);
  const [coins, setCoins] = useState(null);
  const [newCoins, setNewCoins] = useState(0);

  const discordClientId = '831465297394401291';
  const redirectUri = 'https://discord.com/oauth2/authorize?client_id=831465297394401291&response_type=code&redirect_uri=http%3A%2F%2Flocalhost%3A3000%2Fcallback&scope=email';

  const handleLogin = () => {
    const discordOAuthUrl = `https://discord.com/api/oauth2/authorize?client_id=${discordClientId}&redirect_uri=${redirectUri}&response_type=token&scope=identify`;
    window.location.href = discordOAuthUrl;
  };

  useEffect(() => {
    const hash = window.location.hash;
    if (hash) {
      const token = new URLSearchParams(hash.replace('#', '')).get('access_token');
      if (token) {
        axios.get('https://discord.com/api/users/@me', {
          headers: { Authorization: `Bearer ${token}` },
        })
        .then(response => {
          setUser(response.data);
          fetchMemberCoins(response.data.id);
        })
        .catch(err => console.error(err));
      }
    }
  }, []);

  const fetchMemberCoins = (discordId) => {
    axios.get(`http://localhost:5000/member/${discordId}`)
      .then(response => setCoins(response.data.coins))
      .catch(err => console.error(err));
  };

  const updateCoins = () => {
    if (user) {
      axios.put(`http://localhost:5000/member/${user.id}/coins`, { coins: newCoins })
        .then(() => {
          setCoins(newCoins);
        })
        .catch(err => console.error(err));
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Login with Discord</h1>
        <div>
      <h1>Welcome to the Lottery App</h1>
      <Lottery />  {/* Use the Lottery component here */}
    </div>
        {user ? (
          <div>
            <h2>Welcome, {user.username}#{user.discriminator}</h2>
            <img src={`https://cdn.discordapp.com/avatars/${user.id}/${user.avatar}.png`} alt="User Avatar" />
            <p>Coins: {coins}</p>
            <input
              type="number"
              value={newCoins}
              onChange={(e) => setNewCoins(e.target.value)}
              placeholder="New coins amount"
            />
            <button onClick={updateCoins}>Update Coins</button>
          </div>
        ) : (
          <button onClick={handleLogin}>Login with Discord</button>
        )}
      </header>
    </div>
  );
}

export default App;

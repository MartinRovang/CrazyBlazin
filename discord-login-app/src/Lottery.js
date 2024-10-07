import React, { useState } from 'react';
import axios from 'axios';

function Lottery() {
  const [betAmount, setBetAmount] = useState(0);
  const [userId, setUserId] = useState(1);  // Mocked user ID, replace with actual user ID
  const [message, setMessage] = useState('');

  const placeBet = () => {
    axios.post('http://localhost:5000/bet', {
      user_id: userId,
      bet_amount: betAmount
    })
    .then(response => setMessage(response.data.message))
    .catch(err => setMessage('Error placing bet'));
  };

  return (
    <div>
      <h2>Lottery</h2>
      <input
        type="number"
        value={betAmount}
        onChange={e => setBetAmount(Number(e.target.value))}
        placeholder="Bet amount"
      />
      <button onClick={placeBet}>Place Bet</button>
      <p>{message}</p>
    </div>
  );
}

export default Lottery;

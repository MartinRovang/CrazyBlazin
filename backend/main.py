import random
import sqlite3
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler


app = Flask(__name__)
CORS(app)

# Function to connect to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('/data/coins.db')  # Change to 'coins.db'
    conn.row_factory = sqlite3.Row
    return conn

# Get user details (including coins) based on user_id
@app.route('/member/<int:user_id>', methods=['GET'])
def get_user(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    if user is None:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(dict(user))

# Update user's coin balance
@app.route('/member/<int:user_id>/coins', methods=['PUT'])
def update_coins(user_id):
    data = request.json
    coins = data.get('coins')
    if coins is None:
        return jsonify({'error': 'Missing coins value'}), 400

    conn = get_db_connection()
    cursor = conn.execute('UPDATE users SET coins = ? WHERE user_id = ?', (coins, user_id))
    conn.commit()
    conn.close()

    if cursor.rowcount == 0:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'message': 'Coins updated'}), 200

# Place a bet
@app.route('/bet', methods=['POST'])
def place_bet():
    data = request.json
    user_id = data.get('user_id')
    bet_amount = data.get('bet_amount')

    if user_id is None or bet_amount is None:
        return jsonify({'error': 'Missing user_id or bet_amount'}), 400

    # Check if the user has enough coins
    conn = get_db_connection()
    user = conn.execute('SELECT coins FROM users WHERE user_id = ?', (user_id,)).fetchone()

    if user is None or user['coins'] < bet_amount:
        conn.close()
        return jsonify({'error': 'Insufficient coins'}), 400

    # Deduct the bet amount from the user's coins
    conn.execute('UPDATE users SET coins = coins - ? WHERE user_id = ?', (bet_amount, user_id))

    # Get the current lottery round (use the timestamp divided by 8 hours)
    current_round = int(time.time() // (8 * 60 * 60))

    # Record the bet in the bets table
    conn.execute('INSERT INTO bets (user_id, bet_amount, lottery_round) VALUES (?, ?, ?)',
                 (user_id, bet_amount, current_round))

    conn.commit()
    conn.close()

    return jsonify({'message': 'Bet placed successfully'}), 200

# Manually trigger lottery draw (for demonstration)
@app.route('/lottery', methods=['POST'])
def run_lottery():
    # Get the current round
    current_round = int(time.time() // (8 * 60 * 60))

    conn = get_db_connection()

    # Get all the bets in the current round
    bets = conn.execute('SELECT * FROM bets WHERE lottery_round = ?', (current_round,)).fetchall()

    if len(bets) == 0:
        conn.close()
        return jsonify({'error': 'No bets in the current round'}), 400

    # Calculate total pool
    total_pool = sum([bet['bet_amount'] for bet in bets])

    # Select a random winner
    winner_bet = random.choice(bets)
    winner_id = winner_bet['user_id']

    # Update the winner's coin balance
    conn.execute('UPDATE users SET coins = coins + ? WHERE user_id = ?', (total_pool, winner_id))

    # Store the lottery result
    conn.execute('INSERT INTO lottery_history (winner_id, total_pool, timestamp) VALUES (?, ?, ?)',
                 (winner_id, total_pool, time.time()))

    conn.commit()
    conn.close()

    return jsonify({'message': 'Lottery completed', 'winner_id': winner_id, 'total_pool': total_pool}), 200


def lottery_job():
    # This function will automatically run the lottery every 8 hours
    with app.app_context():
        run_lottery()

# Initialize the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(lottery_job, 'interval', hours=8)  # Run every 8 hours
scheduler.start()


if __name__ == '__main__':
    app.run(port=5000)

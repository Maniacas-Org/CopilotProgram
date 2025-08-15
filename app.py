from flask import Flask, render_template, session, request, jsonify, redirect, url_for
import random
import string
import os

app = Flask(__name__)
# For a real deployment, set a secure SECRET_KEY via env var
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-for-demo')

# Long English words to guess (kept family-friendly and fun)
WORDS = [
    'internationalization',
    'characteristically',
    'misunderstanding',
    'counterintuitive',
    'extraordinary',
    'phenomenon',
    'inconsequential',
    'congratulations',
    'multiplication',
    'hippopotamus',
]

MAX_FAILS = 6


def start_new_game():
    word = random.choice(WORDS).lower()
    session['word'] = word
    session['guessed'] = []
    session['success'] = 0
    session['fail'] = 0
    session['max_fails'] = MAX_FAILS
    session.modified = True


def masked_word(word, guessed):
    return ' '.join([c if (not c.isalpha()) or (c in guessed) else '_' for c in word])


@app.route('/')
def index():
    if 'word' not in session:
        start_new_game()
    word = session.get('word')
    guessed = session.get('guessed', [])
    return render_template('index.html', masked=masked_word(word, guessed), length=len(word))


@app.route('/new', methods=['POST'])
def new_game():
    start_new_game()
    return jsonify(state=True, message='New word selected')


@app.route('/guess', methods=['POST'])
def guess():
    data = request.get_json() or {}
    letter = (data.get('letter') or '').strip().lower()
    if not letter or len(letter) != 1 or not letter.isalpha():
        return jsonify(error='Please send a single letter (a-z).'), 400

    if 'word' not in session:
        start_new_game()

    word = session['word']
    guessed = session.get('guessed', [])

    if letter in guessed:
        # already guessed
        state = {
            'masked': masked_word(word, guessed),
            'guessed': guessed,
            'success': session.get('success', 0),
            'fail': session.get('fail', 0),
            'message': f'You already tried "{letter}"',
        }
        return jsonify(state)

    guessed.append(letter)
    session['guessed'] = guessed

    if letter in word:
        # count how many letters revealed
        count = sum(1 for c in word if c == letter)
        session['success'] = session.get('success', 0) + count
        correct = True
        message = random.choice(['Nice!', 'Great guess!', 'You found some letters!', 'Bingo!'])
    else:
        session['fail'] = session.get('fail', 0) + 1
        correct = False
        message = random.choice(['Oops!', 'Not this time', 'Try again!', 'Almost...'])

    masked = masked_word(word, guessed)
    won = all((not c.isalpha()) or (c in guessed) for c in word)
    lost = session.get('fail', 0) >= session.get('max_fails', MAX_FAILS)

    if won:
        message = 'You won! 🎉 — ' + word
    elif lost:
        message = 'Game over 😢 — the word was: ' + word

    state = {
        'masked': masked,
        'guessed': guessed,
        'success': session.get('success', 0),
        'fail': session.get('fail', 0),
        'max_fails': session.get('max_fails', MAX_FAILS),
        'correct': correct,
        'message': message,
        'won': won,
        'lost': lost,
    }

    session.modified = True
    return jsonify(state)


@app.route('/state')
def state():
    if 'word' not in session:
        start_new_game()
    word = session['word']
    guessed = session.get('guessed', [])
    return jsonify({
        'masked': masked_word(word, guessed),
        'guessed': guessed,
        'success': session.get('success', 0),
        'fail': session.get('fail', 0),
        'max_fails': session.get('max_fails', MAX_FAILS),
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

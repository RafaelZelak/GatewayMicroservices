# NÃO MEXER NESTE ARQUIVO!

from flask import session, redirect, url_for, request, render_template
from config_flask import create_app

app = create_app()

@app.route('/')
def index():
    """Rota principal que usa os templates globais (pasta /templates)."""
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("index"))
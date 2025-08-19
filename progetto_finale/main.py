import discord
from discord.ext import commands
import threading

import os

file_error = 'Purtroppo non riusciamo più a trovare il tuo file di salvataggio, ti chiediamo immensamente scusa ma dovrai ricominciare tutto da capo. Per favore, registrati di nuovo con $signup se vuoi continuare.'



intents = discord.Intents.default()
intents.message_content = True
intents.members = False
intents.presences = False
bot = commands.Bot(command_prefix='$', intents=intents)



from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here'
db = SQLAlchemy(app)



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f'<User {self.id}>'

with app.app_context():
    db.create_all()



discord_user = ""

@bot.event
async def on_ready():
    print(f'Sono pronto ~{bot.user.name}')



@bot.command()
async def login(ctx, username=None, password=None):
    global discord_user
    if discord_user:
        await ctx.send(f'Se sei già loggato come {discord_user}, esegui il logout prima di effettuare un nuovo login.')
        return
    if username == None and password == None:
        await ctx.send('Devi inserire lo username e la password, purtroppo questa versione non dispone di un sistema di lettura della mente \U0001F609.')
        return
    elif password == None:
        await ctx.send('Devi inserire la password, purtroppo questa versione non dispone di un sistema di lettura della mente \U0001F609')
        return
    else:
        with app.app_context():
            user = User.query.filter_by(username=username, password=password).first()
        if user:
            discord_user = username
            await ctx.send(f'Login effettuato come {username}')
            try:
                with open(f'data/{username}.txt', 'r') as f:
                    stats = f.read()
            except FileNotFoundError:
                await ctx.send(file_error)
        else:
            await ctx.send('Credenziali non valide. Prima volta? Registrati con $signup.')



@bot.command()
async def logout(ctx):
    global discord_user
    if not discord_user:
        await ctx.send('Non sei loggato')
        return
    await ctx.send(f'Logout effettuato da {discord_user}')
    discord_user = ""



@bot.command()
async def signup(ctx, username=None, password=None):
    if username == None and password == None:
        await ctx.send('Devi inserire lo username e la password, purtroppo questa versione non dispone di un sistema di lettura della mente \U0001F609.')
        return
    elif password == None:
        await ctx.send('Devi inserire la password, purtroppo questa versione non dispone di un sistema di lettura della mente \U0001F609.')
        return
    else:
        with app.app_context():
            if User.query.filter_by(username=username).first():
                await ctx.send('Username già in uso. Scegline un altro.')
                return
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
        with open(f'data/{username}.txt', 'w') as f:
            f.write('0')
        await ctx.send(f'Utente {username} registrato con successo! (Sei anche stato automaticamente loggato.)')
        global discord_user
        discord_user = username



@bot.command()
async def stats(ctx):
    if not discord_user:
        await ctx.send('Devi essere loggato per vedere le tue statistiche.')
        return
    try:
        with open(f'data/{discord_user}.txt', 'r') as f:
            stats = f.read()
        if stats == '0':
            stats = 'Hai ancora 0 punti, ma tranquillo devi ancora iniziare!'
        await ctx.send(f'Statistiche per {discord_user}: {stats}')
    except FileNotFoundError:
        await ctx.send(file_error)



@bot.command()
async def tutorial(ctx):
    await ctx.send('Questo bot ti pormette di conoscere il cambiamento climatico e come puoi aiutare a fermarlo (È necessario un browser poiché userai un sito web per procedere nella tua avventura). Nei vari livelli imparerai varie cose riguardo al cambiamento climatico e guadagnerai punti risolvendo quiz. il tuo obiettivo è 500 punti che guadagnerai in 5 livelli diversi. Quando sei pronto comincia pure!\n\nQui di seguito trovi i comandi che puoi usare:\n\n$login <username> <password> - Per effettuare il login\n$logout - Per effettuare il logout\n$signup <username> <password> - Per registrarti\n$stats - Per vedere le tue statistiche\n$proceed per andare avanti nell\'avventura\n$tutorial - Per vedere questo messaggio di aiuto')



@bot.command()
async def proceed(ctx):
    if not discord_user:
        await ctx.send('Devi essere loggato per procedere.')
        return
    try:
        with open(f'data/{discord_user}.txt', 'r') as f:
            stats = f.read()
        if  stats == '0':
            await ctx.send('Inizia il tuo viaggio! Visita il sito web per iniziare: http://127.0.0.1:5000/login_stage_one')
        elif stats == '100':
            await ctx.send('Continua il tuo viaggio! Visita il sito web per proseguire: http://127.0.0.1:5000/login_stage_two')
        elif stats == '200':
            await ctx.send('Stai facendo progressi! Visita il sito web per continuare: http://127.0.0.1:5000/login_stage_three')
        elif stats == '300':
            await ctx.send('Quasi alla fine! Visita il sito web per il prossimo passo: http://127.0.0.1:5000/login_stage_four')
        elif stats == '400':
            await ctx.send('Ultimo passo! Visita il sito web per completare la tua avventura: http://127.0.0.1:5000/login_stage_five')
        else:
            await ctx.send('Hai già completato l\'avventura! È stato un piacere aiutarti a conoscere il cambiamento climatico.')
    except FileNotFoundError:
        await ctx.send(file_error)



@app.route('/login_stage_one', methods=['GET', 'POST'])
def login_stage_one():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        if username and password:
            user = User.query.filter_by(username=username, password=password).first()
            if user:
                with open(f'data/{user.username}.txt', 'r') as f:
                    if f.read() != '0':
                        return render_template('wrong_page.html', username=username)
                    session['user'] = username
                    session.modified = True
                    return redirect(url_for('stage_one'))
            else:
                return render_template('login_one.html', error='Credenziali non valide. Riprova.')
    return render_template('login_one.html')

@app.route('/stage_one', methods=['GET', 'POST'])
def stage_one():
    user = session.get("user", "")
    if user:
        if request.method == 'POST':
            answer = request.form.get("answer")
            if answer:
                with open(f'data/{user}.txt', 'r') as f:
                    if f.read() == '100':
                        esito = 'Hai già completato questo livello.'
                    else:
                        if answer.lower() == '10':
                            with open(f'data/{user}.txt', 'w') as t:
                                t.write('100')
                            esito = 'Corretto! Hai guadagnato 100 punti.'
                        else:
                            esito = 'No, non è corretto. Riprova.'
                return render_template('stage_one.html', username=user, esito=esito)
        with open(f'data/{user}.txt', 'r') as f:
            if f.read() != '0':
                return render_template('wrong_page.html', username=user)
        return render_template('stage_one.html', username=user)
    else:
        return redirect(url_for('login_stage_one'))
    


@app.route('/login_stage_two', methods=['GET', 'POST'])
def login_stage_two():
    web_user = ""
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        user = None
        if username and password:
            user = User.query.filter_by(username=username, password=password).first()
            if user:
                web_user = username
                with open(f'data/{web_user}.txt', 'r') as f:
                    if f.read() != '100':
                        return render_template('wrong_page.html', username=web_user)
                    session["user"] = web_user
                    return redirect('/stage_two')
            else:
                return render_template('login_two.html', error='Credenziali non valide. Riprova.')
    return render_template('login_two.html')

@app.route('/stage_two', methods=['GET', 'POST'])
def stage_two():
    user = session.get("user", "")
    if user:
        if request.method == 'POST':
            answer = request.form.get("answer")
            if answer:
                with open(f'data/{user}.txt', 'r') as f:
                    if f.read() == '200':
                        esito = 'Hai già completato questo livello.'
                    else:
                        if answer.lower() == 'sì':
                            with open(f'data/{user}.txt', 'w') as t:
                                t.write('200')
                            esito = 'Corretto! Hai guadagnato 100 punti.'
                        else:
                            esito = 'No, non è corretto. Riprova.'
                return render_template('stage_two.html', username=user, esito=esito)
        with open(f'data/{user}.txt', 'r') as f:
            if f.read() != '100':
                return render_template('wrong_page.html', username=user)
        return render_template('stage_two.html', username=user)
    else:
        return redirect('/login_stage_two')

@app.route('/login_stage_three', methods=['GET', 'POST'])
def login_stage_three():
    web_user = ""
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        
        user = None
        if username and password:
            user = User.query.filter_by(username=username, password=password).first()
            if user:
                web_user = username
                with open(f'data/{web_user}.txt', 'r') as f:
                    if f.read() != '200':
                        return render_template('wrong_page.html', username=web_user)
                    else:
                        session["user"] = web_user
                        return redirect('/stage_three')
            else:
                return render_template('login_three.html', error='Credenziali non valide. Riprova.')
    return render_template('login_three.html')

@app.route('/stage_three', methods=['GET', 'POST'])
def stage_three():
    user = session.get("user", "")
    if user:
        if request.method == 'POST':
            answer = request.form.get("answer")
            if answer:
                with open(f'data/{user}.txt', 'r') as f:
                    if f.read() == '300':
                        esito = 'Hai già completato questo livello.'
                    else:
                        if answer.lower() == '3':
                            with open(f'data/{user}.txt', 'w') as t:
                                t.write('300')
                            esito = 'Corretto! Hai guadagnato 100 punti.'
                        else:
                            esito = 'No, non è corretto. Riprova.'
                return render_template('stage_three.html', username=user, esito=esito)
        with open(f'data/{user}.txt', 'r') as f:
            if f.read() != '200':
                return render_template('wrong_page.html', username=user)
        return render_template('stage_three.html', username=user)
    else:
        return redirect('/login_stage_three')

@app.route('/login_stage_four', methods=['GET', 'POST'])
def login_stage_four():
    web_user = ""
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        
        user = None
        if username and password:
            user = User.query.filter_by(username=username, password=password).first()
            if user:
                web_user = username
                with open(f'data/{web_user}.txt', 'r') as f:
                    if f.read() != '300':
                        return render_template('wrong_page.html', username=web_user)
                    else:
                        session["user"] = web_user
                        return redirect('/stage_four')
            else:
                return render_template('login_four.html', error='Credenziali non valide. Riprova.')
    return render_template('login_four.html')

@app.route('/stage_four', methods=['GET', 'POST'])
def stage_four():
    user = session.get("user", "")
    if user:
        if request.method == 'POST':
            answer = request.form.get("answer")
            if answer:
                with open(f'data/{user}.txt', 'r') as f:
                    if f.read() == '400':
                        esito = 'Hai già completato questo livello.'
                    else:
                        if answer.lower() == 'sì':
                            with open(f'data/{user}.txt', 'w') as t:
                                t.write('400')
                            esito = 'Corretto! Hai guadagnato 100 punti.'
                        else:
                            esito = 'No, non è corretto. Riprova.'
                return render_template('stage_four.html', username=user, esito=esito)
        with open(f'data/{user}.txt', 'r') as f:
            if f.read() != '300':
                return render_template('wrong_page.html', username=user)
        return render_template('stage_four.html', username=user)
    else:
        return redirect('/login_stage_four')

@app.route('/login_stage_five', methods=['GET', 'POST'])
def login_stage_five():
    web_user = ""
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        
        user = None
        if username and password:
            user = User.query.filter_by(username=username, password=password).first()
            if user:
                web_user = username
                with open(f'data/{web_user}.txt', 'r') as f:
                    if f.read() != '400':
                        return render_template('wrong_page.html', username=web_user)
                    else:
                        session["user"] = web_user
                        return redirect('/stage_five')
            else:
                return render_template('login_five.html', error='Credenziali non valide. Riprova.')
    return render_template('login_five.html')

@app.route('/stage_five', methods=['GET', 'POST'])
def stage_five():
    user = session.get("user", "")
    if user:
        if request.method == 'POST':
            answer = request.form.get("answer")
            if answer:
                with open(f'data/{user}.txt', 'r') as f:
                    if f.read() == '500':
                        esito = 'Hai già completato questo livello.'
                    else:
                        if answer.lower() == '2':
                            with open(f'data/{user}.txt', 'w') as t:
                                t.write('500')
                            esito = 'Corretto! Hai guadagnato 100 punti, Grazie per aver preso parte alla lotta contro il riscaldamento climatico.'
                        else:
                            esito = 'No, non è corretto. Riprova.'
                return render_template('stage_five.html', username=user, esito=esito)
        with open(f'data/{user}.txt', 'r') as f:
            if f.read() != '400':
                return render_template('wrong_page.html', username=user)
        return render_template('stage_five.html', username=user)
    else:
        return redirect('/login_stage_five')



if __name__ == '__main__':
    flask_thread = threading.Thread(target=app.run, kwargs={'debug': True, 'use_reloader': False})
    flask_thread.start()
    bot.run('YOUR_DISCORD_BOT_TOKEN')
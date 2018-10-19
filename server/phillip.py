from bottle import Bottle, run, template
import subprocess
import time

app = Bottle()

def validate(code):
  return len(code) == 8 and code.isalnum()

start_times = []

def cull_times():
  global start_times

  current = time.time()

  # remove anything more than an hour old
  start_times = [t for t in start_times if current - t < 3600]

  return len(start_times)


MAX_GAMES = 10

@app.route('/phillip/<code>')
def play(code):
  if not validate(code):
    return template('Invalid code <b>{{name}}</b>', code=code)

  if cull_times() >= MAX_GAMES:
    return template('Sorry, too many games running')

  command = 'sbatch -t 0-1 -c 2 --mem 1G -x node[001-030] --qos tenenbaum netplay.sh %s' % code
  print(command)
  subprocess.run(command.split())
  start_times.append(time.time())
  return template('Phillip netplay started with code <b>{{code}}</b>!', code=code)

@app.get('/')
def request_match_page():
  return '''
    <form action="/request_match" method="post">
      Code: <input name="code" type="text" />
      Delay: <input name="delay" type="text" />
    </form>
  '''

@app.post('/request_match')
def request_match():
  code = request.forms.get('code')
  return play(code)
    
run(app, host='0.0.0.0', port=8484)

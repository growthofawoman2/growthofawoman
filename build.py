import os, sys, re, shutil, glob, html as _html
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "site")
shutil.rmtree(OUT, ignore_errors=True)
os.makedirs(os.path.join(OUT, "images", "uploads"))
os.makedirs(os.path.join(OUT, "files"))
os.makedirs(os.path.join(OUT, "admin"))
for f in os.listdir(ROOT):
    p = os.path.join(ROOT, f)
    if not os.path.isfile(p):
        continue
    ext = f.rsplit(".", 1)[-1].lower()
    if ext in ("png", "jpg", "jpeg", "gif", "webp") and f not in ("favicon.png", "apple-touch-icon.png"):
        shutil.copy(p, os.path.join(OUT, "images", f))
    elif ext == "pdf":
        shutil.copy(p, os.path.join(OUT, "files", f))
    elif f in ("style.css", "favicon.ico", "favicon.png", "apple-touch-icon.png"):
        shutil.copy(p, os.path.join(OUT, f))
shutil.copy(os.path.join(ROOT, "admin-index.html"), os.path.join(OUT, "admin", "index.html"))
shutil.copy(os.path.join(ROOT, "admin-config.yml"), os.path.join(OUT, "admin", "config.yml"))
_up = os.path.join(ROOT, "uploads")
if os.path.isdir(_up):
    for f in os.listdir(_up):
        shutil.copy(os.path.join(_up, f), os.path.join(OUT, "images", "uploads", f))
import markdown, yaml

PAGES = [("index.html", "Home"), ("about.html", "About"), ("libraries.html", "Libraries"),
         ("blog.html", "Blog"), ("shop.html", "Shop"), ("polls.html", "Polls")]

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="Growth of a Woman: life lessons, shared knowledge and continued growth. Books, guides and journals by S. Inas.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Playfair+Display:ital,wght@0,500;0,600;1,500&family=Great+Vibes&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css">
<link rel="icon" href="favicon.ico" sizes="any">
<link rel="icon" type="image/png" href="favicon.png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Growth of a Woman">
<meta property="og:title" content="{title}">
<meta property="og:description" content="Life Lessons. Shared Knowledge. Continued Growth. Books, guides and journals by S. Inas.">
<meta property="og:image" content="https://growthofawoman.com/images/share.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://growthofawoman.com/images/share.jpg">
</head>
<body>
<div class="topbar">Life Lessons. Shared Knowledge. Continued Growth.</div>
<header class="site"><div class="wrap">
  <a class="brand" href="index.html"><b>Growth of a Woman</b><small>BOOKS &bull; WISDOM &bull; LEGACY</small></a>
  <button class="menu-btn" onclick="document.querySelector('nav.main').classList.toggle('open')" aria-label="Open menu">Menu</button>
  <nav class="main">{nav}</nav>
</div></header>
<main>
"""

FOOT = """</main>
<footer class="site"><div class="wrap">
  <div class="cols">
    <div>
      <h4>Growth of a Woman</h4>
      <p>A publishing house for the endlessly curious.</p>
      <p><span class="script" style="font-size:26px">Life Lessons. Shared Knowledge. Continued Growth.</span></p>
    </div>
    <div><ul>
      <li><a href="about.html">About</a></li>
      <li><a href="libraries.html">Libraries</a></li>
      <li><a href="blog.html">Blog</a></li>
    </ul></div>
    <div><ul>
      <li><a href="shop.html">Shop</a></li>
      <li><a href="polls.html">Polls</a></li>
      <li><a href="free-guide.html">Free Guide</a></li>
      <li><a href="mailto:hello@growthofawoman.com">hello@growthofawoman.com</a></li>
    </ul></div>
  </div>
  <div class="copy">&copy; 2026 Growth of a Woman. All rights reserved.</div>
</div></footer>
</body>
</html>
"""

def page(fname, title, body):
    nav = "".join(f'<a href="{f}"{" class=on" if f == fname else ""}>{n}</a>' for f, n in PAGES)
    with open(os.path.join(OUT, fname), "w", encoding="utf-8") as fh:
        fh.write(HEAD.format(title=title, nav=nav) + body + FOOT)

LIBS = [
    ("01", "Women's Shared Wisdom", "Guides, journals, reflections, and practical knowledge, gathered from women's experiences.", "women"),
    ("02", "Children's Library", "Stories, educational books, and activities for young readers.", "children"),
    ("03", "Family &amp; Legacy", "Parenting resources, traditions, and family history.", "family"),
]
# (category, title, slug, summary, date) -- Part 1 is a hand-built page kept in legacy/
POSTS = [
    ("Marriage", "Did I Have Unrealistic Expectations? Part 1", "unrealistic-expectations-part-1",
     "At 18, I had my whole life planned until 30. Married by 22. Boutique by 25. Done having babies by 30. Here's how that went.", "2026-11-15"),
]
MD_POSTS = []
for f in sorted(glob.glob(os.path.join(ROOT, "content", "posts", "*.md"))):
    if os.path.basename(f).lower() == "readme.md":
        continue
    raw = open(f, encoding="utf-8").read()
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", raw, re.S)
    if not m:
        continue
    meta = yaml.safe_load(m.group(1)) or {}
    if meta.get("draft"):
        continue
    meta["slug"] = os.path.splitext(os.path.basename(f))[0]
    meta["body"] = m.group(2)
    meta["date"] = str(meta.get("date", ""))[:10]
    MD_POSTS.append(meta)
    POSTS.append((meta.get("category", ""), meta.get("title", ""), meta["slug"], meta.get("summary", ""), meta["date"]))
POSTS.sort(key=lambda p: p[4], reverse=True)
CURLY_TEXT = "Discover the power of building a hair-care routine that works for you. Learn to understand your hair's needs, make confident choices, and recognize when professional support can help."
CURLY_LINK = "https://payhip.com/b/8gNXA"

def lib_cards():
    return "".join(f'''<div class="card"><p class="num">{n} / LIBRARY</p><h3>{t}</h3><p>{d}</p>
<a class="more" href="libraries.html#{a}">Explore &rarr;</a></div>''' for n, t, d, a in LIBS)

def post_cards(limit=None):
    out = []
    for cat, t, slug, dek, _d in POSTS[:limit]:
        out.append(f'''<a class="card post" href="{slug}.html"><p class="meta">{cat}</p><h3>{t}</h3>
<p>{dek}</p><p style="margin-top:12px;color:var(--plum-deep)">Read the post &rarr;</p></a>''')
    return "".join(out)


def signup(eyebrow="Free guide for curly girls"):
    return f'''<form class="card signup" name="free-guide" method="POST" data-netlify="true" netlify-honeypot="bot-field" action="free-guide-thank-you.html">
<input type="hidden" name="form-name" value="free-guide">
<p style="display:none"><label>Leave this empty: <input name="bot-field"></label></p>
<p class="eyebrow">{eyebrow}</p>
<h3>Haircut or Trim?</h3>
<p>When is it time for a trim? How often? What should you ask your stylist? Get the free one-page guide by S. Inas.</p>
<label>First name<input type="text" name="first-name" required autocomplete="given-name"></label>
<label>Email<input type="email" name="email" required autocomplete="email"></label>
<button class="btn" type="submit">Send me the free guide</button>
<p class="anon">No spam. Your email stays private.</p>
</form>'''

# ---------- HOME ----------
page("index.html", "Growth of a Woman | Life Lessons Worth Sharing", f"""
<section class="hero"><div class="wrap">
  <p class="orn">&#10047; &#10022; &#10047;</p>
  <p class="eyebrow">A publishing house for the endlessly curious</p>
  <h1>Growth of a Woman</h1>
  <p class="tag">Life Lessons. Shared Knowledge. Continued Growth.</p>
  <p class="lead">Growth of a Woman is where Muslim women find honest guidance, rooted in faith and lived experience, for every season of womanhood.</p>
  <a class="btn" href="libraries.html">Discover our libraries</a>&nbsp;
  <a class="btn ghost" href="blog.html">Read the blog</a>
</div></section>

<section id="free-guide" style="padding-top:8px"><div class="wrap" style="max-width:620px">{signup()}</div></section>

<section class="quote"><div class="wrap">
  <blockquote>&ldquo;You don't know what you didn't know until you know!&rdquo;</blockquote>
  <p>Our signature philosophy</p>
</div></section>

<section><div class="wrap">
  <p class="eyebrow">Explore the collections</p>
  <h2>A library for every chapter of life.</h2>
  <p class="lead" style="margin-bottom:32px">Different readers. Different stories. One shared belief: there's always something more to learn.</p>
  <div class="grid g3">{lib_cards()}</div>
</div></section>

<section style="background:var(--card);border-top:1px solid var(--line);border-bottom:1px solid var(--line)"><div class="wrap split">
  <img class="cover" src="images/for-curly-girls.png" alt="For Curly Girls! A Lazy Hair Guide, book cover">
  <div>
    <p class="eyebrow">Featured &bull; Women's Shared Wisdom</p>
    <h2>For Curly Girls!<br><span style="font-size:.6em;color:var(--muted)">A Lazy Hair Guide</span></h2>
    <p>{CURLY_TEXT}</p>
    <p class="price">Digital PDF guide &middot; $7.99 &middot; Secure checkout through Payhip</p>
    <a class="btn" href="{CURLY_LINK}">Buy now &mdash; $7.99</a>
  </div>
</div></section>

<section><div class="wrap">
  <p class="eyebrow">From the blog</p>
  <h2>Latest writing</h2>
  <div class="grid" style="margin-top:24px;max-width:720px">{post_cards(1)}</div>
</div></section>

<section style="background:var(--card);border-top:1px solid var(--line)"><div class="wrap prose">
  <p class="eyebrow">The heart behind the pages</p>
  <h2>Our Purpose.</h2>
  <p><b>Life lessons are meant to be shared.</b></p>
  <p>Growth of a Woman is a publishing and educational brand dedicated to sharing knowledge, practical wisdom, and lessons learned through life experiences.</p>
  <p>We believe some of life's most valuable lessons are the ones we were never taught, didn't know to ask about, or discovered through our own experiences.</p>
  <p>Through books, educational guides, journals, and digital resources, we aim to make that knowledge accessible, useful, and meaningful.</p>
  <p>Our philosophy: there is always something more to learn, no matter your age or stage of life.</p>
  <a class="btn ghost" href="about.html">Meet S. Inas</a>
</div></section>
""")

# ---------- ABOUT ----------
page("about.html", "About S. Inas | Growth of a Woman", """
<section><div class="wrap prose">
  <p class="eyebrow">About the author</p>
  <h1 style="font-size:clamp(36px,6vw,56px)">S. Inas</h1>
  <p class="lead">Brooklyn-raised Black American Muslim, educator, mother, writer, licensed cosmetologist, lifelong learner</p>
  <p>I always knew, on a spiritual level, that I was destined for greatness.</p>
  <p>I grew up in Brooklyn. My parents converted to Islam coming from the Nation of Islam, and I was simply raised in Islam, an '80s baby who grew up with traditional values. That is my foundation. It shaped my life, and so did my mother and the women in my family. Watching them, I made a study out of marriage and family: what I didn't want, and in the end, what I did.</p>
  <p>By 18 I had it all planned. Fashion school, a design career, my own boutique, a Brooklyn brownstone, marriage and four children by 30. But life taught me what my faith already said: we make plans, and Allah is the best of planners.</p>
  <p>The design career never came, so I studied business, then cosmetology. I've done hair for over 15 years. Along the way I became a wife and a mother and earned my bachelor's degree in family science from the University of Maryland. Who would have thought that someone who never saw herself going to a traditional university, let alone graduating from one, would go on to teaching and pursue a master's in education?</p>
  <p>Every detour taught me something. Growth of a Woman is where I share it, so you can grow through your seasons with a little more wisdom and a lot more grace.</p>
  <p class="script" style="font-size:38px;margin-top:8px">S. Inas</p>
</div></section>
""")

# ---------- LIBRARIES ----------
page("libraries.html", "Libraries | Growth of a Woman", f"""
<section><div class="wrap">
  <p class="eyebrow">Explore the collections</p>
  <h1 style="font-size:clamp(36px,6vw,56px)">Our Libraries</h1>
  <p class="lead">Different readers. Different stories. One shared belief: there's always something more to learn.</p>
</div></section>

<section id="women" style="padding-top:0"><div class="wrap">
  <p class="eyebrow">01 / Library</p><h2>Women's Shared Wisdom</h2>
  <p class="lead" style="margin-bottom:28px">{LIBS[0][2]}</p>
  <div class="grid g3">
    <div class="card"><img class="cover" src="images/for-curly-girls.png" alt="For Curly Girls cover" style="margin-bottom:16px">
      <h3>For Curly Girls! A Lazy Hair Guide</h3><p style="margin-bottom:8px">{CURLY_TEXT}</p><p class="price">$7.99 &middot; Digital PDF</p><a class="btn" href="{CURLY_LINK}">Buy now</a></div>
    <div class="card"><img class="cover" src="images/ramadan-goals.jpg" alt="Ramadan Goals: A Journal for Women, book cover" style="margin-bottom:16px"><span class="soon">Coming soon</span>
      <h3>Ramadan Goals: A Journal for Women</h3><p style="margin-bottom:8px">The purpose of this journal is to help you remove mental obstacles from your path and focus on what is important, which is building your connection with your Creator.</p></div>
  </div>
</div></section>

<section id="children" style="background:var(--card);border-top:1px solid var(--line);border-bottom:1px solid var(--line)"><div class="wrap">
  <p class="eyebrow">02 / Library</p><h2>Children's Library</h2>
  <p class="lead" style="margin-bottom:28px">{LIBS[1][2]}</p>
  <div class="grid g3">
    <div class="card"><img class="cover" src="images/khadijahs-wash-day.jpg" alt="Khadijah's Wash Day, book cover" style="margin-bottom:16px;aspect-ratio:4/3;object-fit:cover;max-width:100%"><span class="soon">Coming soon</span>
      <h3>Khadijah's Wash Day</h3><p style="margin-bottom:8px">Khadijah isn't a fan of wash day. As her mom cares for her curls, Khadijah tries to make sense of why her mother wears hijab outside the house but not at home, and learns that her mom keeps her beauty for her family.</p></div>
  </div>
</div></section>

<section id="family"><div class="wrap">
  <p class="eyebrow">03 / Library</p><h2>Family &amp; Legacy</h2>
  <p class="lead" style="margin-bottom:28px">{LIBS[2][2]}</p>
  <div class="card" style="max-width:520px"><span class="soon">Coming soon</span><p>New titles for this library are on the way.</p></div>
</div></section>
""")

# ---------- BLOG ----------
page("blog.html", "Blog | Growth of a Woman", f"""
<section><div class="wrap">
  <p class="eyebrow">The blog</p>
  <h1 style="font-size:clamp(36px,6vw,56px)">Life lessons worth sharing</h1>
  <div class="grid" style="margin-top:24px;max-width:720px">{post_cards()}</div>
  <div style="max-width:620px;margin-top:40px">{signup()}</div>
</div></section>
""")
page("unrealistic-expectations-part-1.html", "Did I Have Unrealistic Expectations? Part 1 | Growth of a Woman", open(os.path.join(ROOT, "part1.html"), encoding="utf-8").read())


def post_page(p):
    e = _html.escape
    img = p.get("image")
    hero_bg = f"#E9DEE5 url({img}) center/cover no-repeat" if img else "#E9DEE5"
    body = markdown.markdown(p["body"], extensions=["extra", "sane_lists"])
    q = p.get("question")
    talk = f'''<div class="card" style="margin-top:32px;background:var(--bg)"><p style="margin:0;color:var(--ink)"><b>Let's talk:</b> {e(q)}</p></div>''' if q else ""
    fn = "comments-" + p["slug"]
    page(p["slug"] + ".html", f"{e(p.get('title',''))} | Growth of a Woman", f'''<article>
<div class="post-hero" style="background:{hero_bg};padding:72px 0 64px;text-align:center"><div class="wrap" style="max-width:760px">
<p class="eyebrow" style="color:#7A5A6D"><a href="blog.html" style="text-decoration:none;color:#7A5A6D">&larr; The blog</a> &nbsp;&bull;&nbsp; {e(p.get('category',''))}</p>
<h1 style="font-size:clamp(32px,5.5vw,52px);color:#5A4253">{e(p.get('title',''))}</h1>
<p style="color:#5A4253;font-style:italic;margin:0">By S. Inas | Growth of a Woman</p></div></div>
<section><div class="wrap prose">
<p class="lead" style="color:var(--ink)"><b>{e(p.get('summary',''))}</b></p>
{body}
{talk}
<form class="card" name="{fn}" method="POST" data-netlify="true" netlify-honeypot="bot-field" action="thank-you-comment.html" style="margin-top:32px">
<input type="hidden" name="form-name" value="{fn}">
<p style="display:none"><label>Leave this empty: <input name="bot-field"></label></p>
<h3 style="margin-bottom:6px">Leave a comment</h3>
<p class="anon" style="margin-bottom:16px">Comments are reviewed before they appear.</p>
<label style="display:block;font-size:14px;margin-bottom:4px">Name (optional)</label>
<input name="name" type="text" style="width:100%;padding:10px 12px;border:1px solid var(--line);border-radius:10px;font:inherit;margin-bottom:14px;background:#fff">
<label style="display:block;font-size:14px;margin-bottom:4px">Your comment</label>
<textarea name="comment" required rows="5" style="width:100%;padding:10px 12px;border:1px solid var(--line);border-radius:10px;font:inherit;margin-bottom:14px;background:#fff"></textarea>
<button class="btn" type="submit">Post comment</button>
</form>
<div style="margin-top:40px">{signup()}</div>
</div></section></article>''')

for _p in MD_POSTS:
    post_page(_p)

# ---------- SHOP ----------
page("shop.html", "Shop | Growth of a Woman", f"""
<section><div class="wrap">
  <p class="eyebrow">Shop</p>
  <h1 style="font-size:clamp(36px,6vw,56px)">Books, guides &amp; journals</h1>
  <p class="lead" style="margin-bottom:32px">Secure checkout through Payhip.</p>
  <div class="grid g3">
    <div class="card"><img class="cover" src="images/for-curly-girls.png" alt="For Curly Girls cover" style="margin-bottom:16px">
      <h3>For Curly Girls! A Lazy Hair Guide</h3><p>{CURLY_TEXT}</p>
      <p class="price" style="margin-top:12px">Digital PDF &middot; $7.99</p><a class="btn" href="{CURLY_LINK}">Buy now</a></div>
    <div class="card"><img class="cover" src="images/ramadan-goals.jpg" alt="Ramadan Goals: A Journal for Women, book cover" style="margin-bottom:16px"><span class="soon">Coming soon</span>
      <h3>Ramadan Goals: A Journal for Women</h3><p style="margin-bottom:8px">The purpose of this journal is to help you remove mental obstacles from your path and focus on what is important, which is building your connection with your Creator.</p></div>
    <div class="card"><img class="cover" src="images/khadijahs-wash-day.jpg" alt="Khadijah's Wash Day, book cover" style="margin-bottom:16px;aspect-ratio:4/3;object-fit:cover;max-width:100%"><span class="soon">Coming soon</span>
      <h3>Khadijah's Wash Day</h3><p style="margin-bottom:8px">Khadijah isn't a fan of wash day. As her mom cares for her curls, Khadijah tries to make sense of why her mother wears hijab outside the house but not at home, and learns that her mom keeps her beauty for her family.</p></div>
  </div>
</div></section>
""")

# ---------- POLLS ----------
def poll(name, q, opts):
    items = "".join(f'<label><input type="radio" name="answer" value="{o}" required> {o}</label>' for o in opts)
    return f'''<form class="card poll" name="{name}" method="POST" data-netlify="true" action="thank-you.html">
<input type="hidden" name="form-name" value="{name}">
<fieldset><legend>{q}</legend>{items}</fieldset>
<p class="anon">Your answer is anonymous.</p>
<button class="btn" type="submit">Submit</button></form>'''

page("polls.html", "Polls | Growth of a Woman", f"""
<section><div class="wrap">
  <p class="eyebrow">Polls</p>
  <h1 style="font-size:clamp(36px,6vw,56px)">Share your voice</h1>
  <p class="lead" style="margin-bottom:32px">Your answer is anonymous.</p>
  <div class="grid g2">
  {poll("children-books-faces", "For your children's books, which illustrations do you prefer?", ["Characters with full faces", "Faceless characters", "Either is fine"])}
  {poll("hair-under-hijab", "What's your biggest hair struggle under your hijab?", ["Breakage or thinning edges", "Dryness", "Itchy scalp or buildup", "Tangles and matting", "No time to care for it"])}
  {poll("marriage-journey", "Where are you in your search for a husband?", ["Not looking yet, preparing myself", "Actively looking", "Talking to someone", "Engaged or intended", "Married or divorced, here to learn or share"])}
  </div>
</div></section>
""")

page("thank-you.html", "Thank you | Growth of a Woman", """
<section class="hero"><div class="wrap">
  <p class="orn">&#10047; &#10022; &#10047;</p>
  <h2>Thank you for sharing.</h2>
  <p class="lead">Your answer is anonymous.</p>
  <a class="btn" href="index.html">Back to home</a>
</div></section>
""")
page("free-guide.html", "Free Guide: Haircut or Trim? | Growth of a Woman", f"""
<section><div class="wrap" style="max-width:620px">{signup()}</div></section>
""")
page("free-guide-thank-you.html", "Your free guide | Growth of a Woman", """
<section class="hero"><div class="wrap">
  <p class="orn">&#10047; &#10022; &#10047;</p>
  <h2>Here's your free guide.</h2>
  <p class="lead">Thank you for joining Growth of a Woman.</p>
  <a class="btn" href="files/Haircut-or-Trim_Free-Guide.pdf" download>Download Haircut or Trim?</a>
  <p style="margin-top:28px"><a href="blog.html">Read the blog &rarr;</a></p>
</div></section>
""")
page("thank-you-comment.html", "Thank you | Growth of a Woman", """
<section class="hero"><div class="wrap">
  <p class="orn">&#10047; &#10022; &#10047;</p>
  <h2>Thank you for your comment.</h2>
  <p class="lead">It will appear on the post once it's been reviewed.</p>
  <a class="btn" href="blog.html">Back to the blog</a>
</div></section>
""")
print("built")

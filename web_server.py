from flask import Flask, jsonify, request, render_template_string, send_from_directory
import hashlib
import hmac
import json
import os
import threading
import time
from urllib.parse import parse_qsl

from config import BOT_TOKEN, UPLOADS_PATH
from database import db

app = Flask(__name__)

STAGE_NAMES = {
    1: "الأولى",
    2: "الثانية",
    3: "الثالثة",
    4: "الرابعة",
}

CATEGORIES = [
    ("subjects", "المواد الدراسية", "📚"),
    ("explanations", "الشروحات", "📖"),
    ("lab", "المختبر", "🔬"),
    ("exams", "الامتحانات", "✍️"),
    ("research", "قسم الرابعة", "🎓"),
]

WEB_APP_HTML = r"""
<!doctype html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>بوت المرحلة</title>
  <script src="https://telegram.org/js/telegram-web-app.js"></script>
  <style>
    :root {
      color-scheme: light dark;
      --bg: #f7f8fb;
      --panel: #ffffff;
      --text: #121826;
      --muted: #667085;
      --line: #dde3ec;
      --accent: #0f766e;
      --accent-2: #2563eb;
      --danger: #b42318;
    }
    body.dark {
      --bg: #101418;
      --panel: #171d23;
      --text: #eef2f6;
      --muted: #a5b1bf;
      --line: #2b3540;
      --accent: #2dd4bf;
      --accent-2: #60a5fa;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      background: var(--bg);
      color: var(--text);
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      letter-spacing: 0;
    }
    header {
      position: sticky;
      top: 0;
      z-index: 10;
      background: var(--panel);
      border-bottom: 1px solid var(--line);
      padding: 14px 16px;
    }
    .wrap { max-width: 860px; margin: 0 auto; padding: 16px; }
    .title { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
    h1 { margin: 0; font-size: 20px; line-height: 1.35; }
    .sub { color: var(--muted); font-size: 13px; margin-top: 4px; }
    .badge {
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 7px 10px;
      color: var(--muted);
      font-size: 12px;
      white-space: nowrap;
    }
    .grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
    .section { margin-top: 14px; }
    button, .link-button {
      width: 100%;
      border: 1px solid var(--line);
      background: var(--panel);
      color: var(--text);
      border-radius: 8px;
      padding: 13px 12px;
      font: inherit;
      text-align: right;
      cursor: pointer;
      text-decoration: none;
      display: block;
    }
    button.primary { border-color: transparent; background: var(--accent); color: white; }
    button.back { color: var(--accent-2); }
    .list { display: grid; gap: 8px; }
    .item-title { font-weight: 700; }
    .item-meta { color: var(--muted); font-size: 12px; margin-top: 5px; }
    .content-text {
      white-space: pre-wrap;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      margin-top: 8px;
      line-height: 1.7;
    }
    .empty, .error {
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
      background: var(--panel);
      color: var(--muted);
      text-align: center;
    }
    .error { color: var(--danger); }
    @media (max-width: 520px) {
      .wrap { padding: 12px; }
      .grid { grid-template-columns: 1fr; }
      h1 { font-size: 18px; }
    }
  </style>
</head>
<body>
  <header>
    <div class="title">
      <div>
        <h1 id="page-title">بوت المرحلة</h1>
        <div class="sub" id="page-subtitle">جار التحميل...</div>
      </div>
      <div class="badge" id="stage-badge">Telegram</div>
    </div>
  </header>
  <main class="wrap">
    <div id="app" class="section"></div>
  </main>
  <script>
    const tg = window.Telegram && window.Telegram.WebApp ? window.Telegram.WebApp : null;
    if (tg) {
      tg.ready();
      tg.expand();
      if (tg.colorScheme === 'dark') document.body.classList.add('dark');
      tg.BackButton.onClick(() => goBack());
    }

    const state = { stack: [], profile: null, categories: [], currentCategory: null, currentSubject: null };
    const app = document.getElementById('app');
    const title = document.getElementById('page-title');
    const subtitle = document.getElementById('page-subtitle');
    const badge = document.getElementById('stage-badge');

    function setHeader(main, sub, stageText) {
      title.textContent = main;
      subtitle.textContent = sub || '';
      badge.textContent = stageText || 'Telegram';
    }
    function setView(name, renderer) {
      state.stack.push(renderer);
      renderBackButton();
      renderer();
    }
    function goBack() {
      if (state.stack.length <= 1) return;
      state.stack.pop();
      renderBackButton();
      state.stack[state.stack.length - 1]();
    }
    function renderBackButton() {
      if (!tg) return;
      if (state.stack.length > 1) tg.BackButton.show();
      else tg.BackButton.hide();
    }
    function esc(value) {
      return String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
    }
    async function api(path, options = {}) {
      const res = await fetch(path, {
        ...options,
        headers: { 'Content-Type': 'application/json', ...(options.headers || {}) }
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'حدث خطأ');
      return data;
    }
    function showError(message) {
      app.innerHTML = `<div class="error">${esc(message)}</div>`;
    }
    function showHome() {
      const profile = state.profile;
      setHeader('بوت المرحلة', profile.full_name || profile.first_name || 'أهلاً بك', `المرحلة ${profile.stage_name}`);
      app.innerHTML = `<div class="grid">${
        state.categories.map(c => `<button data-category="${esc(c.key)}"><span class="item-title">${esc(c.icon)} ${esc(c.name)}</span><div class="item-meta">${c.count} عنصر</div></button>`).join('')
      }</div>`;
      app.querySelectorAll('[data-category]').forEach(btn => {
        btn.addEventListener('click', () => {
          state.currentCategory = state.categories.find(c => c.key === btn.dataset.category);
          setView('subjects', showSubjects);
        });
      });
    }
    function showSubjects() {
      const category = state.currentCategory;
      setHeader(category.name, 'اختر المادة أو القسم', `المرحلة ${state.profile.stage_name}`);
      const subjects = category.subjects || [];
      if (!subjects.length) {
        app.innerHTML = '<div class="empty">لا توجد عناصر حالياً</div>';
        return;
      }
      app.innerHTML = `<div class="list">${subjects.map(s => `<button data-subject="${esc(s.key)}"><span class="item-title">${esc(s.name)}</span></button>`).join('')}</div>`;
      app.querySelectorAll('[data-subject]').forEach(btn => {
        btn.addEventListener('click', () => {
          state.currentSubject = subjects.find(s => s.key === btn.dataset.subject);
          setView('chapters', showChapters);
        });
      });
    }
    function showChapters() {
      const subject = state.currentSubject;
      const category = state.currentCategory.key;
      const chapters = ['lab', 'exams', 'research'].includes(category) || subject.key === 'practical_education'
        ? [1]
        : [1, 2, 3, 4, 5, 6];
      setHeader(subject.name, 'اختر الفصل', `المرحلة ${state.profile.stage_name}`);
      app.innerHTML = `<div class="grid">${chapters.map(ch => `<button data-chapter="${ch}"><span class="item-title">${chapters.length === 1 ? 'المحتوى' : 'الفصل ' + ch}</span></button>`).join('')}</div>`;
      app.querySelectorAll('[data-chapter]').forEach(btn => {
        btn.addEventListener('click', () => setView('content', () => showContent(Number(btn.dataset.chapter))));
      });
    }
    async function showContent(chapter) {
      const subject = state.currentSubject;
      setHeader(subject.name, `الفصل ${chapter}`, `المرحلة ${state.profile.stage_name}`);
      app.innerHTML = '<div class="empty">جار تحميل المحتوى...</div>';
      try {
        const data = await api(`/api/content?stage=${state.profile.stage}&subject_key=${encodeURIComponent(subject.key)}&chapter=${chapter}`);
        if (!data.items.length) {
          app.innerHTML = '<div class="empty">لا يوجد محتوى مرفوع لهذا القسم بعد</div>';
          return;
        }
        app.innerHTML = `<div class="list">${data.items.map(item => `
          <div class="content-text">
            <div class="item-title">#${item.number} - ${esc(item.description || item.type_name)}</div>
            ${item.text ? `<div class="content-text">${esc(item.text)}</div>` : ''}
            ${item.file_url ? `<a class="link-button" href="${esc(item.file_url)}" target="_blank">فتح الملف</a>` : ''}
          </div>
        `).join('')}</div>`;
      } catch (err) {
        showError(err.message);
      }
    }
    async function boot() {
      try {
        const initData = tg ? tg.initData : '';
        const data = await api('/api/bootstrap', {
          method: 'POST',
          body: JSON.stringify({ initData })
        });
        state.profile = data.profile;
        state.categories = data.categories;
        setView('home', showHome);
      } catch (err) {
        setHeader('بوت المرحلة', 'تعذر فتح التطبيق', 'خطأ');
        showError(err.message);
      }
    }
    boot();
  </script>
</body>
</html>
"""


@app.route("/")
def home():
    return "✅ بوت تيليجرام شغال! افتح /app لتجربة واجهة الويب."


@app.route("/app")
def web_app():
    return render_template_string(WEB_APP_HTML)


@app.route("/health")
def health():
    return "OK", 200


@app.route("/api/bootstrap", methods=["POST"])
def api_bootstrap():
    payload = request.get_json(silent=True) or {}
    telegram_user = verify_telegram_init_data(payload.get("initData", ""))
    if not telegram_user:
        return jsonify({"error": "تعذر التحقق من جلسة Telegram. افتح الصفحة من زر Open داخل البوت."}), 401

    user_id = int(telegram_user["id"])
    user_stage = db.get_user_stage(user_id)
    if not user_stage:
        return jsonify({"error": "يرجى إكمال التسجيل من داخل البوت أولاً."}), 403

    stage, full_name = user_stage
    profile = {
        "user_id": user_id,
        "first_name": telegram_user.get("first_name", ""),
        "username": telegram_user.get("username", ""),
        "full_name": full_name,
        "stage": stage,
        "stage_name": STAGE_NAMES.get(stage, str(stage)),
    }
    return jsonify({"profile": profile, "categories": build_categories(stage)})


@app.route("/api/content")
def api_content():
    try:
        stage = int(request.args.get("stage", "0"))
        subject_key = request.args.get("subject_key", "").strip()
        chapter = int(request.args.get("chapter", "1"))
    except ValueError:
        return jsonify({"error": "بيانات الطلب غير صحيحة"}), 400

    if stage not in STAGE_NAMES or not subject_key:
        return jsonify({"error": "بيانات الطلب غير مكتملة"}), 400

    items = []
    for content_id, content_type, description, date_added, content_number in db.get_stage_content(stage, subject_key, chapter):
        content = db.get_stage_content_by_id(content_id)
        if not content:
            continue
        file_path = content[5]
        file_url = build_file_url(file_path)
        items.append({
            "id": content_id,
            "type": content_type,
            "type_name": content_type_name(content_type),
            "description": description,
            "date_added": date_added,
            "number": content_number,
            "text": content[7],
            "file_url": file_url,
        })
    return jsonify({"items": items})


@app.route("/files/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOADS_PATH, filename, as_attachment=False)


def verify_telegram_init_data(init_data):
    if not BOT_TOKEN or not init_data:
        return None

    parsed = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = parsed.pop("hash", None)
    if not received_hash:
        return None

    auth_date = parsed.get("auth_date")
    if auth_date:
        try:
            if time.time() - int(auth_date) > 86400:
                return None
        except ValueError:
            return None

    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(parsed.items()))
    secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(calculated_hash, received_hash):
        return None

    try:
        return json.loads(parsed.get("user", "{}"))
    except json.JSONDecodeError:
        return None


def build_categories(stage):
    result = []
    for key, name, icon in CATEGORIES:
        if key == "research" and stage != 4:
            continue
        subjects = [
            {"name": subject_name, "key": subject_key}
            for subject_name, subject_key in db.get_stage_subjects_by_category(stage, key)
        ]
        result.append({
            "key": key,
            "name": name,
            "icon": icon,
            "count": len(subjects),
            "subjects": subjects,
        })
    return result


def build_file_url(file_path):
    if not file_path:
        return None
    filename = os.path.basename(file_path)
    full_path = os.path.join(UPLOADS_PATH, filename)
    if not os.path.exists(full_path):
        return None
    return f"/files/{filename}"


def content_type_name(content_type):
    return {
        "video": "فيديو",
        "document": "ملف",
        "photo": "صورة",
        "text": "نص",
        "audio": "ملف صوتي",
        "voice": "بصمة صوتية",
    }.get(content_type, "محتوى")


def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)


def start_web_server():
    """تشغيل خادم الويب في خيط منفصل"""
    thread = threading.Thread(target=run_web_server, daemon=True)
    thread.start()
    print(f"🌐 خادم الويب شغال على منفذ {os.environ.get('PORT', 10000)}")
# في نهاية web_server.py، أضف:
if __name__ == "__main__":
    import threading
    import asyncio
    
    # تشغيل الخادم في خيط
    thread = threading.Thread(target=run_web_server, daemon=True)
    thread.start()
    
    # تشغيل البوت
    import main
    asyncio.run(main.main())

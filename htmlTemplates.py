# htmlTemplate.py — Glassy Light (default), Soft Dark companion, High-Contrast friendly
# Uses CSS variables defined in the main app theme (app.py). Falls back to sensible defaults.

css = '''
<style>
:root {
  --radius: 16px;
  --blur: 14px;
  --border-alpha: 0.18;
  /* Fallbacks if app-level variables aren't injected */
  --text: #0e1525;
  --text-muted: #54607a;
  --user-bg: linear-gradient(180deg, rgba(224,242,254,.85), rgba(219,234,254,.7));
  --bot-bg:  linear-gradient(180deg, rgba(248,250,252,.8), rgba(241,245,249,.6));
}

/* Chat bubbles */
.chat-message {
  display: flex;
  gap: 14px;
  align-items: flex-start;
  margin: 10px 0;
  padding: 14px 16px;
  border-radius: 14px;
  color: var(--text);
  backdrop-filter: blur(var(--blur));
  -webkit-backdrop-filter: blur(var(--blur));
  border: 1px solid rgba(255,255,255,var(--border-alpha));
  box-shadow: 0 8px 28px rgba(0,0,0,.08);
  animation: bubble-in .18s ease-out;
}

.chat-message.user {
  background: var(--user-bg);
}

.chat-message.bot {
  background: var(--bot-bg);
}

.chat-message .avatar {
  flex: 0 0 44px;
  width: 44px;
  height: 44px;
}

.chat-message .avatar img {
  width: 44px;
  height: 44px;
  max-width: 44px;
  max-height: 44px;
  border-radius: 50%;
  object-fit: cover;
  box-shadow: 0 4px 12px rgba(0,0,0,.12);
}

.chat-message .message {
  flex: 1;
  min-width: 0;
  padding: 0 .25rem;
  color: var(--text);
}

.chat-message .message p {
  margin: 0 0 .5rem;
  line-height: 1.55;
}

.chat-message .message pre,
.chat-message .message code {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace;
}

.chat-message .message pre {
  background: rgba(0,0,0,.08);
  border: 1px solid rgba(0,0,0,.08);
  padding: .75rem;
  border-radius: 12px;
  overflow: auto;
}

.chat-message .message code {
  background: rgba(0,0,0,.06);
  padding: .15rem .4rem;
  border-radius: 8px;
}

/* Subtle entrance animation (respects reduced motion) */
@keyframes bubble-in {
  from { transform: translateY(4px); opacity: 0; }
  to   { transform: translateY(0);   opacity: 1; }
}
@media (prefers-reduced-motion: reduce) {
  .chat-message { animation: none; }
}

/* Mobile tweaks */
@media (max-width: 640px) {
  .chat-message { padding: 12px; }
  .chat-message .avatar { flex-basis: 36px; width: 36px; height: 36px; }
  .chat-message .avatar img { width: 36px; height: 36px; max-width: 36px; max-height: 36px; }
}

/* Optional high-contrast helper: add class="hc" to a parent container if desired.
   (In the app, the High Contrast theme already increases outlines; this is just a utility.) */
.hc .chat-message {
  outline: 2px solid #111;
  box-shadow: none;
}
</style>
'''

bot_template = '''
<div class="chat-message bot">
  <div class="avatar">
    <img src="https://i.ibb.co/cN0nmSj/Screenshot-2023-05-28-at-02-37-21.png" alt="Bot" />
  </div>
  <div class="message">{{MSG}}</div>
</div>
'''

user_template = '''
<div class="chat-message user">
  <div class="avatar">
    <img src="https://i.ibb.co/rdZC7LZ/Photo-logo-1.png" alt="You" />
  </div>
  <div class="message">{{MSG}}</div>
</div>
'''

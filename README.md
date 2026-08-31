# Kino Kod Bot 🔑🎬

Telegram uchun **kod orqali** kino/drama/serial/anime/multfilm topib beruvchi bot.
Har bir video o'ziga xos noyob **kod**ga ega — foydalanuvchi shu kodni yozsa, mos
video (tavsif bilan) darhol yuboriladi. Majburiy obuna, to'liq admin panel va
stikerlar bilan jonli muloqot mavjud.

## Ishlash tartibi

1. Foydalanuvchi `/start` bosadi
2. Bot majburiy obunani tekshiradi — obuna bo'lmasa, kanal(lar)ga havola beradi
3. Obuna tasdiqlangach, bot: **"🔑 Kodni kiriting..."** deb so'raydi
4. Foydalanuvchi kodni yozadi (masalan `1234`)
5. Kod topilsa — mos video, nomi, kategoriyasi va tavsifi bilan yuboriladi
6. Kod topilmasa — **"❌ Bu kod bo'yicha hech qanday narsa topilmadi"** deb javob beriladi
7. Foydalanuvchi istalgan vaqt yana yangi kod yozishi mumkin

## Admin panel (`/admin`)

- ➕ **Video qo'shish** — kategoriya → nom → tavsif → **noyob kod** → video fayl
  (kod band bo'lsa, bot darhol xabar berib boshqa kod so'raydi)
- 🗑 **Video o'chirish** — kod orqali
- 👤 **Admin qo'shish / o'chirish** — Telegram user_id orqali
- 📊 **Statistika** — foydalanuvchilar, videolar, ko'rishlar, top-5 kontent
- 📣 **Xabar yuborish** — barcha foydalanuvchilarga broadcast

## Stikerlar

Bot quyidagi holatlarda stiker yuboradi (ixtiyoriy, sozlanadi):

- Xush kelibsiz (obunadan keyin)
- "Kodni kiriting" so'raganda
- Kod topilganda
- Kod topilmaganda
- Majburiy obuna xabarida

**Stiker ID sini qanday olish:** botga istalgan stikerni yuboring (hech qanday
menyu/holat ochiq bo'lmasa) — agar siz admin bo'lsangiz, bot avtomatik ravishda
o'sha stikerning `file_id` sini yozib beradi. Shu ID ni nusxalab, `.env`
faylidagi tegishli `STICKER_*` qatoriga joylashtiring.

## O'rnatish

```bash
pip install -r requirements.txt
```

`config.py` faylini oching va yuqori qismidagi qiymatlarni to'g'ridan-to'g'ri to'ldiring:
- `BOT_TOKEN` — @BotFather'dan olingan token
- `OWNER_ID` — sizning Telegram ID raqamingiz (bosh admin)
- `REQUIRED_CHANNELS` — majburiy obuna kanal(lar)i, masalan `["@kanalim", "-1001234567890"]`
- `STICKERS` — xohlasangiz, stiker file_id larini keyinroq to'ldirsangiz ham bo'ladi

**Muhim:** `REQUIRED_CHANNELS` da private kanal ID ishlatsangiz, botni o'sha
kanalga **admin** qilib qo'shing va **"Invite users via link"** huquqini bering
— aks holda bot obuna havolasini yasab bera olmaydi.

**Diqqat — xavfsizlik:** `config.py` ichida bot tokeningiz ochiq matn holida
turadi. Agar bu repo **public** bo'lsa, tokeningizni ko'rgan har kim botingizni
to'liq boshqarib olishi mumkin. Repo albatta **private** bo'lishini tavsiya
qilaman (GitHub → Settings → Danger Zone → Change visibility).

Ishga tushirish:
```bash
python main.py
```

## Loyiha tuzilishi (barcha fayllar bitta papkada, papkalarsiz)

```
kodbot/
├── main.py
├── config.py
├── database.py
├── keyboards.py
├── states.py
├── admin.py         # admin panel
├── user.py           # kod so'rash, tekshirish, video yuborish
├── subscription.py    # majburiy obuna tekshiruvi
├── stickers.py          # xavfsiz stiker yuborish
├── requirements.txt
└── .gitignore
```

## Railway'ga deploy

1. GitHub repo'ga push qiling — repo **private** bo'lsin (tokeningiz config.py'da ochiq turadi)
2. Railway'da yangi loyiha yaratib, repo'ni ulang
3. Start command: `python main.py`
4. SQLite fayli doimiy saqlanishi uchun Railway'da Volume ulashni tavsiya qilaman

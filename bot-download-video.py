# استيراد مكتبة TeleBot لإنشاء بوت تيليجرام
import telebot

# استيراد مكتبة os للتعامل مع الملفات والمجلدات
import os

# استيراد مكتبة re لمعالجة النصوص (Regex)
import re

# استيراد مكتبة pytubefix لتحميل فيديوهات يوتيوب
from pytubefix import YouTube


# توكن البوت (ضع التوكن الحقيقي هنا)
BOT_TOKEN = "ضع التوكن الخاص بك هنا"

# مجلد حفظ الملفات المحملة
OUTPUT = "videos"

# الحد الأقصى لحجم الملف المسموح (50 ميجا)
MAX_SIZE = 50 * 1024 * 1024


# إنشاء كائن البوت باستخدام التوكن
bot = telebot.TeleBot(BOT_TOKEN)

# إنشاء مجلد التحميل إذا لم يكن موجودًا
os.makedirs(OUTPUT, exist_ok=True)


# قاموس لتتبع حالة كل مستخدم (هل ينتظر رابط فيديو أو صوت...)
user_states = {}


# دالة تحميل فيديو من يوتيوب
def download_vd(url):

    # إنشاء كائن الفيديو من الرابط
    yt = YouTube(url)

    # تنظيف عنوان الفيديو من الرموز غير المسموح بها في أسماء الملفات
    safe_title = re.sub(r'[\\/*?:"<>|]', "_", yt.title)

    # إذا كان الفيديو أطول من 10 دقائق
    if yt.length > 600:

        # محاولة تحميل جودة 360p لتقليل الحجم
        stream = yt.streams.filter(res="360p", file_extension='mp4').first()

        # إذا لم توجد جودة 360p نأخذ أقل جودة متاحة
        if not stream:
            stream = yt.streams.get_lowest_resolution()

    else:
        # إذا الفيديو قصير نأخذ أعلى جودة
        stream = yt.streams.get_highest_resolution()

    # تحميل الفيديو إلى المجلد المحدد
    file_path = stream.download(
        output_path=OUTPUT,
        filename=safe_title + ".mp4"
    )

    # طباعة رسالة في الكونسول
    print("Done Download Successfully!")

    # إرجاع مسار الملف والعنوان
    return file_path, safe_title


# دالة تحميل الصوت فقط من الفيديو
def download_mp3(url):
    try:
        # إنشاء كائن الفيديو
        yt = YouTube(url)

        # اختيار أول ستريم صوت فقط
        audio_stream = yt.streams.filter(only_audio=True).first()

        # طباعة اسم الفيديو
        print(f"Downloading: {yt.title}")

        # تنظيف العنوان
        safe_title = re.sub(r'[\\/*?:"<>|]', "_", yt.title)

        # تحميل الملف الصوتي
        out_file = audio_stream.download(
            output_path=OUTPUT,
            filename=safe_title + ".mp3"
        )

        print(f"Downloaded successfully: {out_file}")

        return out_file

    except Exception as e:
        # طباعة الخطأ
        print(f"Error: {e}")
        return None


# التعامل مع أمر /start
@bot.message_handler(commands=['start'])
def start(msg):

    # الرد برسالة ترحيب
    bot.reply_to(msg, "Hi Bro! You Can Download YouTube videos from this bot now!")

    # إنشاء كيبورد أزرار
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2)

    # زر تحميل فيديو
    itembtn1 = telebot.types.KeyboardButton('تحميل فديو')

    # زر تحميل صوت
    itembtn2 = telebot.types.KeyboardButton('تحميل صوت')

    # إضافة الأزرار للكيبورد
    markup.add(itembtn1, itembtn2)

    # إرسال رسالة مع الكيبورد
    bot.send_message(
        msg.chat.id,
        "اختر من الخيارات التالية:",
        reply_markup=markup
    )

    # تعيين حالة المستخدم إلى القائمة
    user_states[msg.chat.id] = "menu"


# التعامل مع اختيار المستخدم من الأزرار
@bot.message_handler(func=lambda message: message.text in ['تحميل فديو', 'تحميل صوت'])
def handle_options(msg):

    if msg.text == 'تحميل فديو':
        # تغيير الحالة إلى انتظار رابط فيديو
        user_states[msg.chat.id] = "waiting_for_video_url"
        bot.reply_to(msg, "أرسل رابط الفيديو الآن...")

    elif msg.text == 'تحميل صوت':
        # تغيير الحالة إلى انتظار رابط صوت
        user_states[msg.chat.id] = "waiting_for_audio_url"
        bot.reply_to(msg, "أرسل رابط الفيديو لتحويله إلى صوت...")


# التعامل مع الرسائل التي تحتوي على روابط يوتيوب
@bot.message_handler(func=lambda message: "youtube.com" in message.text or "youtu.be" in message.text)
def handle_url(msg):

    # استخراج الرابط
    url = msg.text.strip()

    # رقم المحادثة
    chat_id = msg.chat.id

    if chat_id in user_states:

        # إذا كان المستخدم يريد تحميل فيديو
        if user_states[chat_id] == "waiting_for_video_url":

            bot.reply_to(msg, "جاري تحميل الفيديو ...")

            try:
                # تحميل الفيديو
                file_path, safe_title = download_vd(url)

                # حساب حجم الملف
                file_size = os.path.getsize(file_path)

                # التحقق من الحجم
                if file_size > MAX_SIZE:
                    bot.reply_to(msg, f"❌ حجم الفيديو كبير جداً ({file_size//(1024*1024)}MB)\nالحد الأقصى هو 50MB")

                    # حذف الملف
                    if os.path.exists(file_path):
                        os.remove(file_path)

                    user_states[chat_id] = "menu"
                    return

                # إرسال الفيديو
                with open(file_path, "rb") as f:
                    bot.send_video(
                        chat_id,
                        f,
                        caption=f"تم التحميل بنجاح: {safe_title}",
                        timeout=120,
                        supports_streaming=True
                    )

                # حذف الملف بعد الإرسال
                if os.path.exists(file_path):
                    os.remove(file_path)

                # العودة للقائمة
                user_states[chat_id] = "menu"

            except Exception as e:
                bot.reply_to(msg, f"❌ حدث خطأ في تحميل الفيديو:\n{str(e)}")
                user_states[chat_id] = "menu"

                if 'file_path' in locals() and file_path and os.path.exists(file_path):
                    os.remove(file_path)

        # إذا كان المستخدم يريد تحميل صوت
        elif user_states[chat_id] == "waiting_for_audio_url":

            bot.reply_to(msg, "جاري تحميل الصوت ...")

            try:
                file_path = download_mp3(url)

                if file_path and os.path.exists(file_path):

                    # إرسال الملف الصوتي
                    with open(file_path, "rb") as f:
                        bot.send_audio(
                            chat_id,
                            f,
                            caption="تم تحميل الصوت بنجاح",
                            timeout=120
                        )

                    os.remove(file_path)

                else:
                    bot.reply_to(msg, "❌ فشل في تحميل الصوت")

                user_states[chat_id] = "menu"

            except Exception as e:
                bot.reply_to(msg, f"❌ حدث خطأ في تحميل الصوت:\n{str(e)}")
                user_states[chat_id] = "menu"

                if 'file_path' in locals() and file_path and os.path.exists(file_path):
                    os.remove(file_path)

    else:
        # إذا لم تكن هناك حالة محفوظة للمستخدم
        user_states[chat_id] = "waiting_for_video_url"
        handle_url(msg)


# التعامل مع أي رسالة أخرى
@bot.message_handler(func=lambda message: True)
def handle_other_messages(msg):
    bot.reply_to(msg, "❌ يرجى إرسال رابط يوتيوب صحيح أو اختيار أحد الخيارات من الكيبورد")


# طباعة رسالة في الكونسول
print("The bot is running..")

# تشغيل البوت باستمرار
bot.infinity_polling(timeout=60, long_polling_timeout=60)

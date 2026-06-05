# keyboards.py
from telethon import Button
from telethon.tl import types
from database import db
from config import DEVELOPER_ID, WEBAPP_URL, WEBAPP_URL_VALID

class Keyboards:
    @staticmethod
    def main_menu(user_id, stage=4):
        """Main menu for specific stage with Web App button"""
        stage_name = ['أولى', 'ثانية', 'ثالثة', 'رابعة'][stage-1]
        
        buttons = []
        
        # ✅ إضافة زر فتح التطبيق (Web App) - سيكون ظاهراً دائماً
        if WEBAPP_URL_VALID:
            buttons.append([types.KeyboardButtonWebView("🌐 فتح التطبيق", f"{WEBAPP_URL}/app")])
        
        # الأزرار الأساسية
        buttons.extend([
            [Button.inline("📚 المواد الدراسية", f'stage_{stage}:subjects'),
             Button.inline("📖 الشروحات", f'stage_{stage}:explanations')],
            [Button.inline("🔬 المختبر", f'stage_{stage}:lab')],
            [Button.inline("✍️ الامتحانات", f'stage_{stage}:exams'),
             Button.inline("🔍 كلمة البحث", f'stage_{stage}:search')],
            [Button.inline("🤖 الذكاء الاصطناعي", f'stage_{stage}:ai')],
        ])
        
        # قسم خاص بالمرحلة الرابعة
        if stage == 4:
            buttons.append([Button.inline("🎓 قسم خاص بالرابعة", f'stage_{stage}:research')])
        
        # أزرار الدعم والمعلومات
        buttons.extend([
            [Button.inline("📬 تواصل مع الدعم", 'support:contact'),
             Button.inline("⚛️ معلومة فيزيائية", f'stage_{stage}:physics_info')],
            [Button.url("👨‍💼 DevloPeR", "https://t.me/shahm41")]
        ])
        
        # زر إدارة الأدمن (للمطور فقط)
        if user_id == DEVELOPER_ID:
            buttons.append([Button.inline("🔐 إدارة الأدمن", 'admin:manage')])
            
        return buttons

    @staticmethod
    def lab_courses_menu(stage):
        """Keyboard for lab courses selection"""
        return [
            [Button.inline("الكورس الأول", f'lab_course:select:{stage}:1')],
            [Button.inline("الكورس الثاني", f'lab_course:select:{stage}:2')],
            [Button.inline("العودة", f'stage_{stage}:home')]
        ]

    @staticmethod
    def stage_category_menu(stage, category, is_admin=False):
        """Category menu for specific stage - ترتيب الأزرار بشكل متناسق"""
        subjects = db.get_stage_subjects_by_category(stage, category)
        
        # ترتيب المواد بشكل منظم حسب النوع
        if category in ['subjects', 'explanations', 'lab', 'exams', 'research']:
            subjects.sort(key=lambda x: x[0])
        
        buttons = []
        
        # تقسيم المواد إلى صفوف بنظام: صف فردي زرين، صف زوجي زر واحد
        i = 0
        while i < len(subjects):
            if i % 2 == 0:  # الصفوف الزوجية (0, 2, 4...) - زرين
                if i + 1 < len(subjects):
                    name_ar1, key1 = subjects[i]
                    name_ar2, key2 = subjects[i + 1]
                    display_name1 = name_ar1[:15] + "..." if len(name_ar1) > 15 else name_ar1
                    display_name2 = name_ar2[:15] + "..." if len(name_ar2) > 15 else name_ar2
                    buttons.append([
                        Button.inline(display_name1, f'stage_subject:{stage}:{key1}'),
                        Button.inline(display_name2, f'stage_subject:{stage}:{key2}')
                    ])
                    i += 2
                else:  # إذا كان عدد المواد فردي وآخر عنصر
                    name_ar, key = subjects[i]
                    display_name = name_ar[:15] + "..." if len(name_ar) > 15 else name_ar
                    buttons.append([Button.inline(display_name, f'stage_subject:{stage}:{key}')])
                    i += 1
            else:  # الصفوف الفردية (1, 3, 5...) - زر واحد
                name_ar, key = subjects[i]
                display_name = name_ar[:15] + "..." if len(name_ar) > 15 else name_ar
                buttons.append([Button.inline(display_name, f'stage_subject:{stage}:{key}')])
                i += 1
        
        # زر العودة
        if category == 'lab':
            buttons.append([Button.inline("العودة", f'stage_{stage}:lab')])
        else:
            buttons.append([Button.inline("العودة", f'stage_{stage}:home')])
        
        return buttons

    @staticmethod
    def stage_chapters_menu(stage, subject_key, is_admin=False):
        """Chapters menu for specific stage"""
        subject = db.get_stage_subject(stage, subject_key)
        if not subject:
            return None
            
        # إذا كانت التربية العملية في المرحلة الرابعة، لا تعرض فصول
        if stage == 4 and subject_key == 'practical_education':
            return None
            
        if subject[3] in ['lab', 'exams', 'research']:
            return None
        
        buttons = []
        
        # ترتيب الفصول بنظام: صف فردي زرين، صف زوجي زر واحد
        chapters = list(range(1, 7))
        i = 0
        while i < len(chapters):
            if i % 2 == 0:  # الصفوف الزوجية (0, 2, 4...) - زرين
                if i + 1 < len(chapters):
                    buttons.append([
                        Button.inline(f"الفصل {chapters[i]}", f'stage_chapter:{stage}:{subject_key}:{chapters[i]}'),
                        Button.inline(f"الفصل {chapters[i+1]}", f'stage_chapter:{stage}:{subject_key}:{chapters[i+1]}')
                    ])
                    i += 2
                else:  # إذا كان عدد الفصول فردي وآخر فصل
                    buttons.append([Button.inline(f"الفصل {chapters[i]}", f'stage_chapter:{stage}:{subject_key}:{chapters[i]}')])
                    i += 1
            else:  # الصفوف الفردية (1, 3, 5...) - زر واحد
                buttons.append([Button.inline(f"الفصل {chapters[i]}", f'stage_chapter:{stage}:{subject_key}:{chapters[i]}')])
                i += 1
        
        buttons.append([Button.inline("العودة", f'stage_{stage}:{subject[3]}')])
        return buttons

    @staticmethod
    def stage_chapter_empty_menu(stage, subject_key, chapter_num, is_admin=False):
        """قائمة الفصل عندما لا يوجد محتوى"""
        buttons = []
        
        if is_admin:
            buttons.append([Button.inline("➕ إضافة محتوى", f'stage_content:add:{stage}:{subject_key}:{chapter_num}')])
        
        subject = db.get_stage_subject(stage, subject_key)
        buttons.append([Button.inline("العودة", f'stage_{stage}:{subject[3]}')])
        
        return buttons

    @staticmethod
    def stage_content_list_menu(stage, subject_key, chapter_num, content_list, is_admin=False):
        """قائمة المحتوى في الفصل"""
        buttons = []
        
        for content_id, content_type, description, date_added, content_number in content_list:
            icon = '🎥' if content_type == 'video' else '📄' if content_type == 'document' else '🖼️' if content_type == 'photo' else '📝' if content_type == 'text' else '🎵' if content_type == 'audio' else '🎤'
            btn_text = f"{icon} #{content_number} - {description[:15]}..." if description else f"{icon} محتوى #{content_number}"
            buttons.append([Button.inline(btn_text, f'stage_content:view:{content_id}')])
        
        if is_admin:
            buttons.append([Button.inline("➕ إضافة محتوى", f'stage_content:add:{stage}:{subject_key}:{chapter_num}')])
        
        subject = db.get_stage_subject(stage, subject_key)
        buttons.append([Button.inline("العودة", f'stage_{stage}:{subject[3]}')])
        
        return buttons

    @staticmethod
    def content_type_selection_menu(stage, subject_key, chapter_num):
        """قائمة اختيار نوع المحتوى محدثة"""
        return [
            [Button.inline("🎥 فيديو", f'stage_content:upload_type:{stage}:{subject_key}:{chapter_num}:video'),
             Button.inline("📄 ملف", f'stage_content:upload_type:{stage}:{subject_key}:{chapter_num}:document')],
            [Button.inline("🖼️ صورة", f'stage_content:upload_type:{stage}:{subject_key}:{chapter_num}:photo'),
             Button.inline("📝 نص", f'stage_content:upload_type:{stage}:{subject_key}:{chapter_num}:text')],
            [Button.inline("🎵 ملف صوتي", f'stage_content:upload_type:{stage}:{subject_key}:{chapter_num}:audio'),
             Button.inline("🎤 بصمة صوت", f'stage_content:upload_type:{stage}:{subject_key}:{chapter_num}:voice')],
            [Button.inline("❌ إلغاء", f'stage_chapter:{stage}:{subject_key}:{chapter_num}')]
        ]

    @staticmethod
    def admin_management_menu():
        """Keyboard for admin management"""
        return [
            [Button.inline("👥 قسم الأدمنية", 'admin:admin_section'), Button.inline("🚫 قسم الحظر", 'admin:ban_section')],
            [Button.inline("📊 قسم الإحصائيات", 'admin:stats_section')],
            [Button.inline("🔍 قنوات البحث", 'admin:search_channels'), Button.inline("📢 القناة الإجبارية", 'admin:channel_manage')],
            [Button.inline("💬 إدارة التعليقات", 'admin:manage_comments')],
            [Button.inline("📩 تذاكر الدعم", 'admin:support_tickets'), Button.inline("🔎 استعراض المراحل", 'admin:select_stage')],
            [Button.inline("🤖 إعدادات الذكاء", 'admin:ai_settings'), Button.inline("📚 إعدادات المعلومات", 'admin:physics_settings')],
            [Button.inline("العودة", 'main:home')]
        ]

    @staticmethod
    def admin_stage_selector():
        """Keyboard allowing admin/developer to select any stage to browse"""
        return [
            [Button.inline("المرحلة الأولى", 'admin:select_stage:1'),
             Button.inline("المرحلة الثانية", 'admin:select_stage:2')],
            [Button.inline("المرحلة الثالثة", 'admin:select_stage:3'),
             Button.inline("المرحلة الرابعة", 'admin:select_stage:4')],
            [Button.inline("العودة", 'admin:manage')]
        ]

    @staticmethod
    def admin_section_menu():
        """Sub-menu for admin management"""
        return [
            [Button.inline("➕ رفع أدمن", 'admin:add'),
             Button.inline("➖ حذف أدمن", 'admin:remove')],
            [Button.inline("📋 قائمة الأدمن", 'admin:list')],
            [Button.inline("العودة", 'admin:manage')]
        ]

    @staticmethod
    def ban_section_menu():
        """Sub-menu for ban management"""
        return [
            [Button.inline("🚫 حظر مستخدم", 'admin:ban_user'),
             Button.inline("✅ إلغاء حظر مستخدم", 'admin:unban_user')],
            [Button.inline("العودة", 'admin:manage')]
        ]

    @staticmethod
    def stats_section_menu():
        """Sub-menu for statistics - محدث مع جميع الخيارات"""
        return [
            [Button.inline("👥 جميع المستخدمين", 'admin:user_stats:all')],
            [Button.inline("🎓 المرحلة الأولى", 'admin:user_stats:1'),
             Button.inline("🎓 المرحلة الثانية", 'admin:user_stats:2')],
            [Button.inline("🎓 المرحلة الثالثة", 'admin:user_stats:3'),
             Button.inline("🎓 المرحلة الرابعة", 'admin:user_stats:4')],
            [Button.inline("📊 إحصائيات شاملة", 'admin:detailed_stats')],
            [Button.inline("👤 المستخدمين الجدد", 'admin:new_users')],
            [Button.inline("📢 إرسال إذاعة", 'admin:broadcast')],
            [Button.inline("العودة", 'admin:manage')]
        ]

    @staticmethod
    def channel_management_menu():
        """Keyboard for channel management"""
        channel_info = db.get_required_channel()
        
        if channel_info:
            return [
                [Button.inline("➖ إزالة القناة الإجبارية", 'admin:channel_remove')],
                [Button.url("🔗 الانتقال للقناة", f"https://t.me/{channel_info[1]}")],
                [Button.inline("العودة", 'admin:manage')]
            ]
        else:
            return [
                [Button.inline("➕ إضافة قناة إجبارية", 'admin:channel_add')],
                [Button.inline("العودة", 'admin:manage')]
            ]
        
    @staticmethod
    def search_channels_management(stage=None):
        """Keyboard for search channels management مع إمكانية التصفية حسب المرحلة"""
        if stage:
            channels = db.get_search_channels(stage)
        else:
            channels = db.get_search_channels()
            
        buttons = []
        
        # تجميع القنوات حسب المرحلة
        channels_by_stage = {}
        for channel in channels:
            channel_stage = channel[3]
            if channel_stage not in channels_by_stage:
                channels_by_stage[channel_stage] = []
            channels_by_stage[channel_stage].append(channel)
        
        # عرض القنوات مصنفة حسب المرحلة
        for stage_num in sorted(channels_by_stage.keys()):
            stage_name = ['أولى', 'ثانية', 'ثالثة', 'رابعة'][stage_num-1]
            buttons.append([Button.inline(f"🎓 المرحلة {stage_name}", f'none')])
            
            for channel in channels_by_stage[stage_num]:
                btn_text = f"➖ {channel[2]} (@{channel[1]})"
                buttons.append([Button.inline(btn_text, f'admin:remove_search_channel:{channel[0]}:{stage_num}')])
        
        buttons.extend([
            [Button.inline("➕ إضافة قناة بحث", 'admin:add_search_channel')],
            [Button.inline("🔄 فحص جميع القنوات", 'admin:check_all_channels'),
             Button.inline("📊 إحصائيات البحث", 'admin:search_stats')],
            [Button.inline("العودة", 'admin:search_channels')]
        ])
        return buttons

    @staticmethod
    def stage_selection_for_channel():
        """Keyboard for selecting stage when adding search channel"""
        return [
            [Button.inline("المرحلة الأولى", f'admin:add_search_channel_stage:1'),
             Button.inline("المرحلة الثانية", f'admin:add_search_channel_stage:2')],
            [Button.inline("المرحلة الثالثة", f'admin:add_search_channel_stage:3'),
             Button.inline("المرحلة الرابعة", f'admin:add_search_channel_stage:4')],
            [Button.inline("العودة", 'admin:search_channels')]
        ]

    @staticmethod
    def admin_comments_menu():
        """Keyboard for admin to view all comments"""
        comments = db.get_all_comments()
        buttons = []
        
        if not comments:
            buttons.append([Button.inline("لا توجد تعليقات", f'none')])
        else:
            for comment in comments:
                user_info = f"{comment[3]}" if comment[3] else f"@{comment[4]}" if comment[4] else f"المستخدم {comment[0]}"
                btn_text = f"💬 {comment[5]} - {user_info} (المرحلة {comment[6]})"
                buttons.append([Button.inline(btn_text, f'comment:admin_view:{comment[0]}')])
        
        buttons.append([Button.inline("العودة", 'admin:manage')])
        return buttons

    @staticmethod
    def support_tickets_menu():
        """Keyboard for support tickets"""
        tickets = db.get_support_tickets()
        buttons = []
        
        if not tickets:
            buttons.append([Button.inline("لا توجد تذاكر مفتوحة", f'none')])
        else:
            for ticket in tickets:
                user_info = f"{ticket[3]}" if ticket[3] else f"@{ticket[4]}" if ticket[4] else f"المستخدم {ticket[0]}"
                btn_text = f"📩 {user_info} - {ticket[1][:20]}... (المرحلة {ticket[2]})"
                buttons.append([Button.inline(btn_text, f'admin:view_ticket:{ticket[0]}')])
        
        buttons.append([Button.inline("العودة", 'admin:manage')])
        return buttons

    @staticmethod
    def stage_selection_menu(full_name):
        """Keyboard for stage selection during registration"""
        return [
            [Button.inline("المرحلة الأولى", f'register_stage:1:{full_name}'),
             Button.inline("المرحلة الثانية", f'register_stage:2:{full_name}')],
            [Button.inline("المرحلة الثالثة", f'register_stage:3:{full_name}'),
             Button.inline("المرحلة الرابعة", f'register_stage:4:{full_name}')]
        ]

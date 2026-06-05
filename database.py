# database.py
import json
import os
import threading
import time
import logging
from json import JSONDecodeError
from datetime import datetime, date
from config import DEVELOPER_ID, DB_FILES

class Database:
    def __init__(self):
        self.db_files = DB_FILES
        self._lock = threading.RLock()
        self.create_files()
        self.insert_default_data()

        # simple in-memory rate-limit cache: {user_id: last_comment_timestamp}
        self._last_comment_ts = {}
        logging.basicConfig(level=logging.INFO)

    def create_files(self):
        """إنشاء ملفات JSON إذا لم تكن موجودة"""
        for key, file in self.db_files.items():
            if not os.path.exists(file):
                default = []
                # بعض الملفات من الأفضل أن تكون قواميس
                if key in ('settings', 'comments_meta', 'ai_usage'):
                    default = {}
                with open(file, 'w', encoding='utf-8') as f:
                    json.dump(default, f, ensure_ascii=False, indent=4)

    def insert_default_data(self):
        """إدخال البيانات الافتراضية (المواد، المطور، إعدادات الذكاء الاصطناعي)"""
        # المواد الافتراضية
        all_subjects = [
            # المرحلة الأولى - الأسماء المحدثة
            (1, 'الرياضيات', 'mathematics', 'mathematics', 'subjects'),
            (1, 'اللغة العربية', 'arabic', 'arabic', 'subjects'),
            (1, 'اللغة الانجليزية', 'english', 'english', 'subjects'),
            (1, 'الحراره وخواص المادة', 'heat_material', 'heat_material', 'subjects'),
            (1, 'الكهربائية', 'electricity', 'electricity', 'subjects'),
            (1, 'اصول التربية', 'education_principles', 'education_principles', 'subjects'),
            (1, 'علم النفس', 'psychology', 'psychology', 'subjects'),
            (1, 'المكانيك', 'mechanics', 'mechanics', 'subjects'),
            (1, 'الحقوق والديمقراطية', 'rights_democracy', 'rights_democracy', 'subjects'),
            (1, 'الحاسوب', 'computer', 'computer', 'subjects'),
            
            # شروحات المرحلة الأولى
            (1, 'شرح الرياضيات', 'mathematics_exp', 'mathematics_exp', 'explanations'),
            (1, 'شرح اللغة العربية', 'arabic_exp', 'arabic_exp', 'explanations'),
            (1, 'شرح اللغة الانجليزية', 'english_exp', 'english_exp', 'explanations'),
            (1, 'شرح الحراره وخواص المادة', 'heat_material_exp', 'heat_material_exp', 'explanations'),
            (1, 'شرح الكهربائية', 'electricity_exp', 'electricity_exp', 'explanations'),
            (1, 'شرح اصول التربية', 'education_principles_exp', 'education_principles_exp', 'explanations'),
            (1, 'شرح علم النفس', 'psychology_exp', 'psychology_exp', 'explanations'),
            (1, 'شرح المكانيك', 'mechanics_exp', 'mechanics_exp', 'explanations'),
            (1, 'شرح الحقوق والديمقراطية', 'rights_democracy_exp', 'rights_democracy_exp', 'explanations'),
            (1, 'شرح الحاسوب', 'computer_exp', 'computer_exp', 'explanations'),
            
            # مختبرات المرحلة الأولى (محدثة)
            (1, 'مختبر الميكانيك', 'mechanics_lab', 'mechanics_lab', 'lab'),
            (1, 'مختبر الكهربائية', 'electricity_lab', 'electricity_lab', 'lab'),
            (1, 'مختبر الحاسبات', 'computers_lab', 'computers_lab', 'lab'),
            
            # امتحانات المرحلة الأولى
            (1, 'امتحان الرياضيات', 'mathematics_exam', 'mathematics_exam', 'exams'),
            (1, 'امتحان اللغة العربية', 'arabic_exam', 'arabic_exam', 'exams'),
            (1, 'امتحان اللغة الانجليزية', 'english_exam', 'english_exam', 'exams'),
            (1, 'امتحان الحراره وخواص المادة', 'heat_material_exam', 'heat_material_exam', 'exams'),
            (1, 'امتحان الكهربائية', 'electricity_exam', 'electricity_exam', 'exams'),
            (1, 'امتحان اصول التربية', 'education_principles_exam', 'education_principles_exam', 'exams'),
            (1, 'امتحان علم النفس', 'psychology_exam', 'psychology_exam', 'exams'),
            (1, 'امتحان المكانيك', 'mechanics_exam', 'mechanics_exam', 'exams'),
            (1, 'امتحان الحقوق والديمقراطية', 'rights_democracy_exam', 'rights_democracy_exam', 'exams'),
            (1, 'امتحان الحاسوب', 'computer_exam', 'computer_exam', 'exams'),
            
            # المرحلة الثانية
            (2, 'الرياضيات', 'mathematics', 'mathematics', 'subjects'),
            (2, 'الفلك', 'astronomy', 'astronomy', 'subjects'),
            (2, 'جرائم البعث', 'baath_crimes', 'baath_crimes', 'subjects'),
            (2, 'الصوت', 'sound', 'sound', 'subjects'),
            (2, 'الكهربائية', 'electricity', 'electricity', 'subjects'),
            (2, 'البصريات', 'optics', 'optics', 'subjects'),
            (2, 'الانكليزية', 'english', 'english', 'subjects'),
            (2, 'عربي', 'arabic', 'arabic', 'subjects'),
            (2, 'حاسبات', 'computer', 'computer', 'subjects'),
            (2, 'الادارة', 'management', 'management', 'subjects'),
            (2, 'تعليم التفكير', 'thinking_education', 'thinking_education', 'subjects'),
            (2, 'المنهج والبحث العلمي', 'curriculum_research', 'curriculum_research', 'subjects'),
            
            (2, 'شرح الرياضيات', 'mathematics_exp', 'mathematics_exp', 'explanations'),
            (2, 'شرح الفلك', 'astronomy_exp', 'astronomy_exp', 'explanations'),
            (2, 'شرح جرائم البعث', 'baath_crimes_exp', 'baath_crimes_exp', 'explanations'),
            (2, 'شرح الصوت', 'sound_exp', 'sound_exp', 'explanations'),
            (2, 'شرح الكهربائية', 'electricity_exp', 'electricity_exp', 'explanations'),
            (2, 'شرح البصريات', 'optics_exp', 'optics_exp', 'explanations'),
            (2, 'شرح الانكليزية', 'english_exp', 'english_exp', 'explanations'),
            (2, 'شرح عربي', 'arabic_exp', 'arabic_exp', 'explanations'),
            (2, 'شرح حاسبات', 'computer_exp', 'computer_exp', 'explanations'),
            (2, 'شرح الادارة', 'management_exp', 'management_exp', 'explanations'),
            (2, 'شرح تعليم التفكير', 'thinking_education_exp', 'thinking_education_exp', 'explanations'),
            (2, 'شرح المنهج والبحث العلمي', 'curriculum_research_exp', 'curriculum_research_exp', 'explanations'),
            
            (2, 'مختبر البرمجة', 'programming_lab', 'programming_lab', 'lab'),
            (2, 'مختبر الكهربائية', 'electricity_lab', 'electricity_lab', 'lab'),
            (2, 'مختبر البصريات', 'optics_lab', 'optics_lab', 'lab'),
            
            (2, 'امتحان الرياضيات', 'mathematics_exam', 'mathematics_exam', 'exams'),
            (2, 'امتحان الفلك', 'astronomy_exam', 'astronomy_exam', 'exams'),
            (2, 'امتحان جرائم البعث', 'baath_crimes_exam', 'baath_crimes_exam', 'exams'),
            (2, 'امتحان الصوت', 'sound_exam', 'sound_exam', 'exams'),
            (2, 'امتحان الكهربائية', 'electricity_exam', 'electricity_exam', 'exams'),
            (2, 'امتحان البصريات', 'optics_exam', 'optics_exam', 'exams'),
            (2, 'امتحان الانكليزية', 'english_exam', 'english_exam', 'exams'),
            (2, 'امتحان عربي', 'arabic_exam', 'arabic_exam', 'exams'),
            (2, 'امتحان حاسبات', 'computer_exam', 'computer_exam', 'exams'),
            (2, 'امتحان الادارة', 'management_exam', 'management_exam', 'exams'),
            (2, 'امتحان تعليم التفكير', 'thinking_education_exam', 'thinking_education_exam', 'exams'),
            (2, 'امتحان المنهج والبحث العلمي', 'curriculum_research_exam', 'curriculum_research_exam', 'exams'),
            
            # المرحلة الثالثة
            (3, 'الدوال العقدية', 'complex_functions', 'complex_functions', 'subjects'),
            (3, 'الفيزياء الذرية', 'atomic_physics', 'atomic_physics', 'subjects'),
            (3, 'الالكترونيات', 'electronics', 'electronics', 'subjects'),
            (3, 'الثرموداينمك', 'thermodynamics', 'thermodynamics', 'subjects'),
            (3, 'مناهج وطرق التدريس', 'teaching_methods', 'teaching_methods', 'subjects'),
            (3, 'الارشاد التربوي', 'educational_guidance', 'educational_guidance', 'subjects'),
            (3, 'الميكانيك المتقدم', 'advanced_mechanics', 'advanced_mechanics', 'subjects'),
            (3, 'الانواء الجوية', 'meteorology', 'meteorology', 'subjects'),
            
            (3, 'شرح الدوال العقدية', 'complex_functions_exp', 'complex_functions_exp', 'explanations'),
            (3, 'شرح الفيزياء الذرية', 'atomic_physics_exp', 'atomic_physics_exp', 'explanations'),
            (3, 'شرح الالكترونيات', 'electronics_exp', 'electronics_exp', 'explanations'),
            (3, 'شرح الثرموداينمك', 'thermodynamics_exp', 'thermodynamics_exp', 'explanations'),
            (3, 'شرح مناهج وطرق التدريس', 'teaching_methods_exp', 'teaching_methods_exp', 'explanations'),
            (3, 'شرح الارشاد التربوي', 'educational_guidance_exp', 'educational_guidance_exp', 'explanations'),
            (3, 'شرح الميكانيك المتقدم', 'advanced_mechanics_exp', 'advanced_mechanics_exp', 'explanations'),
            (3, 'شرح الانواء الجوية', 'meteorology_exp', 'meteorology_exp', 'explanations'),
            
            (3, 'مختبر الالكترونيات', 'electronics_lab', 'electronics_lab', 'lab'),
            (3, 'مختبر الذرية', 'atomic_lab', 'atomic_lab', 'lab'),
            
            (3, 'امتحان الدوال العقدية', 'complex_functions_exam', 'complex_functions_exam', 'exams'),
            (3, 'امتحان الفيزياء الذرية', 'atomic_physics_exam', 'atomic_physics_exam', 'exams'),
            (3, 'امتحان الالكترونيات', 'electronics_exam', 'electronics_exam', 'exams'),
            (3, 'امتحان الثرموداينمك', 'thermodynamics_exam', 'thermodynamics_exam', 'exams'),
            (3, 'امتحان مناهج وطرق التدريس', 'teaching_methods_exam', 'teaching_methods_exam', 'exams'),
            (3, 'امتحان الارشاد التربوي', 'educational_guidance_exam', 'educational_guidance_exam', 'exams'),
            (3, 'امتحان الميكانيك المتقدم', 'advanced_mechanics_exam', 'advanced_mechanics_exam', 'exams'),
            (3, 'امتحان الانواء الجوية', 'meteorology_exam', 'meteorology_exam', 'exams'),
            
            # المرحلة الرابعة - محدثة لتشمل 7 مواد مع النووية والليزر
            (4, 'الميكانيك الكمي', 'quantum_mechanics', 'quantum_mechanics', 'subjects'),
            (4, 'الفيزياء الصلبة', 'solid_state_physics', 'solid_state_physics', 'subjects'),
            (4, 'الفيزياء النووية', 'nuclear_physics', 'nuclear_physics', 'subjects'),
            (4, 'الليزر', 'laser', 'laser', 'subjects'),
            (4, 'الكهرومغناطيسية', 'electromagnetism', 'electromagnetism', 'subjects'),
            (4, 'التربية العملية', 'practical_education', 'practical_education', 'subjects'),
            (4, 'القياس والتقويم', 'measurement_evaluation', 'measurement_evaluation', 'subjects'),
            
            # شروحات المرحلة الرابعة
            (4, 'شرح الميكانيك الكمي', 'quantum_mechanics_exp', 'quantum_mechanics_exp', 'explanations'),
            (4, 'شرح الفيزياء الصلبة', 'solid_state_physics_exp', 'solid_state_physics_exp', 'explanations'),
            (4, 'شرح الفيزياء النووية', 'nuclear_physics_exp', 'nuclear_physics_exp', 'explanations'),
            (4, 'شرح الليزر', 'laser_exp', 'laser_exp', 'explanations'),
            (4, 'شرح الكهرومغناطيسية', 'electromagnetism_exp', 'electromagnetism_exp', 'explanations'),
            (4, 'شرح التربية العملية', 'practical_education_exp', 'practical_education_exp', 'explanations'),
            (4, 'شرح القياس والتقويم', 'measurement_evaluation_exp', 'measurement_evaluation_exp', 'explanations'),
            
            # مختبرات المرحلة الرابعة (أصبحت جزء من المواد الدراسية)
            (4, 'مختبر الميكانيك الكمي', 'quantum_mechanics_lab', 'quantum_mechanics_lab', 'lab'),
            (4, 'مختبر الفيزياء النووية', 'nuclear_physics_lab', 'nuclear_physics_lab', 'lab'),
            (4, 'مختبر الليزر', 'laser_lab', 'laser_lab', 'lab'),
            
            # امتحانات المرحلة الرابعة
            (4, 'امتحان الميكانيك الكمي', 'quantum_mechanics_exam', 'quantum_mechanics_exam', 'exams'),
            (4, 'امتحان الفيزياء الصلبة', 'solid_state_physics_exam', 'solid_state_physics_exam', 'exams'),
            (4, 'امتحان الفيزياء النووية', 'nuclear_physics_exam', 'nuclear_physics_exam', 'exams'),
            (4, 'امتحان الليزر', 'laser_exam', 'laser_exam', 'exams'),
            (4, 'امتحان الكهرومغناطيسية', 'electromagnetism_exam', 'electromagnetism_exam', 'exams'),
            (4, 'امتحان التربية العملية', 'practical_education_exam', 'practical_education_exam', 'exams'),
            (4, 'امتحان القياس والتقويم', 'measurement_evaluation_exam', 'measurement_evaluation_exam', 'exams'),
            
            # قسم البحث للمرحلة الرابعة
            (4, 'البحث', 'physics_research', 'physics_research', 'research'),
            (4, 'المشاهدة', 'mathematics_research', 'mathematics_research', 'research'),
            (4, 'التطبيق ', 'computer_research', 'computer_research', 'research')
        ]
        
        # نكتب المواد في ملف subjects.json فقط إذا لم يكن الملف يحتوي بيانات
        subjects_data = []
        for subject in all_subjects:
            subjects_data.append({
                'stage': subject[0],
                'name_ar': subject[1],
                'name_en': subject[2],
                'key': subject[3],
                'category': subject[4]
            })
        current_subjects = self._read_data('subjects')
        if not current_subjects:
            self._write_data('subjects', subjects_data)
        
        # إضافة المطور كأدمن افتراضي إذا لم يكن موجوداً
        admins = self._read_data('admins')
        if not any(a.get('user_id') == DEVELOPER_ID for a in admins):
            admins.append({
                'user_id': DEVELOPER_ID,
                'username': 'shahm41',
                'full_name': 'عباس غزوان عبد',
                'date_added': datetime.now().isoformat(),
                'added_by': DEVELOPER_ID
            })
            self._write_data('admins', admins)

    def _read_data(self, key):
        """قراءة البيانات من ملف JSON"""
        filename = self.db_files[key]
        try:
            with self._lock:
                with open(filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except FileNotFoundError:
            # إذا لم يكن الملف موجوداً، إنشاؤه كقائمة فارغة
            default = []
            if key in ('settings', 'comments_meta', 'ai_usage'):
                default = {}
            with self._lock:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(default, f, ensure_ascii=False, indent=4)
            return default
        except JSONDecodeError:
            # ملف تالف — إعادة تهيئته لقائمة فارغة (لا تفشل العملية)
            default = []
            if key in ('settings', 'comments_meta', 'ai_usage'):
                default = {}
            with self._lock:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(default, f, ensure_ascii=False, indent=4)
            return default

    def _safe_write(self, key, data, retries: int = 3, delay: float = 0.1):
        """Safe atomic write with retries."""
        filename = self.db_files[key]
        tmp_filename = filename + '.tmp'
        for attempt in range(retries):
            try:
                with self._lock:
                    with open(tmp_filename, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=4)
                    os.replace(tmp_filename, filename)
                return True
            except Exception as e:
                logging.exception('Write failed for %s (attempt %s): %s', filename, attempt + 1, e)
                time.sleep(delay)
        raise

    def _write_data(self, key, data):
        """كتابة البيانات إلى ملف JSON"""
        return self._safe_write(key, data)

    # ========== User Management ========== #

    def add_user(self, user_id, username, first_name, last_name):
        users = self._read_data('users')
        # التحقق إذا كان المستخدم موجوداً بالفعل
        for user in users:
            if user['user_id'] == user_id:
                # تحديث البيانات
                user['username'] = username
                user['first_name'] = first_name
                user['last_name'] = last_name
                user['last_active'] = datetime.now().isoformat()
                user['is_new'] = False
                break
        else:
            # إضافة مستخدم جديد
            users.append({
                'user_id': user_id,
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'date_joined': datetime.now().isoformat(),
                'last_active': datetime.now().isoformat(),
                'is_new': True,
                'is_banned': False
            })
        self._write_data('users', users)
        return True

    def get_user_stage(self, user_id):
        users_stages = self._read_data('users_stages')
        for user_stage in users_stages:
            if user_stage['user_id'] == user_id:
                return (user_stage['stage'], user_stage['full_name'])
        return None

    def set_user_stage(self, user_id, full_name, stage):
        users_stages = self._read_data('users_stages')
        # البحث عن المستخدم وتحديثه أو إضافته
        for user_stage in users_stages:
            if user_stage['user_id'] == user_id:
                user_stage['full_name'] = full_name
                user_stage['stage'] = stage
                user_stage['date_registered'] = datetime.now().isoformat()
                break
        else:
            users_stages.append({
                'user_id': user_id,
                'full_name': full_name,
                'stage': stage,
                'date_registered': datetime.now().isoformat()
            })
        self._write_data('users_stages', users_stages)
        
        # تحديث حالة المستخدم ليصبح غير جديد
        users = self._read_data('users')
        for user in users:
            if user['user_id'] == user_id:
                user['is_new'] = False
                user['last_active'] = datetime.now().isoformat()
                break
        self._write_data('users', users)
        return True

    def update_user_activity(self, user_id):
        users = self._read_data('users')
        for user in users:
            if user['user_id'] == user_id:
                user['last_active'] = datetime.now().isoformat()
                break
        self._write_data('users', users)

    def get_all_users(self):
        users = self._read_data('users')
        return [user['user_id'] for user in users if not user.get('is_banned', False)]

    def get_new_users(self):
        users = self._read_data('users')
        new_users = []
        for user in users:
            if user.get('is_new', False) and not user.get('is_banned', False):
                new_users.append((
                    user['user_id'],
                    user.get('first_name', ''),
                    user.get('last_name', ''),
                    user.get('username', '')
                ))
        return new_users

    def count_users(self):
        users = self._read_data('users')
        return len([user for user in users if not user.get('is_banned', False)])

    def is_banned(self, user_id):
        users = self._read_data('users')
        for user in users:
            if user['user_id'] == user_id:
                return user.get('is_banned', False)
        return False

    def ban_user(self, user_id):
        users = self._read_data('users')
        for user in users:
            if user['user_id'] == user_id:
                user['is_banned'] = True
                self._write_data('users', users)
                return True
        return False

    def unban_user(self, user_id):
        users = self._read_data('users')
        for user in users:
            if user['user_id'] == user_id:
                user['is_banned'] = False
                self._write_data('users', users)
                return True
        return False

    # ========== Admin Management ========== #

    def is_admin(self, user_id):
        admins = self._read_data('admins')
        for admin in admins:
            if admin['user_id'] == user_id:
                return True
        return False

    def add_admin(self, user_id, username, full_name, added_by):
        admins = self._read_data('admins')
        # التحقق من عدم وجود الأدمن مسبقاً
        for admin in admins:
            if admin['user_id'] == user_id:
                return False
        admins.append({
            'user_id': user_id,
            'username': username,
            'full_name': full_name,
            'date_added': datetime.now().isoformat(),
            'added_by': added_by
        })
        self._write_data('admins', admins)
        return True

    def remove_admin(self, user_id):
        if user_id == DEVELOPER_ID:
            return False
        admins = self._read_data('admins')
        for i, admin in enumerate(admins):
            if admin['user_id'] == user_id:
                del admins[i]
                self._write_data('admins', admins)
                return True
        return False

    def get_admins(self):
        admins = self._read_data('admins')
        return [(admin['user_id'], admin.get('username'), admin.get('full_name')) for admin in admins]

    # ========== Content Management ========== #

    def get_stage_subjects_by_category(self, stage, category):
        subjects = self._read_data('subjects')
        result = []
        for subject in subjects:
            if subject['stage'] == stage and subject['category'] == category:
                result.append((subject['name_ar'], subject['key']))
        # ترتيب حسب الاسم العربي
        result.sort(key=lambda x: x[0])
        return result

    def get_stage_subject(self, stage, subject_key):
        subjects = self._read_data('subjects')
        for subject in subjects:
            if subject['stage'] == stage and subject['key'] == subject_key:
                return (subject['name_ar'], subject['name_en'], subject['key'], subject['category'])
        return None

    # ========== Channel Management ========== #

    def get_required_channel(self):
        channels = self._read_data('required_channels')
        if channels:
            channel = channels[0]
            return (channel['channel_id'], channel['channel_username'], channel['channel_title'])
        return None

    def add_required_channel(self, channel_id, channel_username, channel_title, added_by):
        channels = [{
            'channel_id': channel_id,
            'channel_username': channel_username,
            'channel_title': channel_title,
            'date_added': datetime.now().isoformat(),
            'added_by': added_by
        }]
        self._write_data('required_channels', channels)
        return True

    def remove_required_channel(self):
        self._write_data('required_channels', [])
        return True

    # ========== Search Channels Management ========== #

    def add_search_channel(self, channel_id, channel_username, channel_title, stage, added_by):
        channels = self._read_data('search_channels')
        # التحقق من عدم تكرار القناة في نفس المرحلة
        for channel in channels:
            if channel['channel_id'] == channel_id and channel['stage'] == stage:
                return False
        
        # إنشاء معرف فريد للسجل
        new_id = max([c.get('id', 0) for c in channels], default=0) + 1
        
        channels.append({
            'id': new_id,
            'channel_id': channel_id,
            'channel_username': channel_username,
            'channel_title': channel_title,
            'stage': stage,
            'added_by': added_by,
            'date_added': datetime.now().isoformat()
        })
        self._write_data('search_channels', channels)
        return True

    def get_search_channels(self, stage=None):
        channels = self._read_data('search_channels')
        if stage is None:
            return [(channel['id'], channel['channel_username'], channel['channel_title'], channel['stage']) 
                    for channel in channels]
        else:
            return [(channel['id'], channel['channel_username'], channel['channel_title'], channel['stage'])
                    for channel in channels if channel['stage'] == stage]

    def remove_search_channel(self, record_id, stage=None):
        channels = self._read_data('search_channels')
        for i, channel in enumerate(channels):
            if channel['id'] == record_id:
                if stage is None or channel['stage'] == stage:
                    del channels[i]
                    self._write_data('search_channels', channels)
                    return True
        return False

    def get_search_channel_by_id(self, record_id):
        channels = self._read_data('search_channels')
        for channel in channels:
            if channel['id'] == record_id:
                return channel
        return None

    # ========== Support Tickets ========== #

    def add_support_ticket(self, user_id, message, stage):
        tickets = self._read_data('support_tickets')
        ticket_id = max([t.get('id', 0) for t in tickets], default=0) + 1
        tickets.append({
            'id': ticket_id,
            'user_id': user_id,
            'message': message,
            'stage': stage,
            'date': datetime.now().isoformat()
        })
        self._write_data('support_tickets', tickets)
        return ticket_id

    def get_support_tickets(self):
        tickets = self._read_data('support_tickets')
        result = []
        for ticket in tickets:
            # نحتاج إلى معلومات المستخدم من ملف users
            user = self._get_user_by_id(ticket['user_id'])
            if user:
                result.append((
                    ticket['id'],
                    ticket['message'],
                    ticket['stage'],
                    user.get('first_name', ''),
                    user.get('username', ''),
                    ticket['date']
                ))
        # ترتيب حسب التاريخ (الأحدث أولاً)
        result.sort(key=lambda x: x[5], reverse=True)
        return result

    def get_ticket_info(self, ticket_id):
        tickets = self._read_data('support_tickets')
        for ticket in tickets:
            if ticket['id'] == ticket_id:
                user = self._get_user_by_id(ticket['user_id'])
                if user:
                    return (
                        ticket['user_id'],
                        ticket['message'],
                        ticket['stage'],
                        user.get('first_name', ''),
                        user.get('username', ''),
                        ticket['date']
                    )
        return None

    def delete_support_ticket(self, ticket_id):
        tickets = self._read_data('support_tickets')
        for i, ticket in enumerate(tickets):
            if ticket['id'] == ticket_id:
                del tickets[i]
                self._write_data('support_tickets', tickets)
                return True
        return False

    def _get_user_by_id(self, user_id):
        users = self._read_data('users')
        for user in users:
            if user['user_id'] == user_id:
                return user
        return None

    # ========== Stage Content Management ========== #

    def add_stage_content(self, stage, subject_key, chapter_num, content_type, file_id, file_name=None, text=None, description=None, added_by=None):
        contents = self._read_data('stage_content')
        # الحصول على آخر رقم تسلسلي لهذا الموضوع والفصل
        content_numbers = [c['content_number'] for c in contents 
                          if c['stage'] == stage and c['subject_key'] == subject_key and c['chapter_num'] == chapter_num]
        content_number = max(content_numbers) + 1 if content_numbers else 1
        
        content_id = max([c.get('id', 0) for c in contents], default=0) + 1
        contents.append({
            'id': content_id,
            'stage': stage,
            'subject_key': subject_key,
            'chapter_num': chapter_num,
            'content_type': content_type,
            'file_id': file_id,
            'file_name': file_name,
            'text': text,
            'description': description,
            'added_by': added_by,
            'date_added': datetime.now().isoformat(),
            'content_number': content_number
        })
        self._write_data('stage_content', contents)
        return content_id

    def get_stage_content(self, stage, subject_key, chapter_num):
        contents = self._read_data('stage_content')
        result = []
        for content in contents:
            if (content['stage'] == stage and 
                content['subject_key'] == subject_key and 
                content['chapter_num'] == chapter_num):
                result.append((
                    content['id'],
                    content['content_type'],
                    content['description'],
                    content['date_added'],
                    content['content_number']
                ))
        # ترتيب حسب الرقم التسلسلي
        result.sort(key=lambda x: x[4])
        return result

    def get_stage_content_by_id(self, content_id):
        contents = self._read_data('stage_content')
        for content in contents:
            if content['id'] == content_id:
                return (
                    content['id'],
                    content['stage'],
                    content['subject_key'],
                    content['chapter_num'],
                    content['content_type'],
                    content.get('file_id'),
                    content.get('file_name'),
                    content.get('text'),
                    content.get('description'),
                    content.get('added_by'),
                    content.get('content_number')
                )
        return None

    def update_content_description(self, content_id, description):
        contents = self._read_data('stage_content')
        for content in contents:
            if content['id'] == content_id:
                content['description'] = description
                self._write_data('stage_content', contents)
                return True
        return False

    def delete_stage_content(self, content_id):
        contents = self._read_data('stage_content')
        for i, content in enumerate(contents):
            if content['id'] == content_id:
                del contents[i]
                self._write_data('stage_content', contents)
                return True
        return False

    # ========== Comments Management ========== #
    def get_all_comments(self):
        comments = self._read_data('comments')
        result = []
        for comment in comments:
            user = self._get_user_by_id(comment['user_id'])
            if user:
                result.append((
                    comment['id'],
                    comment['user_id'],
                    comment['text'],
                    comment['date'],
                    user.get('first_name', ''),
                    user.get('username', ''),
                    comment.get('stage', 1)
                ))
        # ترتيب حسب التاريخ (الأحدث أولاً)
        result.sort(key=lambda x: x[3], reverse=True)
        return result

    def can_user_comment(self, user_id, min_interval_seconds=10):
        """منع السبام: السماح بتعليق واحد كل min_interval_seconds"""
        now = time.time()
        last = self._last_comment_ts.get(user_id, 0)
        if now - last < min_interval_seconds:
            return False
        self._last_comment_ts[user_id] = now
        return True

    def add_comment(self, user_id, content_id, text, stage=None):
        """إضافة تعليق مرتبط بمحتوى محدد مع فحص بسيط لمنع السبام."""
        if not self.can_user_comment(user_id):
            return None

        comments = self._read_data('comments')
        comment_id = max([c.get('id', 0) for c in comments], default=0) + 1
        comment = {
            'id': comment_id,
            'user_id': user_id,
            'content_id': content_id,
            'text': text,
            'stage': stage,
            'date': datetime.now().isoformat()
        }
        comments.append(comment)
        self._write_data('comments', comments)

        # Update comments_meta counts
        meta = self._read_data('comments_meta') or {}
        meta_for_content = meta.get(str(content_id), {'count': 0})
        meta_for_content['count'] = meta_for_content.get('count', 0) + 1
        meta[str(content_id)] = meta_for_content
        self._write_data('comments_meta', meta)

        return comment_id

    def get_comments_for_content(self, content_id):
        comments = self._read_data('comments')
        result = []
        for c in comments:
            if c.get('content_id') == content_id:
                user = self._get_user_by_id(c['user_id'])
                result.append((c['id'], c['user_id'], c['text'], c['date'], user.get('first_name', ''), user.get('username', '')))
        result.sort(key=lambda x: x[3], reverse=False)
        return result

    def delete_comment(self, comment_id, requestor_id=None):
        comments = self._read_data('comments')
        for i, c in enumerate(comments):
            if c['id'] == comment_id:
                # allow deletion if requestor is author or admin
                if requestor_id is None or requestor_id == c['user_id'] or self.is_admin(requestor_id):
                    del comments[i]
                    self._write_data('comments', comments)
                    # decrement meta
                    meta = self._read_data('comments_meta') or {}
                    key = str(c.get('content_id'))
                    if key in meta:
                        meta[key]['count'] = max(0, meta[key].get('count', 1) - 1)
                        self._write_data('comments_meta', meta)
                    return True
        return False

    # ========== AI Settings Management ========== #
    def set_ai_enabled(self, enabled):
        """تفعيل أو تعطيل الذكاء الاصطناعي"""
        settings = self._read_data('settings')
        if not isinstance(settings, dict):
            settings = {}
        settings['ai_enabled'] = enabled
        settings['ai_updated'] = datetime.now().isoformat()
        self._write_data('settings', settings)
        return True

    def get_ai_enabled(self):
        """الحصول على حالة الذكاء الاصطناعي"""
        settings = self._read_data('settings')
        if isinstance(settings, dict):
            return settings.get('ai_enabled', False)
        return False

    # ========== Physical Info Settings Management ========== #
    def set_physics_info_channel(self, channel_id, channel_username, channel_title, added_by):
        """تعيين قناة المعلومات الفيزيائية"""
        channels = [{
            'channel_id': channel_id,
            'channel_username': channel_username,
            'channel_title': channel_title,
            'added_by': added_by,
            'date_added': datetime.now().isoformat()
        }]
        self._write_data('physics_channel', channels)
        return True

    def get_physics_info_channel(self):
        """الحصول على قناة المعلومات الفيزيائية"""
        channels = self._read_data('physics_channel')
        if channels and len(channels) > 0:
            channel = channels[0]
            return (channel['channel_id'], channel['channel_username'], channel['channel_title'])
        return None

    def remove_physics_info_channel(self):
        """إزالة قناة المعلومات الفيزيائية"""
        self._write_data('physics_channel', [])
        return True

    def add_user_physics_info_request(self, user_id, timestamp=None):
        """تسجيل طلب معلومة فيزيائية من المستخدم"""
        requests = self._read_data('physics_requests')
        if not isinstance(requests, list):
            requests = []
        
        requests.append({
            'user_id': user_id,
            'timestamp': timestamp or datetime.now().isoformat(),
            'delivered': False
        })
        self._write_data('physics_requests', requests)
        return True

    def get_users_eligible_for_physics_info(self, hours_since=24):
        """الحصول على المستخدمين المؤهلين لتلقي معلومة فيزيائية كل 24 ساعة"""
        users_stages = self._read_data('users_stages')
        requests = self._read_data('physics_requests')
        if not isinstance(requests, list):
            requests = []
        
        now = datetime.now()
        eligible_users = []
        
        for user_stage in users_stages:
            user_id = user_stage['user_id']
            
            # البحث عن آخر طلب للمستخدم
            last_request = None
            for req in sorted(requests, key=lambda x: x['timestamp'], reverse=True):
                if req['user_id'] == user_id:
                    last_request = req
                    break
            
            # إذا لم يكن هناك طلب سابق أو مرت 24 ساعة
            if last_request is None:
                eligible_users.append(user_id)
            else:
                last_time = datetime.fromisoformat(last_request['timestamp'])
                if (now - last_time).total_seconds() >= hours_since * 3600:
                    eligible_users.append(user_id)
        
        return eligible_users

    # ==================== دوال الإحصائيات الجديدة ====================
    def count_users_by_stage(self, stage=None):
        """عدد المستخدمين حسب المرحلة"""
        users_stages = self._read_data('users_stages')
        if stage:
            return len([u for u in users_stages if u['stage'] == stage])
        else:
            return len(users_stages)

    def get_users_by_stage(self, stage=None):
        """الحصول على قائمة المستخدمين حسب المرحلة"""
        users_stages = self._read_data('users_stages')
        users = self._read_data('users')
        
        # إنشاء قاموس للمستخدمين للوصول السريع
        users_dict = {u['user_id']: u for u in users}
        
        result = []
        for user_stage in users_stages:
            if stage is None or user_stage['stage'] == stage:
                user_id = user_stage['user_id']
                user_info = users_dict.get(user_id, {})
                result.append({
                    'user_id': user_id,
                    'full_name': user_stage.get('full_name', ''),
                    'stage': user_stage['stage'],
                    'username': user_info.get('username', ''),
                    'first_name': user_info.get('first_name', ''),
                    'last_name': user_info.get('last_name', ''),
                    'date_joined': user_info.get('date_joined', ''),
                    'last_active': user_info.get('last_active', ''),
                    'is_banned': user_info.get('is_banned', False)
                })
        
        # ترتيب حسب تاريخ الانضمام (الأحدث أولاً)
        result.sort(key=lambda x: x.get('date_joined', ''), reverse=True)
        return result

    def get_stage_statistics(self):
        """إحصائيات كاملة عن المراحل"""
        users_stages = self._read_data('users_stages')
        users = self._read_data('users')
        
        # إحصائيات المراحل
        stages_count = {1: 0, 2: 0, 3: 0, 4: 0}
        for user_stage in users_stages:
            stage = user_stage['stage']
            if stage in stages_count:
                stages_count[stage] += 1
        
        # إجمالي المستخدمين (غير المحظورين)
        total_users = len([u for u in users if not u.get('is_banned', False)])
        
        # المستخدمين الجدد اليوم
        today = date.today().isoformat()
        new_users_today = len([u for u in users 
                              if u.get('date_joined', '').startswith(today) 
                              and not u.get('is_banned', False)])
        
        # المستخدمين النشطين اليوم
        active_today = len([u for u in users 
                           if u.get('last_active', '').startswith(today)
                           and not u.get('is_banned', False)])
        
        return {
            'total_users': total_users,
            'new_users_today': new_users_today,
            'active_today': active_today,
            'stage_1': stages_count[1],
            'stage_2': stages_count[2],
            'stage_3': stages_count[3],
            'stage_4': stages_count[4],
            'total_registered': sum(stages_count.values())
        }

# إنشاء كائن قاعدة البيانات
db = Database()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mostafa - Vodafone Charge App
Works directly on Vodafone data
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty
import requests
import json
import threading

# ==================== CONFIG ====================
SUPABASE_URL = 'https://qippgvyupkeruvzkfdkz.supabase.co'
SUPABASE_KEY = 'sb_publishable_zUyj8k4QKYqognMAL6I1Qw_8cBGPFyf'
VODAFONE_CLIENT_SECRET = 'b86e30a8-ae29-467a-a71f-65c73f2ff5e3'
VODAFONE_CLIENT_ID = 'cash-app'
ADMIN_PHONE = '01019502983'

# ==================== PRODUCTS ====================
FAKKA_PRODUCTS = [
    {"id": "Fakka_2.5_Unite", "name": "فكة 2.5 جنيه", "price": 2.5, "units": 45, "validity": "24 ساعة"},
    {"id": "Fakka_4.25_Unite", "name": "فكة 4.25 جنيه", "price": 4.25, "units": 190, "validity": "24 ساعة"},
    {"id": "Fakka_5_Unite", "name": "فكة 5 جنيه", "price": 5, "units": 225, "validity": "24 ساعة"},
    {"id": "Fakka_7_Unite", "name": "فكة 7 جنيه", "price": 7, "units": 300, "validity": "3 أيام"},
    {"id": "Fakka_10_Unite", "name": "فكة 10 جنيه", "price": 10, "units": 450, "validity": "7 أيام"},
    {"id": "Fakka_15_Unite", "name": "فكة 15 جنيه", "price": 15, "units": 550, "validity": "7 أيام"},
    {"id": "Fakka_20_Unite", "name": "فكة 20 جنيه", "price": 20, "units": 0, "validity": "10 أيام"},
    {"id": "Fakka_26_Unite", "name": "فكة 26 جنيه", "price": 26, "units": 0, "validity": "شهر"},
]

MARED_PRODUCTS = [
    {"id": "Mared_10_Minuts", "name": "مارد 10 دقائق", "price": 10, "units": 10, "type": "دقائق", "validity": "24 ساعة"},
    {"id": "Mared_10_Flexs", "name": "مارد 10 فليكس", "price": 10, "units": 10, "type": "فليكس", "validity": "24 ساعة"},
    {"id": "Mared_10_Social", "name": "مارد 10 سوشيال", "price": 10, "units": 10, "type": "سوشيال", "validity": "24 ساعة"},
]

ALL_PRODUCTS = FAKKA_PRODUCTS + MARED_PRODUCTS

POINTS_PACKAGES = [
    {"points": 10, "price": 20, "label": "10 نقاط - 20 جنيه"},
    {"points": 25, "price": 50, "label": "25 نقطة - 50 جنيه"},
    {"points": 50, "price": 100, "label": "50 نقطة - 100 جنيه"},
    {"points": 100, "price": 200, "label": "100 نقطة - 200 جنيه"},
]

# ==================== APP ====================
class VodafoneApp(App):
    user_phone = StringProperty('')
    points = NumericProperty(0)

    def build(self):
        Window.clearcolor = (0.03, 0, 0, 1)
        self.title = 'Mostafa - شحن كروت فودافون'

        self.main_layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        self.show_login()
        return self.main_layout

    def show_login(self):
        self.main_layout.clear_widgets()

        # Title
        title = Label(
            text='[b][color=E60000]Mostafa[/color][/b]\nشحن كروت فودافون',
            markup=True,
            font_size='22sp',
            size_hint_y=None,
            height=100
        )
        self.main_layout.add_widget(title)

        # Spacer
        self.main_layout.add_widget(Label(size_hint_y=0.3))

        # Phone input
        self.phone_input = TextInput(
            hint_text='رقم الهاتف (01XXXXXXXXX)',
            multiline=False,
            input_filter='int',
            size_hint_y=None,
            height=55,
            background_color=(0.1, 0.1, 0.1, 1),
            foreground_color=(1, 1, 1, 1),
            hint_text_color=(0.5, 0.5, 0.5, 1),
            padding=(15, 10),
            font_size='16sp'
        )
        self.main_layout.add_widget(self.phone_input)

        # Login button
        login_btn = Button(
            text='دخول',
            size_hint_y=None,
            height=55,
            background_color=(0.9, 0, 0, 1),
            color=(1, 1, 1, 1),
            font_size='16sp',
            bold=True
        )
        login_btn.bind(on_press=self.do_login)
        self.main_layout.add_widget(login_btn)

        # Spacer
        self.main_layout.add_widget(Label(size_hint_y=0.5))

    def do_login(self, instance):
        phone = self.phone_input.text
        if len(phone) != 11 or not phone.startswith('01'):
            self.show_popup('خطأ', 'رقم الهاتف غير صحيح\nيجب أن يكون 11 رقم ويبدأ بـ 01')
            return

        self.user_phone = phone
        self.load_user_data()
        self.show_home()

    def load_user_data(self):
        try:
            headers = {
                'apikey': SUPABASE_KEY,
                'Authorization': f'Bearer {SUPABASE_KEY}'
            }
            response = requests.get(
                f'{SUPABASE_URL}/rest/v1/users?phone=eq.{self.user_phone}&select=*',
                headers=headers,
                timeout=10
            )
            data = response.json()
            if data:
                self.points = data[0].get('points', 0)
            else:
                requests.post(
                    f'{SUPABASE_URL}/rest/v1/users',
                    headers={**headers, 'Content-Type': 'application/json'},
                    json={'phone': self.user_phone, 'points': 0},
                    timeout=10
                )
                self.points = 0
        except Exception as e:
            print(f'Error loading user: {e}')
            self.points = 0

    def show_home(self):
        self.main_layout.clear_widgets()

        # Header
        header = BoxLayout(size_hint_y=None, height=70, spacing=10)

        points_btn = Button(
            text=f'⭐ {self.points} نقطة',
            size_hint_x=0.5,
            background_color=(0.97, 0.79, 0.28, 0.2),
            color=(0.97, 0.79, 0.28, 1),
            font_size='14sp',
            bold=True
        )
        points_btn.bind(on_press=self.show_points_dialog)
        header.add_widget(points_btn)

        recharge_btn = Button(
            text='شحن نقاط',
            size_hint_x=0.5,
            background_color=(0.97, 0.79, 0.28, 0.3),
            color=(0.97, 0.79, 0.28, 1),
            font_size='14sp',
            bold=True
        )
        recharge_btn.bind(on_press=self.show_recharge_dialog)
        header.add_widget(recharge_btn)

        self.main_layout.add_widget(header)

        # Category buttons
        cat_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)

        all_btn = Button(
            text='الكل',
            background_color=(0.9, 0, 0, 0.3),
            color=(1, 1, 1, 1),
            font_size='12sp'
        )
        all_btn.bind(on_press=lambda x: self.show_products('all'))
        cat_layout.add_widget(all_btn)

        fakka_btn = Button(
            text='⚡ فكة',
            background_color=(0.9, 0, 0, 0.3),
            color=(1, 1, 1, 1),
            font_size='12sp'
        )
        fakka_btn.bind(on_press=lambda x: self.show_products('fakka'))
        cat_layout.add_widget(fakka_btn)

        mared_btn = Button(
            text='🔥 مارد',
            background_color=(0.9, 0, 0, 0.3),
            color=(1, 1, 1, 1),
            font_size='12sp'
        )
        mared_btn.bind(on_press=lambda x: self.show_products('mared'))
        cat_layout.add_widget(mared_btn)

        self.main_layout.add_widget(cat_layout)

        # Products area
        self.products_layout = BoxLayout(orientation='vertical')
        self.main_layout.add_widget(self.products_layout)

        self.show_products('all')

    def show_products(self, category):
        self.products_layout.clear_widgets()

        if category == 'all':
            products = ALL_PRODUCTS
        elif category == 'fakka':
            products = FAKKA_PRODUCTS
        else:
            products = MARED_PRODUCTS

        scroll = ScrollView()
        grid = GridLayout(cols=2, spacing=10, padding=10, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        for product in products:
            btn = Button(
                text=f'[b]{product["name"]}[/b]\n{product["price"]} جنيه\n{product.get("units", 0)} {product.get("type", "وحدة")}',
                markup=True,
                size_hint_y=None,
                height=120,
                background_color=(0.9, 0, 0, 0.2),
                color=(1, 1, 1, 1),
                font_size='12sp'
            )
            btn.bind(on_press=lambda x, p=product: self.show_charge_dialog(p))
            grid.add_widget(btn)

        scroll.add_widget(grid)
        self.products_layout.add_widget(scroll)

    def show_charge_dialog(self, product):
        content = BoxLayout(orientation='vertical', spacing=15, padding=20)

        # Info
        info = Label(
            text=f'[b]{product["name"]}[/b]\nالسعر: {product["price"]} جنيه\nسيتم خصم نقطة واحدة',
            markup=True,
            font_size='14sp',
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=80
        )
        content.add_widget(info)

        # Target phone
        target_input = TextInput(
            hint_text='رقم الهاتف للشحن',
            multiline=False,
            input_filter='int',
            size_hint_y=None,
            height=50,
            background_color=(0.1, 0.1, 0.1, 1),
            foreground_color=(1, 1, 1, 1),
            hint_text_color=(0.5, 0.5, 0.5, 1),
            padding=(15, 10),
            font_size='14sp'
        )
        content.add_widget(target_input)

        # PIN
        pin_input = TextInput(
            hint_text='الرقم السري للمحفظة',
            multiline=False,
            password=True,
            size_hint_y=None,
            height=50,
            background_color=(0.1, 0.1, 0.1, 1),
            foreground_color=(1, 1, 1, 1),
            hint_text_color=(0.5, 0.5, 0.5, 1),
            padding=(15, 10),
            font_size='14sp'
        )
        content.add_widget(pin_input)

        # Buttons
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)

        cancel_btn = Button(
            text='إلغاء',
            background_color=(0.5, 0.5, 0.5, 1),
            color=(1, 1, 1, 1)
        )

        charge_btn = Button(
            text='تأكيد الشحن',
            background_color=(0.9, 0, 0, 1),
            color=(1, 1, 1, 1),
            bold=True
        )

        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(charge_btn)
        content.add_widget(btn_layout)

        popup = Popup(
            title=f'شحن {product["name"]}',
            content=content,
            size_hint=(0.9, 0.7),
            auto_dismiss=False
        )

        cancel_btn.bind(on_press=popup.dismiss)

        def do_charge(instance):
            if self.points <= 0:
                self.show_popup('خطأ', 'لا توجد نقاط كافية\nاشحن نقاط أولاً')
                return

            target = target_input.text
            pin = pin_input.text

            if len(target) != 11 or not target.startswith('01'):
                self.show_popup('خطأ', 'رقم الهاتف غير صحيح')
                return

            if len(pin) < 4:
                self.show_popup('خطأ', 'الرقم السري قصير جداً')
                return

            popup.dismiss()
            self.charge_card(target, pin, product)

        charge_btn.bind(on_press=do_charge)
        popup.open()

    def charge_card(self, msisdn, pin, product):
        # Loading popup
        loading_content = BoxLayout(orientation='vertical', padding=20, spacing=10)
        loading_content.add_widget(Label(text='جاري الشحن...', font_size='16sp'))
        progress = ProgressBar(max=100, value=50)
        loading_content.add_widget(progress)

        loading_popup = Popup(
            title='الرجاء الانتظار',
            content=loading_content,
            size_hint=(0.8, 0.3),
            auto_dismiss=False
        )
        loading_popup.open()

        def charge_thread():
            try:
                # Deduct point
                self.points -= 1
                self.update_points()

                # Call API
                result = self.call_vodafone_api(msisdn, pin, product['id'])

                Clock.schedule_once(lambda dt: loading_popup.dismiss(), 0)

                if result['success']:
                    Clock.schedule_once(lambda dt: self.show_popup('نجاح', result['message']), 0)
                    self.save_operation(product, msisdn, 'success')
                else:
                    # Refund point
                    self.points += 1
                    self.update_points()
                    Clock.schedule_once(lambda dt: self.show_popup('فشل', result['message']), 0)
                    self.save_operation(product, msisdn, 'failed')

                Clock.schedule_once(lambda dt: self.show_home(), 0)

            except Exception as e:
                Clock.schedule_once(lambda dt: loading_popup.dismiss(), 0)
                self.points += 1
                self.update_points()
                Clock.schedule_once(lambda dt: self.show_popup('خطأ', str(e)), 0)

        threading.Thread(target=charge_thread).start()

    def call_vodafone_api(self, msisdn, pin, product_id):
        session = requests.Session()

        headers_base = {
            'User-Agent': 'okhttp/4.12.0',
            'Accept-Encoding': 'gzip',
            'Connection': 'Keep-Alive',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ar',
            'x-agent-operatingsystem': '13',
            'x-agent-device': 'Android Device',
            'x-agent-version': '2026.4.1',
            'x-agent-build': '1139',
        }

        # Step 1 - HTTPS for mobile data
        resp1 = session.get(
            'https://mobile.vodafone.com.eg/checkSeamless/realms/vf-realm/protocol/openid-connect/auth',
            params={'client_id': 'ana-vodafone-app-seamless'},
            headers=headers_base,
            timeout=30
        )

        if resp1.status_code != 200:
            return {'success': False, 'message': 'فشل الاتصال الأولي بفودافون'}

        seamless_token = resp1.json().get('seamlessToken')

        # Step 2
        headers_token = headers_base.copy()
        headers_token.update({
            'seamlessToken': seamless_token,
            'clientId': 'AnaVodafoneAndroid',
            'silentLogin': 'true',
            'firstTimeLogin': 'true',
            'Content-Type': 'application/x-www-form-urlencoded'
        })

        token_data = {
            'grant_type': 'password',
            'client_secret': VODAFONE_CLIENT_SECRET,
            'client_id': VODAFONE_CLIENT_ID
        }

        resp2 = session.post(
            'https://mobile.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/token',
            data=token_data,
            headers=headers_token,
            timeout=30
        )

        if resp2.status_code != 200:
            return {'success': False, 'message': 'فشل تسجيل الدخول\nتأكد من فتح داتا فودافون'}

        access_token = resp2.json().get('access_token')

        # Step 3
        headers_order = headers_token.copy()
        headers_order.update({
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}',
            'api-host': 'ProductOrderingManagement',
            'useCase': 'CashFakkaAndMared',
            'api-version': 'v2',
            'msisdn': msisdn
        })

        order_body = {
            "channel": {"name": "MobileApp"},
            "orderItem": [{
                "action": "insert",
                "id": product_id,
                "product": {
                    "characteristic": [
                        {"name": "PaymentMethod", "value": "VFCash"},
                        {"name": "USE_EMONEY", "value": "False"},
                        {"name": "MerchantCode", "value": ""}
                    ],
                    "id": product_id,
                    "relatedParty": [
                        {"id": msisdn.replace("0", "", 1), "name": "MSISDN", "role": "Subscriber"},
                        {"id": msisdn, "name": "Receiver", "role": "Receiver"}
                    ]
                },
                "@type": product_id,
                "eCode": 0
            }],
            "relatedParty": [{"id": pin, "name": "pin", "role": "Requestor"}],
            "@type": "CashFakkaAndMared"
        }

        resp3 = session.post(
            'https://mobile.vodafone.com.eg/services/dxl/pom/productOrder',
            json=order_body,
            headers=headers_order,
            timeout=30
        )

        result = resp3.json()

        if resp3.status_code == 200:
            return {'success': True, 'message': 'تم الشحن بنجاح!'}
        elif result.get('code') == '6051':
            balance = next((item['value'] for item in result.get('characteristic', []) if item['name'] == 'RemainingBalance'), 'غير معروف')
            return {'success': False, 'message': f'لا يوجد رصيد كافي\nرصيدك: {balance} جنيه'}
        else:
            return {'success': False, 'message': result.get('reason', 'خطأ غير معروف')}

    def update_points(self):
        try:
            headers = {
                'apikey': SUPABASE_KEY,
                'Authorization': f'Bearer {SUPABASE_KEY}',
                'Content-Type': 'application/json'
            }
            requests.patch(
                f'{SUPABASE_URL}/rest/v1/users?phone=eq.{self.user_phone}',
                headers=headers,
                json={'points': self.points},
                timeout=10
            )
        except:
            pass

    def save_operation(self, product, phone, status):
        try:
            headers = {
                'apikey': SUPABASE_KEY,
                'Authorization': f'Bearer {SUPABASE_KEY}',
                'Content-Type': 'application/json'
            }
            requests.post(
                f'{SUPABASE_URL}/rest/v1/operations',
                headers=headers,
                json={
                    'user_phone': self.user_phone,
                    'product': product['name'],
                    'product_id': product['id'],
                    'price': product['price'],
                    'target_phone': phone,
                    'status': status
                },
                timeout=10
            )
        except:
            pass

    def show_points_dialog(self, instance=None):
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
        content.add_widget(Label(
            text=f'[b][color=F7C948]⭐ {self.points} نقطة[/color][/b]',
            markup=True,
            font_size='24sp'
        ))
        content.add_widget(Label(
            text='كل شحنة تخصم نقطة واحدة',
            font_size='12sp',
            color=(0.7, 0.7, 0.7, 1)
        ))

        close_btn = Button(
            text='إغلاق',
            size_hint_y=None,
            height=50,
            background_color=(0.5, 0.5, 0.5, 1)
        )

        popup = Popup(title='رصيد النقاط', content=content, size_hint=(0.8, 0.4))
        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)
        popup.open()

    def show_recharge_dialog(self, instance=None):
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)

        content.add_widget(Label(
            text='اختر الباقة:',
            font_size='14sp',
            color=(1, 1, 1, 1)
        ))

        for pkg in POINTS_PACKAGES:
            btn = Button(
                text=pkg['label'],
                size_hint_y=None,
                height=50,
                background_color=(0.97, 0.79, 0.28, 0.2),
                color=(0.97, 0.79, 0.28, 1)
            )
            btn.bind(on_press=lambda x, p=pkg: self.send_recharge_request(p))
            content.add_widget(btn)

        close_btn = Button(
            text='إلغاء',
            size_hint_y=None,
            height=50,
            background_color=(0.5, 0.5, 0.5, 1)
        )

        popup = Popup(title='شحن نقاط', content=content, size_hint=(0.9, 0.7))
        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)
        popup.open()

    def send_recharge_request(self, package):
        msg = (
            f"🔔 طلب شحن نقاط جديد!\n"
            f"👤 العميل: {self.user_phone}\n"
            f"⭐ النقاط: {package['points']}\n"
            f"💰 المبلغ: {package['price']} جنيه"
        )

        import webbrowser
        webbrowser.open(f'https://wa.me/2{ADMIN_PHONE}?text={msg}')

        self.show_popup('تم', 'تم فتح واتساب\nأرسل لقطة الشحن')

    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', padding=20, spacing=10)
        content.add_widget(Label(text=message, font_size='14sp'))

        btn = Button(text='حسناً', size_hint_y=None, height=50)
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.open()

if __name__ == '__main__':
    VodafoneApp().run()

import os
import shutil
from kivymd.app import MDApp
from kivymd.uix.navigationdrawer import MDNavigationLayout, MDNavigationDrawer
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.button import MDIconButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import MDList, OneLineListItem
from kivymd.uix.label import MDLabel
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.uix.modalview import ModalView
from kivy.uix.carousel import Carousel
from kivy.uix.behaviors import ButtonBehavior
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.utils import platform

# Clickable Image for Long Press and Zoom
class ClickableImage(ButtonBehavior, Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.long_press_time = 1.0
        self.path = ""

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._clockev = Clock.schedule_once(lambda dt: self.on_long_press(), self.long_press_time)
            return super().on_touch_down(touch)
        return False

    def on_touch_up(self, touch):
        if hasattr(self, '_clockev'):
            Clock.unschedule(self._clockev)
        return super().on_touch_up(touch)

    def on_long_press(self):
        app = MDApp.get_running_app()
        app.show_delete_dialog(self.path)

class Prish_Valut(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.all_images = []
        self.file_manager = None

    def build(self):
        self.theme_cls.primary_palette = "Indigo"
        self.theme_cls.theme_style = "Light"
        
        # Storage Path Logic
        if platform == 'android':
            from android.storage import app_storage_path
            self.storage_path = os.path.join(app_storage_path(), "PrishVault_Data")
        else:
            self.storage_path = os.path.join(self.user_data_dir, "PrishVault_Data")
            
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)

        self.nav_layout = MDNavigationLayout()
        self.screen_manager = MDScreenManager()

        # --- Home Screen ---
        home_screen = MDScreen(name='home')
        home_layout = MDBoxLayout(orientation='vertical')
        self.toolbar = MDTopAppBar(
            title="Prish_Vault",
            elevation=4,
            left_action_items=[['menu', lambda x: self.nav_drawer.set_state("open")]],
            right_action_items=[["plus", lambda x: self.open_file_manager()]]
        )
        self.scroll = ScrollView()
        self.grid = MDGridLayout(cols=3, adaptive_height=True, padding=dp(4), spacing=dp(4))
        self.scroll.add_widget(self.grid)
        home_layout.add_widget(self.toolbar)
        home_layout.add_widget(self.scroll)
        home_screen.add_widget(home_layout)

        # --- Developer Info Screen ---
        dev_screen = MDScreen(name='dev_info')
        dev_main_layout = MDBoxLayout(orientation='vertical')
        dev_main_layout.add_widget(MDTopAppBar(title="Developer Info", left_action_items=[["arrow-left", self.go_home]]))
        dev_scroll = ScrollView()
        dev_content = MDBoxLayout(orientation='vertical', adaptive_height=True, padding=dp(20), spacing=dp(20))
        dev_content.add_widget(MDLabel(
            text="Hey friends, this app is made for a school project.\n\nI'm a student and I made this app to spend my study time productively. My friend helped me design the logo. Although some of my coding concepts are still clearing up, I'm proud of this vault.", 
            halign="center", font_style="Body1", theme_text_color="Custom", text_color=(0,0,1,1), size_hint_y=None, height=dp(300)))
        dev_content.add_widget(MDLabel(text="Thank you\nBy Prish_Developer", halign="right", font_style="H6", theme_text_color="Custom", text_color=(1,0,0,1), size_hint_y=None, height=dp(100)))
        dev_scroll.add_widget(dev_content)
        dev_main_layout.add_widget(dev_scroll)
        dev_screen.add_widget(dev_main_layout)

        # --- About Screen ---
        about_screen = MDScreen(name='about')
        about_main_layout = MDBoxLayout(orientation='vertical')
        about_main_layout.add_widget(MDTopAppBar(title="About Prish_Vault", left_action_items=[["arrow-left", self.go_home]]))
        about_scroll = ScrollView()
        about_content = MDBoxLayout(orientation='vertical', adaptive_height=True, padding=dp(15), spacing=dp(15))
        about_text = (
            "Prish_Vault is a secure personal media companion.\n\n"
            "[b]Key Features:[/b]\n"
            "* Persistent Storage: Creates a permanent copy.\n"
            "* Gallery Independence: Delete from gallery, keep here.\n\n"
            "[b]Warning:[/b] Deleting the app will delete stored photos. Take backups!"
        )
        lbl = MDLabel(text=about_text, markup=True, halign="left", size_hint_y=None)
        lbl.bind(texture_size=lbl.setter('size'))
        about_content.add_widget(lbl)
        about_scroll.add_widget(about_content)
        about_main_layout.add_widget(about_scroll)
        about_screen.add_widget(about_main_layout)

        self.screen_manager.add_widget(home_screen)
        self.screen_manager.add_widget(dev_screen)
        self.screen_manager.add_widget(about_screen)

        # Navigation Drawer
        self.nav_drawer = MDNavigationDrawer()
        drawer_content = MDBoxLayout(orientation="vertical", padding=dp(8), spacing=dp(8))
        menu_list = MDList()
        menu_list.add_widget(OneLineListItem(text="Home", on_press=self.go_home))
        menu_list.add_widget(OneLineListItem(text="Developer Info", on_press=self.go_settings))
        menu_list.add_widget(OneLineListItem(text="About", on_press=self.go_about))
        drawer_content.add_widget(menu_list)
        self.nav_drawer.add_widget(drawer_content)

        self.nav_layout.add_widget(self.screen_manager)
        self.nav_layout.add_widget(self.nav_drawer)

        self.load_gallery()
        return self.nav_layout

    def on_start(self):
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])

    def on_pause(self):
        return True

    def go_home(self, *args):
        self.screen_manager.current = "home"
        self.nav_drawer.set_state("close")

    def go_settings(self, *args):
        self.screen_manager.current = "dev_info"
        self.nav_drawer.set_state("close")

    def go_about(self, *args):
        self.screen_manager.current = "about"
        self.nav_drawer.set_state("close")

    def open_file_manager(self):
        if not self.file_manager:
            self.file_manager = MDFileManager(exit_manager=self.close_manager, select_path=self.save_photo)
        
        if platform == 'android':
            from android.storage import primary_external_storage_path
            path = primary_external_storage_path()
        else:
            path = os.path.expanduser("~")
        self.file_manager.show(path) 

    def close_manager(self, *args):
        if self.file_manager:
            self.file_manager.close()

    def save_photo(self, path):
        try:
            if os.path.isfile(path):
                filename = os.path.basename(path)
                destination = os.path.join(self.storage_path, filename)
                shutil.copy(path, destination)
                self.close_manager()
                Clock.schedule_once(lambda dt: self.load_gallery())
        except Exception as e:
            print(f"Error: {e}")

    def load_gallery(self):
        self.grid.clear_widgets()
        self.all_images = []
        if not os.path.exists(self.storage_path): return
        
        files = [f for f in os.listdir(self.storage_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
        for index, file in enumerate(files):
            full_path = os.path.join(self.storage_path, file)
            self.all_images.append(full_path)
            img = ClickableImage(source=full_path, size_hint=(None, None), size=(dp(100), dp(100)), allow_stretch=True)
            img.path = full_path
            img.bind(on_release=lambda x, idx=index: self.show_zoom_photo(idx))
            self.grid.add_widget(img)

    def show_delete_dialog(self, path):
        self.dialog = MDDialog(
            title="Delete Photo?",
            text="Do you want to permanently delete this photo from the vault?",
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda x: self.dialog.dismiss()),
                MDFlatButton(text="DELETE", theme_text_color="Custom", text_color=(1,0,0,1), on_release=lambda x: self.delete_photo(path)),
            ],
        )
        self.dialog.open()

    def delete_photo(self, path):
        if os.path.exists(path):
            os.remove(path)
        if self.dialog: self.dialog.dismiss()
        self.load_gallery()

    def show_zoom_photo(self, index):
        view = ModalView(size_hint=(1, 1), background_color=(0,0,0,1))
        carousel = Carousel(index=index)
        for path in self.all_images:
            carousel.add_widget(Image(source=path))
        close_btn = MDIconButton(icon="close", pos_hint={"top": 1, "right": 1}, theme_text_color="Custom", text_color=(1,1,1,1), on_release=view.dismiss)
        view.add_widget(carousel)
        view.add_widget(close_btn)
        view.open()

if __name__ == "__main__":
    Prish_Valut().run()

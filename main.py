import random
from itertools import combinations
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Rectangle
from kivy.core.window import Window

class DartsSorsolo(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.padding = 20
        self.spacing = 10
        self.jatekosok = [] # Üres lista, kézzel kell beírni
        self.mod = "csoport"
        self.csoportok_szama = 2
        self.tovabbjutok_szama = 2
        self.meccsek_eredmenyei = {} # (jatekos1, jatekos2): (p1_leg, p2_leg)
        self.aktualis_versenyzok = []
        self.parok = []
        self.meccs_gombok = {}

        with self.canvas.before:
            self.bg = Rectangle(source='hatter.jpg', pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)

        self.main_content = BoxLayout(orientation='vertical', spacing=10)
        self.add_widget(self.main_content)
        self.setup_settings_view()

    def update_bg(self, *args):
        self.bg.pos, self.bg.size = self.pos, self.size

    def setup_settings_view(self, *args):
        self.main_content.clear_widgets()
        self.meccsek_eredmenyei = {} # Új verseny, töröljük az előző eredményeket
        
        mod_sor = BoxLayout(size_hint_y=None, height=50, spacing=5)
        for t, m in [("Csoportkör", "csoport"), ("Egyenes kiesés", "kieseses")]:
            btn = Button(text=t, background_color=(0.2, 0.5, 1, 1) if self.mod == m else (0.5, 0.5, 0.5, 1))
            btn.bind(on_press=lambda x, mode=m: self.valts_mod(mode))
            mod_sor.add_widget(btn)
        self.main_content.add_widget(mod_sor)

        bev_sor = BoxLayout(size_hint_y=None, height=50, spacing=10)
        self.nev_input = TextInput(hint_text='Név...', multiline=False, font_size='20sp')
        bev_sor.add_widget(self.nev_input)
        bev_sor.add_widget(Button(text='+', size_hint_x=0.2, on_press=self.jatekos_hozzaadas))
        self.main_content.add_widget(bev_sor)

        self.lista_container = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.lista_container.bind(minimum_height=self.lista_container.setter('height'))
        scroll = ScrollView(size_hint=(1, 0.6))
        scroll.add_widget(self.lista_container)
        self.main_content.add_widget(scroll)
        self.lista_frissites()

        if self.mod == "csoport":
            beall = GridLayout(cols=2, size_hint_y=None, height=100)
            beall.add_widget(Label(text=f"Csoportok: {self.csoportok_szama}"))
            c_g = BoxLayout(); c_g.add_widget(Button(text="-", on_press=lambda x: self.allit_csop(-1))); c_g.add_widget(Button(text="+", on_press=lambda x: self.allit_csop(1)))
            beall.add_widget(c_g)
            beall.add_widget(Label(text=f"Továbbjutók: {self.tovabbjutok_szama}"))
            t_g = BoxLayout(); t_g.add_widget(Button(text="-", on_press=lambda x: self.allit_tov(-1))); t_g.add_widget(Button(text="+", on_press=lambda x: self.allit_tov(1)))
            beall.add_widget(t_g)
            self.main_content.add_widget(beall)

        self.main_content.add_widget(Button(text='INDÍTÁS', size_hint_y=None, height=60, background_color=(0, 0.7, 0, 1), on_press=self.inditas))

    def valts_mod(self, m): self.mod = m; self.setup_settings_view()
    def allit_csop(self, e): self.csoportok_szama = max(1, self.csoportok_szama + e); self.setup_settings_view()
    def allit_tov(self, e): self.tovabbjutok_szama = max(1, self.tovabbjutok_szama + e); self.setup_settings_view()
    def jatekos_hozzaadas(self, *args): 
        if self.nev_input.text: self.jatekosok.append(self.nev_input.text.strip()); self.lista_frissites(); self.nev_input.text = ""
    def jatekos_torles(self, n): self.jatekosok.remove(n); self.lista_frissites()
    def lista_frissites(self):
        self.lista_container.clear_widgets()
        for n in self.jatekosok:
            s = BoxLayout(size_hint_y=None, height=35); s.add_widget(Label(text=n))
            b = Button(text='X', size_hint_x=None, width=40, background_color=(0.8, 0, 0, 1))
            b.bind(on_release=lambda x, name=n: self.jatekos_torles(name)); s.add_widget(b); self.lista_container.add_widget(s)

    def inditas(self, *args):
        if len(self.jatekosok) < 2: return
        self.aktualis_versenyzok = self.jatekosok[:]
        random.shuffle(self.aktualis_versenyzok)
        if self.mod == "kieseses":
            self.kieseses_fordulo_generalas()
        else:
            self.csoportkor_meccsek_nezet()

    def csoportkor_meccsek_nezet(self):
        self.main_content.clear_widgets()
        scroll = ScrollView(); grid = GridLayout(cols=1, spacing=10, size_hint_y=None); grid.bind(minimum_height=grid.setter('height'))
        
        csoportok = [[] for _ in range(self.csoportok_szama)]
        for i, n in enumerate(self.aktualis_versenyzok): csoportok[i % self.csoportok_szama].append(n)
        
        for i, c in enumerate(csoportok):
            grid.add_widget(Label(text=f"{chr(65+i)} CSOPORT", font_size='22sp', color=(1,0.8,0,1), size_hint_y=None, height=40))
            meccsek = list(combinations(c, 2))
            for m1, m2 in meccsek:
                meccs_sor = BoxLayout(size_hint_y=None, height=50, spacing=5)
                meccs_sor.add_widget(Label(text=f"{m1}", halign='right'))
                p1_input = TextInput(text='0', multiline=False, input_filter='int', size_hint_x=0.2)
                p2_input = TextInput(text='0', multiline=False, input_filter='int', size_hint_x=0.2)
                meccs_sor.add_widget(p1_input)
                meccs_sor.add_widget(Label(text=":", size_hint_x=0.1))
                meccs_sor.add_widget(p2_input)
                meccs_sor.add_widget(Label(text=f"{m2}", halign='left'))
                
                # Eredmény rögzítése gomb
                rogzit_btn = Button(text='✓', size_hint_x=0.2, background_color=(0, 0.6, 0, 1))
                rogzit_btn.bind(on_press=lambda btn, p1=p1_input, p2=p2_input, m=(m1, m2): self.eredmeny_rogzites(p1, p2, m, btn))
                meccs_sor.add_widget(rogzit_btn)
                
                grid.add_widget(meccs_sor)

        scroll.add_widget(grid)
        self.main_content.add_widget(scroll)
        self.main_content.add_widget(Button(text='TABELLA MEGTEKINTÉSE', size_hint_y=None, height=50, on_press=lambda x: self.csoportkor_tabella_nezet(csoportok)))
        self.main_content.add_widget(Button(text='VISSZA A MENÜBE', size_hint_y=None, height=50, on_press=self.setup_settings_view))

    def eredmeny_rogzites(self, p1_input, p2_input, meccs, button):
        try:
            p1_leg = int(p1_input.text)
            p2_leg = int(p2_input.text)
            self.meccsek_eredmenyei[meccs] = (p1_leg, p2_leg)
            # Vizuális visszajelzés
            button.background_color = (0, 0.2, 0.8, 1) # Kék lesz, ha rögzítve
            # print(f"Rögzítve: {meccs}: {p1_leg}-{p2_leg}")
        except ValueError:
            pass # Ha nem számot írtak be

    def csoportkor_tabella_nezet(self, csoportok):
        self.main_content.clear_widgets()
        scroll = ScrollView(); grid = GridLayout(cols=1, spacing=20, size_hint_y=None); grid.bind(minimum_height=grid.setter('height'))

        for i, c in enumerate(csoportok):
            stats = {nev: {"pont": 0, "lg": 0, "lk": 0} for nev in c}
            for (p1, p2), (lg1, lg2) in self.meccsek_eredmenyei.items():
                if p1 in c: # Ellenőrizzük, hogy ez a meccs a jelenlegi csoporté-e
                    if lg1 > lg2: stats[p1]["pont"] += 2
                    elif lg2 > lg1: stats[p2]["pont"] += 2
                    stats[p1]["lg"] += lg1; stats[p1]["lk"] += lg2
                    stats[p2]["lg"] += lg2; stats[p2]["lk"] += lg1

            # Sorbarendezés: Pontszám, majd Legkülönbség alapján
            ranglista = sorted(stats.items(), key=lambda item: (item[1]["pont"], item[1]["lg"] - item[1]["lk"]), reverse=True)
            
            doboz = BoxLayout(orientation='vertical', size_hint_y=None, height=len(c)*50 + 70, padding=10)
            doboz.add_widget(Label(text=f"{chr(65+i)} CSOPORT TABELLA", font_size='22sp', color=(1,0.8,0,1)))
            
            for j, (nev, adatok) in enumerate(ranglista):
                szin = (1, 1, 0, 1) if j < self.tovabbjutok_szama else (1, 1, 1, 1) # Sárga kiemelés
                doboz.add_widget(Label(text=f"{j+1}. {nev} - {adatok['pont']}p ({adatok['lg']}:{adatok['lk']})", color=szin))
            
            grid.add_widget(doboz)

        scroll.add_widget(grid)
        self.main_content.add_widget(scroll)
        self.main_content.add_widget(Button(text='VISSZA A MECCSEKHEZ', size_hint_y=None, height=50, on_press=self.csoportkor_meccsek_nezet))
        self.main_content.add_widget(Button(text='VISSZA A MENÜBE', size_hint_y=None, height=50, on_press=self.setup_settings_view))

    def kieseses_fordulo_generalas(self, *args):
        self.main_content.clear_widgets()
        self.aktualis_kor_gyoztesei = []
        self.parok = []
        self.meccs_gombok = {}
        
        if len(self.aktualis_versenyzok) == 1:
            self.main_content.add_widget(Label(text=f"GYŐZTES: {self.aktualis_versenyzok[0]}", font_size='40sp', color=(1, 0.8, 0, 1)))
            self.main_content.add_widget(Button(text='VISSZA A MENÜBE', size_hint_y=None, height=60, on_press=self.setup_settings_view))
            return

        grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        
        temp = self.aktualis_versenyzok[:]
        while len(temp) > 1:
            p1 = temp.pop(0); p2 = temp.pop(0)
            self.parok.append([p1, p2])
        if temp:
            eronnyero = temp.pop(0)
            self.aktualis_kor_gyoztesei.append(eronnyero)
            grid.add_widget(Label(text=f"{eronnyero} - ERŐNYERŐ (Továbbjutott)", color=(0.5, 1, 0.5, 1), size_hint_y=None, height=40))

        for i, par in enumerate(self.parok):
            sor = BoxLayout(size_hint_y=None, height=60, spacing=10)
            btn1 = Button(text=par[0], on_press=lambda x, p=par[0], idx=i: self.gyoztes_valasztas(p, idx))
            vs = Label(text="VS", size_hint_x=0.2)
            btn2 = Button(text=par[1], on_press=lambda x, p=par[1], idx=i: self.gyoztes_valasztas(p, idx))
            sor.add_widget(btn1); sor.add_widget(vs); sor.add_widget(btn2)
            grid.add_widget(sor)
            self.meccs_gombok[i] = (btn1, btn2)

        scroll = ScrollView(); scroll.add_widget(grid)
        self.main_content.add_widget(Label(text=f"ÁGAK - {len(self.aktualis_versenyzok)} JÁTÉKOS", size_hint_y=None, height=40))
        self.main_content.add_widget(scroll)
        
        self.kov_gomb = Button(text='KÖVETKEZŐ FORDULÓ', size_hint_y=None, height=60, background_color=(0.5, 0.5, 0.5, 1), disabled=True)
        self.kov_gomb.bind(on_press=self.kovetkezo_fordulo)
        self.main_content.add_widget(self.kov_gomb)
        self.main_content.add_widget(Button(text='VISSZA A MENÜBE', size_hint_y=None, height=50, on_press=self.setup_settings_view))


    def gyoztes_valasztas(self, nev, par_index):
        aktualis_par = self.parok[par_index]
        for p in aktualis_par:
            if p in self.aktualis_kor_gyoztesei:
                self.aktualis_kor_gyoztesei.remove(p)
        
        self.aktualis_kor_gyoztesei.append(nev)
        
        btn1, btn2 = self.meccs_gombok[par_index]
        if btn1.text == nev:
            btn1.background_color = (0, 0, 0.8, 1) # Kék
            btn2.background_color = (1, 1, 1, 1) # Alap
        else:
            btn2.background_color = (0, 0, 0.8, 1) # Kék
            btn1.background_color = (1, 1, 1, 1) # Alap

        if len(self.aktualis_kor_gyoztesei) >= (len(self.parok) + (1 if len(self.aktualis_versenyzok) % 2 != 0 else 0)):
            self.kov_gomb.disabled = False
            self.kov_gomb.background_color = (0, 0.7, 0, 1)

    def kovetkezo_fordulo(self, *args):
        self.aktualis_versenyzok = self.aktualis_kor_gyoztesei[:]
        random.shuffle(self.aktualis_versenyzok)
        self.kieseses_fordulo_generalas()

class DartsApp(App):
    def build(self):
        Window.size = (450, 800); return DartsSorsolo()

if __name__ == '__main__': DartsApp().run()

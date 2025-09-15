import json
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.graphics import Rectangle, Color, RoundedRectangle


# BaseScreen com fundo
class BaseScreen(Screen):
    def __init__(self, **kwargs):
        super(BaseScreen, self).__init__(**kwargs)
        self.layout = FloatLayout()
        self.add_widget(self.layout)

        # Fundo
        with self.layout.canvas.before:
            self.bg = Rectangle(source="Trio_01 (1).png", size=self.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)

    def _update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos


# Tela inicial herdando BaseScreen
class StartScreen(BaseScreen):
    def __init__(self, **kwargs):
        super(StartScreen, self).__init__(**kwargs)

        # --- Card central ---
        self.card = BoxLayout(
            orientation='vertical',
            spacing=15,
            padding=20,
            size_hint=(0.6, 0.5),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )

        # Fundo arredondado do card
        with self.card.canvas.before:
            Color(0, 0, 0, 0.5)
            self.round_rect = RoundedRectangle(size=self.card.size, pos=self.card.pos, radius=[20])
        self.card.bind(size=self._update_round_rect, pos=self._update_round_rect)

        # Título
        title = Label(
            text="Quiz Gnatus",
            halign="center",
            valign="middle",
            size_hint=(1, None),
            font_size="30sp",
            bold=True,
            color=(1, 1, 1, 1)
        )
        title.bind(size=lambda lbl, _: setattr(lbl, "text_size", lbl.size))

        # Subtítulo
        subtitle = Label(
            text="Teste seus conhecimentos dos equipamentos Gnatus",
            font_size="20sp",
            halign="center",
            valign="middle",
            size_hint=(1, None),
            color=(1, 1, 1, 1)
        )
        subtitle.bind(size=lambda lbl, _: setattr(lbl, "text_size", lbl.size))

        # Botão jogar
        play_btn = Button(
            text="Jogar",
            size_hint=(None, None),
            size=(150, 50),
            pos_hint={"center_x": 0.5},
            background_normal="",
            background_color=(1, 1, 1, 1),
            color=(0, 0, 0, 1)
        )
        play_btn.bind(on_release=self.start_game)

        # Adicionar no card
        self.card.add_widget(title)
        self.card.add_widget(subtitle)
        self.card.add_widget(play_btn)

        # Adicionar card no layout principal
        self.layout.add_widget(self.card)

    def start_game(self, instance):
        self.manager.current = "game"

    def _update_round_rect(self, instance, value):
        self.round_rect.size = instance.size
        self.round_rect.pos = instance.pos


# Carregar perguntas
with open("perguntas.json", "r", encoding="utf-8") as f:
    perguntas = json.load(f)


# Tela de jogo herdando BaseScreen
class GameScreen(BaseScreen):
    def __init__(self, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        self.index = 0
        self.score = 0

        # Card do jogo
        self.card = BoxLayout(
            orientation="vertical",
            spacing=15,
            padding=20,
            size_hint=(0.7, 0.6),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )

        with self.card.canvas.before:
            Color(0, 0, 0, 0.5)
            self.round_rect = RoundedRectangle(size=self.card.size, pos=self.card.pos, radius=[20])
        self.card.bind(size=self._update_round_rect, pos=self._update_round_rect)

        self.layout.add_widget(self.card)

        # Pergunta
        self.label_pergunta = Label(
            font_size="22sp",
            halign="center",
            color=(1, 1, 1, 1)
        )
        self.label_pergunta.bind(size=lambda lbl, _: setattr(lbl, "text_size", lbl.size))
        self.card.add_widget(self.label_pergunta)

        # Botões de resposta
        self.botoes = []
        for i in range(3):
            btn = Button(
                size_hint=(1, None),
                height=50,
                background_normal="",
                background_color=(1, 1, 1, 1),
                color=(0, 0, 0, 1)
            )
            btn.bind(on_release=self.verificar_resposta)
            self.botoes.append(btn)
            self.card.add_widget(btn)

        # Resultado
        self.label_resultado = Label(font_size="18sp", color=(1, 1, 1, 1))
        self.card.add_widget(self.label_resultado)

        # Botão próxima
        self.btn_proxima = Button(
            text="Próxima",
            size_hint=(None, None),
            size=(150, 50),
            pos_hint={"center_x": 0.5},
            background_normal="",
            background_color=(0.2, 0.4, 0.8, 1),
            color=(1, 1, 1, 1)
        )
        self.btn_proxima.bind(on_release=self.proxima_pergunta)
        self.card.add_widget(self.btn_proxima)

        self.carregar_pergunta()

    def carregar_pergunta(self):
        if self.index < len(perguntas):
            pergunta = perguntas[self.index]
            self.label_pergunta.text = pergunta["pergunta"]

            for i, alt in enumerate(pergunta["alternativas"]):
                self.botoes[i].text = alt
                self.botoes[i].disabled = False

            self.label_resultado.text = ""
            self.btn_proxima.disabled = True
        else:
            # Abre popup de resultado final
            self.mostrar_resultado_final()

    def verificar_resposta(self, instance):
        pergunta = perguntas[self.index]
        resposta_correta = pergunta["correta"]
        escolhida = self.botoes.index(instance)

        if escolhida == resposta_correta:
            self.label_resultado.text = "Correta!"
            self.label_resultado.color = (0, 1, 0, 1)
            self.score += 1
        else:
            self.label_resultado.text = f"Errado! Resposta correta: {pergunta['alternativas'][resposta_correta]}"
            self.label_resultado.color = (1, 0, 0, 1)

        for btn in self.botoes:
            btn.disabled = True

        self.btn_proxima.disabled = False

    def proxima_pergunta(self, instance):
        self.index += 1
        self.carregar_pergunta()

    def mostrar_resultado_final(self):
        total = len(perguntas)
        resultado_texto = f"[b]Quiz Concluído![/b]\n\n"
        resultado_texto += f"{self.score}/{total}\n"

        if self.score == total:
            resultado_texto += "\nParabéns! Você acertou todas!"
        elif self.score >= total // 2:
            resultado_texto += "\nMuito bom! Mas pode melhorar!"
        else:
            resultado_texto += "\nInfelizmente não conseguiu, tente novamente!"

        lbl = Label(
            text=resultado_texto,
            markup=True,
            halign="center",
            valign="middle"
        )
        lbl.bind(size=lambda l, _: setattr(l, "text_size", l.size))

        btn_reiniciar = Button(
            text="Jogar Novamente",
            size_hint=(None, None),
            size=(200, 50),
            pos_hint={"center_x": 0.5},
            background_normal="",
            background_color=(0.5, 0, 1, 1),
            color=(1, 1, 1, 1)
        )
        btn_reiniciar.bind(on_release=self.reiniciar_quiz)

        box = BoxLayout(orientation="vertical", spacing=20, padding=20)
        box.add_widget(lbl)
        box.add_widget(btn_reiniciar)

        popup = Popup(
            title="",
            content=box,
            size_hint=(0.7, 0.6),
            auto_dismiss=False
        )
        self.popup_final = popup
        popup.open()

    def reiniciar_quiz(self, instance):
        self.index = 0
        self.score = 0
        self.carregar_pergunta()
        self.popup_final.dismiss()

    def _update_round_rect(self, instance, value):
        self.round_rect.size = instance.size
        self.round_rect.pos = instance.pos


# App principal
class QuizApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(StartScreen(name="start"))
        sm.add_widget(GameScreen(name="game"))
        return sm


if __name__ == "__main__":
    QuizApp().run()
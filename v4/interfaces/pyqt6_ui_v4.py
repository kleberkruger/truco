"""Interface de apresentação em PyQt6 • Edição Ultra Modern Spatial Canvas (100% Seamless Floating Scoreboard)."""
from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import (
    QFont, QColor, QPixmap, QPainter, QPen, QBrush, 
    QPainterPath, QLinearGradient
)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QListWidget, QStackedWidget, QDialog,
    QGraphicsDropShadowEffect, QGridLayout
)

from aplicacao.sessao import Sessao
from dominio.truco import Estado

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"

# Style CSS 100% Borderless, Seamless Floating HUD & Custom Scrollbar
QSS_THEME = """
QMainWindow {
    background-color: #05070a;
}

QFrame, QWidget {
    border: none;
    outline: none;
}

/* Placar Topo 100% Flutuante e Transparente (Sem Caixas ou Bordas) */
QFrame#hud-top-container {
    background: transparent;
}

/* Arena Radial Central */
QFrame.arena-canvas {
    background: qradialgradient(cx:0.5, cy:0.5, radius:0.75, fx:0.5, fy:0.5, stop:0 #0c3327, stop:0.65 #061e17, stop:1 #020b08);
    border-radius: 44px;
}

QLabel {
    color: #f1f5f9;
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, sans-serif;
    border: none;
}

/* Botões Modernos e Táteis */
QPushButton {
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif;
    border: none;
    outline: none;
}

QPushButton#btn-gold, QPushButton.btn-gold {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #fbbf24, stop:1 #d97706);
    color: #000000;
    font-weight: 800;
    font-size: 15px;
    border-radius: 16px;
    padding: 12px 24px;
}

QPushButton#btn-gold:hover, QPushButton.btn-gold:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #fcd34d, stop:1 #fbbf24);
}

QPushButton#btn-gold:disabled, QPushButton.btn-gold:disabled {
    background-color: #1e2433;
    color: #475569;
}

QPushButton#btn-dark, QPushButton.btn-dark {
    background-color: rgba(30, 41, 59, 0.6);
    color: #f8fafc;
    font-weight: 700;
    font-size: 13px;
    border-radius: 14px;
    padding: 8px 18px;
}

QPushButton#btn-dark:hover, QPushButton.btn-dark:hover {
    background-color: rgba(51, 65, 85, 0.85);
}

/* Ticker Flutuante de Eventos com Barra de Rolagem Customizada */
QListWidget#hud-ticker {
    background-color: rgba(9, 12, 19, 0.75);
    border-radius: 18px;
    color: #94a3b8;
    padding: 10px;
    font-size: 12px;
}

QListWidget#hud-ticker::item {
    padding: 6px 8px;
    border: none;
}

/* Custom Scrollbar Ultra Fina */
QScrollBar:vertical {
    border: none;
    background: rgba(15, 23, 42, 0.2);
    width: 5px;
    margin: 4px 2px 4px 2px;
    border-radius: 2px;
}

QScrollBar::handle:vertical {
    background: rgba(255, 255, 255, 0.2);
    min-height: 24px;
    border-radius: 2px;
}

QScrollBar::handle:vertical:hover {
    background: #fbbf24;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}
"""


class CardWidget(QWidget):
    """Carta com suporte a inclinação vetorial em leque (Fan Physics) e iluminação 3D."""

    def __init__(self, carta=None, verso=False, width=94, height=138, angle=0.0, parent=None, callback=None):
        super().__init__(parent)
        self.carta = carta
        self.verso = verso
        self.card_width = width
        self.card_height = height
        self.angle = angle
        self.callback = callback
        self.hovered = False

        self.setFixedSize(width + 20, height + 30)
        self.setCursor(Qt.CursorShape.PointingHandCursor if (callback and not verso) else Qt.CursorShape.ArrowCursor)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 190))
        shadow.setYOffset(8)
        self.setGraphicsEffect(shadow)

    def enterEvent(self, event):
        if self.callback and not self.verso:
            self.hovered = True
            self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.callback and not self.verso:
            self.hovered = False
            self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if self.callback and event.button() == Qt.MouseButton.LeftButton and not self.verso:
            self.callback()
        super().mousePressEvent(event)

    def _obter_pixmap_asset(self) -> QPixmap | None:
        if not self.carta and not self.verso:
            return None
        
        if self.verso:
            key = "verso"
        else:
            naipe_map = {"♦": "D", "♠": "S", "♥": "H", "♣": "C"}
            naipe_code = naipe_map.get(str(self.carta.naipe.value), "")
            rank_code = str(self.carta.rank.value)
            key = f"{rank_code}_{naipe_code}"

        filepath = ASSETS_DIR / f"{key}.png"
        if filepath.exists():
            pix = QPixmap(str(filepath))
            if not pix.isNull():
                return pix.scaled(
                    self.card_width, self.card_height,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
        return None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        current_angle = self.angle * 0.3 if self.hovered else self.angle
        y_lift = 0 if self.hovered else 14

        painter.save()
        center_x = self.width() / 2.0
        center_y = self.height() / 2.0
        painter.translate(center_x, center_y)
        painter.rotate(current_angle)
        painter.translate(-center_x, -center_y + y_lift)

        card_rect = QRectF(10, 0, self.card_width, self.card_height)

        pixmap = self._obter_pixmap_asset()
        if pixmap:
            painter.drawPixmap(int(card_rect.x()), int(card_rect.y()), pixmap)
            painter.restore()
            return

        if self.verso or not self.carta:
            self._draw_back(painter, card_rect)
        else:
            self._draw_front(painter, card_rect)

        painter.restore()

    def _draw_back(self, painter: QPainter, rect: QRectF):
        path = QPainterPath()
        path.addRoundedRect(rect, 8, 8)
        painter.fillPath(path, QBrush(QColor("#ffffff")))

        inner_rect = rect.adjusted(4, 4, -4, -4)
        inner_path = QPainterPath()
        inner_path.addRoundedRect(inner_rect, 6, 6)

        grad = QLinearGradient(inner_rect.topLeft(), inner_rect.bottomRight())
        grad.setColorAt(0, QColor("#1e293b"))
        grad.setColorAt(1, QColor("#0f172a"))
        painter.fillPath(inner_path, QBrush(grad))

        painter.setPen(QPen(QColor(251, 191, 36, 80), 1))
        painter.drawEllipse(inner_rect.center(), 14, 22)

    def _draw_front(self, painter: QPainter, rect: QRectF):
        naipe_symbol = str(self.carta.naipe.value)
        rank_str = str(self.carta.rank.value)
        is_red = naipe_symbol in ("♦", "♥")

        color = QColor("#e11d48" if is_red else "#0f172a")

        path = QPainterPath()
        path.addRoundedRect(rect, 8, 8)
        painter.fillPath(path, QBrush(QColor("#ffffff")))

        font_rank = QFont("Georgia", int(self.card_height * 0.15), QFont.Weight.Bold)
        font_suit = QFont("Arial", int(self.card_height * 0.12))

        painter.setPen(color)
        painter.setFont(font_rank)
        painter.drawText(int(rect.x() + 6), int(rect.y() + font_rank.pointSize() + 4), rank_str)
        painter.setFont(font_suit)
        painter.drawText(int(rect.x() + 6), int(rect.y() + font_rank.pointSize() + font_suit.pointSize() + 6), naipe_symbol)

        # Canto Invertido
        painter.save()
        painter.translate(rect.right() - 6, rect.bottom() - 6)
        painter.rotate(180)
        painter.setFont(font_rank)
        painter.drawText(0, font_rank.pointSize(), rank_str)
        painter.setFont(font_suit)
        painter.drawText(0, font_rank.pointSize() + font_suit.pointSize() + 2, naipe_symbol)
        painter.restore()

        # Centro
        font_large = QFont("Arial", int(self.card_height * 0.38))
        font_court = QFont("Georgia", int(self.card_height * 0.32), QFont.Weight.Bold)
        center_area = rect.adjusted(20, 20, -20, -20)

        if rank_str == "A":
            painter.setFont(font_large)
            painter.drawText(center_area, Qt.AlignmentFlag.AlignCenter, naipe_symbol)
        elif rank_str in ("K", "Q", "J"):
            painter.setFont(font_court)
            painter.drawText(center_area, Qt.AlignmentFlag.AlignCenter, rank_str)
        else:
            painter.setFont(QFont("Arial", int(self.card_height * 0.18)))
            painter.drawText(center_area, Qt.AlignmentFlag.AlignCenter, naipe_symbol)

        if self.carta.manilha:
            painter.setFont(QFont("Arial", 8, QFont.Weight.Bold))
            badge_rect = QRectF(rect.right() - 20, rect.top() + 4, 16, 16)
            painter.setBrush(QBrush(QColor("#f59e0b")))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(badge_rect)
            painter.setPen(QColor("#000000"))
            painter.drawText(badge_rect, Qt.AlignmentFlag.AlignCenter, "M")


class DialogoCustom(QDialog):
    """Modal Flutuante de Alta Definição."""

    def __init__(self, titulo: str, mensagem: str, opcoes: list[tuple[str, callable, bool]], widget_extra: QWidget | None = None, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(440)

        layout = QVBoxLayout(self)
        panel = QFrame()
        panel.setStyleSheet("background-color: #0f1420; border-radius: 24px;")

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 230))
        shadow.setYOffset(10)
        panel.setGraphicsEffect(shadow)

        p_layout = QVBoxLayout(panel)
        p_layout.setContentsMargins(28, 28, 28, 28)
        p_layout.setSpacing(14)

        lbl_title = QLabel(titulo)
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_title.setStyleSheet("color: #fbbf24; font-size: 22px; font-weight: 800;")
        p_layout.addWidget(lbl_title)

        if mensagem:
            lbl_msg = QLabel(mensagem)
            lbl_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_msg.setWordWrap(True)
            lbl_msg.setStyleSheet("color: #94a3b8; font-size: 14px;")
            p_layout.addWidget(lbl_msg)

        if widget_extra:
            p_layout.addWidget(widget_extra)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        for texto, action, destaque in opcoes:
            btn = QPushButton(texto)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(46)
            btn.setStyleSheet(
                "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #fbbf24, stop:1 #f59e0b); color: #000; font-weight: 800; border-radius: 12px;"
                if destaque else
                "background-color: #1e293b; color: #f8fafc; font-weight: 700; border-radius: 12px;"
            )
            btn.clicked.connect(self.accept)
            if action:
                btn.clicked.connect(action)
            btn_layout.addWidget(btn)

        p_layout.addLayout(btn_layout)
        layout.addWidget(panel)


class TelaTrucoPyQt(QMainWindow):
    def __init__(self, modalidade: int = 2, limpo: bool = True, seed=None):
        super().__init__()
        self.setWindowTitle("TRUCO PAULISTA • Spatial Arena 360°")
        self.resize(1280, 820)
        self.setMinimumSize(1024, 700)
        self.setStyleSheet(QSS_THEME)

        self.sessao: Sessao | None = None
        self.modalidade = modalidade
        self.limpo = limpo
        self.seed = seed

        self.timer_bot = QTimer(self)
        self.timer_bot.setInterval(700)
        self.timer_bot.timeout.connect(self._loop_bot)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self._criar_menu()
        self._criar_tela_jogo()

        self.stack.setCurrentIndex(0)

    # ------------------ MENU PRINCIPAL ------------------
    def _criar_menu(self):
        menu_widget = QWidget()
        layout = QVBoxLayout(menu_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        panel = QFrame()
        panel.setStyleSheet("background-color: rgba(15, 20, 32, 0.85); border-radius: 28px;")
        panel.setFixedSize(480, 420)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(36)
        shadow.setColor(QColor(0, 0, 0, 200))
        shadow.setYOffset(10)
        panel.setGraphicsEffect(shadow)

        p_layout = QVBoxLayout(panel)
        p_layout.setContentsMargins(36, 36, 36, 36)

        lbl_logo = QLabel("TRUCO PAULISTA")
        lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_logo.setStyleSheet("color: #fbbf24; font-size: 32px; font-weight: 900; letter-spacing: 2px;")
        p_layout.addWidget(lbl_logo)

        lbl_sub = QLabel("Arena Radial 360° • Seamless Canvas")
        lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_sub.setStyleSheet("color: #64748b; font-size: 14px; margin-bottom: 24px;")
        p_layout.addWidget(lbl_sub)

        # Modalidade
        lbl_mod = QLabel("MODALIDADE")
        lbl_mod.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: 800;")
        p_layout.addWidget(lbl_mod)

        grid_mod = QHBoxLayout()
        grid_mod.setSpacing(10)
        self.btns_mod = []
        for idx, (nome, m) in enumerate([("1 × 1", 1), ("2 × 2", 2), ("3 × 3", 3)]):
            btn = QPushButton(nome)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, val=m: self._set_modalidade(val))
            grid_mod.addWidget(btn)
            self.btns_mod.append((btn, m))
        p_layout.addLayout(grid_mod)

        p_layout.addSpacing(10)

        # Baralho
        lbl_bar = QLabel("BARALHO")
        lbl_bar.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: 800;")
        p_layout.addWidget(lbl_bar)

        grid_bar = QHBoxLayout()
        grid_bar.setSpacing(10)
        self.btn_limpo = QPushButton("Limpo (24 cartas)")
        self.btn_sujo = QPushButton("Sujo (40 cartas)")
        for b in (self.btn_limpo, self.btn_sujo):
            b.setCheckable(True)
            b.setCursor(Qt.CursorShape.PointingHandCursor)

        self.btn_limpo.clicked.connect(lambda: self._set_baralho(True))
        self.btn_sujo.clicked.connect(lambda: self._set_baralho(False))
        grid_bar.addWidget(self.btn_limpo)
        grid_bar.addWidget(self.btn_sujo)
        p_layout.addLayout(grid_bar)

        p_layout.addSpacing(24)

        btn_start = QPushButton("ENTRAR NA ARENA")
        btn_start.setObjectName("btn-gold")
        btn_start.setFixedHeight(48)
        btn_start.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_start.clicked.connect(self._iniciar_jogo)
        p_layout.addWidget(btn_start)

        self._atualizar_estilos_menu()
        layout.addWidget(panel)
        self.stack.addWidget(menu_widget)

    def _set_modalidade(self, m: int):
        self.modalidade = m
        if m == 3:
            self.limpo = False
        self._atualizar_estilos_menu()

    def _set_baralho(self, limpo: bool):
        if self.modalidade != 3:
            self.limpo = limpo
        self._atualizar_estilos_menu()

    def _atualizar_estilos_menu(self):
        for btn, m in self.btns_mod:
            btn.setChecked(m == self.modalidade)
            btn.setStyleSheet(
                "background-color: #fbbf24; color: #000; font-weight: 800; border-radius: 10px; padding: 10px;"
                if m == self.modalidade else
                "background-color: #1e293b; color: #94a3b8; border-radius: 10px; padding: 10px;"
            )
        self.btn_limpo.setChecked(self.limpo)
        self.btn_sujo.setChecked(not self.limpo)
        self.btn_limpo.setEnabled(self.modalidade != 3)

        for b, act in [(self.btn_limpo, self.limpo), (self.btn_sujo, not self.limpo)]:
            b.setStyleSheet(
                "background-color: #fbbf24; color: #000; font-weight: 800; border-radius: 10px; padding: 10px;"
                if act else
                "background-color: #1e293b; color: #94a3b8; border-radius: 10px; padding: 10px;"
            )

    # ------------------ ARENA DE JOGO (RADIAL 360°) ------------------
    def _criar_tela_jogo(self):
        jogo_widget = QWidget()
        arena_layout = QGridLayout(jogo_widget)
        arena_layout.setContentsMargins(24, 16, 24, 16)

        # 1. Topo: HUD 100% Seamless & Transparente (Sem Caixas ou Bordas)
        hud_top = QFrame()
        hud_top.setObjectName("hud-top-container")
        hud_top.setFixedHeight(56)
        h_layout = QHBoxLayout(hud_top)
        h_layout.setContentsMargins(8, 4, 8, 4)

        # Placar da Sua Equipe
        lbl_e0_title = QLabel("SUA EQUIPE")
        lbl_e0_title.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: 800; letter-spacing: 1px;")
        self.lbl_score_eq0 = QLabel("0")
        self.lbl_score_eq0.setStyleSheet("color: #fbbf24; font-size: 32px; font-weight: 900;")

        h_layout.addWidget(lbl_e0_title)
        h_layout.addSpacing(8)
        h_layout.addWidget(self.lbl_score_eq0)

        # Divisor de Luz Vertical Minimalista
        lbl_sep = QLabel("│")
        lbl_sep.setStyleSheet("color: rgba(255, 255, 255, 0.15); font-size: 18px; margin: 0 14px;")
        h_layout.addWidget(lbl_sep)

        # Placar da Equipe Adversária
        self.lbl_score_eq1 = QLabel("0")
        self.lbl_score_eq1.setStyleSheet("color: #f8fafc; font-size: 32px; font-weight: 900;")
        lbl_e1_title = QLabel("ADVERSÁRIOS")
        lbl_e1_title.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: 800; letter-spacing: 1px;")

        h_layout.addWidget(self.lbl_score_eq1)
        h_layout.addSpacing(8)
        h_layout.addWidget(lbl_e1_title)

        h_layout.addStretch()

        # Indicador Luminoso Flutuante + Status da Mão
        lbl_dot = QLabel("●")
        lbl_dot.setStyleSheet("color: #fbbf24; font-size: 10px;")
        self.lbl_mao_info = QLabel("MÃO 1  •  VALE 1 PONTO")
        self.lbl_mao_info.setStyleSheet("color: #e2e8f0; font-weight: 800; font-size: 13px; letter-spacing: 0.5px;")

        h_layout.addWidget(lbl_dot)
        h_layout.addSpacing(6)
        h_layout.addWidget(self.lbl_mao_info)

        h_layout.addStretch()

        btn_menu = QPushButton("SAIR")
        btn_menu.setObjectName("btn-dark")
        btn_menu.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_menu.clicked.connect(self._voltar_menu)
        h_layout.addWidget(btn_menu)

        arena_layout.addWidget(hud_top, 0, 0, 1, 3)

        # 2. Centro: Mesa de Feltro Circular Total
        self.mesa_feltro = QFrame()
        self.mesa_feltro.setProperty("class", "arena-canvas")
        m_layout = QVBoxLayout(self.mesa_feltro)
        m_layout.setContentsMargins(24, 16, 24, 16)

        # Norte: Parceiro / Bot Topo
        self.container_norte = QHBoxLayout()
        self.container_norte.setAlignment(Qt.AlignmentFlag.AlignCenter)
        m_layout.addLayout(self.container_norte)

        # Centro Mesa: Oeste | Vira + Jogadas | Leste
        centro_mid = QHBoxLayout()
        
        self.container_oeste = QVBoxLayout()
        self.container_oeste.setAlignment(Qt.AlignmentFlag.AlignCenter)
        centro_mid.addLayout(self.container_oeste)

        centro_mid.addStretch()

        # Slot do Vira e Mesa
        v_box = QVBoxLayout()
        v_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_v = QLabel("VIRA")
        lbl_v.setStyleSheet("color: #64748b; font-size: 10px; font-weight: 800;")
        v_box.addWidget(lbl_v)
        self.vira_slot = QWidget()
        v_box.addWidget(self.vira_slot)
        centro_mid.addLayout(v_box)

        centro_mid.addSpacing(30)

        # Cartas Jogadas
        self.layout_cartas_mesa = QHBoxLayout()
        self.layout_cartas_mesa.setSpacing(12)
        centro_mid.addLayout(self.layout_cartas_mesa)

        centro_mid.addStretch()

        self.container_leste = QVBoxLayout()
        self.container_leste.setAlignment(Qt.AlignmentFlag.AlignCenter)
        centro_mid.addLayout(self.container_leste)

        m_layout.addLayout(centro_mid)
        m_layout.addStretch()

        # Sul: Seu Leque de Cartas + Floating Action Hub
        sul_box = QHBoxLayout()
        sul_box.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Leque de Cartas Humano
        self.layout_leque_humano = QHBoxLayout()
        self.layout_leque_humano.setSpacing(-24)
        sul_box.addLayout(self.layout_leque_humano)

        sul_box.addSpacing(20)

        # Botão Truco Flutuante
        self.btn_truco = QPushButton("TRUCO!")
        self.btn_truco.setObjectName("btn-gold")
        self.btn_truco.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_truco.setFixedSize(140, 50)
        self.btn_truco.clicked.connect(self._pedir_truco)
        sul_box.addWidget(self.btn_truco)

        m_layout.addLayout(sul_box)

        arena_layout.addWidget(self.mesa_feltro, 1, 0, 1, 3)

        # 3. Rodapé Flutuante: Ticker Overlay de Eventos (Expandido com Scrollbar Ultrafina)
        self.log_list = QListWidget()
        self.log_list.setObjectName("hud-ticker")
        self.log_list.setFixedHeight(180)
        self.log_list.setFixedWidth(340)
        arena_layout.addWidget(self.log_list, 1, 0, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)

        self.stack.addWidget(jogo_widget)

    # ------------------ LÓGICA E ATUALIZAÇÃO ------------------
    def _iniciar_jogo(self):
        self.sessao = Sessao(modalidade=self.modalidade, limpo=self.limpo, seed=self.seed)
        self.stack.setCurrentIndex(1)
        self.timer_bot.start()
        self._atualizar_interface()

    def _voltar_menu(self):
        self.timer_bot.stop()
        self.sessao = None
        self.stack.setCurrentIndex(0)

    def _loop_bot(self):
        if not self.sessao:
            return
        p = self.sessao.partida

        if p.estado == Estado.PEDIDO_PENDENTE and p.pedido_pendente and p.pedido_pendente[0] == 1:
            self._tratar_pedido_pendente()
            return
        if p.mao_de_onze == 0:
            self._tratar_mao_de_onze()
            return
        if p.estado == Estado.AGUARDANDO:
            self._tratar_mao_encerrada()
            return
        if p.estado == Estado.ENCERRADA:
            self._tratar_fim_jogo()
            return

        if self.sessao.avancar_bot():
            self._atualizar_interface()

    def _atualizar_interface(self):
        if not self.sessao:
            return
        p = self.sessao.partida
        humano = self.sessao.humano

        self.lbl_score_eq0.setText(str(p.pontos[0]))
        self.lbl_score_eq1.setText(str(p.pontos[1]))
        self.lbl_mao_info.setText(f"MÃO {p.mao_numero}  •  VALE {p.valor_mao} PTS")

        # Ticker Feed
        self.log_list.clear()
        for ev in self.sessao.eventos[-15:]:
            self.log_list.addItem(ev.mensagem)
        self.log_list.scrollToBottom()

        # Vira
        for child in self.vira_slot.children():
            if isinstance(child, QWidget):
                child.deleteLater()
        if p.vira:
            v_layout = QVBoxLayout(self.vira_slot)
            v_layout.setContentsMargins(0, 0, 0, 0)
            v_layout.addWidget(CardWidget(carta=p.vira, width=76, height=110))

        # Cartas na Mesa
        while self.layout_cartas_mesa.count():
            item = self.layout_cartas_mesa.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if p.jogadas:
            maior_forca = max(j.carta.forca for j in p.jogadas)
            for j in p.jogadas:
                box_j = QVBoxLayout()
                box_j.setAlignment(Qt.AlignmentFlag.AlignCenter)
                is_maior = (j.carta.forca == maior_forca)
                
                card_w = CardWidget(carta=j.carta, width=80, height=116)
                box_j.addWidget(card_w)

                lbl_n = QLabel(f"{j.jogador.nome} {'★' if is_maior else ''}")
                lbl_n.setStyleSheet("color: #fbbf24; font-size: 11px; font-weight: 800;" if is_maior else "color: #94a3b8; font-size: 11px;")
                box_j.addWidget(lbl_n)

                w_item = QWidget()
                w_item.setLayout(box_j)
                self.layout_cartas_mesa.addWidget(w_item)

        # Distribuir Bots nos Containers Radiais
        for layout_c in (self.container_norte, self.container_oeste, self.container_leste):
            while layout_c.count():
                item = layout_c.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

        outros = [j for j in p.jogadores if j is not humano]
        posicoes = [self.container_norte, self.container_oeste, self.container_leste]

        for idx, bot in enumerate(outros):
            target_layout = posicoes[idx % len(posicoes)]
            b_box = QVBoxLayout()
            b_box.setAlignment(Qt.AlignmentFlag.AlignCenter)

            is_vez = (p.jogador_da_vez is bot)
            is_parceiro = (bot in p.equipes[0].jogadores)

            lbl_avatar = QLabel(bot.nome[0].upper())
            lbl_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_avatar.setFixedSize(38, 38)
            bg_col = "#fbbf24" if is_vez else ("#10b981" if is_parceiro else "#1e293b")
            lbl_avatar.setStyleSheet(f"background-color: {bg_col}; color: #000; font-weight: 900; border-radius: 19px;")
            b_box.addWidget(lbl_avatar)

            lbl_name = QLabel(bot.nome)
            lbl_name.setStyleSheet("color: #fbbf24; font-size: 10px; font-weight: 800;" if is_parceiro else "color: #94a3b8; font-size: 10px;")
            b_box.addWidget(lbl_name)

            h_cards = QHBoxLayout()
            h_cards.setSpacing(2)
            for _ in range(len(bot.cartas)):
                h_cards.addWidget(CardWidget(verso=True, width=26, height=38))

            w_c = QWidget()
            w_c.setLayout(h_cards)
            b_box.addWidget(w_c)

            w_bot = QWidget()
            w_bot.setLayout(b_box)
            target_layout.addWidget(w_bot)

        # Leque do Jogador Humano
        while self.layout_leque_humano.count():
            item = self.layout_leque_humano.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        pode_jogar = self.sessao.precisa_humano
        num_cartas = len(humano.cartas)

        angles = [-8.0, 0.0, 8.0] if num_cartas == 3 else ([-5.0, 5.0] if num_cartas == 2 else [0.0])

        for idx, carta in enumerate(humano.cartas):
            ang = angles[idx] if idx < len(angles) else 0.0
            cb = (lambda i=idx: self._jogar_carta_humano(i)) if pode_jogar else None
            cw = CardWidget(carta=carta, width=94, height=136, angle=ang, callback=cb)
            self.layout_leque_humano.addWidget(cw)

        # Botão Truco
        pode_trucar = self.sessao.pode_trucar()
        self.btn_truco.setEnabled(pode_trucar)
        self.btn_truco.setText("TRUCO!" if p.valor_mao == 1 else {3: "SEIS!", 6: "NOVE!", 9: "DOZE!"}.get(p.valor_mao, "AUMENTAR!"))

    def _jogar_carta_humano(self, idx: int):
        try:
            self.sessao.jogar(idx)
            self._atualizar_interface()
        except ValueError:
            pass

    def _pedir_truco(self):
        try:
            self.sessao.pedir_truco()
            self._atualizar_interface()
        except ValueError:
            pass

    # ------------------ DIÁLOGOS ------------------
    def _tratar_pedido_pendente(self):
        self.timer_bot.stop()
        p = self.sessao.partida
        solicitante, valor = p.pedido_pendente

        opcoes = [
            ("ACEITAR", lambda: self.sessao.responder(True), True),
            ("CORRER", lambda: self.sessao.responder(False), False)
        ]
        if valor < 12:
            opcoes.append(("AUMENTAR", lambda: self.sessao.aumentar(), False))

        dlg = DialogoCustom(f"PEDIRAM {valor} PONTOS!", "Decida a jogada da sua equipe:", opcoes, parent=self)
        dlg.exec()
        self.timer_bot.start()
        self._atualizar_interface()

    def _tratar_mao_de_onze(self):
        self.timer_bot.stop()
        dlg = DialogoCustom("MÃO DE ONZE", "Desejam jogar esta mão valendo 3 pontos?", [
            ("JOGAR MÃO", lambda: self.sessao.decidir_onze(True), True),
            ("CORRER", lambda: self.sessao.decidir_onze(False), False)
        ], parent=self)
        dlg.exec()
        self.timer_bot.start()
        self._atualizar_interface()

    def _tratar_mao_encerrada(self):
        self.timer_bot.stop()
        p = self.sessao.partida

        score_w = QWidget()
        sl = QHBoxLayout(score_w)
        sl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sl.setSpacing(16)

        for e_idx, (nome, pts) in enumerate([("SUA EQUIPE", p.pontos[0]), ("ADVERSÁRIOS", p.pontos[1])]):
            box = QFrame()
            box.setStyleSheet("background-color: #1e293b; border-radius: 14px;")
            bl = QVBoxLayout(box)
            bl.setContentsMargins(16, 10, 16, 10)
            lbl_t = QLabel(nome)
            lbl_t.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: 800;")
            lbl_v = QLabel(str(pts))
            lbl_v.setStyleSheet("color: #fbbf24; font-size: 34px; font-weight: 900;" if e_idx == 0 else "color: #f8fafc; font-size: 34px; font-weight: 900;")
            bl.addWidget(lbl_t, 0, Qt.AlignmentFlag.AlignCenter)
            bl.addWidget(lbl_v, 0, Qt.AlignmentFlag.AlignCenter)
            sl.addWidget(box)

        dlg = DialogoCustom("MÃO ENCERRADA", "Placar atual:", [("PRÓXIMA MÃO", lambda: self.sessao.proxima_mao(), True)], widget_extra=score_w, parent=self)
        dlg.exec()
        self.timer_bot.start()
        self._atualizar_interface()

    def _tratar_fim_jogo(self):
        self.timer_bot.stop()
        p = self.sessao.partida
        venceu = (p.vencedor == 0)

        dlg = DialogoCustom(
            "🏆 VITÓRIA!" if venceu else "FIM DE JOGO",
            "Sua equipe venceu a partida!" if venceu else "Os adversários venceram.",
            [("NOVA PARTIDA", self._voltar_menu, True)],
            parent=self
        )
        dlg.exec()

    def executar(self):
        self.show()


def main():
    app = QApplication(sys.argv)
    tela = TelaTrucoPyQt()
    tela.executar()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
"""Interface gráfica PyQt6 para o Truco Paulista.

Interface moderna com mesa de jogo, cartas visuais,
placar lateral e diálogos para decisões.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import (
    QFont, QColor, QPixmap, QPainter, QPen, QBrush,
    QPainterPath, QLinearGradient,
)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QListWidget, QStackedWidget, QDialog,
    QGraphicsDropShadowEffect, QSizePolicy,
)

from aplicacao.sessao import Sessao
from dominio.estado import EstadoPartida
from dominio.carta import Carta
from estrategia.ia import Dificuldade

ASSETS_DIR = Path(__file__).resolve().parent.parent / 'assets'

# ---------------------------------------------------------------------------
# Tema visual
# ---------------------------------------------------------------------------

QSS_THEME = """
QMainWindow {
    background-color: #05070a;
}
QFrame, QWidget {
    border: none;
    outline: none;
}
QFrame.arena-canvas {
    background: qradialgradient(cx:0.5, cy:0.5, radius:0.75, fx:0.5, fy:0.5,
        stop:0 #0c3327, stop:0.65 #061e17, stop:1 #020b08);
    border-radius: 36px;
}
QFrame#hud-side-container {
    background-color: rgba(15, 20, 32, 0.85);
    border-radius: 24px;
}
QLabel {
    color: #f1f5f9;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    border: none;
}
QPushButton {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    border: none;
    outline: none;
}
QPushButton#btn-gold {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #fbbf24, stop:1 #d97706);
    color: #000;
    font-weight: 800;
    font-size: 15px;
    border-radius: 16px;
    padding: 14px 24px;
}
QPushButton#btn-gold:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #fcd34d, stop:1 #fbbf24);
}
QPushButton#btn-gold:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #d97706, stop:1 #b45309);
}
QPushButton#btn-gold:disabled {
    background-color: #1e2433;
    color: #475569;
}
QPushButton#btn-dark {
    background-color: rgba(30, 41, 59, 0.8);
    color: #f8fafc;
    font-weight: 700;
    font-size: 13px;
    border-radius: 12px;
    padding: 10px 18px;
}
QPushButton#btn-dark:hover {
    background-color: rgba(51, 65, 85, 0.95);
}
QPushButton#btn-dark:pressed {
    background-color: rgba(71, 85, 105, 0.95);
}
QListWidget#hud-ticker {
    background-color: rgba(15, 20, 32, 0.7);
    border-radius: 20px;
    color: #94a3b8;
    padding: 12px;
    font-size: 12px;
}
QListWidget#hud-ticker::item {
    padding: 6px 8px;
}
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
"""


# ---------------------------------------------------------------------------
# Carta visual
# ---------------------------------------------------------------------------

class CardWidget(QWidget):
    """Widget que desenha uma carta do baralho."""

    def __init__(
        self,
        carta: Carta | None = None,
        verso: bool = False,
        width: int = 94,
        height: int = 138,
        angle: float = 0.0,
        parent: QWidget | None = None,
        callback: callable | None = None,
    ) -> None:
        super().__init__(parent)
        self.carta = carta
        self.verso = verso
        self.card_width = width
        self.card_height = height
        self.angle = angle
        self.callback = callback
        self.hovered = False

        self.setFixedSize(width + 20, height + 30)
        self.setCursor(
            Qt.CursorShape.PointingHandCursor
            if (callback and not verso)
            else Qt.CursorShape.ArrowCursor
        )

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 190))
        shadow.setYOffset(8)
        self.setGraphicsEffect(shadow)

    def enterEvent(self, event) -> None:
        if self.callback and not self.verso:
            self.hovered = True
            self.update()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        if self.callback and not self.verso:
            self.hovered = False
            self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event) -> None:
        if self.callback and event.button() == Qt.MouseButton.LeftButton and not self.verso:
            self.callback()
        super().mousePressEvent(event)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        current_angle = self.angle * 0.3 if self.hovered else self.angle
        y_lift = 0 if self.hovered else 14

        painter.save()
        cx = self.width() / 2.0
        cy = self.height() / 2.0
        painter.translate(cx, cy)
        painter.rotate(current_angle)
        painter.translate(-cx, -cy + y_lift)

        card_rect = QRectF(10, 0, self.card_width, self.card_height)

        pixmap = self._obter_pixmap()
        if pixmap:
            painter.drawPixmap(int(card_rect.x()), int(card_rect.y()), pixmap)
            painter.restore()
            return

        if self.verso or not self.carta:
            self._draw_back(painter, card_rect)
        else:
            self._draw_front(painter, card_rect)

        painter.restore()

    def _obter_pixmap(self) -> QPixmap | None:
        if self.verso:
            filepath = ASSETS_DIR / 'verso.png'
        elif self.carta:
            naipe_map = {'♦': 'D', '♠': 'S', '♥': 'H', '♣': 'C'}
            naipe_code = naipe_map.get(str(self.carta.naipe.value), '')
            rank_code = str(self.carta.rank.value)
            filepath = ASSETS_DIR / f'{rank_code}_{naipe_code}.png'
        else:
            return None

        if filepath.exists():
            pix = QPixmap(str(filepath))
            if not pix.isNull():
                return pix.scaled(
                    self.card_width, self.card_height,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
        return None

    def _draw_back(self, painter: QPainter, rect: QRectF) -> None:
        path = QPainterPath()
        path.addRoundedRect(rect, 6, 6)
        grad = QLinearGradient(rect.topLeft(), rect.bottomRight())
        grad.setColorAt(0, QColor('#1e293b'))
        grad.setColorAt(0.5, QColor('#111827'))
        grad.setColorAt(1, QColor('#0f172a'))
        painter.fillPath(path, QBrush(grad))

    def _draw_front(self, painter: QPainter, rect: QRectF) -> None:
        if self.carta is None:
            return

        naipe_symbol = str(self.carta.naipe.value)
        rank_str = str(self.carta.rank.value)
        is_red = naipe_symbol in ('♦', '♥')
        color = QColor('#e11d48' if is_red else '#0f172a')

        path = QPainterPath()
        path.addRoundedRect(rect, 8, 8)
        painter.fillPath(path, QBrush(QColor('#ffffff')))

        font_rank = QFont('Georgia', int(self.card_height * 0.15), QFont.Weight.Bold)
        font_suit = QFont('Arial', int(self.card_height * 0.12))

        painter.setPen(color)
        painter.setFont(font_rank)
        painter.drawText(int(rect.x() + 6), int(rect.y() + font_rank.pointSize() + 4), rank_str)
        painter.setFont(font_suit)
        painter.drawText(int(rect.x() + 6), int(rect.y() + font_rank.pointSize() + font_suit.pointSize() + 6), naipe_symbol)

        # Centro
        font_large = QFont('Arial', int(self.card_height * 0.38))
        center_area = rect.adjusted(20, 20, -20, -20)
        if rank_str == 'A':
            painter.setFont(font_large)
            painter.drawText(center_area, Qt.AlignmentFlag.AlignCenter, naipe_symbol)
        else:
            painter.setFont(QFont('Arial', int(self.card_height * 0.18)))
            painter.drawText(center_area, Qt.AlignmentFlag.AlignCenter, naipe_symbol)

        if self.carta.manilha:
            painter.setFont(QFont('Arial', 8, QFont.Weight.Bold))
            badge_rect = QRectF(rect.right() - 20, rect.top() + 4, 16, 16)
            painter.setBrush(QBrush(QColor('#f59e0b')))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(badge_rect)
            painter.setPen(QColor('#000000'))
            painter.drawText(badge_rect, Qt.AlignmentFlag.AlignCenter, 'M')


# ---------------------------------------------------------------------------
# Diálogo modal
# ---------------------------------------------------------------------------

class DialogoCustom(QDialog):
    """Diálogo modal estilizado para decisões do jogo."""

    def __init__(
        self,
        titulo: str,
        mensagem: str,
        opcoes: list[tuple[str, callable, bool]],
        widget_extra: QWidget | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(440)

        layout = QVBoxLayout(self)
        panel = QFrame()
        panel.setStyleSheet('background-color: #0f1420; border-radius: 24px;')

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
        lbl_title.setStyleSheet('color: #fbbf24; font-size: 22px; font-weight: 800;')
        p_layout.addWidget(lbl_title)

        if mensagem:
            lbl_msg = QLabel(mensagem)
            lbl_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_msg.setWordWrap(True)
            lbl_msg.setStyleSheet('color: #94a3b8; font-size: 14px;')
            p_layout.addWidget(lbl_msg)

        if widget_extra:
            p_layout.addWidget(widget_extra)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        for texto, action, destaque in opcoes:
            btn = QPushButton(texto)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(46)
            if destaque:
                btn.setStyleSheet(
                    'background: qlineargradient(x1:0, y1:0, x2:1, y2:0, '
                    'stop:0 #fbbf24, stop:1 #f59e0b); color: #000; font-weight: 800; '
                    'border-radius: 12px;'
                )
            else:
                btn.setStyleSheet(
                    'background-color: #1e293b; color: #f8fafc; '
                    'font-weight: 700; border-radius: 12px;'
                )
            btn.clicked.connect(self.accept)
            if action:
                btn.clicked.connect(action)
            btn_layout.addWidget(btn)

        p_layout.addLayout(btn_layout)
        layout.addWidget(panel)


# ---------------------------------------------------------------------------
# Janela principal
# ---------------------------------------------------------------------------

class TelaTrucoPyQt(QMainWindow):
    """Janela principal da interface PyQt6."""

    def __init__(
        self,
        modalidade: int = 2,
        limpo: bool = True,
        dificuldade: str = Dificuldade.MEDIO,
        seed: int | None = None,
    ) -> None:
        super().__init__()
        self.setWindowTitle('TRUCO PAULISTA')
        self.resize(1280, 820)
        self.setMinimumSize(1024, 700)
        self.setStyleSheet(QSS_THEME)

        self.sessao: Sessao | None = None
        self.modalidade = modalidade
        self.limpo = limpo
        self.dificuldade = dificuldade
        self.seed = seed

        self.timer_bot = QTimer(self)
        self.timer_bot.setInterval(1300)
        self.timer_bot.timeout.connect(self._loop_bot)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self._criar_menu()
        self._criar_tela_jogo()
        self.stack.setCurrentIndex(0)

    # ------------------------------------------------------------------
    # Menu principal
    # ------------------------------------------------------------------

    def _criar_menu(self) -> None:
        menu_widget = QWidget()
        layout = QVBoxLayout(menu_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        panel = QFrame()
        panel.setStyleSheet('background-color: rgba(15, 20, 32, 0.85); border-radius: 28px;')
        panel.setFixedSize(480, 500)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(36)
        shadow.setColor(QColor(0, 0, 0, 200))
        shadow.setYOffset(10)
        panel.setGraphicsEffect(shadow)

        p_layout = QVBoxLayout(panel)
        p_layout.setContentsMargins(36, 36, 36, 36)

        lbl_logo = QLabel('TRUCO PAULISTA')
        lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_logo.setStyleSheet('color: #fbbf24; font-size: 32px; font-weight: 900; letter-spacing: 2px;')
        p_layout.addWidget(lbl_logo)

        lbl_sub = QLabel('Versão 5 — Arquitetura Modular')
        lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_sub.setStyleSheet('color: #64748b; font-size: 14px; margin-bottom: 24px;')
        p_layout.addWidget(lbl_sub)

        # Modalidade
        lbl_mod = QLabel('MODALIDADE')
        lbl_mod.setStyleSheet('color: #94a3b8; font-size: 11px; font-weight: 800;')
        p_layout.addWidget(lbl_mod)

        grid_mod = QHBoxLayout()
        grid_mod.setSpacing(10)
        self.btns_mod: list[tuple[QPushButton, int]] = []
        for nome, m in [('1 × 1', 1), ('2 × 2', 2), ('3 × 3', 3)]:
            btn = QPushButton(nome)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, val=m: self._set_modalidade(val))
            grid_mod.addWidget(btn)
            self.btns_mod.append((btn, m))
        p_layout.addLayout(grid_mod)

        p_layout.addSpacing(10)

        # Baralho
        lbl_bar = QLabel('BARALHO')
        lbl_bar.setStyleSheet('color: #94a3b8; font-size: 11px; font-weight: 800;')
        p_layout.addWidget(lbl_bar)

        grid_bar = QHBoxLayout()
        grid_bar.setSpacing(10)
        self.btn_limpo = QPushButton('Limpo (24 cartas)')
        self.btn_sujo = QPushButton('Sujo (40 cartas)')
        for b in (self.btn_limpo, self.btn_sujo):
            b.setCheckable(True)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_limpo.clicked.connect(lambda: self._set_baralho(True))
        self.btn_sujo.clicked.connect(lambda: self._set_baralho(False))
        grid_bar.addWidget(self.btn_limpo)
        grid_bar.addWidget(self.btn_sujo)
        p_layout.addLayout(grid_bar)

        p_layout.addSpacing(10)

        # Dificuldade
        lbl_diff = QLabel('DIFICULDADE')
        lbl_diff.setStyleSheet('color: #94a3b8; font-size: 11px; font-weight: 800;')
        p_layout.addWidget(lbl_diff)

        grid_diff = QHBoxLayout()
        grid_diff.setSpacing(10)
        self.btns_diff: list[tuple[QPushButton, str]] = []
        for nome, d in [('Fácil', Dificuldade.FACIL), ('Médio', Dificuldade.MEDIO), ('Difícil', Dificuldade.DIFICIL)]:
            btn = QPushButton(nome)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, val=d: self._set_dificuldade(val))
            grid_diff.addWidget(btn)
            self.btns_diff.append((btn, d))
        p_layout.addLayout(grid_diff)

        p_layout.addSpacing(24)

        btn_start = QPushButton('ENTRAR NA ARENA')
        btn_start.setObjectName('btn-gold')
        btn_start.setFixedHeight(52)
        btn_start.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_start.clicked.connect(self._iniciar_jogo)
        btn_start.setStyleSheet(
            'background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #fbbf24, stop:1 #d97706);'
            ' color: #000; font-weight: 800; font-size: 15px; border-radius: 16px; padding: 14px 24px;'
        )
        p_layout.addStretch()
        p_layout.addWidget(btn_start)

        self._atualizar_estilos_menu()
        layout.addWidget(panel)
        self.stack.addWidget(menu_widget)

    def _set_modalidade(self, m: int) -> None:
        self.modalidade = m
        if m == 3:
            self.limpo = False
        self._atualizar_estilos_menu()

    def _set_baralho(self, limpo: bool) -> None:
        if self.modalidade != 3:
            self.limpo = limpo
        self._atualizar_estilos_menu()

    def _set_dificuldade(self, d: str) -> None:
        self.dificuldade = d
        self._atualizar_estilos_menu()

    def _atualizar_estilos_menu(self) -> None:
        gold = 'background-color: #fbbf24; color: #000; font-weight: 800; border-radius: 10px; padding: 10px;'
        dark = 'background-color: #1e293b; color: #94a3b8; border-radius: 10px; padding: 10px;'

        for btn, m in self.btns_mod:
            btn.setChecked(m == self.modalidade)
            btn.setStyleSheet(gold if m == self.modalidade else dark)

        self.btn_limpo.setChecked(self.limpo)
        self.btn_sujo.setChecked(not self.limpo)
        self.btn_limpo.setEnabled(self.modalidade != 3)
        for b, act in [(self.btn_limpo, self.limpo), (self.btn_sujo, not self.limpo)]:
            b.setStyleSheet(gold if act else dark)

        for btn, d in self.btns_diff:
            btn.setChecked(d == self.dificuldade)
            btn.setStyleSheet(gold if d == self.dificuldade else dark)

    # ------------------------------------------------------------------
    # Arena de jogo
    # ------------------------------------------------------------------

    def _criar_tela_jogo(self) -> None:
        jogo_widget = QWidget()
        main_layout = QHBoxLayout(jogo_widget)
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(18)

        # Mesa central
        self.mesa_feltro = QFrame()
        self.mesa_feltro.setProperty('class', 'arena-canvas')
        m_layout = QVBoxLayout(self.mesa_feltro)
        m_layout.setContentsMargins(24, 20, 24, 20)

        # Norte
        self.container_norte = QHBoxLayout()
        self.container_norte.setAlignment(Qt.AlignmentFlag.AlignCenter)
        m_layout.addLayout(self.container_norte)

        # Centro
        centro_mid = QHBoxLayout()
        self.container_oeste = QVBoxLayout()
        self.container_oeste.setAlignment(Qt.AlignmentFlag.AlignCenter)
        centro_mid.addLayout(self.container_oeste)
        centro_mid.addStretch()

        centro_mesa_vbox = QVBoxLayout()
        centro_mesa_vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        centro_mesa_vbox.setSpacing(8)

        self.area_cartas_jogadas = QWidget()
        self.area_cartas_jogadas.setFixedHeight(168)
        self.layout_cartas_mesa = QHBoxLayout(self.area_cartas_jogadas)
        self.layout_cartas_mesa.setContentsMargins(0, 0, 0, 0)
        self.layout_cartas_mesa.setSpacing(4)
        self.layout_cartas_mesa.setAlignment(Qt.AlignmentFlag.AlignCenter)
        centro_mesa_vbox.addWidget(self.area_cartas_jogadas)

        v_box = QHBoxLayout()
        v_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v_box.setSpacing(6)
        lbl_v = QLabel('VIRA:')
        lbl_v.setStyleSheet('color: #64748b; font-size: 11px; font-weight: 800;')
        v_box.addWidget(lbl_v)
        self.vira_slot = QWidget()
        self.vira_layout = QHBoxLayout(self.vira_slot)
        self.vira_layout.setContentsMargins(0, 0, 0, 0)
        self.vira_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v_box.addWidget(self.vira_slot)
        centro_mesa_vbox.addLayout(v_box)
        centro_mid.addLayout(centro_mesa_vbox)
        centro_mid.addStretch()

        self.container_leste = QVBoxLayout()
        self.container_leste.setAlignment(Qt.AlignmentFlag.AlignCenter)
        centro_mid.addLayout(self.container_leste)
        m_layout.addLayout(centro_mid)
        m_layout.addStretch()

        # Sul — cartas do humano + botão truco
        sul_box = QHBoxLayout()
        sul_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout_leque_humano = QHBoxLayout()
        self.layout_leque_humano.setSpacing(-24)
        sul_box.addLayout(self.layout_leque_humano)
        sul_box.addSpacing(20)

        self.btn_truco = QPushButton('TRUCO!')
        self.btn_truco.setObjectName('btn-gold')
        self.btn_truco.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_truco.setFixedSize(140, 50)
        self.btn_truco.clicked.connect(self._pedir_truco)
        sul_box.addWidget(self.btn_truco)
        m_layout.addLayout(sul_box)

        main_layout.addWidget(self.mesa_feltro, stretch=3)

        # Sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(280)
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(0, 0, 0, 0)
        side_layout.setSpacing(16)

        hud_score = QFrame()
        hud_score.setObjectName('hud-side-container')
        score_vlayout = QVBoxLayout(hud_score)
        score_vlayout.setContentsMargins(18, 18, 18, 18)
        score_vlayout.setSpacing(14)

        info_box = QHBoxLayout()
        info_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_dot = QLabel('●')
        lbl_dot.setStyleSheet('color: #fbbf24; font-size: 10px;')
        self.lbl_mao_info = QLabel('MÃO 1  •  VALE 1 PTS')
        self.lbl_mao_info.setStyleSheet('color: #e2e8f0; font-weight: 800; font-size: 12px;')
        info_box.addWidget(lbl_dot)
        info_box.addSpacing(6)
        info_box.addWidget(self.lbl_mao_info)
        score_vlayout.addLayout(info_box)

        scores_container = QHBoxLayout()
        scores_container.setSpacing(10)

        eq0_box = QVBoxLayout()
        eq0_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_e0 = QLabel('SUA EQUIPE')
        lbl_e0.setStyleSheet('color: #94a3b8; font-size: 10px; font-weight: 800;')
        self.lbl_score_eq0 = QLabel('0')
        self.lbl_score_eq0.setStyleSheet('color: #fbbf24; font-size: 36px; font-weight: 900;')
        eq0_box.addWidget(lbl_e0, 0, Qt.AlignmentFlag.AlignCenter)
        eq0_box.addWidget(self.lbl_score_eq0, 0, Qt.AlignmentFlag.AlignCenter)

        lbl_div = QLabel('─')
        lbl_div.setStyleSheet('color: rgba(255, 255, 255, 0.15); font-size: 16px;')

        eq1_box = QVBoxLayout()
        eq1_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_e1 = QLabel('ADVERSÁRIOS')
        lbl_e1.setStyleSheet('color: #94a3b8; font-size: 10px; font-weight: 800;')
        self.lbl_score_eq1 = QLabel('0')
        self.lbl_score_eq1.setStyleSheet('color: #f8fafc; font-size: 36px; font-weight: 900;')
        eq1_box.addWidget(lbl_e1, 0, Qt.AlignmentFlag.AlignCenter)
        eq1_box.addWidget(self.lbl_score_eq1, 0, Qt.AlignmentFlag.AlignCenter)

        scores_container.addLayout(eq0_box)
        scores_container.addWidget(lbl_div, 0, Qt.AlignmentFlag.AlignCenter)
        scores_container.addLayout(eq1_box)
        score_vlayout.addLayout(scores_container)

        # Vazas ganhas na mão atual (menor, abaixo do placar geral)
        vazas_box = QHBoxLayout()
        vazas_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vazas_box.setSpacing(8)

        lbl_vazas_sep = QLabel('─')
        lbl_vazas_sep.setStyleSheet('color: rgba(255, 255, 255, 0.1); font-size: 10px;')
        vazas_box.addWidget(lbl_vazas_sep, 0, Qt.AlignmentFlag.AlignCenter)

        lbl_vazas_label = QLabel('VAZAS')
        lbl_vazas_label.setStyleSheet('color: #64748b; font-size: 9px; font-weight: 700;')
        vazas_box.addWidget(lbl_vazas_label, 0, Qt.AlignmentFlag.AlignCenter)

        self.lbl_vazas_eq0 = QLabel('0')
        self.lbl_vazas_eq0.setStyleSheet('color: #fbbf24; font-size: 14px; font-weight: 900;')
        vazas_box.addWidget(self.lbl_vazas_eq0, 0, Qt.AlignmentFlag.AlignCenter)

        lbl_vazas_dash = QLabel('─')
        lbl_vazas_dash.setStyleSheet('color: rgba(255, 255, 255, 0.2); font-size: 12px;')
        vazas_box.addWidget(lbl_vazas_dash, 0, Qt.AlignmentFlag.AlignCenter)

        self.lbl_vazas_eq1 = QLabel('0')
        self.lbl_vazas_eq1.setStyleSheet('color: #f8fafc; font-size: 14px; font-weight: 900;')
        vazas_box.addWidget(self.lbl_vazas_eq1, 0, Qt.AlignmentFlag.AlignCenter)

        vazas_box.addWidget(lbl_vazas_sep, 0, Qt.AlignmentFlag.AlignCenter)
        score_vlayout.addLayout(vazas_box)

        btn_menu = QPushButton('SAIR DA ARENA')
        btn_menu.setObjectName('btn-dark')
        btn_menu.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_menu.clicked.connect(self._voltar_menu)
        score_vlayout.addWidget(btn_menu)
        side_layout.addWidget(hud_score)

        lbl_log_title = QLabel('ACONTECIMENTOS')
        lbl_log_title.setStyleSheet('color: #fbbf24; font-size: 11px; font-weight: 800; padding-left: 4px;')
        side_layout.addWidget(lbl_log_title)

        self.log_list = QListWidget()
        self.log_list.setObjectName('hud-ticker')
        self.log_list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        side_layout.addWidget(self.log_list)

        main_layout.addWidget(sidebar, stretch=1)
        self.stack.addWidget(jogo_widget)

    # ------------------------------------------------------------------
    # Lógica
    # ------------------------------------------------------------------

    def _iniciar_jogo(self) -> None:
        self.sessao = Sessao(
            modalidade=self.modalidade,
            limpo=self.limpo,
            dificuldade=self.dificuldade,
            seed=self.seed,
        )
        self.stack.setCurrentIndex(1)
        self.timer_bot.start()
        self._atualizar_interface()

    def _voltar_menu(self) -> None:
        self.timer_bot.stop()
        self.sessao = None
        self.stack.setCurrentIndex(0)

    def _loop_bot(self) -> None:
        if not self.sessao:
            return
        p = self.sessao.partida

        if p.estado == EstadoPartida.PEDIDO_PENDENTE and p.pedido_pendente and p.pedido_pendente[0] == 1:
            self._tratar_pedido_pendente()
            return
        if p.mao_de_onze == 0:
            self._tratar_mao_de_onze()
            return
        if p.estado == EstadoPartida.AGUARDANDO:
            self._tratar_mao_encerrada()
            return
        if p.estado == EstadoPartida.ENCERRADA:
            self._tratar_fim_jogo()
            return

        if self.sessao.avancar_bot():
            self._atualizar_interface()

    def _criar_widget_bot(self, bot) -> QWidget:
        p = self.sessao.partida
        b_box = QVBoxLayout()
        b_box.setAlignment(Qt.AlignmentFlag.AlignCenter)

        is_vez = p.jogador_da_vez is bot
        is_parceiro = bot in p.equipes[0].jogadores

        lbl_avatar = QLabel(bot.nome[0].upper())
        lbl_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_avatar.setFixedSize(38, 38)
        bg_col = '#fbbf24' if is_vez else ('#10b981' if is_parceiro else '#1e293b')
        lbl_avatar.setStyleSheet(
            f'background-color: {bg_col}; color: #000; font-weight: 900; border-radius: 19px;'
        )
        b_box.addWidget(lbl_avatar)

        lbl_name = QLabel(f'{bot.nome}{" (Parceiro)" if is_parceiro else ""}')
        lbl_name.setStyleSheet(
            'color: #fbbf24; font-size: 10px; font-weight: 800;'
            if is_parceiro
            else 'color: #94a3b8; font-size: 10px;'
        )
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
        return w_bot

    def _limpar_layout(self, layout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _atualizar_interface(self) -> None:
        if not self.sessao:
            return
        p = self.sessao.partida
        humano = self.sessao.humano

        self.lbl_score_eq0.setText(str(p.pontos[0]))
        self.lbl_score_eq1.setText(str(p.pontos[1]))
        self.lbl_mao_info.setText(f'MÃO {p.mao_numero}  •  VALE {p.valor_mao} PTS')

        # Contar vazas ganhas por equipe na mão atual
        vazas_eq0 = sum(1 for r in p.resultados if r.equipe_vencedora == 0)
        vazas_eq1 = sum(1 for r in p.resultados if r.equipe_vencedora == 1)
        self.lbl_vazas_eq0.setText(str(vazas_eq0))
        self.lbl_vazas_eq1.setText(str(vazas_eq1))

        self.log_list.clear()
        for ev in self.sessao.eventos[-15:]:
            self.log_list.addItem(ev.mensagem)
        self.log_list.scrollToBottom()

        # Vira
        self._limpar_layout(self.vira_layout)
        if p.vira:
            self.vira_layout.addWidget(CardWidget(carta=p.vira, width=68, height=98))

        # Cartas na mesa
        self._limpar_layout(self.layout_cartas_mesa)
        if p.jogadas_atuais:
            maior_forca = max(j.carta.forca for j in p.jogadas_atuais)
            for j in p.jogadas_atuais:
                box_j = QVBoxLayout()
                box_j.setAlignment(Qt.AlignmentFlag.AlignCenter)
                is_maior = j.carta.forca == maior_forca
                card_w = CardWidget(carta=j.carta, width=80, height=116)
                box_j.addWidget(card_w)
                lbl_n = QLabel(f'{j.jogador.nome} {"★" if is_maior else ""}')
                lbl_n.setStyleSheet(
                    'color: #fbbf24; font-size: 11px; font-weight: 800;'
                    if is_maior
                    else 'color: #94a3b8; font-size: 11px;'
                )
                box_j.addWidget(lbl_n)
                w_item = QWidget()
                w_item.setLayout(box_j)
                self.layout_cartas_mesa.addWidget(w_item)

        # Posicionamento dos bots
        for layout_c in (self.container_norte, self.container_oeste, self.container_leste):
            self._limpar_layout(layout_c)

        num_jogadores = len(p.jogadores)
        idx_humano = p.jogadores.index(humano)

        if num_jogadores == 2:
            adv = p.jogadores[(idx_humano + 1) % 2]
            self.container_norte.addWidget(self._criar_widget_bot(adv))
        elif num_jogadores == 4:
            adv_leste = p.jogadores[(idx_humano + 1) % 4]
            parc_norte = p.jogadores[(idx_humano + 2) % 4]
            adv_oeste = p.jogadores[(idx_humano + 3) % 4]
            self.container_leste.addWidget(self._criar_widget_bot(adv_leste))
            self.container_norte.addWidget(self._criar_widget_bot(parc_norte))
            self.container_oeste.addWidget(self._criar_widget_bot(adv_oeste))
        elif num_jogadores == 6:
            adv1 = p.jogadores[(idx_humano + 1) % 6]
            parc1 = p.jogadores[(idx_humano + 2) % 6]
            adv2 = p.jogadores[(idx_humano + 3) % 6]
            parc2 = p.jogadores[(idx_humano + 4) % 6]
            adv3 = p.jogadores[(idx_humano + 5) % 6]
            self.container_leste.addWidget(self._criar_widget_bot(adv1))
            w_norte = QWidget()
            h_norte = QHBoxLayout(w_norte)
            h_norte.setSpacing(16)
            h_norte.addWidget(self._criar_widget_bot(parc1))
            h_norte.addWidget(self._criar_widget_bot(adv2))
            h_norte.addWidget(self._criar_widget_bot(parc2))
            self.container_norte.addWidget(w_norte)
            self.container_oeste.addWidget(self._criar_widget_bot(adv3))

        # Leque do humano
        self._limpar_layout(self.layout_leque_humano)
        pode_jogar = self.sessao.precisa_humano
        num_cartas = len(humano.cartas)
        angles = [-8.0, 0.0, 8.0] if num_cartas == 3 else ([-5.0, 5.0] if num_cartas == 2 else [0.0])

        for idx, carta in enumerate(humano.cartas):
            ang = angles[idx] if idx < len(angles) else 0.0
            cb = (lambda i=idx: self._jogar_carta_humano(i)) if pode_jogar else None
            cw = CardWidget(carta=carta, width=94, height=136, angle=ang, callback=cb)
            self.layout_leque_humano.addWidget(cw)

        # Botão truco
        pode_trucar = self.sessao.pode_trucar()
        self.btn_truco.setEnabled(pode_trucar)
        self.btn_truco.setText(
            'TRUCO!' if p.valor_mao == 1
            else {3: 'SEIS!', 6: 'NOVE!', 9: 'DOZE!'}.get(p.valor_mao, 'AUMENTAR!')
        )

    def _jogar_carta_humano(self, idx: int) -> None:
        try:
            self.sessao.jogar(idx)
            self._atualizar_interface()
        except ValueError:
            pass

    def _pedir_truco(self) -> None:
        try:
            self.sessao.pedir_truco()
            self._atualizar_interface()
        except ValueError:
            pass

    # ------------------------------------------------------------------
    # Diálogos
    # ------------------------------------------------------------------

    def _tratar_pedido_pendente(self) -> None:
        self.timer_bot.stop()
        p = self.sessao.partida
        solicitante, valor = p.pedido_pendente

        opcoes = [
            ('ACEITAR', lambda: self.sessao.responder(True), True),
            ('CORRER', lambda: self.sessao.responder(False), False),
        ]
        if valor < 12:
            opcoes.append(('AUMENTAR', lambda: self.sessao.aumentar(), False))

        dlg = DialogoCustom(
            f'PEDIRAM {valor} PONTOS!',
            'Decida a jogada da sua equipe:',
            opcoes,
            parent=self,
        )
        dlg.exec()
        self.timer_bot.start()
        self._atualizar_interface()

    def _tratar_mao_de_onze(self) -> None:
        self.timer_bot.stop()
        dlg = DialogoCustom(
            'MÃO DE ONZE',
            'Desejam jogar esta mão valendo 3 pontos?',
            [
                ('JOGAR MÃO', lambda: self.sessao.decidir_onze(True), True),
                ('CORRER', lambda: self.sessao.decidir_onze(False), False),
            ],
            parent=self,
        )
        dlg.exec()
        self.timer_bot.start()
        self._atualizar_interface()

    def _tratar_mao_encerrada(self) -> None:
        self.timer_bot.stop()
        p = self.sessao.partida

        score_w = QWidget()
        sl = QHBoxLayout(score_w)
        sl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sl.setSpacing(16)

        for e_idx, (nome, pts) in enumerate([
            ('SUA EQUIPE', p.pontos[0]),
            ('ADVERSÁRIOS', p.pontos[1]),
        ]):
            box = QFrame()
            box.setStyleSheet('background-color: #1e293b; border-radius: 14px;')
            bl = QVBoxLayout(box)
            bl.setContentsMargins(16, 10, 16, 10)
            lbl_t = QLabel(nome)
            lbl_t.setStyleSheet('color: #94a3b8; font-size: 11px; font-weight: 800;')
            lbl_v = QLabel(str(pts))
            lbl_v.setStyleSheet(
                'color: #fbbf24; font-size: 34px; font-weight: 900;'
                if e_idx == 0
                else 'color: #f8fafc; font-size: 34px; font-weight: 900;'
            )
            bl.addWidget(lbl_t, 0, Qt.AlignmentFlag.AlignCenter)
            bl.addWidget(lbl_v, 0, Qt.AlignmentFlag.AlignCenter)
            sl.addWidget(box)

        dlg = DialogoCustom(
            'MÃO ENCERRADA',
            'Placar atual:',
            [('PRÓXIMA MÃO', lambda: self.sessao.proxima_mao(), True)],
            widget_extra=score_w,
            parent=self,
        )
        dlg.exec()
        self.timer_bot.start()
        self._atualizar_interface()

    def _tratar_fim_jogo(self) -> None:
        self.timer_bot.stop()
        p = self.sessao.partida
        venceu = p.vencedor == 0

        dlg = DialogoCustom(
            '🏆 VITÓRIA!' if venceu else 'FIM DE JOGO',
            'Sua equipe venceu a partida!' if venceu else 'Os adversários venceram.',
            [('NOVA PARTIDA', self._voltar_menu, True)],
            parent=self,
        )
        dlg.exec()

    def executar(self) -> None:
        self.show()


def main() -> None:
    app = QApplication(sys.argv)
    tela = TelaTrucoPyQt()
    tela.executar()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

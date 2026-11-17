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
QSS_FILE = Path(__file__).resolve().parent / 'estilos.qss'


def _carregar_estilos() -> str:
    """Carrega todos os estilos do arquivo QSS centralizado."""
    if QSS_FILE.exists():
        return QSS_FILE.read_text(encoding='utf-8')
    return ''


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
        panel.setObjectName('panel')

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 230))
        shadow.setYOffset(10)
        panel.setGraphicsEffect(shadow)

        p_layout = QVBoxLayout(panel)
        p_layout.setContentsMargins(28, 28, 28, 28)
        p_layout.setSpacing(14)

        lbl_title = QLabel(titulo)
        lbl_title.setObjectName('lbl_title')
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        p_layout.addWidget(lbl_title)

        if mensagem:
            lbl_msg = QLabel(mensagem)
            lbl_msg.setObjectName('lbl_msg')
            lbl_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_msg.setWordWrap(True)
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
                btn.setObjectName('btn-destaque')
            else:
                btn.setObjectName('btn-secundario')
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
        dificuldade: Dificuldade = Dificuldade.MEDIO,
        seed: int | None = None,
    ) -> None:
        super().__init__()
        self.setWindowTitle('TRUCO PAULISTA')
        self.resize(1280, 820)
        self.setMinimumSize(1024, 700)
        self.setStyleSheet(_carregar_estilos())

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
        panel.setObjectName('menu-panel')
        panel.setFixedSize(480, 500)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(36)
        shadow.setColor(QColor(0, 0, 0, 200))
        shadow.setYOffset(10)
        panel.setGraphicsEffect(shadow)

        p_layout = QVBoxLayout(panel)
        p_layout.setContentsMargins(36, 36, 36, 36)

        lbl_logo = QLabel('TRUCO PAULISTA')
        lbl_logo.setObjectName('lbl_logo')
        lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_logo.setAutoFillBackground(False)
        p_layout.addWidget(lbl_logo)

        lbl_sub = QLabel('Versão 5 — Arquitetura Modular')
        lbl_sub.setObjectName('lbl_sub')
        lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_sub.setAutoFillBackground(False)
        p_layout.addWidget(lbl_sub)

        # Modalidade
        lbl_mod = QLabel('MODALIDADE')
        lbl_mod.setObjectName('lbl_mod')
        lbl_mod.setAutoFillBackground(False)
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
        lbl_bar.setObjectName('lbl_bar')
        lbl_bar.setAutoFillBackground(False)
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
        lbl_diff.setObjectName('lbl_diff')
        lbl_diff.setAutoFillBackground(False)
        p_layout.addWidget(lbl_diff)

        grid_diff = QHBoxLayout()
        grid_diff.setSpacing(10)
        self.btns_diff: list[tuple[QPushButton, Dificuldade]] = []
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
        btn_start.setObjectName('btn_start')
        btn_start.setFixedHeight(52)
        btn_start.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_start.clicked.connect(self._iniciar_jogo)
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

    def _set_dificuldade(self, d: Dificuldade) -> None:
        self.dificuldade = d
        self._atualizar_estilos_menu()

    def _atualizar_estilos_menu(self) -> None:
        for btn, m in self.btns_mod:
            btn.setChecked(m == self.modalidade)
            btn.setProperty('menu-state', 'selected' if m == self.modalidade else 'unselected')
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        self.btn_limpo.setChecked(self.limpo)
        self.btn_sujo.setChecked(not self.limpo)
        self.btn_limpo.setEnabled(self.modalidade != 3)
        for b, act in [(self.btn_limpo, self.limpo), (self.btn_sujo, not self.limpo)]:
            b.setProperty('menu-state', 'selected' if act else 'unselected')
            b.style().unpolish(b)
            b.style().polish(b)

        for btn, d in self.btns_diff:
            btn.setChecked(d == self.dificuldade)
            btn.setProperty('menu-state', 'selected' if d == self.dificuldade else 'unselected')
            btn.style().unpolish(btn)
            btn.style().polish(btn)

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
        lbl_v.setObjectName('lbl_v')
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
        side_layout.setSpacing(24)

        hud_score = QFrame()
        hud_score.setObjectName('hud-side-container')
        score_vlayout = QVBoxLayout(hud_score)
        score_vlayout.setContentsMargins(28, 28, 28, 28)
        score_vlayout.setSpacing(20)

        # Título de pontuação geral
        lbl_pontuacao_geral = QLabel('PONTUAÇÃO GERAL')
        lbl_pontuacao_geral.setObjectName('lbl_pontuacao_geral')
        lbl_pontuacao_geral.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_pontuacao_geral.setAutoFillBackground(False)
        score_vlayout.addWidget(lbl_pontuacao_geral)
        score_vlayout.addSpacing(10)

        # Placar: Sua equipe X Adversários
        scores_container = QHBoxLayout()
        scores_container.setSpacing(10)

        eq0_box = QVBoxLayout()
        eq0_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_e0 = QLabel('SUA EQUIPE')
        lbl_e0.setObjectName('lbl_e0')
        lbl_e0.setAutoFillBackground(False)
        self.lbl_score_eq0 = QLabel('0')
        self.lbl_score_eq0.setObjectName('lbl_score_eq0')
        self.lbl_score_eq0.setAutoFillBackground(False)
        eq0_box.addWidget(lbl_e0, 0, Qt.AlignmentFlag.AlignCenter)
        eq0_box.addWidget(self.lbl_score_eq0, 0, Qt.AlignmentFlag.AlignCenter)

        lbl_div = QLabel('×')
        lbl_div.setObjectName('lbl_div')
        lbl_div.setAutoFillBackground(False)

        eq1_box = QVBoxLayout()
        eq1_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_e1 = QLabel('ADVERSÁRIOS')
        lbl_e1.setObjectName('lbl_e1')
        lbl_e1.setAutoFillBackground(False)
        self.lbl_score_eq1 = QLabel('0')
        self.lbl_score_eq1.setObjectName('lbl_score_eq1')
        self.lbl_score_eq1.setAutoFillBackground(False)
        eq1_box.addWidget(lbl_e1, 0, Qt.AlignmentFlag.AlignCenter)
        eq1_box.addWidget(self.lbl_score_eq1, 0, Qt.AlignmentFlag.AlignCenter)

        scores_container.addLayout(eq0_box)
        scores_container.addWidget(lbl_div, 0, Qt.AlignmentFlag.AlignCenter)
        scores_container.addLayout(eq1_box)
        score_vlayout.addLayout(scores_container)
        score_vlayout.addSpacing(12)

        # Separador
        separator = QFrame()
        separator.setObjectName('separator')
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        score_vlayout.addWidget(separator)
        score_vlayout.addSpacing(2)

        # Componente do placar da mão
        mao_frame = QFrame()
        mao_layout = QVBoxLayout(mao_frame)
        mao_layout.setContentsMargins(12, 12, 12, 12)
        mao_layout.setSpacing(8)

        self.lbl_mao_info = QLabel('MÃO 1  •  VALE 1 PTS')
        self.lbl_mao_info.setObjectName('lbl_mao_info')
        self.lbl_mao_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_mao_info.setAutoFillBackground(False)
        mao_layout.addWidget(self.lbl_mao_info)
        mao_layout.addSpacing(4)

        # Vazas da mão
        vazas_row = QHBoxLayout()
        vazas_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vazas_row.setSpacing(10)

        lbl_vazas_label = QLabel('VAZAS')
        lbl_vazas_label.setObjectName('lbl_vazas_label')
        lbl_vazas_label.setAutoFillBackground(False)
        vazas_row.addWidget(lbl_vazas_label, 0, Qt.AlignmentFlag.AlignCenter)

        vazas_sep1 = QLabel('─')
        vazas_sep1.setObjectName('vazas_sep1')
        vazas_sep1.setAutoFillBackground(False)
        vazas_row.addWidget(vazas_sep1, 0, Qt.AlignmentFlag.AlignCenter)

        self.lbl_vazas_eq0 = QLabel('0')
        self.lbl_vazas_eq0.setObjectName('lbl_vazas_eq0')
        self.lbl_vazas_eq0.setAutoFillBackground(False)
        vazas_row.addWidget(self.lbl_vazas_eq0, 0, Qt.AlignmentFlag.AlignCenter)

        lbl_vazas_dash = QLabel('─')
        lbl_vazas_dash.setObjectName('lbl_vazas_dash')
        lbl_vazas_dash.setAutoFillBackground(False)
        vazas_row.addWidget(lbl_vazas_dash, 0, Qt.AlignmentFlag.AlignCenter)

        self.lbl_vazas_eq1 = QLabel('0')
        self.lbl_vazas_eq1.setObjectName('lbl_vazas_eq1')
        self.lbl_vazas_eq1.setAutoFillBackground(False)
        vazas_row.addWidget(self.lbl_vazas_eq1, 0, Qt.AlignmentFlag.AlignCenter)

        vazas_sep2 = QLabel('─')
        vazas_sep2.setObjectName('vazas_sep2')
        vazas_sep2.setAutoFillBackground(False)
        vazas_row.addWidget(vazas_sep2, 0, Qt.AlignmentFlag.AlignCenter)

        mao_layout.addLayout(vazas_row)
        score_vlayout.addWidget(mao_frame)

        btn_menu = QPushButton('SAIR DA ARENA')
        btn_menu.setObjectName('btn-dark')
        btn_menu.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_menu.clicked.connect(self._voltar_menu)
        score_vlayout.addWidget(btn_menu)
        side_layout.addWidget(hud_score)

        lbl_log_title = QLabel('ACONTECIMENTOS')
        lbl_log_title.setObjectName('lbl_log_title')
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
        if is_vez:
            lbl_avatar.setObjectName('avatar-vez')
        elif is_parceiro:
            lbl_avatar.setObjectName('avatar-parceiro')
        else:
            lbl_avatar.setObjectName('avatar-adversario')
        b_box.addWidget(lbl_avatar)

        lbl_name = QLabel(f'{bot.nome}{" (Parceiro)" if is_parceiro else ""}')
        if is_parceiro:
            lbl_name.setObjectName('nome-parceiro')
        else:
            lbl_name.setObjectName('nome-adversario')
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
                if is_maior:
                    lbl_n.setObjectName('lbl_carta-maior')
                else:
                    lbl_n.setObjectName('lbl_carta-menor')
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
            box.setObjectName('score-box')
            bl = QVBoxLayout(box)
            bl.setContentsMargins(16, 10, 16, 10)
            lbl_t = QLabel(nome)
            lbl_t.setObjectName('score-nome')
            lbl_v = QLabel(str(pts))
            if e_idx == 0:
                lbl_v.setObjectName('score-valor-0')
            else:
                lbl_v.setObjectName('score-valor-1')
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

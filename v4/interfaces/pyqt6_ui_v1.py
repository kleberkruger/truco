"""Interface de apresentação em PyQt6: Design Ultra Moderno, Borderless (Sem Bordas), Responsivo e Flat."""
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
    QGraphicsDropShadowEffect, QSizePolicy
)

from aplicacao.sessao import Sessao
from dominio.truco import Estado

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"

# Tema CSS 100% Borderless, Minimalista e Moderno
QSS_THEME = """
QMainWindow {
    background-color: #0a0b0e;
}

/* Painéis de Camada Sem Nenhuma Borda */
QFrame, QWidget {
    border: none;
}

QFrame.glass-panel {
    background-color: #14161e;
    border-radius: 20px;
}

QFrame.table-felt {
    background: qradialgradient(cx:0.5, cy:0.5, radius:0.75, fx:0.5, fy:0.5, stop:0 #0f3d30, stop:0.65 #09261e, stop:1 #04120e);
    border-radius: 40px;
}

QLabel {
    color: #f3f4f6;
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, sans-serif;
    border: none;
}

/* Estilo Global de Botões sem Bordas */
QPushButton {
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif;
    border: none;
    outline: none;
}

QPushButton#btn-gold, QPushButton.btn-gold {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #fbbf24, stop:1 #f59e0b);
    color: #000000;
    font-weight: 800;
    font-size: 15px;
    border-radius: 14px;
    padding: 12px 24px;
}

QPushButton#btn-gold:hover, QPushButton.btn-gold:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #fcd34d, stop:1 #fbbf24);
}

QPushButton#btn-gold:disabled, QPushButton.btn-gold:disabled {
    background-color: #232733;
    color: #4b5563;
}

QPushButton#btn-dark, QPushButton.btn-dark {
    background-color: #232733;
    color: #f3f4f6;
    font-weight: 700;
    font-size: 14px;
    border-radius: 12px;
    padding: 10px 20px;
}

QPushButton#btn-dark:hover, QPushButton.btn-dark:hover {
    background-color: #2f3444;
    color: #ffffff;
}

QListWidget {
    background-color: #101218;
    border: none;
    border-radius: 14px;
    color: #9ca3af;
    padding: 8px;
    font-size: 13px;
}

QListWidget::item {
    padding: 8px 6px;
    border: none;
    border-bottom: 1px solid #191c26;
}
"""


class CardWidget(QWidget):
    """Carta estilo baralho real com corte vetorial sem bordas duras e sombra realista."""

    def __init__(self, carta=None, verso=False, width=92, height=136, parent=None, callback=None):
        super().__init__(parent)
        self.carta = carta
        self.verso = verso
        self.card_width = width
        self.card_height = height
        self.callback = callback
        self.hovered = False

        self.setFixedSize(width, height + 16)
        self.setCursor(Qt.CursorShape.PointingHandCursor if (callback and not verso) else Qt.CursorShape.ArrowCursor)

        # Sombra de Projeção Suave em vez de Borda
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(18)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setYOffset(6)
        shadow.setXOffset(0)
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

        y_offset = 0 if self.hovered else 14
        card_rect = QRectF(0, y_offset, self.card_width, self.card_height)

        pixmap = self._obter_pixmap_asset()
        if pixmap:
            painter.drawPixmap(int(card_rect.x()), int(card_rect.y()), pixmap)
            return

        if self.verso or not self.carta:
            self._draw_traditional_back(painter, card_rect)
        else:
            self._draw_traditional_front(painter, card_rect)

    def _draw_traditional_back(self, painter: QPainter, rect: QRectF):
        """Verso de Baralho Clássico em Grafite/Carvão sem bordas externas."""
        path = QPainterPath()
        path.addRoundedRect(rect, 8, 8)

        # Fundo Branco da Carta
        painter.fillPath(path, QBrush(QColor("#ffffff")))
        
        # Bloco Interno Dark
        inner_rect = rect.adjusted(4, 4, -4, -4)
        inner_path = QPainterPath()
        inner_path.addRoundedRect(inner_rect, 6, 6)

        gradient = QLinearGradient(inner_rect.topLeft(), inner_rect.bottomRight())
        gradient.setColorAt(0, QColor("#222634"))
        gradient.setColorAt(1, QColor("#141620"))
        painter.fillPath(inner_path, QBrush(gradient))

        # Detalhe Central
        painter.setPen(QPen(QColor(251, 191, 36, 70), 1))
        c = inner_rect.center()
        painter.drawEllipse(c, 14, 22)

    def _draw_traditional_front(self, painter: QPainter, rect: QRectF):
        """Frente de Carta Tradicional limpa e nítida sem linhas de contorno."""
        naipe_symbol = str(self.carta.naipe.value)
        rank_str = str(self.carta.rank.value)
        is_red = naipe_symbol in ("♦", "♥")

        color_code = "#dc2626" if is_red else "#111827"
        card_color = QColor(color_code)

        path = QPainterPath()
        path.addRoundedRect(rect, 8, 8)
        painter.fillPath(path, QBrush(QColor("#ffffff")))

        font_rank = QFont("Georgia", int(self.card_height * 0.14), QFont.Weight.Bold)
        font_suit = QFont("Arial", int(self.card_height * 0.12))

        painter.setPen(card_color)

        # Top-Left
        painter.setFont(font_rank)
        painter.drawText(int(rect.x() + 6), int(rect.y() + font_rank.pointSize() + 4), rank_str)
        painter.setFont(font_suit)
        painter.drawText(int(rect.x() + 6), int(rect.y() + font_rank.pointSize() + font_suit.pointSize() + 6), naipe_symbol)

        # Bottom-Right Invertido
        painter.save()
        painter.translate(rect.right() - 6, rect.bottom() - 6)
        painter.rotate(180)
        painter.setFont(font_rank)
        painter.drawText(0, font_rank.pointSize(), rank_str)
        painter.setFont(font_suit)
        painter.drawText(0, font_rank.pointSize() + font_suit.pointSize() + 2, naipe_symbol)
        painter.restore()

        # Centro
        self._draw_center_pips(painter, rect, rank_str, naipe_symbol, card_color)

        # Badge de Manilha
        if self.carta.manilha:
            painter.setFont(QFont("Arial", 8, QFont.Weight.Bold))
            badge_rect = QRectF(rect.right() - 20, rect.top() + 4, 16, 16)
            painter.setBrush(QBrush(QColor("#f59e0b")))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(badge_rect)
            painter.setPen(QColor("#000000"))
            painter.drawText(badge_rect, Qt.AlignmentFlag.AlignCenter, "M")

    def _draw_center_pips(self, painter: QPainter, rect: QRectF, rank: str, suit: str, color: QColor):
        center_area = rect.adjusted(22, 22, -22, -22)
        cx = center_area.center().x()
        cy = center_area.center().y()
        w = center_area.width()
        h = center_area.height()

        font_pip = QFont("Arial", int(self.card_height * 0.18))
        font_large = QFont("Arial", int(self.card_height * 0.38))
        font_court = QFont("Georgia", int(self.card_height * 0.32), QFont.Weight.Bold)

        painter.setPen(color)

        if rank == "A":
            painter.setFont(font_large)
            painter.drawText(center_area, Qt.AlignmentFlag.AlignCenter, suit)
            return

        if rank in ("K", "Q", "J"):
            painter.setFont(font_court)
            painter.drawText(center_area, Qt.AlignmentFlag.AlignCenter, rank)
            return

        painter.setFont(font_pip)
        points = []

        if rank == "2":
            points = [(cx, cy - h * 0.3), (cx, cy + h * 0.3)]
        elif rank == "3":
            points = [(cx, cy - h * 0.35), (cx, cy), (cx, cy + h * 0.35)]
        elif rank == "4":
            points = [
                (cx - w * 0.3, cy - h * 0.3), (cx + w * 0.3, cy - h * 0.3),
                (cx - w * 0.3, cy + h * 0.3), (cx + w * 0.3, cy + h * 0.3)
            ]
        elif rank == "5":
            points = [
                (cx - w * 0.3, cy - h * 0.3), (cx + w * 0.3, cy - h * 0.3),
                (cx, cy),
                (cx - w * 0.3, cy + h * 0.3), (cx + w * 0.3, cy + h * 0.3)
            ]
        elif rank == "6":
            points = [
                (cx - w * 0.3, cy - h * 0.35), (cx + w * 0.3, cy - h * 0.35),
                (cx - w * 0.3, cy), (cx + w * 0.3, cy),
                (cx - w * 0.3, cy + h * 0.35), (cx + w * 0.3, cy + h * 0.35)
            ]
        elif rank == "7":
            points = [
                (cx - w * 0.3, cy - h * 0.35), (cx + w * 0.3, cy - h * 0.35),
                (cx, cy - h * 0.15),
                (cx - w * 0.3, cy), (cx + w * 0.3, cy),
                (cx - w * 0.3, cy + h * 0.35), (cx + w * 0.3, cy + h * 0.35)
            ]
        else:
            points = [(cx, cy)]

        for px, py in points:
            pip_rect = QRectF(px - 10, py - 10, 20, 20)
            painter.drawText(pip_rect, Qt.AlignmentFlag.AlignCenter, suit)


class DialogoCustom(QDialog):
    """Modal sem bordas, com sombra flutuante e botões de alta visibilidade."""

    def __init__(
        self,
        titulo: str,
        mensagem: str,
        opcoes: list[tuple[str, callable, bool]],
        widget_extra: QWidget | None = None,
        parent=None
    ):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(440)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        panel = QFrame()
        panel.setStyleSheet("background-color: #1a1d26; border-radius: 24px;")

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(36)
        shadow.setColor(QColor(0, 0, 0, 220))
        shadow.setYOffset(10)
        panel.setGraphicsEffect(shadow)

        p_layout = QVBoxLayout(panel)
        p_layout.setContentsMargins(28, 28, 28, 28)
        p_layout.setSpacing(16)

        lbl_title = QLabel(titulo)
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_title.setStyleSheet("color: #f59e0b; font-size: 22px; font-weight: 800; letter-spacing: 0.5px;")
        p_layout.addWidget(lbl_title)

        if mensagem:
            lbl_msg = QLabel(mensagem)
            lbl_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_msg.setWordWrap(True)
            lbl_msg.setStyleSheet("color: #9ca3af; font-size: 14px; line-height: 1.4;")
            p_layout.addWidget(lbl_msg)

        if widget_extra:
            p_layout.addWidget(widget_extra)

        p_layout.addSpacing(6)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        for texto, action, destaque in opcoes:
            btn = QPushButton(texto)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(48)

            if destaque:
                btn.setStyleSheet(
                    "QPushButton {"
                    "   background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #fbbf24, stop:1 #f59e0b);"
                    "   color: #000000;"
                    "   font-weight: 800;"
                    "   font-size: 15px;"
                    "   border-radius: 14px;"
                    "   border: none;"
                    "   padding: 0 20px;"
                    "}"
                    "QPushButton:hover {"
                    "   background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #fcd34d, stop:1 #fbbf24);"
                    "}"
                )
            else:
                btn.setStyleSheet(
                    "QPushButton {"
                    "   background-color: #2b303f;"
                    "   color: #f3f4f6;"
                    "   font-weight: 700;"
                    "   font-size: 14px;"
                    "   border-radius: 14px;"
                    "   border: none;"
                    "   padding: 0 18px;"
                    "}"
                    "QPushButton:hover {"
                    "   background-color: #373e52;"
                    "   color: #ffffff;"
                    "}"
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
        self.setWindowTitle("TRUCO PAULISTA")
        self.resize(1280, 800)
        self.setMinimumSize(1000, 680)
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
        panel.setProperty("class", "glass-panel")
        panel.setFixedSize(480, 420)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setYOffset(8)
        panel.setGraphicsEffect(shadow)

        p_layout = QVBoxLayout(panel)
        p_layout.setContentsMargins(36, 36, 36, 36)

        lbl_logo = QLabel("TRUCO PAULISTA")
        lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_logo.setStyleSheet("color: #f59e0b; font-size: 32px; font-weight: 800; letter-spacing: 1px;")
        p_layout.addWidget(lbl_logo)

        lbl_sub = QLabel("Mesa Profissional Borderless")
        lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_sub.setStyleSheet("color: #6b7280; font-size: 14px; margin-bottom: 20px;")
        p_layout.addWidget(lbl_sub)

        # Seleção de Modalidade
        lbl_mod = QLabel("MODALIDADE")
        lbl_mod.setStyleSheet("color: #9ca3af; font-size: 12px; font-weight: 700;")
        p_layout.addWidget(lbl_mod)

        grid_mod = QHBoxLayout()
        grid_mod.setSpacing(8)
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

        # Seleção de Baralho
        lbl_bar = QLabel("BARALHO")
        lbl_bar.setStyleSheet("color: #9ca3af; font-size: 12px; font-weight: 700;")
        p_layout.addWidget(lbl_bar)

        grid_bar = QHBoxLayout()
        grid_bar.setSpacing(8)
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

        p_layout.addSpacing(20)

        btn_start = QPushButton("INICIAR JOGO")
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
                "background-color: #f59e0b; color: #000000; font-weight: 800; border-radius: 10px; padding: 10px;"
                if m == self.modalidade else
                "background-color: #232733; color: #9ca3af; border-radius: 10px; padding: 10px;"
            )
        self.btn_limpo.setChecked(self.limpo)
        self.btn_sujo.setChecked(not self.limpo)
        self.btn_limpo.setEnabled(self.modalidade != 3)

        for b, act in [(self.btn_limpo, self.limpo), (self.btn_sujo, not self.limpo)]:
            b.setStyleSheet(
                "background-color: #f59e0b; color: #000000; font-weight: 800; border-radius: 10px; padding: 10px;"
                if act else
                "background-color: #232733; color: #9ca3af; border-radius: 10px; padding: 10px;"
            )

    # ------------------ TELA DO JOGO ------------------
    def _criar_tela_jogo(self):
        jogo_widget = QWidget()
        main_layout = QHBoxLayout(jogo_widget)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)

        area_centro = QVBoxLayout()
        area_centro.setSpacing(14)

        # Header / Placar Topo
        header = QFrame()
        header.setFixedHeight(64)
        header.setProperty("class", "glass-panel")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(20, 10, 20, 10)

        lbl_p_title = QLabel("PLACAR")
        lbl_p_title.setStyleSheet("color: #6b7280; font-weight: 800; font-size: 11px; letter-spacing: 1px;")
        
        self.lbl_pontos_eq0 = QLabel("0")
        self.lbl_pontos_eq0.setStyleSheet("color: #f59e0b; font-size: 24px; font-weight: 800;")
        
        lbl_x = QLabel("—")
        lbl_x.setStyleSheet("color: #4b5563; font-size: 16px;")
        
        self.lbl_pontos_eq1 = QLabel("0")
        self.lbl_pontos_eq1.setStyleSheet("color: #f3f4f6; font-size: 24px; font-weight: 800;")

        h_layout.addWidget(lbl_p_title)
        h_layout.addSpacing(8)
        h_layout.addWidget(QLabel("SUA EQUIPE"))
        h_layout.addWidget(self.lbl_pontos_eq0)
        h_layout.addWidget(lbl_x)
        h_layout.addWidget(self.lbl_pontos_eq1)
        h_layout.addWidget(QLabel("ADVERSÁRIOS"))

        h_layout.addStretch()

        self.lbl_mao_info = QLabel("MÃO 1  •  VALE 1 PONTO")
        self.lbl_mao_info.setStyleSheet("color: #f59e0b; font-weight: 700; font-size: 14px;")
        h_layout.addWidget(self.lbl_mao_info)

        h_layout.addStretch()

        btn_menu = QPushButton("MENU")
        btn_menu.setObjectName("btn-dark")
        btn_menu.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_menu.clicked.connect(self._voltar_menu)
        h_layout.addWidget(btn_menu)

        area_centro.addWidget(header)

        # Mesa de Feltro (Centro)
        self.mesa_frame = QFrame()
        self.mesa_frame.setProperty("class", "table-felt")
        mesa_layout = QVBoxLayout(self.mesa_frame)
        mesa_layout.setContentsMargins(20, 14, 20, 14)

        # Faltam Jogar Badge
        self.lbl_faltantes = QLabel("")
        self.lbl_faltantes.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_faltantes.setStyleSheet("color: #10b981; font-size: 13px; font-weight: 700; background-color: rgba(6, 78, 59, 0.4); border-radius: 16px; padding: 4px 14px;")
        mesa_layout.addWidget(self.lbl_faltantes)

        # Bots Container
        self.container_bots = QHBoxLayout()
        self.container_bots.setSpacing(20)
        mesa_layout.addLayout(self.container_bots)

        # Centro da Mesa (Vira + Cartas Jogadas)
        centro_layout = QHBoxLayout()
        centro_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Box do Vira
        v_box = QVBoxLayout()
        v_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_vira_tag = QLabel("VIRA")
        lbl_vira_tag.setStyleSheet("color: #6b7280; font-size: 11px; font-weight: 800; letter-spacing: 1px;")
        v_box.addWidget(lbl_vira_tag)
        self.vira_widget_container = QWidget()
        v_box.addWidget(self.vira_widget_container)
        centro_layout.addLayout(v_box)

        centro_layout.addSpacing(36)

        # Cartas na Mesa
        mesa_cartas_box = QVBoxLayout()
        mesa_cartas_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_mesa_tag = QLabel("CARTAS NA MESA")
        lbl_mesa_tag.setStyleSheet("color: #f59e0b; font-size: 11px; font-weight: 800; letter-spacing: 1px;")
        mesa_cartas_box.addWidget(lbl_mesa_tag)

        self.layout_cartas_mesa = QHBoxLayout()
        self.layout_cartas_mesa.setSpacing(14)
        mesa_cartas_box.addLayout(self.layout_cartas_mesa)

        centro_layout.addLayout(mesa_cartas_box)

        mesa_layout.addLayout(centro_layout)
        mesa_layout.addStretch()

        area_centro.addWidget(self.mesa_frame)

        # Rodapé / Mão do Jogador Humano
        footer = QFrame()
        footer.setFixedHeight(175)
        footer.setProperty("class", "glass-panel")
        f_layout = QHBoxLayout(footer)
        f_layout.setContentsMargins(20, 10, 20, 10)

        v_humano = QVBoxLayout()
        self.lbl_status_humano = QLabel("SUAS CARTAS")
        self.lbl_status_humano.setStyleSheet("color: #f59e0b; font-size: 13px; font-weight: 800;")
        v_humano.addWidget(self.lbl_status_humano)

        self.layout_mao_humano = QHBoxLayout()
        self.layout_mao_humano.setSpacing(14)
        v_humano.addLayout(self.layout_mao_humano)

        f_layout.addLayout(v_humano)
        f_layout.addStretch()

        self.btn_truco = QPushButton("TRUCO!")
        self.btn_truco.setObjectName("btn-gold")
        self.btn_truco.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_truco.setFixedSize(150, 48)
        self.btn_truco.clicked.connect(self._pedir_truco)
        f_layout.addWidget(self.btn_truco)

        area_centro.addWidget(footer)

        main_layout.addLayout(area_centro, stretch=4)

        # Painel Lateral (Histórico)
        side_panel = QFrame()
        side_panel.setFixedWidth(260)
        side_panel.setProperty("class", "glass-panel")
        s_layout = QVBoxLayout(side_panel)
        s_layout.setContentsMargins(14, 14, 14, 14)

        lbl_log_title = QLabel("ACONTECIMENTOS")
        lbl_log_title.setStyleSheet("color: #f59e0b; font-size: 11px; font-weight: 800; letter-spacing: 1px;")
        s_layout.addWidget(lbl_log_title)

        self.log_list = QListWidget()
        s_layout.addWidget(self.log_list)

        main_layout.addWidget(side_panel, stretch=1)

        self.stack.addWidget(jogo_widget)

    # ------------------ LÓGICA E ATUALIZAÇÃO DA TELA ------------------
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

        self.lbl_pontos_eq0.setText(str(p.pontos[0]))
        self.lbl_pontos_eq1.setText(str(p.pontos[1]))
        self.lbl_mao_info.setText(f"MÃO {p.mao_numero}  •  VALE {p.valor_mao} PONTO(S)")

        self.log_list.clear()
        for ev in self.sessao.eventos[-12:]:
            self.log_list.addItem(ev.mensagem)
        self.log_list.scrollToBottom()

        # Vira
        for child in self.vira_widget_container.children():
            if isinstance(child, QWidget):
                child.deleteLater()
        if p.vira:
            v_layout = QVBoxLayout(self.vira_widget_container)
            v_layout.setContentsMargins(0, 0, 0, 0)
            v_layout.addWidget(CardWidget(carta=p.vira, width=80, height=115))

        # Cartas na Mesa
        while self.layout_cartas_mesa.count():
            item = self.layout_cartas_mesa.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if p.jogadas:
            maior_forca = max(j.carta.forca for j in p.jogadas)
            for j in p.jogadas:
                box_jogada = QVBoxLayout()
                box_jogada.setAlignment(Qt.AlignmentFlag.AlignCenter)

                is_maior = (j.carta.forca == maior_forca)
                is_parceiro = (j.jogador in p.equipes[0].jogadores and j.jogador is not humano)
                tag_parceiro = " (Parceiro)" if is_parceiro else ""

                card_w = CardWidget(carta=j.carta, width=82, height=118)
                box_jogada.addWidget(card_w)

                tag_texto = f"{j.jogador.nome}{tag_parceiro}"
                if is_maior:
                    tag_texto += " ★"

                lbl_nome = QLabel(tag_texto)
                lbl_nome.setStyleSheet("color: #f59e0b; font-size: 11px; font-weight: 700;" if is_maior else "color: #9ca3af; font-size: 11px;")
                box_jogada.addWidget(lbl_nome)

                w_item = QWidget()
                w_item.setLayout(box_jogada)
                self.layout_cartas_mesa.addWidget(w_item)

        # Faltam Jogar
        if p.estado == Estado.JOGANDO and p.jogador_da_vez:
            primeiro_jogador = p.jogadas[0].jogador if p.jogadas else p.jogador_da_vez
            idx_inicio = p.jogadores.index(primeiro_jogador)
            ordem_vaza = [p.jogadores[(idx_inicio + i) % len(p.jogadores)] for i in range(len(p.jogadores))]
            faltantes = ordem_vaza[len(p.jogadas):]

            fmt_faltantes = []
            for j in faltantes:
                is_parceiro = (j in p.equipes[0].jogadores and j is not humano)
                suffix = " (Parceiro)" if is_parceiro else ""
                is_voce = " (Você)" if j is humano else ""
                fmt_faltantes.append(f"{j.nome}{is_voce}{suffix}")

            self.lbl_faltantes.setText(f"FALTAM JOGAR:  { '  •  '.join(fmt_faltantes) }")
        else:
            self.lbl_faltantes.setText("")

        # Bots
        while self.container_bots.count():
            item = self.container_bots.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        outros = [j for j in p.jogadores if j is not humano]
        for bot in outros:
            b_box = QVBoxLayout()
            b_box.setAlignment(Qt.AlignmentFlag.AlignCenter)

            is_vez = (p.jogador_da_vez is bot)
            is_parceiro = (bot in p.equipes[0].jogadores)

            lbl_avatar = QLabel(bot.nome[0].upper())
            lbl_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_avatar.setFixedSize(40, 40)

            bg_color = "#f59e0b" if is_vez else ("#10b981" if is_parceiro else "#232733")
            text_color = "#000000" if is_vez else "#f3f4f6"

            lbl_avatar.setStyleSheet(
                f"background-color: {bg_color}; color: {text_color}; font-weight: 800; font-size: 16px; border-radius: 20px;"
            )
            b_box.addWidget(lbl_avatar)

            lbl_bname = QLabel(f"{bot.nome} {'(Parceiro)' if is_parceiro else ''}")
            lbl_bname.setStyleSheet("color: #f59e0b; font-size: 11px; font-weight: 700;" if is_parceiro else "color: #9ca3af; font-size: 11px;")
            b_box.addWidget(lbl_bname)

            h_bcartas = QHBoxLayout()
            h_bcartas.setSpacing(4)
            for _ in range(len(bot.cartas)):
                h_bcartas.addWidget(CardWidget(verso=True, width=28, height=40))

            w_bc = QWidget()
            w_bc.setLayout(h_bcartas)
            b_box.addWidget(w_bc)

            w_bot_item = QWidget()
            w_bot_item.setLayout(b_box)
            self.container_bots.addWidget(w_bot_item)

        # Mão do Jogador Humano
        while self.layout_mao_humano.count():
            item = self.layout_mao_humano.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        pode_jogar = self.sessao.precisa_humano
        self.lbl_status_humano.setText("SUA VEZ DE JOGAR" if pode_jogar else "AGUARDANDO DEMAIS JOGADORES...")
        self.lbl_status_humano.setStyleSheet("color: #f59e0b; font-size: 13px; font-weight: 800;" if pode_jogar else "color: #6b7280; font-size: 12px;")

        for idx, carta in enumerate(humano.cartas):
            cb = (lambda i=idx: self._jogar_carta_humano(i)) if pode_jogar else None
            cw = CardWidget(carta=carta, width=90, height=130, callback=cb)
            self.layout_mao_humano.addWidget(cw)

        # Botão Truco
        pode_trucar = self.sessao.pode_trucar()
        self.btn_truco.setEnabled(pode_trucar)
        texto_truco = "TRUCO!" if p.valor_mao == 1 else {3: "SEIS!", 6: "NOVE!", 9: "DOZE!"}.get(p.valor_mao, "AUMENTAR!")
        self.btn_truco.setText(texto_truco)

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

    # ------------------ DIÁLOGOS DE JOGO ------------------
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

        dlg = DialogoCustom(
            titulo=f"PEDIRAM {valor} PONTOS!",
            mensagem="Os adversários aumentaram a aposta da mão. Qual é a sua decisão?",
            opcoes=opcoes,
            parent=self
        )
        dlg.exec()
        self.timer_bot.start()
        self._atualizar_interface()

    def _tratar_mao_de_onze(self):
        self.timer_bot.stop()
        dlg = DialogoCustom(
            titulo="MÃO DE ONZE",
            mensagem="Sua equipe atingiu 11 pontos! Desejam jogar a mão valendo 3 pontos?",
            opcoes=[
                ("JOGAR MÃO", lambda: self.sessao.decidir_onze(True), True),
                ("CORRER", lambda: self.sessao.decidir_onze(False), False)
            ],
            parent=self
        )
        dlg.exec()
        self.timer_bot.start()
        self._atualizar_interface()

    def _tratar_mao_encerrada(self):
        self.timer_bot.stop()
        p = self.sessao.partida

        # Placar totalmente limpo, sem bordas ou linhas
        score_widget = QWidget()
        s_layout = QHBoxLayout(score_widget)
        s_layout.setContentsMargins(0, 8, 0, 8)
        s_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        s_layout.setSpacing(16)

        # Card Sua Equipe
        box_eq0 = QFrame()
        box_eq0.setStyleSheet("background-color: #232733; border-radius: 16px;")
        b0_layout = QVBoxLayout(box_eq0)
        b0_layout.setContentsMargins(20, 14, 20, 14)
        b0_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        b0_layout.setSpacing(4)
        
        lbl_e0_title = QLabel("SUA EQUIPE")
        lbl_e0_title.setStyleSheet("color: #9ca3af; font-size: 11px; font-weight: 700;")
        lbl_e0_val = QLabel(str(p.pontos[0]))
        lbl_e0_val.setStyleSheet("color: #f59e0b; font-size: 36px; font-weight: 800;")
        b0_layout.addWidget(lbl_e0_title, 0, Qt.AlignmentFlag.AlignCenter)
        b0_layout.addWidget(lbl_e0_val, 0, Qt.AlignmentFlag.AlignCenter)

        # Divisor VS
        lbl_vs = QLabel("VS")
        lbl_vs.setStyleSheet("color: #4b5563; font-size: 14px; font-weight: 800;")

        # Card Adversários
        box_eq1 = QFrame()
        box_eq1.setStyleSheet("background-color: #232733; border-radius: 16px;")
        b1_layout = QVBoxLayout(box_eq1)
        b1_layout.setContentsMargins(20, 14, 20, 14)
        b1_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        b1_layout.setSpacing(4)

        lbl_e1_title = QLabel("ADVERSÁRIOS")
        lbl_e1_title.setStyleSheet("color: #9ca3af; font-size: 11px; font-weight: 700;")
        lbl_e1_val = QLabel(str(p.pontos[1]))
        lbl_e1_val.setStyleSheet("color: #f3f4f6; font-size: 36px; font-weight: 800;")
        b1_layout.addWidget(lbl_e1_title, 0, Qt.AlignmentFlag.AlignCenter)
        b1_layout.addWidget(lbl_e1_val, 0, Qt.AlignmentFlag.AlignCenter)

        s_layout.addWidget(box_eq0)
        s_layout.addWidget(lbl_vs)
        s_layout.addWidget(box_eq1)

        dlg = DialogoCustom(
            titulo="MÃO ENCERRADA",
            mensagem="Confira a pontuação atual da partida:",
            opcoes=[
                ("PRÓXIMA MÃO", lambda: self.sessao.proxima_mao(), True)
            ],
            widget_extra=score_widget,
            parent=self
        )
        dlg.exec()
        self.timer_bot.start()
        self._atualizar_interface()

    def _tratar_fim_jogo(self):
        self.timer_bot.stop()
        p = self.sessao.partida
        venceu = (p.vencedor == 0)

        score_widget = QWidget()
        s_layout = QHBoxLayout(score_widget)
        s_layout.setContentsMargins(0, 8, 0, 8)
        s_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        s_layout.setSpacing(16)

        box_eq0 = QFrame()
        box_eq0.setStyleSheet("background-color: #232733; border-radius: 16px;")
        b0_layout = QVBoxLayout(box_eq0)
        b0_layout.setContentsMargins(20, 14, 20, 14)
        b0_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_e0_title = QLabel("SUA EQUIPE")
        lbl_e0_title.setStyleSheet("color: #9ca3af; font-size: 11px; font-weight: 700;")
        lbl_e0_val = QLabel(str(p.pontos[0]))
        lbl_e0_val.setStyleSheet("color: #f59e0b; font-size: 36px; font-weight: 800;" if venceu else "color: #f3f4f6; font-size: 36px; font-weight: 800;")
        b0_layout.addWidget(lbl_e0_title, 0, Qt.AlignmentFlag.AlignCenter)
        b0_layout.addWidget(lbl_e0_val, 0, Qt.AlignmentFlag.AlignCenter)

        lbl_vs = QLabel("VS")
        lbl_vs.setStyleSheet("color: #4b5563; font-size: 14px; font-weight: 800;")

        box_eq1 = QFrame()
        box_eq1.setStyleSheet("background-color: #232733; border-radius: 16px;")
        b1_layout = QVBoxLayout(box_eq1)
        b1_layout.setContentsMargins(20, 14, 20, 14)
        b1_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_e1_title = QLabel("ADVERSÁRIOS")
        lbl_e1_title.setStyleSheet("color: #9ca3af; font-size: 11px; font-weight: 700;")
        lbl_e1_val = QLabel(str(p.pontos[1]))
        lbl_e1_val.setStyleSheet("color: #f3f4f6; font-size: 36px; font-weight: 800;" if venceu else "color: #ef4444; font-size: 36px; font-weight: 800;")
        b1_layout.addWidget(lbl_e1_title, 0, Qt.AlignmentFlag.AlignCenter)
        b1_layout.addWidget(lbl_e1_val, 0, Qt.AlignmentFlag.AlignCenter)

        s_layout.addWidget(box_eq0)
        s_layout.addWidget(lbl_vs)
        s_layout.addWidget(box_eq1)

        dlg = DialogoCustom(
            titulo="🏆 VITÓRIA!" if venceu else "FIM DE JOGO",
            mensagem="Sua equipe venceu a partida!" if venceu else "Os adversários venceram a partida.",
            opcoes=[
                ("NOVA PARTIDA", self._voltar_menu, True)
            ],
            widget_extra=score_widget,
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
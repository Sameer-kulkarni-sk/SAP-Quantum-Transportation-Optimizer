#!/usr/bin/env python3
"""
SAP Quantum Transport Optimizer
SAP Fiori Design Language — Shell Bar · Left Nav · KPI Tiles · Log Panel
"""

import sys
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pathlib import Path
import threading
from datetime import datetime

from PIL import Image, ImageTk

sys.path.insert(0, str(Path(__file__).parent))

from data_loader.csv_loader import CSVLoader

try:
    from optimizers.quantum.qaoa_optimizer import QAOAOptimizer, QISKIT_AVAILABLE
    QUANTUM_AVAILABLE = QISKIT_AVAILABLE
except ImportError:
    QUANTUM_AVAILABLE = False

# ── SAP Fiori color tokens ────────────────────────────────────────────────────
C = {
    'shell_bg':      '#003366',   # Shell / top nav bar
    'shell_text':    '#FFFFFF',
    'page_bg':       '#F5F6F7',   # Application background
    'panel_bg':      '#FFFFFF',   # Cards and panels
    'primary':       '#0070F2',   # SAP brand blue (emphasized actions)
    'primary_hover': '#0064D9',
    'primary_press': '#003B77',
    'nav_hover':     '#EBF5FE',   # Nav item hover
    'nav_active_bg': '#EBF5FE',   # Nav item selected background
    'nav_active_bar':'#0070F2',   # Left accent bar on active nav item
    'text_primary':  '#32363A',   # Primary text
    'text_secondary':'#6A6D70',   # Secondary / label text
    'border':        '#D9D9D9',   # Dividers and borders
    'success':       '#107E3E',
    'warning':       '#E9730C',
    'error':         '#BB0000',
    'quantum':       '#F0AB00',   # Gold accent for quantum
    'tile_cost':     '#0070F2',   # KPI tile accent — cost
    'tile_co2':      '#107E3E',   # KPI tile accent — CO2
    'tile_assigned': '#E9730C',   # KPI tile accent — assigned
    'tile_time':     '#8B49C9',   # KPI tile accent — time
    'log_bg':        '#FAFAFA',
    'log_hdr':       '#003366',
    'log_info':      '#0070F2',
    'log_ok':        '#107E3E',
    'log_warn':      '#E9730C',
    'log_sep':       '#6A6D70',
}

import platform as _platform
if _platform.system() == 'Darwin':
    FONT_SANS = 'Helvetica Neue'
    FONT_MONO = 'Menlo'
else:
    FONT_SANS = 'DejaVu Sans'
    FONT_MONO = 'DejaVu Sans Mono'


def _font(family, size, weight='normal'):
    return (family, size, weight)


class SAPShell:
    """Top shell bar: logo · title · clock · quantum badge."""

    HEIGHT = 56

    def __init__(self, parent, logo_path):
        self.bar = tk.Frame(parent, bg=C['shell_bg'], height=self.HEIGHT)
        self.bar.pack(fill=tk.X)
        self.bar.pack_propagate(False)

        inner = tk.Frame(self.bar, bg=C['shell_bg'])
        inner.pack(fill=tk.BOTH, expand=True, padx=16, pady=0)

        # ── Logo ──────────────────────────────────────────────────────────
        logo_cell = tk.Frame(inner, bg=C['shell_bg'])
        logo_cell.pack(side=tk.LEFT, padx=(0, 12))
        self._load_logo(logo_cell, logo_path)

        # Vertical separator
        tk.Frame(inner, bg='#336699', width=1).pack(
            side=tk.LEFT, fill=tk.Y, pady=14, padx=(0, 14))

        # ── App title ────────────────────────────────────────────────────
        title_cell = tk.Frame(inner, bg=C['shell_bg'])
        title_cell.pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(title_cell, text="Quantum Transport Optimizer",
                 font=_font(FONT_SANS, 15, 'bold'),
                 bg=C['shell_bg'], fg=C['shell_text'],
                 anchor=tk.W).pack(anchor=tk.W, pady=(14, 0))
        tk.Label(title_cell, text="SAP · Powered by Qiskit 2.x + AerSimulator",
                 font=_font(FONT_SANS, 9),
                 bg=C['shell_bg'], fg='#A0B8D0',
                 anchor=tk.W).pack(anchor=tk.W)

        # ── Right cluster ────────────────────────────────────────────────
        right = tk.Frame(inner, bg=C['shell_bg'])
        right.pack(side=tk.RIGHT, fill=tk.Y)

        # Quantum badge
        badge_bg = C['quantum'] if QUANTUM_AVAILABLE else '#6A6D70'
        badge_text = '⚛  Quantum Ready' if QUANTUM_AVAILABLE else '  Classical Mode'
        badge = tk.Label(right, text=badge_text,
                         font=_font(FONT_SANS, 9, 'bold'),
                         bg=badge_bg, fg='#1A1A1A' if QUANTUM_AVAILABLE else '#FFFFFF',
                         padx=10, pady=3, relief=tk.FLAT)
        badge.pack(side=tk.RIGHT, padx=(8, 0), pady=16)

        # Clock
        self._clock = tk.Label(right,
                               text=datetime.now().strftime('%H:%M:%S'),
                               font=_font(FONT_SANS, 13, 'bold'),
                               bg=C['shell_bg'], fg=C['shell_text'])
        self._clock.pack(side=tk.RIGHT, padx=12, pady=16)
        self._tick()

    def _load_logo(self, cell, logo_path):
        loaded = False
        if logo_path:
            try:
                img = Image.open(logo_path).convert('RGBA')

                # Fit into shell bar height: max 160 wide × 38 tall
                img.thumbnail((160, 38), Image.Resampling.LANCZOS)

                # Composite onto shell-bar background colour to eliminate
                # any transparent halo
                shell_r = int(C['shell_bg'][1:3], 16)
                shell_g = int(C['shell_bg'][3:5], 16)
                shell_b = int(C['shell_bg'][5:7], 16)
                bg = Image.new('RGBA', img.size, (shell_r, shell_g, shell_b, 255))
                bg.paste(img, mask=img.split()[3])   # use alpha channel as mask
                final = bg.convert('RGB')

                self._logo_img = ImageTk.PhotoImage(final)
                tk.Label(cell, image=self._logo_img,
                         bg=C['shell_bg']).pack(pady=9)
                loaded = True
            except Exception:
                pass

        if not loaded:
            tk.Label(cell, text='SAP',
                     font=_font(FONT_SANS, 20, 'bold'),
                     bg=C['shell_bg'], fg=C['shell_text']).pack(pady=10)

    def _tick(self):
        self._clock.config(text=datetime.now().strftime('%H:%M:%S'))
        self._clock.after(1000, self._tick)


class NavItem:
    """Single navigation list item with active / hover state."""

    H = 36

    def __init__(self, parent, label, icon, command, section_head=False):
        self.command = command
        self.active  = False
        self.section = section_head

        if section_head:
            self.frame = tk.Frame(parent, bg=C['panel_bg'])
            self.frame.pack(fill=tk.X, pady=(10, 2))
            tk.Label(self.frame, text=label.upper(),
                     font=_font(FONT_SANS, 9, 'bold'),
                     bg=C['panel_bg'], fg=C['text_secondary'],
                     anchor=tk.W).pack(side=tk.LEFT, padx=16)
            return

        self.frame = tk.Frame(parent, bg=C['panel_bg'], height=self.H)
        self.frame.pack(fill=tk.X)
        self.frame.pack_propagate(False)

        self._bar = tk.Frame(self.frame, bg=C['panel_bg'], width=3)
        self._bar.pack(side=tk.LEFT, fill=tk.Y)

        self._lbl = tk.Label(self.frame,
                             text=f'  {icon}  {label}',
                             font=_font(FONT_SANS, 11),
                             bg=C['panel_bg'], fg=C['text_primary'],
                             anchor=tk.W, cursor='hand2')
        self._lbl.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(4, 0))

        for w in (self.frame, self._lbl, self._bar):
            w.bind('<Button-1>', lambda *_: self.command())
            w.bind('<Enter>',    self._hover_on)
            w.bind('<Leave>',    self._hover_off)

    def set_active(self, yes: bool):
        if self.section:
            return
        self.active = yes
        bg  = C['nav_active_bg'] if yes else C['panel_bg']
        bar = C['nav_active_bar'] if yes else C['panel_bg']
        self._bar.config(bg=bar)
        self._lbl.config(bg=bg)
        self.frame.config(bg=bg)

    def _hover_on(self, _):
        if not self.active:
            self._lbl.config(bg=C['nav_hover'])
            self.frame.config(bg=C['nav_hover'])

    def _hover_off(self, _):
        if not self.active:
            self._lbl.config(bg=C['panel_bg'])
            self.frame.config(bg=C['panel_bg'])


class KPITile:
    """Single SAP KPI tile: colored accent bar · label · value · unit."""

    def __init__(self, parent, title, unit, accent_color):
        self.card = tk.Frame(parent, bg=C['panel_bg'],
                             relief=tk.FLAT, bd=0,
                             highlightbackground=C['border'],
                             highlightthickness=1)
        self.card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True,
                       padx=4, pady=0)

        # Colored accent bar (top 4 px)
        tk.Frame(self.card, bg=accent_color, height=4).pack(fill=tk.X)

        inner = tk.Frame(self.card, bg=C['panel_bg'])
        inner.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)

        tk.Label(inner, text=title,
                 font=_font(FONT_SANS, 9),
                 bg=C['panel_bg'], fg=C['text_secondary'],
                 anchor=tk.W).pack(anchor=tk.W)

        self._val = tk.Label(inner, text='—',
                             font=_font(FONT_SANS, 20, 'bold'),
                             bg=C['panel_bg'], fg=C['text_primary'],
                             anchor=tk.W)
        self._val.pack(anchor=tk.W)

        tk.Label(inner, text=unit,
                 font=_font(FONT_SANS, 9),
                 bg=C['panel_bg'], fg=C['text_secondary'],
                 anchor=tk.W).pack(anchor=tk.W)

    def update(self, value: str):
        self._val.config(text=value)


class SAPLogPanel:
    """Right-side log panel with tag-colored output and auto-scroll."""

    def __init__(self, parent):
        # Panel header
        hdr = tk.Frame(parent, bg=C['panel_bg'])
        hdr.pack(fill=tk.X, padx=0, pady=(0, 0))

        tk.Label(hdr, text='Console Output',
                 font=_font(FONT_SANS, 12, 'bold'),
                 bg=C['panel_bg'], fg=C['text_primary']).pack(side=tk.LEFT, padx=16, pady=8)

        # Thin separator below header
        tk.Frame(parent, bg=C['border'], height=1).pack(fill=tk.X)

        # Text widget inside a border frame
        log_frame = tk.Frame(parent,
                             bg=C['border'], bd=0)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        self.text = scrolledtext.ScrolledText(
            log_frame,
            font=_font(FONT_MONO, 10),
            bg=C['log_bg'],
            fg=C['text_primary'],
            wrap=tk.WORD,
            relief=tk.FLAT,
            bd=0,
            padx=14,
            pady=10,
            insertwidth=0,
            state=tk.NORMAL,
        )
        self.text.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        # Tag definitions
        self.text.tag_config('hdr',   foreground=C['log_hdr'],  font=_font(FONT_MONO, 10, 'bold'))
        self.text.tag_config('info',  foreground=C['log_info'])
        self.text.tag_config('ok',    foreground=C['log_ok'])
        self.text.tag_config('warn',  foreground=C['log_warn'])
        self.text.tag_config('error', foreground=C['error'])
        self.text.tag_config('sep',   foreground=C['log_sep'])
        self.text.tag_config('q',     foreground=C['quantum'],  font=_font(FONT_MONO, 10, 'bold'))

    def write(self, msg: str, tag: str = ''):
        self.text.config(state=tk.NORMAL)
        self.text.insert(tk.END, msg + '\n', tag if tag else ())
        self.text.see(tk.END)
        self.text.config(state=tk.NORMAL)

    def clear(self):
        self.text.config(state=tk.NORMAL)
        self.text.delete('1.0', tk.END)


class StatusBar:
    """Bottom status bar: indicator dot · message · progress · exit."""

    def __init__(self, parent):
        bar = tk.Frame(parent, bg=C['panel_bg'],
                       highlightbackground=C['border'],
                       highlightthickness=1,
                       height=32)
        bar.pack(fill=tk.X, side=tk.BOTTOM)
        bar.pack_propagate(False)

        self._dot = tk.Label(bar, text='●',
                             font=_font(FONT_SANS, 10),
                             bg=C['panel_bg'], fg=C['success'])
        self._dot.pack(side=tk.LEFT, padx=(12, 4))

        self._msg = tk.Label(bar, text='Ready',
                             font=_font(FONT_SANS, 10),
                             bg=C['panel_bg'], fg=C['text_primary'],
                             anchor=tk.W)
        self._msg.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self._prog = ttk.Progressbar(bar, mode='indeterminate', length=120)

        exit_btn = tk.Button(bar, text='Exit',
                             font=_font(FONT_SANS, 9, 'bold'),
                             bg=C['panel_bg'], fg=C['text_secondary'],
                             activebackground=C['error'],
                             activeforeground='#FFFFFF',
                             relief=tk.FLAT, bd=0,
                             cursor='hand2', padx=14, pady=0,
                             command=lambda: bar.winfo_toplevel().quit())
        exit_btn.pack(side=tk.RIGHT, padx=10)

    def set(self, msg: str, busy: bool = False, color: str = ''):
        dot_color = C['warning'] if busy else (color or C['success'])
        self._dot.config(fg=dot_color)
        self._msg.config(text=msg)
        if busy:
            self._prog.pack(side=tk.RIGHT, padx=8)
            self._prog.start(12)
        else:
            self._prog.stop()
            self._prog.pack_forget()


class SAPQuantumTransportGUI:
    """Main application window."""

    def __init__(self, root: tk.Tk):
        self.root  = root
        self.data  = None
        self.results: list = []
        self._nav_items: list = []
        self._active_nav = None

        # ── Quantum parameter controls ────────────────────────────────────
        self._size_var  = tk.StringVar(value='4x4')   # problem size
        self._p_var     = tk.IntVar(value=2)           # QAOA depth
        self._shots_var = tk.IntVar(value=2048)        # measurement shots

        root.title('SAP Quantum Transport Optimizer')
        root.geometry('1280x768')
        root.minsize(1024, 600)
        root.configure(bg=C['page_bg'])

        self._build_ui()
        root.bind('<Escape>', lambda *_: root.quit())
        root.bind('<F5>',     lambda *_: self.load_data())
        root.bind('<F1>',     lambda *_: self._show_help())

    # ── UI Construction ───────────────────────────────────────────────────────

    @staticmethod
    def _resolve_logo(root_dir: Path) -> Path | None:
        """
        Return the best available logo path, rasterizing SVG → PNG if needed.
        Priority: SAP_2011_logo.svg  >  sap_logo.png  >  icon.png
        """
        svg = root_dir / 'SAP_2011_logo.svg'
        cached_png = root_dir / 'sap_logo_cached.png'

        if svg.exists():
            # Rasterize SVG once; cache the PNG next to the project root
            if not cached_png.exists():
                try:
                    import cairosvg
                    cairosvg.svg2png(url=str(svg), write_to=str(cached_png),
                                     output_height=40)
                except Exception:
                    pass
            if cached_png.exists():
                return cached_png

        for candidate in [root_dir / 'sap_logo.png', root_dir / 'icon.png']:
            if candidate.exists():
                return candidate

        return None

    def _build_ui(self):
        root_dir  = Path(__file__).parent.parent
        logo_path = self._resolve_logo(root_dir)

        # Shell bar
        SAPShell(self.root, logo_path)

        # Body (nav | content)
        body = tk.Frame(self.root, bg=C['page_bg'])
        body.pack(fill=tk.BOTH, expand=True)

        self._build_nav(body)
        self._build_content(body)

        # Status bar
        self.status = StatusBar(self.root)
        self._welcome()

    def _build_nav(self, parent):
        nav_outer = tk.Frame(parent, bg=C['panel_bg'], width=220,
                             highlightbackground=C['border'],
                             highlightthickness=1)
        nav_outer.pack(side=tk.LEFT, fill=tk.Y)
        nav_outer.pack_propagate(False)

        # Scrollable nav area
        nav = tk.Frame(nav_outer, bg=C['panel_bg'])
        nav.pack(fill=tk.BOTH, expand=True, pady=8)

        def item(label, icon, cmd, section=False):
            ni = NavItem(nav, label, icon, cmd, section_head=section)
            if not section:
                self._nav_items.append(ni)
            return ni

        item('Data', '', None, section=True)
        item('Load Data',          '↓', self.load_data)

        item('Quantum', '', None, section=True)
        item('QAOA Quantum',       '⚛', lambda: self._run('qaoa'))
        item('View Circuit',       '⊞', self._show_circuit)

        item('Analysis', '', None, section=True)
        item('Compare Results',    '≡', self._compare)
        item('Export JSON',        '⬆', self._export)

        item('', '', None, section=True)
        item('Clear Console',      '✕', self._clear)
        item('Help',               '?', self._show_help)

    def _build_controls(self, parent):
        bar = tk.Frame(parent, bg=C['panel_bg'],
                       highlightbackground=C['border'],
                       highlightthickness=1)
        bar.pack(fill=tk.X, pady=(0, 10))

        def group(label):
            f = tk.Frame(bar, bg=C['panel_bg'])
            f.pack(side=tk.LEFT, padx=16, pady=6)
            tk.Label(f, text=label,
                     font=_font(FONT_SANS, 9, 'bold'),
                     bg=C['panel_bg'], fg=C['text_secondary']).pack(anchor=tk.W)
            return f

        # Problem size
        sf = group('Problem Size (qubits)')
        for label, val in [('2×2  (4q)', '2x2'), ('3×3  (9q)', '3x3'),
                           ('4×4 (16q)', '4x4'), ('5×4 (20q)', '5x4')]:
            tk.Radiobutton(sf, text=label, variable=self._size_var, value=val,
                           font=_font(FONT_SANS, 12), bg=C['panel_bg'],
                           fg=C['text_primary'], selectcolor=C['primary'],
                           activebackground=C['panel_bg'], indicatoron=True,
                           relief=tk.FLAT, padx=8, pady=4).pack(side=tk.LEFT, padx=4)

        tk.Frame(bar, bg=C['border'], width=1).pack(side=tk.LEFT, fill=tk.Y, pady=6)

        # QAOA depth p
        pf = group('QAOA Depth  p')
        for val in [1, 2, 3]:
            tk.Radiobutton(pf, text=f'  p = {val}  ', variable=self._p_var, value=val,
                           font=_font(FONT_SANS, 12), bg=C['panel_bg'],
                           fg=C['text_primary'], selectcolor=C['primary'],
                           activebackground=C['panel_bg'], indicatoron=True,
                           relief=tk.FLAT, padx=8, pady=4).pack(side=tk.LEFT, padx=4)

        tk.Frame(bar, bg=C['border'], width=1).pack(side=tk.LEFT, fill=tk.Y, pady=6)

        # Shots
        shf = group('Shots')
        for val in [256, 512, 2048]:
            tk.Radiobutton(shf, text=f'  {val}  ', variable=self._shots_var, value=val,
                           font=_font(FONT_SANS, 12), bg=C['panel_bg'],
                           fg=C['text_primary'], selectcolor=C['primary'],
                           activebackground=C['panel_bg'], indicatoron=True,
                           relief=tk.FLAT, padx=8, pady=4).pack(side=tk.LEFT, padx=4)

        # Fix 4 — live warning for dangerous combo (5×4 + p≥2)
        self._combo_warn = tk.Label(bar, text='',
                                    font=_font(FONT_SANS, 9, 'bold'),
                                    bg=C['panel_bg'], fg=C['warning'])
        self._combo_warn.pack(side=tk.RIGHT, padx=16)

        def _check_combo(*_):
            size = self._size_var.get()
            p    = self._p_var.get()
            if size == '5x4' and p >= 2:
                self._combo_warn.config(
                    text=f'⚠  5×4 + p={p} may take 10–30 min')
            elif size in ('4x4', '5x4') and p == 3:
                self._combo_warn.config(
                    text=f'⚠  {size} + p=3 is slow — consider p=1 or p=2')
            else:
                self._combo_warn.config(text='')

        self._size_var.trace_add('write', _check_combo)
        self._p_var.trace_add('write', _check_combo)

    def _build_content(self, parent):
        content = tk.Frame(parent, bg=C['page_bg'])
        content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True,
                     padx=12, pady=10)

        # ── Quantum parameter controls ────────────────────────────────────
        self._build_controls(content)

        # ── KPI tiles row ─────────────────────────────────────────────────
        tile_row = tk.Frame(content, bg=C['page_bg'], height=90)
        tile_row.pack(fill=tk.X, pady=(0, 10))
        tile_row.pack_propagate(False)

        self.kpi_cost     = KPITile(tile_row, 'Total Cost',      'EUR',     C['tile_cost'])
        self.kpi_co2      = KPITile(tile_row, 'Total CO₂',       'kg',      C['tile_co2'])
        self.kpi_assigned = KPITile(tile_row, 'Shipments Assigned', '/ total', C['tile_assigned'])
        self.kpi_time     = KPITile(tile_row, 'Computation Time', 'seconds', C['tile_time'])

        # ── Log panel ────────────────────────────────────────────────────
        log_card = tk.Frame(content, bg=C['panel_bg'],
                            highlightbackground=C['border'],
                            highlightthickness=1)
        log_card.pack(fill=tk.BOTH, expand=True)
        self.log = SAPLogPanel(log_card)

    # ── Welcome message ───────────────────────────────────────────────────────

    def _welcome(self):
        L = self.log
        L.write('─' * 72, 'sep')
        L.write('  SAP QUANTUM TRANSPORT OPTIMIZER', 'hdr')
        L.write('  Powered by Qiskit 2.x  ·  AerSimulator  ·  RasQberry Edition', 'q')
        L.write('─' * 72, 'sep')
        L.write('')
        L.write('  Quick Start:', 'info')
        L.write('    1.  Load Data          — import shipments, trucks, lanes')
        L.write('    2.  Run QAOA Quantum   — quantum circuit optimises assignments')
        L.write('    3.  Compare Results    — run multiple times to compare QAOA configurations')
        L.write('')
        q_status = 'AVAILABLE  (Qiskit 2.x + AerSimulator)' if QUANTUM_AVAILABLE \
                   else 'NOT AVAILABLE  (install: pip install qiskit qiskit-aer scipy)'
        tag = 'q' if QUANTUM_AVAILABLE else 'warn'
        L.write(f'  Quantum Engine : {q_status}', tag)
        L.write('─' * 72, 'sep')
        L.write('')

    # ── Nav helpers ───────────────────────────────────────────────────────────

    def _activate_nav(self, index: int):
        for i, ni in enumerate(self._nav_items):
            ni.set_active(i == index)

    # ── Data ─────────────────────────────────────────────────────────────────

    def load_data(self):
        self._activate_nav(0)
        self.status.set('Loading data …', busy=True)
        self.log.write('')
        self.log.write('  Loading CSV files …', 'info')
        try:
            data_dir = Path(__file__).parent.parent / 'data' / 'input'
            loader   = CSVLoader(str(data_dir))
            self.data = loader.load_all()
            n_s = len(self.data['shipments'])
            n_t = len(self.data['trucks'])
            n_l = len(self.data['lanes'])
            self.log.write(f'  ✓  {n_s} shipments', 'ok')
            self.log.write(f'  ✓  {n_t} trucks', 'ok')
            self.log.write(f'  ✓  {n_l} lanes', 'ok')
            self.kpi_assigned.update(f'0 / {n_s}')
            self.status.set(f'Data loaded — {n_s} shipments, {n_t} trucks, {n_l} lanes')
        except Exception as exc:
            self.log.write(f'  ✗  {exc}', 'error')
            self.status.set('Error loading data', color=C['error'])
            messagebox.showerror('Load Error', str(exc))

    # ── Optimization ─────────────────────────────────────────────────────────

    def _run(self, algo: str):
        if self.data is None:
            messagebox.showwarning('No Data', 'Please load data first (↓ Load Data).')
            return
        nav_map = {'qaoa': 1}
        self._activate_nav(nav_map.get(algo, 0))
        self.status.set(f'Running {algo} …', busy=True)
        t = threading.Thread(target=self._run_thread, args=(algo,), daemon=True)
        t.start()

    def _run_thread(self, algo: str):
        try:
            label = 'QAOA Quantum'

            self.log.write('')
            self.log.write('─' * 72, 'sep')
            self.log.write(f'  {label}', 'hdr')
            self.log.write('─' * 72, 'sep')

            ships  = self.data['shipments']
            trucks = self.data['trucks']
            lanes  = self.data['lanes']

            if algo == 'qaoa':
                if not QUANTUM_AVAILABLE:
                    self.log.write('  ✗  Quantum packages not available.', 'error')
                    self.status.set('Quantum not available', color=C['error'])
                    return
                size_map = {'2x2': (2, 2), '3x3': (3, 3), '4x4': (4, 4), '5x4': (5, 4)}
                n_s, n_t = size_map.get(self._size_var.get(), (4, 4))
                p      = self._p_var.get()
                shots  = self._shots_var.get()
                n_q    = n_s * n_t

                # Fix 1 — scale max_iter with p so COBYLA has enough budget
                max_iter = 50 * p   # p=1→50, p=2→100, p=3→150

                # Fix 2 — warn when shots may be too low for the qubit count
                min_shots = (2 ** n_q) // 4
                if shots < min_shots:
                    self.log.write(
                        f'  ⚠  {shots} shots may be too low for {n_q} qubits '
                        f'(recommended ≥ {min_shots}). '
                        f'COBYLA energy estimates will be noisy.', 'warn')

                # Fix 3 — runtime warning for large+deep combinations
                if n_q > 16 and p >= 2:
                    self.log.write(
                        f'  ⚠  {n_q} qubits × p={p}: this combination may take '
                        f'10–30 minutes on CPU. Consider reducing size or depth.', 'warn')

                sub_ships  = ships[:n_s]
                sub_trucks = trucks[:n_t]
                self.log.write(
                    f'  Sub-problem: {n_s} shipments × {n_t} trucks = {n_q} qubits'
                    f'  |  p={p}  |  shots={shots}  |  max_iter={max_iter}', 'q')
                self._show_qubit_map_before(sub_ships, sub_trucks)
                result = QAOAOptimizer(
                    sub_ships, sub_trucks, lanes,
                    qaoa_reps=p, max_iter=max_iter, shots=shots
                ).optimize(progress_callback=lambda m: self.log.write(f'  {m}', 'q'))
                result.algorithm = f'QAOA {n_s}×{n_t} ({n_q}q) p={p} shots={shots}'

            self._show_result(result)
            if algo == 'qaoa':
                self._show_qubit_map_after(result)
            self.results.append(result)
            self.status.set(f'{label} completed  |  '
                            f'€{result.total_cost:,.0f}  ·  '
                            f'{result.shipments_assigned} assigned')

        except Exception as exc:
            import traceback
            self.log.write(f'  ✗  {exc}', 'error')
            self.log.write(traceback.format_exc(), 'error')
            self.status.set(f'Error in {algo}', color=C['error'])

    def _show_result(self, r):
        n_total = len(self.data['shipments']) if self.data else r.shipments_assigned

        # KPI tiles
        self.kpi_cost.update(f'{r.total_cost:,.0f}')
        self.kpi_co2.update(f'{r.total_co2:,.0f}')
        self.kpi_assigned.update(f'{r.shipments_assigned} / {n_total}')
        self.kpi_time.update(f'{r.computation_time:.2f}')

        # Log
        W = 30
        self.log.write('')
        self.log.write(f'  Algorithm  : {r.algorithm}', 'info')
        self.log.write(f'  {"Total Cost":<{W}} €{r.total_cost:>14,.2f}')
        self.log.write(f'  {"Total CO₂":<{W}} {r.total_co2:>14,.2f} kg')
        self.log.write(f'  {"Computation Time":<{W}} {r.computation_time:>14.3f} s')
        self.log.write(f'  {"Trucks Used":<{W}} {r.trucks_used:>14}')
        self.log.write(f'  {"Shipments Assigned":<{W}} {r.shipments_assigned:>14}', 'ok')
        self.log.write(f'  {"Shipments Unassigned":<{W}} {r.shipments_unassigned:>14}')

        if r.metadata:
            _skip = {'unassigned_shipments', 'cost_history',
                     'circuit_text', 'best_bitstring', 'shipments', 'trucks'}
            for k, v in r.metadata.items():
                if k not in _skip:
                    self.log.write(f'  {"  · " + str(k):<{W}} {str(v):>14}', 'sep')

        # First 5 assignments
        if r.assignments:
            self.log.write('')
            self.log.write(
                f'  {"Shipment":<12}{"Truck":<10}{"Lane":<10}'
                f'{"Cost (€)":>10}{"CO₂ (kg)":>10}', 'sep')
            self.log.write('  ' + '─' * 54, 'sep')
            for a in r.assignments[:5]:
                self.log.write(
                    f'  {a["shipment"].shipment_id:<12}'
                    f'{a["truck"].truck_id:<10}'
                    f'{a["lane"].lane_id:<10}'
                    f'{a["cost"]:>10.2f}'
                    f'{a["co2"]:>10.2f}')
            if len(r.assignments) > 5:
                self.log.write(
                    f'  … and {len(r.assignments) - 5} more assignments', 'sep')
        self.log.write('─' * 72, 'sep')

    def _show_qubit_map_before(self, ships, trucks):
        n_t = len(trucks)
        self.log.write('', '')
        self.log.write('  QUBIT MAP  (each qubit = one possible assignment)', 'hdr')
        self.log.write(f'  {"Qubit":<7}{"Shipment":<14}{"Truck":<14}{"Meaning"}', 'sep')
        self.log.write('  ' + '─' * 58, 'sep')
        for i, s in enumerate(ships):
            for j, t in enumerate(trucks):
                q = i * n_t + j
                self.log.write(
                    f'  q[{q:<3}]  {s.shipment_id:<14}{t.truck_id:<14}'
                    f'Assign {s.shipment_id} → {t.truck_id}', 'q')
        self.log.write('  ' + '─' * 58, 'sep')
        self.log.write('  Quantum circuit will find which qubits should be |1⟩', 'info')
        self.log.write('', '')

    def _show_qubit_map_after(self, result):
        bs        = result.metadata.get('best_bitstring', '')
        ship_ids  = result.metadata.get('shipments', [])
        truck_ids = result.metadata.get('trucks', [])
        if not bs or not ship_ids or not truck_ids:
            return
        n_t = len(truck_ids)
        assigned = {(a['shipment'].shipment_id, a['truck'].truck_id)
                    for a in result.assignments}
        self.log.write('', '')
        self.log.write('  QUBIT MAP  (measurement result)', 'hdr')
        self.log.write(f'  {"Qubit":<7}{"Shipment":<14}{"Truck":<14}{"Measured":<10}{""}', 'sep')
        self.log.write('  ' + '─' * 58, 'sep')
        for i, sid in enumerate(ship_ids):
            for j, tid in enumerate(truck_ids):
                q   = i * n_t + j
                bit = bs[q] if q < len(bs) else '?'
                tag = 'ok' if bit == '1' else 'sep'
                mark = '  ✓ assigned' if (sid, tid) in assigned else ''
                self.log.write(
                    f'  q[{q:<3}]  {sid:<14}{tid:<14}|{bit}⟩{mark}', tag)
        self.log.write('  ' + '─' * 58, 'sep')
        self.log.write('', '')

    def _show_circuit(self):
        self._activate_nav(2)
        if not self.results:
            messagebox.showinfo('Circuit Viewer', 'Run QAOA first to view the circuit.')
            return
        r = self.results[-1]
        circuit_text  = r.metadata.get('circuit_text', '')
        circuit_depth = r.metadata.get('circuit_depth', '?')
        n_qubits      = r.metadata.get('n_qubits', '?')
        p             = r.metadata.get('qaoa_reps', '?')
        if not circuit_text:
            messagebox.showinfo('Circuit Viewer', 'No circuit data available.')
            return

        win = tk.Toplevel(self.root)
        win.title(f'QAOA Circuit — {n_qubits} qubits  p={p}  depth={circuit_depth}')
        win.geometry('1200x820')
        win.configure(bg=C['page_bg'])

        # Header
        hdr = tk.Frame(win, bg=C['shell_bg'], height=44)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Label(hdr,
                 text=f'  ⚛  QAOA Circuit  ·  {n_qubits} qubits  ·  p={p}  ·  depth={circuit_depth}',
                 font=_font(FONT_SANS, 12, 'bold'),
                 bg=C['shell_bg'], fg=C['shell_text'],
                 anchor=tk.W).pack(side=tk.LEFT, padx=12, pady=8)
        tk.Label(hdr, text='Each row = one qubit  ·  Left → right = time  ·  Gates shown at QAOA block level',
                 font=_font(FONT_SANS, 9),
                 bg=C['shell_bg'], fg='#A0B8D0',
                 anchor=tk.E).pack(side=tk.RIGHT, padx=16)

        # ── Info panel (notation guide + qubit legend) ────────────────────
        info = tk.Frame(win, bg=C['panel_bg'],
                        highlightbackground=C['border'], highlightthickness=1)
        info.pack(fill=tk.X, padx=8, pady=(6, 0))

        # Left column: notation guide
        left = tk.Frame(info, bg=C['panel_bg'])
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=14, pady=8)
        tk.Label(left, text='Circuit Notation',
                 font=_font(FONT_SANS, 10, 'bold'),
                 bg=C['panel_bg'], fg=C['text_primary'],
                 anchor=tk.W).pack(anchor=tk.W)
        for line in [
            'exp(-it H_C)(γ)  →  Cost unitary: rotates state toward lower-cost assignments',
            'exp(-it H_B)(β)  →  Mixer unitary: explores different assignments (superposition)',
            'H                →  Hadamard: puts qubit into equal superposition (start of QAOA)',
            'I  (in Pauli string)  →  Identity: this qubit not involved in this term',
            'Z  (in Pauli string)  →  Cost/penalty on a single qubit (one assignment)',
            'ZZ (in Pauli string)  →  Two-qubit penalty (conflict between two assignments)',
        ]:
            tk.Label(left, text=f'  {line}',
                     font=_font(FONT_MONO, 9),
                     bg=C['panel_bg'], fg=C['text_secondary'],
                     anchor=tk.W).pack(anchor=tk.W)

        # Separator
        tk.Frame(info, bg=C['border'], width=1).pack(side=tk.LEFT, fill=tk.Y, pady=8)

        # Right column: qubit → assignment legend
        right = tk.Frame(info, bg=C['panel_bg'])
        right.pack(side=tk.LEFT, fill=tk.BOTH, padx=14, pady=8)
        tk.Label(right, text='Qubit Map',
                 font=_font(FONT_SANS, 10, 'bold'),
                 bg=C['panel_bg'], fg=C['text_primary'],
                 anchor=tk.W).pack(anchor=tk.W)
        ship_ids  = r.metadata.get('shipments', [])
        truck_ids = r.metadata.get('trucks', [])
        n_t = len(truck_ids)
        assigned = {(a['shipment'].shipment_id, a['truck'].truck_id)
                    for a in r.assignments}
        for i, sid in enumerate(ship_ids):
            for j, tid in enumerate(truck_ids):
                q    = i * n_t + j
                mark = '  ✓' if (sid, tid) in assigned else ''
                tk.Label(right,
                         text=f'  q[{q}]  {sid} → {tid}{mark}',
                         font=_font(FONT_MONO, 9),
                         bg=C['panel_bg'],
                         fg=C['success'] if mark else C['text_secondary'],
                         anchor=tk.W).pack(anchor=tk.W)

        # Scrollable text with horizontal + vertical scrollbars
        frame = tk.Frame(win, bg=C['panel_bg'])
        frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        vscroll = tk.Scrollbar(frame, orient=tk.VERTICAL)
        hscroll = tk.Scrollbar(frame, orient=tk.HORIZONTAL)
        txt = tk.Text(frame,
                      font=_font(FONT_MONO, 11),
                      bg=C['log_bg'], fg=C['text_primary'],
                      wrap=tk.NONE,
                      relief=tk.FLAT, bd=0,
                      padx=12, pady=8,
                      yscrollcommand=vscroll.set,
                      xscrollcommand=hscroll.set,
                      state=tk.NORMAL)
        vscroll.config(command=txt.yview)
        hscroll.config(command=txt.xview)
        vscroll.pack(side=tk.RIGHT,  fill=tk.Y)
        hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        txt.pack(fill=tk.BOTH, expand=True)

        txt.insert(tk.END, circuit_text)
        txt.config(state=tk.DISABLED)

        tk.Button(win, text='Close',
                  font=_font(FONT_SANS, 10, 'bold'),
                  bg=C['primary'], fg='#FFFFFF',
                  activebackground=C['primary_press'],
                  relief=tk.FLAT, padx=20, pady=4,
                  command=win.destroy).pack(pady=(0, 8))

    # ── Compare ──────────────────────────────────────────────────────────────

    def _compare(self):
        self._activate_nav(3)
        if len(self.results) < 2:
            messagebox.showinfo('Compare', 'Run QAOA at least twice to compare configurations.')
            return

        self.log.write('')
        self.log.write('─' * 72, 'sep')
        self.log.write('  QAOA CONFIGURATION COMPARISON', 'hdr')
        self.log.write('─' * 72, 'sep')

        # Group results by problem size (n_qubits)
        groups = {}
        for r in self.results:
            nq = r.metadata.get('n_qubits', 0)
            groups.setdefault(nq, []).append(r)

        mixed = len(groups) > 1
        if mixed:
            self.log.write(
                '  ⚠  Runs have different problem sizes — only runs within the',
                'warn')
            self.log.write(
                '     same qubit count are directly comparable.', 'warn')
            self.log.write('', '')

        hdr = (f'  {"Configuration":<42}{"Assigned":>10}'
               f'{"Cost (€)":>14}{"CO₂ (kg)":>14}{"Energy":>11}{"Time (s)":>11}')
        for nq, runs in sorted(groups.items()):
            self.log.write(f'  ── {nq} qubits ──', 'sep')
            self.log.write(hdr, 'sep')
            self.log.write('  ' + '─' * 80, 'sep')
            for r in runs:
                energy = r.metadata.get('final_energy', float('nan'))
                energy_str = f'{energy:>11.2f}' if energy == energy else '        N/A'
                self.log.write(
                    f'  {r.algorithm:<42}'
                    f'{r.shipments_assigned:>10}'
                    f'{r.total_cost:>14,.0f}'
                    f'{r.total_co2:>14,.0f}'
                    f'{energy_str}'
                    f'{r.computation_time:>11.3f}')
            self.log.write('  ' + '─' * 80, 'sep')

            # Insights — only meaningful within same qubit count
            most_assigned = max(runs, key=lambda r: r.shipments_assigned)
            fastest       = min(runs, key=lambda r: r.computation_time)
            valid_energy  = [r for r in runs
                             if r.metadata.get('final_energy') == r.metadata.get('final_energy')]
            best_energy   = min(valid_energy,
                                key=lambda r: r.metadata['final_energy']) if valid_energy else None

            self.log.write(f'  ⚛  Most assigned : {most_assigned.algorithm}'
                           f'  ({most_assigned.shipments_assigned} shipments)', 'ok')
            self.log.write(f'  ⚡  Fastest run   : {fastest.algorithm}'
                           f'  ({fastest.computation_time:.2f}s)', 'ok')
            if best_energy:
                self.log.write(f'  ↓  Best energy  : {best_energy.algorithm}'
                               f'  (⟨H_C⟩={best_energy.metadata["final_energy"]:.3f})', 'ok')
            self.log.write('', '')

        self.log.write('─' * 72, 'sep')
        self.status.set('Configuration comparison complete')

    # ── Export ───────────────────────────────────────────────────────────────

    def _export(self):
        self._activate_nav(4)
        if not self.results:
            messagebox.showinfo('Export', 'No results to export yet.')
            return
        import json
        out = Path(__file__).parent.parent / 'data' / 'output' / 'gui_results.json'
        out.parent.mkdir(parents=True, exist_ok=True)
        data = [r.to_dict() for r in self.results]
        out.write_text(json.dumps(data, indent=2))
        self.log.write(f'  ✓  Exported {len(data)} results → {out}', 'ok')
        self.status.set(f'Exported to {out.name}')

    # ── Clear ────────────────────────────────────────────────────────────────

    def _clear(self):
        self._activate_nav(5)
        self.results.clear()
        self.log.clear()
        self.kpi_cost.update('—')
        self.kpi_co2.update('—')
        self.kpi_assigned.update('—')
        self.kpi_time.update('—')
        self._welcome()
        self.status.set('Ready')

    # ── Help ─────────────────────────────────────────────────────────────────

    def _show_help(self):
        self._activate_nav(6)
        messagebox.showinfo(
            'SAP Quantum Transport Optimizer — Help',
            'QUANTUM ALGORITHM\n'
            '  QAOA   Real Qiskit 2.x QAOAAnsatz + AerSampler\n\n'
            'HOW IT WORKS\n'
            '  • Shipment-truck pairs encoded as qubits (1 qubit per pair)\n'
            '  • QUBO → Ising Hamiltonian via Pauli-Z mapping\n'
            '  • QAOAAnsatz  p=2 layers (cost + mixer)\n'
            '  • COBYLA classical optimiser tunes variational parameters\n'
            '  • 2048 shots on AerSimulator measure the best assignment\n'
            '  • Qubit map shows exactly which qubit → which assignment\n\n'
            'CURRENT STATE OF QUANTUM COMPUTING\n'
            '  • Quantum advantage for optimisation not yet achieved\n'
            '  • This demo shows the approach SAP is exploring for future\n'
            '    logistics and supply chain optimisation\n\n'
            'KEYBOARD SHORTCUTS\n'
            '  F5   Load Data\n'
            '  F1   This help\n'
            '  ESC  Exit\n\n'
            'https://rasqberry.org'
        )


def main():
    root = tk.Tk()
    SAPQuantumTransportGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()

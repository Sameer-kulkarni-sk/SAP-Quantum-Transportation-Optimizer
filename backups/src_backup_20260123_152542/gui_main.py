#!/usr/bin/env python3
"""
Quantum Transport Optimizer - Touchscreen GUI
Optimized for Raspberry Pi Touch Display 2
"""

from optimizers.classical.local_search import LocalSearchOptimizer
from optimizers.classical.greedy_optimizer import GreedyOptimizer
from data_loader.csv_loader import CSVLoader
import sys
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pathlib import Path
import threading
from datetime import datetime

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))


# Try to import quantum optimizer
try:
    from optimizers.quantum.qaoa_optimizer import QAOAOptimizer
    QUANTUM_AVAILABLE = True
except ImportError:
    QUANTUM_AVAILABLE = False


class QuantumTransportGUI:
    """Main GUI Application for Touchscreen"""

    def __init__(self, root):
        self.root = root
        self.root.title("SAP Quantum Transport Optimizer")

        # Configure for touchscreen (800x480 or 1024x600)
        self.root.geometry("1024x600")
        self.root.configure(bg='#003366')  # SAP Blue

        # Make fullscreen for touchscreen
        # self.root.attributes('-fullscreen', True)

        # Data storage
        self.data = None
        self.results = []
        self.current_algorithm = None

        # Configure styles
        self.setup_styles()

        # Create main UI
        self.create_widgets()

        # Bind escape key to exit fullscreen
        self.root.bind('<Escape>', lambda e: self.root.attributes(
            '-fullscreen', False))

        # Add keyboard shortcut hints
        self.root.bind('<F1>', lambda e: self.show_help())
        self.root.bind('<F5>', lambda e: self.load_data())

    def setup_styles(self):
        """Setup SAP-inspired color scheme and styles"""
        style = ttk.Style()
        style.theme_use('clam')

        # SAP Colors - Professional palette
        self.colors = {
            'sap_blue': '#003366',
            'sap_blue_light': '#0066CC',
            'sap_gold': '#F0AB00',
            'sap_gold_light': '#FFD700',
            'sap_green': '#00A65A',
            'sap_green_light': '#00C853',
            'sap_red': '#E52929',
            'sap_gray': '#6A6A6A',
            'sap_gray_light': '#CCCCCC',
            'white': '#FFFFFF',
            'light_gray': '#F5F5F5',
            'dark_gray': '#333333'
        }

        # Configure button style
        style.configure('SAP.TButton',
                        font=('Arial', 14, 'bold'),
                        padding=15,
                        background=self.colors['sap_blue'],
                        foreground=self.colors['white'])

        style.map('SAP.TButton',
                  background=[('active', self.colors['sap_gold'])])

        # Configure label style
        style.configure('Title.TLabel',
                        font=('Arial', 24, 'bold'),
                        background=self.colors['sap_blue'],
                        foreground=self.colors['sap_gold'])

        style.configure('Subtitle.TLabel',
                        font=('Arial', 12),
                        background=self.colors['sap_blue'],
                        foreground=self.colors['white'])

    def create_widgets(self):
        """Create main UI widgets"""
        # Header with SAP-style logo
        self.create_header()

        # Main content area
        self.create_main_area()

        # Footer with status
        self.create_footer()

    def create_header(self):
        """Create professional header with official SAP branding"""
        header_frame = tk.Frame(
            self.root, bg=self.colors['sap_blue'], height=120)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)

        # SAP Logo area
        logo_frame = tk.Frame(header_frame, bg=self.colors['sap_blue'])
        logo_frame.pack(side=tk.LEFT, padx=30, pady=15)

        # Try to load SAP logo image, fallback to canvas drawing
        try:
            from PIL import Image, ImageTk
            logo_path = Path(__file__).parent.parent / "sap_logo.png"
            if logo_path.exists():
                logo_img = Image.open(logo_path)
                logo_img = logo_img.resize((90, 90), Image.Resampling.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(logo_img)
                logo_label = tk.Label(logo_frame, image=self.logo_photo,
                                      bg=self.colors['sap_blue'])
                logo_label.pack()
            else:
                raise FileNotFoundError("Logo not found")
        except:
            # Fallback: Create SAP logo with canvas
            logo_canvas = tk.Canvas(logo_frame, width=90, height=90,
                                    bg=self.colors['sap_blue'], highlightthickness=0)
            logo_canvas.pack()

            # Official SAP logo style - blue box with white SAP text
            logo_canvas.create_rectangle(5, 30, 85, 60,
                                         fill=self.colors['sap_blue'],
                                         outline=self.colors['white'], width=2)
            logo_canvas.create_text(45, 45, text="SAP",
                                    font=('Arial', 20, 'bold'),
                                    fill=self.colors['white'])

            # Add quantum symbol below
            logo_canvas.create_oval(30, 65, 60, 85,
                                    outline=self.colors['sap_gold'], width=2)
            logo_canvas.create_line(45, 65, 45, 85,
                                    fill=self.colors['sap_gold'], width=2)
            logo_canvas.create_oval(40, 72, 50, 82,
                                    fill=self.colors['sap_gold'])

        # Title section
        title_frame = tk.Frame(header_frame, bg=self.colors['sap_blue'])
        title_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=15)

        # SAP branding
        sap_label = tk.Label(title_frame,
                             text="SAP",
                             font=('Arial', 16, 'bold'),
                             bg=self.colors['sap_blue'],
                             fg=self.colors['sap_gold'])
        sap_label.pack(anchor=tk.W)

        title_label = tk.Label(title_frame,
                               text="Quantum Transport Optimizer",
                               font=('Arial', 22, 'bold'),
                               bg=self.colors['sap_blue'],
                               fg=self.colors['white'])
        title_label.pack(anchor=tk.W)

        subtitle_label = tk.Label(title_frame,
                                  text="Powered by Qiskit • RasQberry Edition",
                                  font=('Arial', 11),
                                  bg=self.colors['sap_blue'],
                                  fg=self.colors['sap_gray_light'])
        subtitle_label.pack(anchor=tk.W)

        # Status indicators
        status_frame = tk.Frame(header_frame, bg=self.colors['sap_blue'])
        status_frame.pack(side=tk.RIGHT, padx=30, pady=15)

        # Time display
        self.time_label = tk.Label(status_frame,
                                   text=datetime.now().strftime("%H:%M:%S"),
                                   font=('Arial', 14, 'bold'),
                                   bg=self.colors['sap_blue'],
                                   fg=self.colors['sap_gold'])
        self.time_label.pack()

        # Quantum status indicator
        self.quantum_status = tk.Label(status_frame,
                                       text="⚛️ Quantum Ready" if QUANTUM_AVAILABLE else "⚠️ Classical Only",
                                       font=('Arial', 9),
                                       bg=self.colors['sap_blue'],
                                       fg=self.colors['sap_green'] if QUANTUM_AVAILABLE else self.colors['sap_red'])
        self.quantum_status.pack()

        self.update_time()

    def create_main_area(self):
        """Create main content area with buttons and results"""
        main_frame = tk.Frame(self.root, bg=self.colors['light_gray'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left panel - Control buttons
        left_panel = tk.Frame(
            main_frame, bg=self.colors['light_gray'], width=250)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)

        # Button panel
        button_frame = tk.Frame(left_panel, bg=self.colors['light_gray'])
        button_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Professional touch-friendly buttons with icons
        buttons = [
            ("📂  Load Data", self.load_data, self.colors['sap_blue'], "F5"),
            ("⚡  Greedy Optimizer", lambda: self.run_optimizer(
                'greedy'), self.colors['sap_green'], ""),
            ("🔄  Local Search", lambda: self.run_optimizer(
                'local_search'), self.colors['sap_green_light'], ""),
            ("⚛️  QAOA Quantum", lambda: self.run_optimizer(
                'qaoa'), self.colors['sap_gold'], ""),
            ("📊  Compare All", self.compare_all,
             self.colors['sap_blue_light'], ""),
            ("🗑️  Clear Results", self.clear_results,
             self.colors['sap_gray'], ""),
        ]

        for text, command, color, shortcut in buttons:
            btn_container = tk.Frame(
                button_frame, bg=self.colors['light_gray'])
            btn_container.pack(fill=tk.X, pady=6, padx=5)

            btn = tk.Button(btn_container, text=text, command=command,
                            font=('Arial', 13, 'bold'),
                            bg=color, fg='white',
                            activebackground=self.colors['sap_gold'],
                            activeforeground='white',
                            relief=tk.FLAT, bd=0,
                            height=2, cursor='hand2',
                            padx=10)
            btn.pack(fill=tk.BOTH, expand=True)

            # Add hover effect
            btn.bind('<Enter>', lambda e, b=btn,
                     c=color: b.config(bg=self.colors['sap_gold']))
            btn.bind('<Leave>', lambda e, b=btn, c=color: b.config(bg=c))

            if shortcut:
                shortcut_label = tk.Label(btn_container, text=shortcut,
                                          font=('Arial', 8),
                                          bg=self.colors['light_gray'],
                                          fg=self.colors['sap_gray'])
                shortcut_label.pack(side=tk.RIGHT, padx=5)

        # Right panel - Results display
        right_panel = tk.Frame(main_frame, bg='white')
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Results text area with scrollbar
        results_label = tk.Label(right_panel, text="Results",
                                 font=('Arial', 14, 'bold'),
                                 bg='white', fg=self.colors['sap_blue'])
        results_label.pack(anchor=tk.W, padx=10, pady=5)

        self.results_text = scrolledtext.ScrolledText(
            right_panel,
            font=('Courier', 10),
            bg='white',
            fg='black',
            wrap=tk.WORD,
            relief=tk.SUNKEN,
            bd=2
        )
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Initial welcome message with styling
        self.log_message("="*70)
        self.log_message("  SAP QUANTUM TRANSPORT OPTIMIZER")
        self.log_message("  Powered by Qiskit & RasQberry")
        self.log_message("="*70)
        self.log_message("")
        self.log_message(
            "👋 Welcome! This application uses quantum computing to optimize")
        self.log_message("   logistics and transportation planning.")
        self.log_message("")
        self.log_message("📌 Quick Start:")
        self.log_message(
            "   1. Press 'Load Data' (F5) to load sample shipments")
        self.log_message("   2. Choose an optimization algorithm")
        self.log_message("   3. Compare results from different approaches")
        self.log_message("")
        self.log_message("⚛️  Quantum Status: " +
                         ("Ready" if QUANTUM_AVAILABLE else "Classical Mode Only"))
        self.log_message("="*70)
        self.log_message("")

    def create_footer(self):
        """Create footer with status bar"""
        footer_frame = tk.Frame(
            self.root, bg=self.colors['sap_blue'], height=40)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        footer_frame.pack_propagate(False)

        self.status_label = tk.Label(footer_frame,
                                     text="Ready",
                                     font=('Arial', 10),
                                     bg=self.colors['sap_blue'],
                                     fg=self.colors['white'],
                                     anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, padx=20, fill=tk.X, expand=True)

        # Exit button
        exit_btn = tk.Button(footer_frame, text="Exit",
                             command=self.root.quit,
                             font=('Arial', 10, 'bold'),
                             bg=self.colors['sap_red'], fg='white',
                             relief=tk.FLAT, cursor='hand2',
                             padx=20)
        exit_btn.pack(side=tk.RIGHT, padx=10, pady=5)

    def update_time(self):
        """Update time display"""
        self.time_label.config(text=datetime.now().strftime("%H:%M:%S"))
        self.root.after(1000, self.update_time)

    def log_message(self, message, color='black'):
        """Add message to results area"""
        self.results_text.insert(tk.END, f"{message}\n")
        self.results_text.see(tk.END)
        self.root.update()

    def update_status(self, message):
        """Update status bar"""
        self.status_label.config(text=message)
        self.root.update()

    def load_data(self):
        """Load data from CSV files"""
        self.update_status("Loading data...")
        self.log_message("\n" + "="*60)
        self.log_message("Loading data from CSV files...")

        try:
            data_dir = Path(__file__).parent.parent / "data" / "input"
            loader = CSVLoader(str(data_dir))
            self.data = loader.load_all()

            self.log_message(
                f"✓ Loaded {len(self.data['shipments'])} shipments")
            self.log_message(f"✓ Loaded {len(self.data['trucks'])} trucks")
            self.log_message(f"✓ Loaded {len(self.data['lanes'])} lanes")
            self.log_message("="*60)

            self.update_status("Data loaded successfully")
            messagebox.showinfo("Success", "Data loaded successfully!")

        except Exception as e:
            self.log_message(f"❌ Error loading data: {e}")
            self.update_status("Error loading data")
            messagebox.showerror("Error", f"Failed to load data:\n{e}")

    def run_optimizer(self, algorithm):
        """Run optimization algorithm in background thread"""
        if self.data is None:
            messagebox.showwarning("Warning", "Please load data first!")
            return

        self.current_algorithm = algorithm
        self.update_status(f"Running {algorithm}...")

        # Run in thread to keep GUI responsive
        thread = threading.Thread(
            target=self._run_optimizer_thread, args=(algorithm,))
        thread.daemon = True
        thread.start()

    def _run_optimizer_thread(self, algorithm):
        """Background thread for optimization"""
        try:
            self.log_message(f"\n{'='*60}")
            self.log_message(f"Running {algorithm.upper()} Optimizer...")
            self.log_message(f"{'='*60}")

            if algorithm == 'greedy':
                optimizer = GreedyOptimizer(
                    self.data['shipments'],
                    self.data['trucks'],
                    self.data['lanes']
                )
                result = optimizer.optimize(objective='balanced')

            elif algorithm == 'local_search':
                optimizer = LocalSearchOptimizer(
                    self.data['shipments'],
                    self.data['trucks'],
                    self.data['lanes']
                )
                result = optimizer.optimize(max_iterations=500)

            elif algorithm == 'qaoa':
                if not QUANTUM_AVAILABLE:
                    self.log_message("❌ Quantum optimizer not available")
                    self.update_status("Quantum optimizer not available")
                    return

                optimizer = QAOAOptimizer(
                    self.data['shipments'],
                    self.data['trucks'],
                    self.data['lanes'],
                    qaoa_reps=2,
                    max_iter=50
                )
                result = optimizer.optimize_with_fallback()

            # Display results
            self.display_result(result)
            self.results.append(result)

            self.update_status(f"{algorithm} completed")

        except Exception as e:
            self.log_message(f"❌ Error: {e}")
            self.update_status(f"Error in {algorithm}")

    def display_result(self, result):
        """Display optimization result"""
        self.log_message(f"\nAlgorithm: {result.algorithm}")
        self.log_message(f"Total Cost:     €{result.total_cost:,.2f}")
        self.log_message(f"Total CO₂:      {result.total_co2:,.2f} kg")
        self.log_message(
            f"Time:           {result.computation_time:.3f} seconds")
        self.log_message(f"Trucks Used:    {result.trucks_used}")
        self.log_message(f"Assigned:       {result.shipments_assigned}")
        self.log_message(f"Unassigned:     {result.shipments_unassigned}")
        self.log_message("="*60)

    def compare_all(self):
        """Compare all algorithm results"""
        if len(self.results) < 2:
            messagebox.showinfo(
                "Info", "Run at least 2 algorithms to compare!")
            return

        self.log_message(f"\n{'='*60}")
        self.log_message("ALGORITHM COMPARISON")
        self.log_message(f"{'='*60}")
        self.log_message(
            f"{'Algorithm':<25} {'Cost (€)':<15} {'CO₂ (kg)':<15}")
        self.log_message("-"*60)

        for result in self.results:
            self.log_message(f"{result.algorithm:<25} "
                             f"{result.total_cost:<15,.2f} "
                             f"{result.total_co2:<15,.2f}")

        self.log_message("-"*60)

        # Find best
        best_cost = min(self.results, key=lambda r: r.total_cost)
        best_co2 = min(self.results, key=lambda r: r.total_co2)

        self.log_message(
            f"\n✓ Best Cost: {best_cost.algorithm} (€{best_cost.total_cost:,.2f})")
        self.log_message(
            f"✓ Best CO₂:  {best_co2.algorithm} ({best_co2.total_co2:,.2f} kg)")
        self.log_message("="*60)

    def clear_results(self):
        """Clear results display"""
        self.results_text.delete(1.0, tk.END)
        self.results = []
        self.log_message("="*70)
        self.log_message("  Results cleared. Ready for new optimization.")
        self.log_message("="*70)
        self.update_status("Ready")

    def show_help(self):
        """Show help dialog"""
        help_text = """
SAP Quantum Transport Optimizer - Help

FEATURES:
• Classical Algorithms: Greedy, Local Search
• Quantum Algorithm: QAOA (Quantum Approximate Optimization)
• Multi-objective: Cost & CO₂ optimization

KEYBOARD SHORTCUTS:
• F1  - Show this help
• F5  - Load data
• ESC - Exit fullscreen

ALGORITHMS:
• Greedy: Fast baseline solution
• Local Search: Improved solution with simulated annealing
• QAOA: Quantum optimization (best for small problems)

For more information, visit: https://rasqberry.org
        """
        messagebox.showinfo("Help - Quantum Transport Optimizer", help_text)


def main():
    """Main entry point"""
    root = tk.Tk()
    app = QuantumTransportGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
SAP Quantum Transport Optimizer - Professional SAP-Themed GUI
Optimized for Raspberry Pi Touch Display with SAP Fiori Design Language
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
from PIL import Image, ImageTk

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Try to import quantum optimizer
try:
    from optimizers.quantum.qaoa_optimizer import QAOAOptimizer
    QUANTUM_AVAILABLE = True
except ImportError:
    QUANTUM_AVAILABLE = False


class SAPQuantumTransportGUI:
    """Professional SAP-Themed GUI Application"""

    def __init__(self, root):
        self.root = root
        self.root.title("SAP Quantum Transport Optimizer")

        # Configure for touchscreen
        self.root.geometry("1024x600")

        # SAP Fiori Color Palette
        self.colors = {
            'sap_blue': '#0070F2',  # SAP Blue (Primary)
            'sky_blue': '#74B3F7',  # Sky Blue (Light)
            'white': '#FFFFFF',
            'light_blue': '#E8F4FD',  # Very light blue background
            'dark_blue': '#003366',  # Dark blue for text
            'sap_gold': '#F0AB00',  # SAP Gold accent
            'success_green': '#107E3E',
            'text_dark': '#32363A',
            'border_gray': '#D9D9D9',
            'hover_blue': '#0064D9'
        }

        # Data storage
        self.data = None
        self.results = []
        self.current_algorithm = None

        # Configure root background
        self.root.configure(bg=self.colors['white'])

        # Setup styles
        self.setup_styles()

        # Create main UI
        self.create_widgets()

        # Bind keys
        self.root.bind('<Escape>', lambda e: self.root.quit())
        self.root.bind('<F1>', lambda e: self.show_help())
        self.root.bind('<F5>', lambda e: self.load_data())

    def setup_styles(self):
        """Setup SAP Fiori-inspired styles"""
        style = ttk.Style()
        style.theme_use('clam')

        # Configure button styles
        style.configure('SAP.TButton',
                        font=('Segoe UI', 12, 'bold'),
                        padding=12,
                        background=self.colors['sap_blue'],
                        foreground=self.colors['white'],
                        borderwidth=0)

        style.map('SAP.TButton',
                  background=[('active', self.colors['hover_blue']),
                              ('pressed', self.colors['dark_blue'])])

    def create_widgets(self):
        """Create professional SAP-themed UI"""
        # Header
        self.create_header()

        # Main content area
        self.create_main_area()

        # Footer
        self.create_footer()

    def create_header(self):
        """Create professional SAP header with logo"""
        header_frame = tk.Frame(
            self.root,
            bg=self.colors['sap_blue'],
            height=140
        )
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)

        # Left side - SAP Logo
        logo_frame = tk.Frame(header_frame, bg=self.colors['sap_blue'])
        logo_frame.pack(side=tk.LEFT, padx=30, pady=15)

        try:
            # Try to load SAP Technology Partner logo first, then fallback to sap_logo.png
            logo_paths = [
                Path(__file__).parent.parent / "351288.png",
                Path(__file__).parent.parent /
                "sap_technology_partner_logo.png",
                Path(__file__).parent.parent / "sap_logo.png"
            ]

            logo_loaded = False
            for logo_path in logo_paths:
                if logo_path.exists():
                    logo_img = Image.open(logo_path)
                    # Make logo BIGGER - resize to larger dimensions
                    logo_img.thumbnail((300, 100), Image.Resampling.LANCZOS)
                    self.logo_photo = ImageTk.PhotoImage(logo_img)
                    logo_label = tk.Label(logo_frame, image=self.logo_photo,
                                          bg=self.colors['sap_blue'])
                    logo_label.pack()
                    logo_loaded = True
                    break

            if not logo_loaded:
                raise FileNotFoundError("Logo not found")
        except Exception as e:
            # Fallback: Create SAP text logo
            sap_label = tk.Label(logo_frame,
                                 text="SAP",
                                 font=('Arial Black', 32, 'bold'),
                                 bg=self.colors['sap_blue'],
                                 fg=self.colors['white'])
            sap_label.pack()

        # Center - Title
        title_frame = tk.Frame(header_frame, bg=self.colors['sap_blue'])
        title_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=15)

        title_label = tk.Label(title_frame,
                               text="Quantum Transport Optimizer",
                               font=('Segoe UI', 24, 'bold'),
                               bg=self.colors['sap_blue'],
                               fg=self.colors['white'])
        title_label.pack(anchor=tk.W, padx=20)

        subtitle_label = tk.Label(title_frame,
                                  text="Powered by Qiskit • RasQberry Edition",
                                  font=('Segoe UI', 10),
                                  bg=self.colors['sap_blue'],
                                  fg=self.colors['sky_blue'])
        subtitle_label.pack(anchor=tk.W, padx=20)

        # Right side - Status
        status_frame = tk.Frame(header_frame, bg=self.colors['sap_blue'])
        status_frame.pack(side=tk.RIGHT, padx=30, pady=15)

        self.time_label = tk.Label(status_frame,
                                   text=datetime.now().strftime("%H:%M:%S"),
                                   font=('Segoe UI', 16, 'bold'),
                                   bg=self.colors['sap_blue'],
                                   fg=self.colors['white'])
        self.time_label.pack()

        quantum_text = "⚛️ Quantum Ready" if QUANTUM_AVAILABLE else "Classical Mode"
        quantum_color = self.colors['sap_gold'] if QUANTUM_AVAILABLE else self.colors['sky_blue']

        self.quantum_status = tk.Label(status_frame,
                                       text=quantum_text,
                                       font=('Segoe UI', 9),
                                       bg=self.colors['sap_blue'],
                                       fg=quantum_color)
        self.quantum_status.pack()

        self.update_time()

    def create_main_area(self):
        """Create main content area with SAP Fiori design"""
        # Main container with light blue background
        main_container = tk.Frame(self.root, bg=self.colors['light_blue'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # Left panel - Action buttons
        left_panel = tk.Frame(
            main_container,
            bg=self.colors['white'],
            width=280,
            relief=tk.FLAT,
            bd=0
        )
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0)
        left_panel.pack_propagate(False)

        # Add shadow effect with border
        left_border = tk.Frame(
            left_panel, bg=self.colors['border_gray'], width=1)
        left_border.pack(side=tk.RIGHT, fill=tk.Y)

        # Button container
        button_container = tk.Frame(left_panel, bg=self.colors['white'])
        button_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=20)

        # Section title
        section_label = tk.Label(button_container,
                                 text="ACTIONS",
                                 font=('Segoe UI', 11, 'bold'),
                                 bg=self.colors['white'],
                                 fg=self.colors['text_dark'],
                                 anchor=tk.W)
        section_label.pack(fill=tk.X, pady=(0, 15))

        # Professional SAP-style buttons
        buttons = [
            ("📂  Load Data", self.load_data,
             self.colors['sap_blue'], "primary"),
            ("⚡  Greedy Optimizer", lambda: self.run_optimizer('greedy'),
             self.colors['success_green'], "success"),
            ("🔄  Local Search", lambda: self.run_optimizer('local_search'),
             self.colors['sky_blue'], "secondary"),
            ("⚛️  QAOA Quantum", lambda: self.run_optimizer('qaoa'),
             self.colors['sap_gold'], "accent"),
            ("📊  Compare All", self.compare_all,
             self.colors['sap_blue'], "primary"),
            ("🗑️  Clear Results", self.clear_results,
             self.colors['border_gray'], "default"),
        ]

        for text, command, color, btn_type in buttons:
            self.create_sap_button(
                button_container, text, command, color, btn_type)

        # Right panel - Results display
        right_panel = tk.Frame(main_container, bg=self.colors['white'])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH,
                         expand=True, padx=15, pady=15)

        # Results header
        results_header = tk.Frame(right_panel, bg=self.colors['white'])
        results_header.pack(fill=tk.X, pady=(0, 10))

        results_title = tk.Label(results_header,
                                 text="Results",
                                 font=('Segoe UI', 16, 'bold'),
                                 bg=self.colors['white'],
                                 fg=self.colors['text_dark'])
        results_title.pack(side=tk.LEFT)

        # Results text area with SAP styling
        results_container = tk.Frame(right_panel,
                                     bg=self.colors['border_gray'],
                                     relief=tk.FLAT,
                                     bd=1)
        results_container.pack(fill=tk.BOTH, expand=True)

        self.results_text = scrolledtext.ScrolledText(
            results_container,
            font=('Consolas', 10),
            bg=self.colors['white'],
            fg=self.colors['text_dark'],
            wrap=tk.WORD,
            relief=tk.FLAT,
            bd=0,
            padx=15,
            pady=15
        )
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        # Welcome message
        self.log_message("="*70, self.colors['sap_blue'])
        self.log_message("  SAP QUANTUM TRANSPORT OPTIMIZER",
                         self.colors['sap_blue'])
        self.log_message("  Powered by Qiskit & RasQberry",
                         self.colors['sky_blue'])
        self.log_message("="*70, self.colors['sap_blue'])
        self.log_message("")
        self.log_message("👋 Welcome to the SAP Quantum Transport Optimizer!")
        self.log_message("")
        self.log_message("📌 Quick Start:")
        self.log_message("   1. Press 'Load Data' to load sample shipments")
        self.log_message("   2. Choose an optimization algorithm")
        self.log_message("   3. Compare results from different approaches")
        self.log_message("")
        status_text = "Ready" if QUANTUM_AVAILABLE else "Classical Mode Only"
        self.log_message(f"⚛️  Quantum Status: {status_text}")
        self.log_message("="*70, self.colors['border_gray'])
        self.log_message("")

    def create_sap_button(self, parent, text, command, color, btn_type):
        """Create a professional SAP Fiori-style button"""
        btn_frame = tk.Frame(parent, bg=self.colors['white'])
        btn_frame.pack(fill=tk.X, pady=6)

        # Determine text color based on button type
        if btn_type == 'default':
            text_color = self.colors['text_dark']
            hover_color = self.colors['border_gray']
        else:
            text_color = self.colors['white']
            hover_color = color

        btn = tk.Button(btn_frame,
                        text=text,
                        command=command,
                        font=('Segoe UI', 12, 'bold'),
                        bg=color,
                        fg=text_color,
                        activebackground=hover_color,
                        activeforeground=self.colors['white'],
                        relief=tk.FLAT,
                        bd=0,
                        height=2,
                        cursor='hand2',
                        padx=15,
                        pady=8)
        btn.pack(fill=tk.BOTH, expand=True)

        # Hover effects
        def on_enter(e):
            if btn_type == 'default':
                btn.config(bg=self.colors['text_dark'],
                           fg=self.colors['white'])
            else:
                btn.config(bg=self.colors['hover_blue'])

        def on_leave(e):
            btn.config(bg=color, fg=text_color)

        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)

    def create_footer(self):
        """Create professional footer"""
        footer_frame = tk.Frame(
            self.root,
            bg=self.colors['light_blue'],
            height=50
        )
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        footer_frame.pack_propagate(False)

        # Status bar
        status_container = tk.Frame(footer_frame, bg=self.colors['white'])
        status_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=8)

        self.status_label = tk.Label(status_container,
                                     text="Ready",
                                     font=('Segoe UI', 10),
                                     bg=self.colors['white'],
                                     fg=self.colors['text_dark'],
                                     anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, padx=10)

        # Exit button
        exit_btn = tk.Button(status_container,
                             text="Exit",
                             command=self.root.quit,
                             font=('Segoe UI', 10, 'bold'),
                             bg=self.colors['border_gray'],
                             fg=self.colors['text_dark'],
                             activebackground=self.colors['text_dark'],
                             activeforeground=self.colors['white'],
                             relief=tk.FLAT,
                             cursor='hand2',
                             padx=20,
                             pady=5)
        exit_btn.pack(side=tk.RIGHT, padx=10)

    def update_time(self):
        """Update time display"""
        self.time_label.config(text=datetime.now().strftime("%H:%M:%S"))
        self.root.after(1000, self.update_time)

    def log_message(self, message, color=None):
        """Add message to results area with optional color"""
        self.results_text.insert(tk.END, f"{message}\n")
        if color:
            # Color the last line
            last_line_start = self.results_text.index("end-2c linestart")
            last_line_end = self.results_text.index("end-1c")
            tag_name = f"color_{color}"
            self.results_text.tag_config(tag_name, foreground=color)
            self.results_text.tag_add(tag_name, last_line_start, last_line_end)
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
        self.log_message("Loading data from CSV files...",
                         self.colors['sap_blue'])

        try:
            data_dir = Path(__file__).parent.parent / "data" / "input"
            loader = CSVLoader(str(data_dir))
            self.data = loader.load_all()

            self.log_message(
                f"✓ Loaded {len(self.data['shipments'])} shipments", self.colors['success_green'])
            self.log_message(
                f"✓ Loaded {len(self.data['trucks'])} trucks", self.colors['success_green'])
            self.log_message(
                f"✓ Loaded {len(self.data['lanes'])} lanes", self.colors['success_green'])
            self.log_message("="*60)

            self.update_status("Data loaded successfully")
            messagebox.showinfo("Success", "Data loaded successfully!")

        except Exception as e:
            self.log_message(
                f"❌ Error loading data: {e}", self.colors['text_dark'])
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
            self.log_message(
                f"Running {algorithm.upper()} Optimizer...", self.colors['sap_blue'])
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

                # Use smaller problem for faster QAOA on Raspberry Pi
                limited_shipments = self.data['shipments'][:2]
                limited_trucks = self.data['trucks'][:2]

                self.log_message(
                    f"Using {len(limited_shipments)} shipments and {len(limited_trucks)} trucks for QAOA demo")
                self.log_message(
                    "(Full problem would take too long on Raspberry Pi)")

                optimizer = QAOAOptimizer(
                    limited_shipments,
                    limited_trucks,
                    self.data['lanes'],
                    qaoa_reps=2,
                    max_iter=100
                )
                result = optimizer.optimize_with_fallback(
                    progress_callback=self.log_message
                )

            # Display results
            self.display_result(result)
            self.results.append(result)

            self.update_status(f"{algorithm} completed")

        except Exception as e:
            self.log_message(f"❌ Error: {e}")
            import traceback
            self.log_message(traceback.format_exc())
            self.update_status(f"Error in {algorithm}")

    def display_result(self, result):
        """Display optimization result with SAP styling"""
        self.log_message(
            f"\nAlgorithm: {result.algorithm}", self.colors['sap_blue'])
        self.log_message(
            f"Total Cost:     €{result.total_cost:,.2f}", self.colors['text_dark'])
        self.log_message(
            f"Total CO₂:      {result.total_co2:,.2f} kg", self.colors['text_dark'])
        self.log_message(
            f"Time:           {result.computation_time:.3f} seconds", self.colors['text_dark'])
        self.log_message(
            f"Trucks Used:    {result.trucks_used}", self.colors['text_dark'])
        self.log_message(
            f"Assigned:       {result.shipments_assigned}", self.colors['success_green'])
        self.log_message(
            f"Unassigned:     {result.shipments_unassigned}", self.colors['text_dark'])
        self.log_message("="*60)

    def compare_all(self):
        """Compare all algorithm results"""
        if len(self.results) < 2:
            messagebox.showinfo(
                "Info", "Run at least 2 algorithms to compare!")
            return

        self.log_message(f"\n{'='*60}")
        self.log_message("ALGORITHM COMPARISON", self.colors['sap_blue'])
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
            f"\n✓ Best Cost: {best_cost.algorithm} (€{best_cost.total_cost:,.2f})",
            self.colors['success_green'])
        self.log_message(
            f"✓ Best CO₂:  {best_co2.algorithm} ({best_co2.total_co2:,.2f} kg)",
            self.colors['success_green'])
        self.log_message("="*60)

    def clear_results(self):
        """Clear results display"""
        self.results_text.delete(1.0, tk.END)
        self.results = []
        self.log_message("="*70, self.colors['sap_blue'])
        self.log_message(
            "  Results cleared. Ready for new optimization.", self.colors['text_dark'])
        self.log_message("="*70, self.colors['sap_blue'])
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
• ESC - Exit application

ALGORITHMS:
• Greedy: Fast baseline solution
• Local Search: Improved solution with simulated annealing
• QAOA: Quantum optimization (best for small problems)

For more information, visit: https://rasqberry.org
        """
        messagebox.showinfo(
            "Help - SAP Quantum Transport Optimizer", help_text)


def main():
    """Main entry point"""
    root = tk.Tk()
    app = SAPQuantumTransportGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

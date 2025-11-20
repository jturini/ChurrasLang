import tkinter as tk
from tkinter import ttk, scrolledtext, font, simpledialog, filedialog

from parser_churras import compile_churras

# --- CORES E FONTES ---
COLOR_BACKGROUND = "#282c34"
COLOR_FRAME = "#21252b"
COLOR_TEXT_AREA_BG = "#282c34"
COLOR_TEXT = "#abb2bf"
COLOR_ERROR_BG = "#5e2323"
COLOR_ACCENT = "#61afef"
COLOR_SUCCESS_BG = "#2f4f4f"
COLOR_ERROR_FG = "#ff6b6b"
COLOR_SUCCESS_FG = "#8fbc8f"

FONT_CODE = ("Consolas", 12)
FONT_UI = ("Segoe UI", 10)

# --- EXEMPLOS DE CÓDIGO ---
EXAMPLE_VALID = """INICIAR_CHURRAS
DESPENSA
    convidados : PICANHA;
    linguicas : PICANHA;
COZINHAR
    SERVIR "Planejador de Churrasco";
    PROVAR convidados;

    linguicas = convidados * 2;

    SERVIR "Para os convidados, sera necessario:";
    SERVIR linguicas;
    SERVIR "linguicas.";
FIM_CHURRAS"""

EXAMPLE_ERROR = """INICIAR_CHURRAS
# Exemplo com erros sintáticos e semânticos
DESPENSA
    a : PICANHA; # Ponto e vírgula faltando aqui
COZINHAR
    a = "texto"; # Erro semântico
    SERVIR b;    # Variável não declarada
    SERVIR 10 / 0; # Divisão por zero
FIM_CHURRAS"""

class LineNumbers(tk.Canvas):
    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs)
        self.text_widget = None

    def attach(self, text_widget):
        self.text_widget = text_widget

    def redraw(self, *args):
        self.delete("all")
        i = self.text_widget.index("@0,0")
        while True:
            dline = self.text_widget.dlineinfo(i)
            if dline is None: break
            y = dline[1]
            line_num = str(i).split(".")[0]
            self.create_text(2, y, anchor="nw", text=line_num, fill=COLOR_TEXT, font=FONT_UI)
            i = self.text_widget.index(f"{i}+1line")

class ChurrasIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("🥩🔥 ChurrasLang IDE")
        self.root.geometry("1200x700")
        self.root.configure(bg=COLOR_BACKGROUND)

        # --- CONFIGURAÇÃO DE ESTILO PARA O TREEVIEW ---
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background=COLOR_TEXT_AREA_BG,
                        foreground=COLOR_TEXT,
                        fieldbackground=COLOR_TEXT_AREA_BG,
                        borderwidth=0)
        style.layout("Treeview.Heading", [('Treeview.heading.cell', {'sticky': 'nswe'})])
        style.configure("Treeview.Heading",
                        background=COLOR_FRAME,
                        foreground=COLOR_ACCENT,
                        font=(FONT_UI[0], 10, 'bold'),
                        padding=(10, 5))
        style.map('Treeview',
                  background=[('selected', COLOR_ACCENT)],
                  foreground=[('selected', 'white')])

        self._setup_widgets()
        self._setup_tags()
        self.code_input.focus_set()

    def _setup_widgets(self):
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)
        file_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Abrir", command=self._open_file)
        file_menu.add_command(label="Salvar", command=self._save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.root.quit)

        example_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Exemplos", menu=example_menu)
        example_menu.add_command(label="Código Válido (PROVAR)", command=lambda: self._load_example(EXAMPLE_VALID))
        example_menu.add_command(label="Código com Erros", command=lambda: self._load_example(EXAMPLE_ERROR))
        example_menu.add_command(label="Limpar Editor", command=self._clear_all)

        main_pane = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, bg=COLOR_BACKGROUND)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        editor_frame = tk.Frame(main_pane, bg=COLOR_FRAME)
        self.line_numbers = LineNumbers(editor_frame, width=30, bg=COLOR_FRAME, highlightthickness=0)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        self.code_input = scrolledtext.ScrolledText(editor_frame, wrap=tk.WORD, undo=True,
            font=FONT_CODE, bg=COLOR_TEXT_AREA_BG, fg=COLOR_TEXT, insertbackground="white",
            relief=tk.FLAT, borderwidth=0, highlightthickness=0)
        self.code_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.line_numbers.attach(self.code_input)
        main_pane.add(editor_frame, minsize=400)

        right_frame = tk.Frame(main_pane, bg=COLOR_BACKGROUND)
        main_pane.add(right_frame, minsize=500)

        tk.Label(right_frame, text="Tabela de Tokens", font=(FONT_UI[0], 11, 'bold'), bg=COLOR_BACKGROUND, fg=COLOR_ACCENT).pack(anchor="w", pady=(0,5))
        token_frame = tk.Frame(right_frame)
        token_frame.pack(fill=tk.BOTH, expand=True)
        self.token_tree = ttk.Treeview(token_frame, columns=("Type", "Lexeme", "Position"), show="headings")
        self.token_tree.heading("Type", text="Tipo de Token")
        self.token_tree.heading("Lexeme", text="Lexema")
        self.token_tree.heading("Position", text="Posição (L, C)")
        self.token_tree.column("Type", width=150)
        self.token_tree.column("Lexeme", width=200)
        self.token_tree.column("Position", width=100)
        self.token_tree.pack(fill=tk.BOTH, expand=True)

        tk.Label(right_frame, text="Saída do Programa", font=(FONT_UI[0], 11, 'bold'), bg=COLOR_BACKGROUND, fg=COLOR_ACCENT).pack(anchor="w", pady=(10,5))
        self.output_display = scrolledtext.ScrolledText(right_frame, font=FONT_CODE, 
            height=5, bg=COLOR_TEXT_AREA_BG, fg="white", relief=tk.FLAT)
        self.output_display.pack(fill=tk.BOTH, expand=False, pady=(0,10))
        self.output_display.config(state=tk.DISABLED)
        
        status_frame = tk.Frame(self.root, bg=COLOR_BACKGROUND)
        status_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        self.status_label = tk.Label(status_frame, text="Pronto para assar!", font=FONT_UI, bg=COLOR_FRAME, fg=COLOR_TEXT, anchor='w', padx=10, pady=5)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.compile_button = ttk.Button(status_frame, text="🥩 ASSAR CÓDIGO", command=self.run_compiler)
        self.compile_button.pack(side=tk.RIGHT, padx=(10,0))

        self.code_input.bind("<<Modified>>", self._on_text_change)
        self.code_input.bind("<Configure>", self._on_text_change)
        
        self._load_example(EXAMPLE_VALID)

    def _on_text_change(self, event=None):
        self.line_numbers.redraw()
        self.code_input.edit_modified(False)

    def _setup_tags(self):
        self.code_input.tag_configure("error", background=COLOR_ERROR_BG)
        # TAGS PARA AS CORES ALTERNADAS DA TABELA
        self.token_tree.tag_configure('evenrow', background=COLOR_TEXT_AREA_BG)
        self.token_tree.tag_configure('oddrow', background=COLOR_FRAME)

    def _clear_tags(self):
        self.code_input.tag_remove("error", "1.0", "end")

    def _highlight_error(self, token):
        if token:
            start = f"{token.line}.{token.col - 1}"
            line_end = self.code_input.index(f"{start} lineend")
            self.code_input.tag_add("error", f"{start} linestart", line_end)
            self.code_input.see(start)

    def _load_example(self, content):
        self._clear_all()
        self.code_input.insert("1.0", content)

    def _clear_all(self):
        self._clear_tags()
        self.code_input.delete("1.0", "end")
        self.token_tree.delete(*self.token_tree.get_children())
        self.output_display.config(state=tk.NORMAL)
        self.output_display.delete("1.0", "end")
        self.output_display.config(state=tk.DISABLED)
        self.status_label.config(text="Pronto para assar!", fg=COLOR_TEXT, bg=COLOR_FRAME)
    
    def _open_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("ChurrasLang Files", "*.churras"), ("All Files", "*.*")])
        if not filepath: return
        with open(filepath, "r", encoding='utf-8') as f:
            self._load_example(f.read())

    def _save_file(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".churras", filetypes=[("ChurrasLang Files", "*.churras"), ("All Files", "*.*")])
        if not filepath: return
        with open(filepath, "w", encoding='utf-8') as f:
            f.write(self.code_input.get("1.0", "end-1c"))

    def run_compiler(self):
        self._clear_tags()
        self.token_tree.delete(*self.token_tree.get_children())
        self.output_display.config(state=tk.NORMAL)
        self.output_display.delete("1.0", "end")

        code_text = self.code_input.get("1.0", "end-1c")
        result = compile_churras(code_text, self.root)

        count = 0
        for token_line in result.get("tokens", []):
            parts = token_line.split('|')
            tag = 'evenrow' if count % 2 == 0 else 'oddrow'
            self.token_tree.insert("", "end", values=(parts[0].strip(), parts[1].strip(), parts[2].strip()), tags=(tag,))
            count += 1

        self.output_display.insert("1.0", result.get("output", ""))
        self.output_display.config(state=tk.DISABLED)

        msg = f'[{result.get("error_stage", "Sucesso")}] {result.get("error_message", "Pronto.")}'
        self.status_label.config(text=msg)
        
        if result["status"] == "error":
            self.status_label.config(bg=COLOR_ERROR_BG, fg=COLOR_ERROR_FG)
            self._highlight_error(result.get("error_token"))
        else:
            self.status_label.config(bg=COLOR_SUCCESS_BG, fg=COLOR_SUCCESS_FG)

if __name__ == "__main__":
    root = tk.Tk()
    ide = ChurrasIDE(root)
    root.mainloop()
# Arquivo: main.py (para executar no terminal)

from parser_churras import compile_churras

def main():
    print("\n--- Compilador ChurrasLang (Modo Terminal) ---")
    print("Digite ou cole seu código. Pressione Enter em uma linha vazia e digite 'ASSAR' para compilar.")
    
    lines = []
    while True:
        try:
            line = input()
            # Uma forma de "sinalizar" o fim da entrada no terminal
            if line.strip().upper() == 'ASSAR':
                break
            lines.append(line)
        except EOFError:
            break
            
    code = "\n".join(lines)
    
    # Chama o compilador SEM passar a referência da janela.
    # O segundo argumento (root_window) será None por padrão.
    result = compile_churras(code)

    print("\n" + "="*50)
    print("--- RELATÓRIO DA COMPILAÇÃO ---")
    print("="*50)

    # Exibe os tokens de forma legível
    print("\n[TOKENS RECONHECIDOS]")
    if result.get("tokens"):
        for token_line in result["tokens"]:
            print(token_line)
    else:
        print("<nenhum>")

    # Exibe a mensagem de status (sucesso ou erro)
    print(f'\n[STATUS: {result.get("error_stage", "Sucesso")}]')
    print(result.get("error_message", "Pronto."))

    # Exibe a saída do programa, se houver
    if result["status"] == "success":
        print("\n[SAÍDA DO PROGRAMA]")
        print(result.get("output", "<nenhuma>"))
    
    print("\n" + "="*50)


if __name__ == "__main__":
    main()
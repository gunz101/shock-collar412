# Ponte Python

A fazer. Responsabilidades:

- dona da porta serial do ESP32
- valida a senha e emite tokens de sessao
- aplica os limites: teto de intensidade, duracao maxima, intervalo minimo, limite por minuto
- servidor HTTP local que a pagina do GitHub Pages consome pelo tunel Cloudflare
- detector de palavras offline com Vosk

A senha global de administrador fica em `config.toml`, que esta no .gitignore.

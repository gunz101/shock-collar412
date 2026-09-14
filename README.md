# Collar Console

Controle de uma coleira de adestramento de 433 MHz a partir do PC, sem nuvem de terceiros
e sem alteração física no computador. O objetivo final tem três gatilhos:

1. **Painel web** com senha, acessível de qualquer lugar.
2. **Palavras no microfone**, detectadas offline, cada uma com sua intensidade.
3. **Minecraft**, com o dano recebido virando choque proporcional.

> **Simulação ao vivo:** [`docs/index.html`](docs/index.html) roda sem nenhum hardware.
> Serve para aprovar o desenho e as funções antes das peças chegarem.

---

## Como funciona

```
navegador  ──HTTPS──►  túnel Cloudflare  ──►  ponte 
                                                  │  valida senha, emite token,
                                                  │  aplica os limites de segurança
                                                  ▼
                                             USB serial
                                                  │
                                              ESP32 + FS1000A
                                                  │  433,92 MHz ASK/OOK
                                                  ▼
                                               coleira
```


---


## Estrutura

```
docs/        página publicada no GitHub Pages (a simulação)
hardware/    lista de compras, ligações, referência de protocolo
firmware/    código do ESP32 (a fazer)
ponte/       serviço Python: serial, autenticação, limites, servidor local (a fazer)
```

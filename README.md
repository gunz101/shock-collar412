# COLEIRA · CONTROLE

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
navegador  ──HTTPS──►  túnel Cloudflare  ──►  ponte Python (seu PC)
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

**A regra que não muda:** os limites de segurança vivem na ponte e no firmware, nunca na
página. A página apenas pede. Se a senha vazar ou o HTML for adulterado, ninguém passa do
que foi autorizado localmente.

---

## Estado

| Parte | Situação |
|---|---|
| Pesquisa de protocolo | concluída |
| Lista de compras | fechada, aguardando entrega |
| Simulação do painel | funcional, em aprovação |
| Firmware do ESP32 | não iniciado |
| Ponte Python | não iniciada |
| Integração com Minecraft | não iniciada |

---

## Estrutura

```
docs/        página publicada no GitHub Pages (a simulação)
hardware/    lista de compras, ligações, referência de protocolo
firmware/    código do ESP32 (a fazer)
ponte/       serviço Python: serial, autenticação, limites, servidor local (a fazer)
DEVLOG.md    registro de decisões, em ordem cronológica
```

---

## Segurança

Leia antes de encostar na coleira.

- Nunca no pescoço, no peito ou sobre a coluna. Coxa, panturrilha ou braço.
- Nunca tocar os dois pinos ao mesmo tempo com as duas mãos.
- Começar em intensidade 5 a 10, com 300 ms, e subir devagar.
- Não usar com problema cardíaco, marcapasso, epilepsia ou gravidez.
- O corte de emergência é físico: puxar o jumper do VCC ou o cabo USB.
- Somente adultos, somente com consentimento.

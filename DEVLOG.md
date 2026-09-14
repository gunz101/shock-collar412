# Devlog

Registro cronológico das decisões. Entrada nova vai no topo.

---

## 2026-09-13 · Painel ganha paletas, padrões e limites de verdade

Reescrita da simulação a partir do que o Lovense Remote faz de fato.

Funções trazidas de lá e adaptadas para a coleira:

- **Três estilos de controle** no mesmo painel: círculo, barra vertical e campo XY.
  O Lovense chama de Circular, Traditional e Floating. No XY o eixo horizontal é
  intensidade e o vertical é duração, então um gesto só define os dois.
- **Padrões pré-prontos**, equivalentes aos Earthquake, Fireworks, Wave e Pulse:
  Terremoto, Fogos, Onda e Pulso, cada um com miniatura da forma de onda.
- **Velocidade de 0,25× a 4×**, a mesma faixa do app original.
- **Editor de padrão próprio**, desenhado arrastando sobre dezesseis barras.
- **Ativação por som** com sensibilidade regulável, que no sistema real será o
  microfone do PC. É o mesmo caminho do detector de palavras.
- **Links de controle**, equivalentes ao Control Link: cada convidado recebe um
  endereço próprio, com teto de intensidade e validade independentes, e revogar
  um não derruba os outros.
- **Modo jogo** reservado para o Minecraft, desligado até a fase 3.

Cinco paletas para escolher: Neon tático, Lovense claro, Petplay, Couro e Cyber.
A troca é por token de CSS, então adotar uma delas depois é mudar uma linha.

**Os limites agora funcionam de verdade na simulação.** O painel de administrador
edita teto de intensidade, duração máxima, intervalo mínimo e limite por minuto, e
o disparo passa a respeitar os quatro. Pedido acima do teto entra no histórico como
recusado ou limitado, com o motivo. Isso existe para provar o princípio antes do
código real: quem decide é a camada local, não a tela.

Nome mudou de "Coleira Remota" para **COLEIRA · CONTROLE**.

---

## 2026-09-13 · Desenho do painel web

Primeira versão da simulação. Decisões de arquitetura:

- **A página é estática e pode morar no GitHub Pages.** Ela não guarda senha nenhuma.
- **A ponte no PC é a autoridade.** Recebe a senha, devolve um token de sessão,
  valida esse token a cada comando e aplica os limites.
- **Trocar a senha invalida todos os tokens na hora.** Quem estava logado com a senha
  antiga é recusado no próximo comando e volta para a tela de entrada, mesmo com um
  disparo já em andamento.
- **Senha global de administrador** fica em `config.toml` no PC e sempre funciona.
  O mesmo arquivo redefine a senha de acesso caso ela seja esquecida.
- **Cloudflare Tunnel** em vez de VPS. O PC precisa estar ligado de qualquer forma,
  porque é ele que segura a porta serial. O túnel dá HTTPS de graça, sem abrir porta
  no roteador.

---

## 2026-09-13 · Compras fechadas

| Item | Preço |
|---|---|
| Coleira PuPoPan, 0 a 99, 3 canais | R$ 74,44 |
| ESP32 DevKit 30 pinos, pinos soldados | R$ 35,88 |
| Kit FS1000A + MX-RM-5V | R$ 20,90 |
| Antena helicoidal SW433-TH22, duas unidades | R$ 25,78 |
| Jumpers fêmea-fêmea, 40 unidades | R$ 17,97 |
| Receptor RXB6 super-heteródino | R$ 35,05 |
| **Total** | **R$ 210,02** |

Mais um cabo micro USB de dados, e possivelmente um cabo de carga DC 3,5 × 1,35 mm
para a coleira, que não usa micro USB.

Protoboard e jumpers macho-macho foram cortados: com seis fios no total, a ligação
direta de módulo para placa é mais simples e não precisa de solda. O RXB6 é alimentado
pelo pino VIN de 5 V, o que resolve a disputa pelo único pino 3V3.

---

## 2026-09-13 · Pesquisa de protocolo

Seis frentes de pesquisa em paralelo, seguidas de verificação adversarial. Dez
afirmações confirmadas, uma refutada, oito não verificadas por limite de sessão.

**Correção importante.** A suposição inicial de que a ROJECO PD521 seria inviável
estava errada. O registro FCC ID **2A5H7-PD529**, da Shenzhen PaiPai Technology,
cobre explicitamente o modelo PD 521 e é concedido em **433,92 MHz ASK**, antena
mola, um canal de rádio. A carta de diferença de modelos do próprio processo lista
PD 529, PD 521, PD 522, PD 523 e outros como o mesmo circuito e o mesmo módulo de
rádio. As fotos internas mostram cristal de 26 MHz e transmissor SOT23-6.

A afirmação refutada foi a de que a ROJECO seria oficialmente fabricada pela
PaiPaitek. As especificações batem e a PaiPaitek oferece OEM, mas o vínculo
societário não se sustenta nas fontes.

**Consultas à FCC a partir do Brasil** precisam ser feitas em `apps.fcc.gov`.
Os espelhos fccid.io, fcc.report e manuals.plus devolvem 403 para a região BR.
O código de produto precisa incluir o hífen na busca.

**Nenhuma coleira barata de 433 MHz já analisada usa código rolante.** Todas usam
quadro fixo com identificador do transmissor, canal, modo, intensidade e checksum.
Reprodução do sinal funciona.

Escolha final: **PuPoPan**, pelos níveis de 0 a 99 e três canais, que são a
assinatura da família CaiXianlin, cujo protocolo já está implementado e publicado.
Se bater, a engenharia reversa é pulada inteira.

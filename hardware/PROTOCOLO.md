# Protocolos de rádio das coleiras de 433 MHz

Referência reunida da pesquisa. Todos os tempos em microssegundos, modulação ASK/OOK,
portadora em 433,92 MHz (a CaiXianlin é descrita como 433,95 MHz em algumas fontes).

**Nenhum destes usa código rolante.** O quadro é estático e determinístico, montado a
partir de identificador, canal, modo e intensidade. Reprodução do sinal funciona.

A coleira só age **enquanto o quadro se repete**. Duração desejada equivale a repetir o
quadro pelo tempo correspondente, algo em torno de 45 ms por quadro.

---

## CaiXianlin  ·  o alvo provável da PuPoPan

Fonte: `CaiXianlinEncoder.cpp`, firmware do OpenShock.

```
preâmbulo   1400 alto  +  750 baixo
bit 1        750 alto  +  250 baixo
bit 0        250 alto  +  750 baixo

payload (32 bits)   [id:16][canal:4][tipo:4][intensidade:8]
checksum  (8 bits)  soma de 8 bits do payload
pós-âmbulo (3 bits) zeros

tipo   1 = choque    2 = vibração    3 = bipe
canal  0 a 2         intensidade 0 a 99
```

Identificação da coleira: níveis de **0 a 99** e **três canais**. Vendida também com as
marcas Heaflex e PuPoPan. Carrega por conector barril **DC 3,5 × 1,35 mm**, não micro USB.

**Pareamento:** ligar, segurar o botão até apitar com o LED piscando rápido, e enviar um
bipe com o identificador escolhido. O identificador é inventado por você, o controle de
fábrica não é necessário.

Para manter o controle original funcionando junto, capture um quadro dele com o RXB6,
extraia os 16 bits do identificador e use o mesmo valor no firmware. Assim os dois
convivem sem disputa e sem parear de novo.

---

## Petrainer 998DR / 998DRB

```
sync    1250 a 1550 alto  +  750 a 800 baixo
bit 1    740 a 750 alto   +  250 a 300 baixo
bit 0    220 a 250 alto   +  750 a 820 baixo

42 bits: cabeçalho 2 + canal 4 + comando 3 + id 17 + intensidade 7
         + checksum 3 + checksum de canal 4 + rodapé 2
comando  001 choque   010 vibração   100 bipe
intensidade 0 a 100
```

---

## Petrainer antigo, não 998DR

Bits por posição de pulso, não por largura.

```
preâmbulo   750 alto  +  750 baixo
bit 1       200 alto  + 1500 baixo
bit 0       200 alto  +  750 baixo
```

---

## D80

```
preâmbulo   1900 alto  + 4000 baixo
bit 1        900 alto  +  300 baixo
bit 0        300 alto  +  900 baixo
pós-âmbulo   200 alto  + 2200 baixo

payload 32 bits = 0x04000000 | id<<8 | (tipo & 3)<<6 | (canal & 3)<<4 | (intensidade & 0xF)
mais checksum de soma 8 bits, 40 bits no total
intensidade 0 a 15, apenas dezesseis níveis
```

---

## T330 (Wellturn)

Também estático. Implementado no firmware do OpenShock. Raramente encontrado.

---

## Modo descoberta

Com os cinco encoders no firmware, a identificação leva menos de um minuto e não envolve
choque nenhum:

1. Colocar a coleira em pareamento.
2. Emitir **apenas bipe**, tipo 3, percorrendo os cinco protocolos em sequência.
3. O protocolo certo é aquele em que a coleira responde com um apito.

Se nenhum responder, a coleira é de uma família não documentada e entra a fase 2:
capturar o controle original com o RXB6.

---

## Captura, caso seja necessária

- Usar o **RXB6 super-heteródino**. O MX-RM-5V que vem no kit do FS1000A é
  super-regenerativo e despeja ruído contínuo na saída de dados mesmo sem sinal.
- **Não usar a biblioteca rc-switch.** O limite `RCSWITCH_MAX_CHANGES` é 67 transições,
  o que dá 32 bits, e estes quadros têm 40 ou mais. Também descarta intervalos abaixo
  de 4300 µs, e o espaço entre quadros aqui é de 750 µs.
- Usar registro bruto por interrupção, no estilo do `SimpleRcScanner.ino`, ou a
  biblioteca `RFControl` do pimatic, que monta o quadro sozinha pelo intervalo final
  e só reporta depois de duas cópias iguais.
- No ESP32, transmitir pelo periférico **RMT**, não por software. O WiFi introduz de
  40 a 50 µs de tremor, o que é fatal para pulsos de 250 µs.

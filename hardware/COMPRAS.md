# Peças e ligações

## Comprado

| Item | Função | Preço |
|---|---|---|
| Coleira PuPoPan, 3300 ft, 0 a 99, 3 canais | o alvo | R$ 74,44 |
| ESP32 DevKit, 30 pinos, pinos soldados | gera os pulsos pelo periférico RMT | R$ 35,88 |
| Kit FS1000A + MX-RM-5V, 433 MHz | transmissor (o receptor do kit não presta) | R$ 20,90 |
| Antena helicoidal SW433-TH22, 2 unidades | uma por módulo | R$ 25,78 |
| Jumpers fêmea-fêmea, 40 unidades | liga módulo na placa sem solda | R$ 17,97 |
| Receptor RXB6 super-heteródino | captura, caso a descoberta falhe | R$ 35,05 |
| **Total** | | **R$ 210,02** |

## Ainda falta

- **Cabo micro USB de dados.** A placa usa micro USB, não USB-C. Cabo só de carga
  não funciona. 1,5 m a 2 m, para deixar a placa longe do gabinete, que bloqueia rádio.
- **Cabo de carga da coleira**, se não vier na caixa. Conector barril DC 3,5 × 1,35 mm.

## Descartado, e por quê

- **Protoboard.** Seis fios no total não justificam. A placa de 30 pinos ainda é larga
  demais e deixa só uma fileira de furos livre de cada lado.
- **Jumpers macho-macho.** Só serviriam com a protoboard.
- **Analisador lógico de 24 MHz.** Facilitaria a captura, mas o próprio ESP32 registra
  os tempos e envia pela serial. Comprar só se a fase 2 ficar difícil.

## Ligações

Fase 1, transmitir, três fios:

```
ESP32 3V3     →  FS1000A VCC
ESP32 GND     →  FS1000A GND
ESP32 GPIO 4  →  FS1000A DATA
```

Fase 2, capturar, mais três. Os dois módulos podem ficar ligados juntos:

```
ESP32 VIN 5V  →  RXB6 VCC     (o RXB6 aceita de 3 a 5,5 V, o que libera o único 3V3)
ESP32 GND     →  RXB6 GND
ESP32 GPIO 5  →  RXB6 DATA
```

Ler a serigrafia das plaquinhas, não contar posição de pino. O RXB6 tem oito pinos e
só três são usados. O pino marcado DER é uma saída analógica auxiliar e é ignorado.

Antena no furo ANT de cada módulo. Se o alcance ficar curto, mover o VCC do FS1000A
do 3V3 para o VIN de 5 V, mantendo o DATA no GPIO. É seguro, porque DATA é entrada do
transmissor e nada de 5 V volta para a placa.

## Alcance esperado

| Configuração | Dentro de casa | Ao ar livre |
|---|---|---|
| FS1000A a 3,3 V, antena mola | 5 a 15 m | 20 a 40 m |
| FS1000A a 5 V, antena mola | 20 a 40 m | 60 a 100 m |
| FS1000A a 5 V, fio reto de 17,3 cm | 30 a 50 m | 100 a 150 m |

O fio reto de um quarto de onda rende mais que a antena mola, e sai de graça.

Medir de verdade com o **modo bipe**, que é inofensivo: disparar a cada dois segundos e
andar pela casa até parar de responder.

## Nota legal

A faixa de 433 a 435 MHz é de radiação restrita no Brasil, pela Resolução 680/2017,
com limite de 10 mW e sem necessidade de licença. A Anatel formalmente exige
homologação mesmo para uso próprio, o que deixa um transmissor caseiro numa zona
cinzenta. Isto não é orientação jurídica.

# Interface visual renovada

A mesa e as 40 faces das cartas são imagens rasterizadas em alta resolução com antialiasing e redução Lanczos. As cartas são armazenadas em `assets/` e carregadas pela interface com `pygame.transform.smoothscale`. Não é necessário Pillow para executar o jogo: as imagens já estão incluídas.

## Execução

```bash
python -m pip install pygame-ce
python main.py
```

No Mac, use o mesmo interpretador no qual instalou o pygame-ce. Exemplo:

```bash
/opt/homebrew/bin/python3.14 main.py
```

## Notas

A lógica de truco não foi modificada. O novo tema substitui somente a renderização gráfica. A interface mantém tamanho lógico de 1200 × 780; em monitores Retina, a renderização do Pygame continua dependente da escala de janela do sistema.

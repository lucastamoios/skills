# Coleta no BRCondos

## Pagina e filtros

Usar `https://ssl.brcondos.com.br/Persons/AccessHistory`. Se a pagina de login aparecer, pedir ao usuario que entre no portal e avise quando estiver pronto. Nao preencher nem submeter credenciais.

O formulario real usa:

- acao: `/Persons/GetHistory`
- formulario: `#form_post`
- inicio: `#Filter_DateStart`
- fim: `#Filter_DateEnd`
- pessoa: `#Filter_Names`
- cartoes: `.container-box .item-flex.brc-bordered-item`

Usar o skill de controle do Chrome e seguir suas regras de localizadores, unicidade e confirmacao.

## Selecionar o periodo

1. Clicar no elemento visivel `#Filter_DateStart + .dpifs-fake-input`.
2. Ler o cabecalho `th.datepicker-switch` do calendario visivel.
3. Navegar um mes por vez com `th.prev` ou `th.next` ate o mes desejado. Limitar a 24 cliques e verificar o cabecalho depois de cada clique.
4. Calcular `Date.UTC(ano, mes - 1, dia)` e clicar no `td.day[data-date="VALOR"]` do calendario visivel. Confirmar que o localizador e unico.
5. Repetir para `#Filter_DateEnd + .dpifs-fake-input` usando o ultimo dia do mes.
6. Selecionar a pessoa no `select#Filter_Names` por `label` exato. Se houver nomes parecidos, pedir confirmacao.
7. Dentro de `#form_post`, clicar no unico botao `Filtrar`.

## Carregar e extrair

Depois do filtro, clicar em `Carregar Mais` enquanto o botao estiver habilitado. Limitar a 50 paginas e confirmar que a quantidade de cartoes aumenta a cada clique. Interromper se ela nao aumentar.

Extrair os cartoes com uma unica avaliacao delimitada:

```javascript
Array.from(document.querySelectorAll(".container-box .item-flex.brc-bordered-item"))
  .map((card) => {
    const text = (card.innerText || "").trim();
    const control = text.match(/ControlId\s+(\d+\/\d+)/i);
    const timestamp = text.match(/(\d{2}\/\d{2}\/\d{4}\s+\d{2}:\d{2}:\d{2})/);
    const lines = text.split(/\n+/).map((line) => line.trim()).filter(Boolean);
    return {
      name: lines[0] || "",
      control_id: control ? control[1] : "",
      timestamp: timestamp ? timestamp[1] : "",
    };
  })
  .filter((record) => record.control_id && record.timestamp);
```

Verificar que todos os registros pertencem a pessoa e ao mes solicitados. Salvar no formato:

```json
{
  "source": "BRCondos /Persons/AccessHistory",
  "records": [
    {
      "name": "NOME",
      "control_id": "1000002045013700/1717658368",
      "timestamp": "31/07/2026 15:48:13"
    }
  ]
}
```

Nao transmitir esses dados a servicos externos. Usar arquivo temporario local e remove-lo ao final.

## Perfil de geracao

Copiar [profile.example.json](profile.example.json) para um arquivo temporario e preencher somente valores confirmados. `break_start` e `break_end` ficam vazios quando o horario do intervalo nao estiver documentado. `special_dates` recebe feriados ou dias tratados separadamente no formato `AAAA-MM-DD`.

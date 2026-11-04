---
name: folha-ponto
description: Busca registros de acesso no BRCondos, interpreta eventos ControlId, calcula horas extras de empregada domestica e gera resumo para WhatsApp e folha de ponto em PDF. Use quando o usuario pedir folha de ponto, banco de horas, horas extras ou registros mensais da funcionaria, inclusive quando ele quiser que o Codex pegue os dados diretamente do portal BRCondos em vez de colar os registros manualmente.
---

# Folha de ponto

## Private configuration

For an ordinary invocation that needs personal defaults or integrations, read the installed `skill-config` skill and resolve the `profile.<key>` fields below. Load only context relevant to the request. Command examples with these fields are templates; substitute configured values as quoted arguments before execution. Ask for required missing fields and skip unavailable optional integrations.

For a prepared worker packet, use only its declared access and supplied configuration. The coordinator resolves private defaults and passes the minimum required values or permitted resources. A worker must not load a machine-wide profile or unrelated context unless the packet explicitly permits it.

Executar o fluxo completo: coletar, revisar, calcular e gerar os arquivos. Manter a coleta separada do calculo para que o resultado seja auditavel.

## Fluxo

1. Confirmar o mes de referencia. Interpretar "este mes" como o mes calendario atual. Nao trocar silenciosamente pelo mes anterior por causa do contexto de fechamento.
2. Coletar os eventos no BRCondos conforme [references/brcondos.md](references/brcondos.md). Usar a sessao autenticada do Chrome e nunca ler cookies, senhas ou armazenamento da sessao.
3. Salvar os eventos normalizados em JSON temporario. Nao incluir CPF, CTPS ou credenciais nesse arquivo.
4. Preparar um perfil JSON temporario apenas com os dados fornecidos pelo usuario. Se CPF, CTPS, cargo ou horario do intervalo nao forem conhecidos, deixar os campos vazios. Nunca inventar dados pessoais nem gravar dados reais dentro deste skill.
5. Executar:

```bash
python3 scripts/build_timesheet.py \
  --records /tmp/folha-ponto/records.json \
  --profile /tmp/folha-ponto/profile.json \
  --month AAAA-MM \
  --output-dir /caminho/de/saida
```

6. Ler `calculo-AAAA-MM.json` antes de entregar. Apresentar as anomalias primeiro.
7. Se `requires_confirmation` for `true`, tratar o PDF como rascunho e pedir confirmacao sobre os dias indicados. Depois da confirmacao, executar novamente com `--confirmed`.
8. Renderizar o PDF final em PNG e verificar visualmente alinhamento, texto cortado, linhas e legibilidade antes de entregar.
9. Entregar o PDF e o texto do WhatsApp. Remover os arquivos temporarios que contenham eventos ou dados pessoais depois da conclusao.

## Regras de calculo e perfil privado

- Ler `profile.timesheet.profile` para obter `controls.entry_prefix`, `controls.exit_prefix`, a jornada e as tolerancias confirmadas. `--profile` pode indicar outro perfil explicitamente.
- Pedir os campos necessarios quando nao houver perfil. Os numeros e horarios do exemplo sao ficticios e nao definem a jornada do usuario.
- Calcular a saida prevista e as excecoes usando a jornada confirmada. Manter a politica de calculo do perfil e registrar anomalias.
- Em registros duplicados, usar a primeira entrada e a ultima saida. Marcar revisao quando a diferenca puder alterar o total em mais de 30 minutos.
- Nao descontar saida antecipada.
- Separar sabados, domingos e datas especiais. Nao soma-los ao total normal.
- Arredondar cada extra diario para cima ate o minuto inteiro.

## Saidas

- `calculo-AAAA-MM.json`: dados auditaveis, anomalias e sinal de confirmacao.
- `resumo-whatsapp-AAAA-MM.txt`: texto pronto para copiar.
- `folha-ponto-AAAA-MM.pdf`: folha A4 com os dias do mes.

Nao preencher horarios de intervalo sem informacao explicita. Os acessos da portaria demonstram entrada e saida do condominio, mas nao comprovam o intervalo intrajornada.

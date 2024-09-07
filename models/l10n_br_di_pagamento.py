# Copyright 2024 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
"""
Este módulo define o modelo `L10nBrDiPagamento`, que representa as informações de pagamento
relacionadas à Declaração de Importação (DI) no Odoo.

Classes:
    - L10nBrDiPagamento: Um modelo Odoo que armazena e manipula dados sobre os pagamentos
      relacionados às Declarações de Importação.

Campos:
    - declaracao_id: Campo Many2one que vincula o pagamento a uma declaração de importação.
    - currency_id: Campo Many2one relacionado à moeda da declaração vinculada, tornando-o
      somente leitura.
    - agencia_pagamento: Campo Char que armazena a agência de pagamento.
    - banco_pagamento: Campo Char que armazena o banco de pagamento.
    - codigo_receita: Campo Char que armazena o código da receita.
    - codigo_tipo_pagamento: Campo Char que armazena o código do tipo de pagamento.
    - conta_pagamento: Campo Char que armazena a conta de pagamento.
    - data_pagamento: Campo Date que armazena a data de pagamento.
    - nome_tipo_pagamento: Campo Char que armazena o nome do tipo de pagamento.
    - numero_retificacao: Campo Char que armazena o número de retificação.
    - valor_juros_encargos: Campo Monetary que armazena o valor dos juros e encargos.
    - valor_multa: Campo Monetary que armazena o valor da multa.
    - valor_receita: Campo Monetary que armazena o valor da receita.

Métodos:
    - _importa_declaracao(pagamento): Este método recebe um objeto de pagamento e retorna
      um dicionário com as informações do pagamento formatadas para importação.

Detalhamento dos métodos:
    - _importa_declaracao: Utiliza o objeto de pagamento recebido e converte seus valores,
      aplicando divisões pelos fatores necessários (D2) para os campos monetários. Também
      formata a data de pagamento usando a função `c_data`, importada de outro módulo.

Uso:
    Este modelo é utilizado para armazenar e manipular as informações de pagamento que
    fazem parte do processo de declaração de importação, permitindo que os dados sejam
    integrados ao sistema Odoo e manipulados conforme necessário para o registro da DI.
"""

from odoo import fields, models

from .l10n_br_di_declaracao import D2, c_data


class L10nBrDiPagamento(models.Model):

    _name = "declaracao_importacao.pagamento"
    _description = "Declaração Importação Pagamento"

    declaracao_id = fields.Many2one(
        "declaracao_importacao.declaracao", string="Declaração", required=True, ondelete="cascade"
    )

    currency_id = fields.Many2one(
        "res.currency",
        related="declaracao_id.currency_id",
        readonly=True,
    )

    agencia_pagamento = fields.Char()
    banco_pagamento = fields.Char()
    codigo_receita = fields.Char()
    codigo_tipo_pagamento = fields.Char()
    conta_pagamento = fields.Char()
    data_pagamento = fields.Date()
    nome_tipo_pagamento = fields.Char()
    numero_retificacao = fields.Char()
    valor_juros_encargos = fields.Monetary()
    valor_multa = fields.Monetary()
    valor_receita = fields.Monetary()

    def _importa_declaracao(self, pagamento):
        return {
            "agencia_pagamento": pagamento.agencia_pagamento,
            "banco_pagamento": pagamento.banco_pagamento,
            "codigo_receita": pagamento.codigo_receita,
            "codigo_tipo_pagamento": pagamento.codigo_tipo_pagamento,
            "conta_pagamento": pagamento.conta_pagamento,
            "data_pagamento": c_data(pagamento.data_pagamento),
            "data_desembaraco": c_data(pagamento.data_desembaraco),
            "nome_tipo_pagamento": pagamento.nome_tipo_pagamento,
            "numero_retificacao": pagamento.numero_retificacao,
            "valor_juros_encargos": int(pagamento.valor_juros_encargos) / D2,
            "valor_multa": int(pagamento.valor_multa) / D2,
            "valor_receita": int(pagamento.valor_receita) / D2,
        }

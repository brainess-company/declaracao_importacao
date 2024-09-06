# Copyright 2024 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
"""
Este módulo define o modelo `L10nBrDespacho`, que representa os dados relacionados ao despacho
de mercadorias em uma Declaração de Importação (DI) no Odoo.

Classes:
    - L10nBrDespacho: Um modelo Odoo que armazena e manipula informações sobre o despacho
      de uma mercadoria no contexto de uma Declaração de Importação.

Campos:
    - declaracao_id: Campo Many2one que vincula o despacho à declaração de importação correspondente.
    - codigo_tipo_documento_despacho: Campo Char que armazena o código do tipo de documento de despacho.
    - nome_documento_despacho: Campo Char que armazena o nome do documento de despacho.
    - numero_documento_despacho: Campo Char que armazena o número do documento de despacho.

Métodos:
    - _importa_declaracao(despacho): Método que recebe um objeto de despacho e retorna um dicionário com as
      informações formatadas para importação.

Detalhamento dos métodos:
    - _importa_declaracao: Extrai os dados do objeto de despacho recebido e formata os campos 
      `codigo_tipo_documento_despacho`, `nome_documento_despacho` e `numero_documento_despacho` 
      para serem utilizados no sistema Odoo.

Uso:
    Este modelo é utilizado para armazenar e manipular as informações relacionadas ao despacho
    de mercadorias em uma Declaração de Importação, permitindo que os dados sejam importados e
    processados no sistema Odoo.
"""

from odoo import fields, models


class L10nBrDespacho(models.Model):

    _name = "l10n_br_di.despacho"
    _description = "Declaração de Importação Despacho"

    declaracao_id = fields.Many2one(
        "l10n_br_di.declaracao", string="Declaração", required=True, ondelete="cascade"
    )

    codigo_tipo_documento_despacho = fields.Char()
    nome_documento_despacho = fields.Char()
    numero_documento_despacho = fields.Char()

    def _importa_declaracao(self, despacho):
        return {
            "codigo_tipo_documento_despacho": despacho.codigo_tipo_documento_despacho,
            "nome_documento_despacho": despacho.nome_documento_despacho,
            "numero_documento_despacho": despacho.numero_documento_despacho,
        }

# Copyright 2024 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
"""
Este módulo define o modelo `L10nBrDiMercadoria`, que representa as mercadorias associadas 
a uma Declaração de Importação (DI) no Odoo.

Classes:
    - L10nBrDiMercadoria: Um modelo Odoo que armazena e manipula dados sobre as mercadorias 
      incluídas na Declaração de Importação.

Campos:
    - declaracao_id: Campo Many2one relacionado à declaração de importação via a adição da mercadoria.
    - currency_id: Campo Many2one que representa a moeda da declaração de importação.
    - adicao_id: Campo Many2one que vincula a mercadoria à adição correspondente.
    - moeda_venda_id: Campo Many2one representando a moeda da venda vinculada à adição.
    - taxa_cambio_venda: Campo Float que armazena a taxa de câmbio aplicada na venda.
    - numero_sequencial_item: Campo Integer que armazena o número sequencial da mercadoria.
    - descricao_mercadoria: Campo Char para a descrição da mercadoria.
    - quantidade: Campo Float que armazena a quantidade da mercadoria.
    - unidade_medida: Campo Char que representa a unidade de medida da mercadoria.
    - valor_unitario: Campo Monetary que armazena o valor unitário da mercadoria.
    - product_id: Campo Many2one para vincular a mercadoria a um produto do Odoo.
    - uom_id: Campo Many2one que vincula a mercadoria à unidade de medida no sistema.
    - price_unit: Campo Monetary que armazena o preço unitário da mercadoria em reais (BRL).
    - amount_subtotal: Campo Monetary que armazena o subtotal da mercadoria na moeda da venda.
    - amount_subtotal_brl: Campo Monetary que armazena o subtotal da mercadoria em reais.
    - unit_addition_deduction: Campo Monetary que representa adições ou deduções no valor unitário.
    - final_price_unit: Campo Monetary que armazena o valor unitário final da mercadoria.
    - amount_other: Campo Monetary que armazena o valor de outros custos associados à mercadoria.
    - amount_total: Campo Monetary que armazena o valor total da mercadoria.
    - amount_afrmm: Campo Monetary que armazena o valor do AFRMM (Adicional ao Frete para Renovação da Marinha Mercante).

Métodos:
    - _compute_totals: Método que calcula os valores totais da mercadoria, como preço unitário, subtotal, 
      adições, deduções e valor final.
    - _importa_declaracao(mercadoria): Método que importa as informações de uma mercadoria a partir de um 
      objeto de declaração e retorna um dicionário com os valores formatados.
    - _match_product_unit(vals, descricao_mercadoria, unidade_medida): Método para buscar o produto 
      correspondente à mercadoria, preenchendo automaticamente os campos `product_id` e `uom_id` com base 
      em declarações anteriores.

Detalhamento dos métodos:
    - _compute_totals: Recalcula diversos campos monetários para a mercadoria, incluindo o valor unitário 
      ajustado pela taxa de câmbio, adições/deduções e o valor total da mercadoria.
    - _importa_declaracao: Extrai dados da mercadoria importada e faz a correspondência dos valores de acordo 
      com a formatação exigida.
    - _match_product_unit: Realiza uma pesquisa nas últimas declarações para tentar encontrar e associar 
      automaticamente o produto e a unidade de medida correspondentes.

Uso:
    Este modelo é utilizado para armazenar e manipular as mercadorias que fazem parte do processo de 
    Declaração de Importação, incluindo cálculos de valores em moeda local e outras informações necessárias 
    para o registro correto da DI.
"""

from odoo import fields, models

from .l10n_br_di_declaracao import D5, D7


class L10nBrDiMercadoria(models.Model):

    _name = "l10n_br_di.mercadoria"
    _description = "Declaração de Importação Mercadoria"

    # @api.depends("product_qty", "price_unit", "currency_rate", "import_addition_id")
    def _compute_totals(self):
        for line in self:
            line.price_unit = line.valor_unitario * line.taxa_cambio_venda
            line.amount_subtotal = line.quantidade * line.valor_unitario
            line.amount_subtotal_brl = line.quantidade * line.price_unit

            line.unit_addition_deduction = (
                line.adicao_id.amount_add_ded_brl
                * line.amount_subtotal_brl
                / line.adicao_id.condicao_venda_valor_reais
            ) / line.quantidade

            line.amount_other = (
                line.adicao_id.valor_outros
                * line.amount_subtotal_brl
                / line.adicao_id.condicao_venda_valor_reais
            )

            line.amount_afrmm = line.amount_other - (
                line.adicao_id.valor_taxa_siscomex
                * line.amount_subtotal_brl
                / line.adicao_id.condicao_venda_valor_reais
            )

            line.final_price_unit = line.price_unit + line.unit_addition_deduction

            line.amount_total = line.final_price_unit * line.quantidade

    declaracao_id = fields.Many2one(
        "l10n_br_di.declaracao",
        related="adicao_id.declaracao_id",
    )

    currency_id = fields.Many2one(
        "res.currency",
        related="declaracao_id.currency_id",
    )

    adicao_id = fields.Many2one(
        "l10n_br_di.adicao", string="Adição", required=True, ondelete="cascade"
    )

    moeda_venda_id = fields.Many2one(
        "res.currency",
        related="adicao_id.moeda_venda_id",
    )

    taxa_cambio_venda = fields.Float(
        digits=(12, 8),
        related="adicao_id.taxa_cambio_venda",
    )

    numero_sequencial_item = fields.Integer(string="Seq.")
    descricao_mercadoria = fields.Char(string="Descrição")
    quantidade = fields.Float(string="Qty")
    unidade_medida = fields.Char(string="Uom")
    valor_unitario = fields.Monetary(
        currency_field="moeda_venda_id",
        string="vUnMoeda",
        digits=(12, 8),
    )

    # Campos do produto para mapeamento do produto:

    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
    )

    uom_id = fields.Many2one("uom.uom", string="Unit of Measure")

    price_unit = fields.Monetary(
        string="vUnBRL",
        digits=(12, 8),
    )

    amount_subtotal = fields.Monetary(
        string="Subtotal (Moeda)",
        digits=(12, 8),
        currency_field="moeda_venda_id",
    )
    amount_subtotal_brl = fields.Monetary(string="Subtotal (BRL)", digits=(12, 8))

    unit_addition_deduction = fields.Monetary(
        string="+/-",
        digits=(12, 8),
        help="Equals to the sum of all di_valor_ids.valor divided by the sum of "
        "di_mercadoria_ids.quantidade",
    )

    final_price_unit = fields.Monetary(string="vUnBRL Final", digits=(12, 8))

    amount_other = fields.Monetary(string="vOutro")

    amount_total = fields.Monetary(string="Total")

    amount_afrmm = fields.Monetary(string="vAFRMM")

    def _importa_declaracao(self, mercadoria):
        vals = {
            "numero_sequencial_item": int(mercadoria.numero_sequencial_item),
            "descricao_mercadoria": mercadoria.descricao_mercadoria,
            "quantidade": int(mercadoria.quantidade) / D5,
            "unidade_medida": mercadoria.unidade_medida,
            "valor_unitario": int(mercadoria.valor_unitario) / D7,
        }
        self._match_product_unit(
            vals,
            mercadoria.descricao_mercadoria,
            mercadoria.unidade_medida,
        )
        return vals

    def _match_product_unit(self, vals, descricao_mercadoria, unidade_medida):
        """
        Método para buscar o produto correspondente a mercadoria,
        pesquisa nas útimas DIs criadas do mesmo produto e tenta preencher
        automaticamente os campos product_id e uom_id.
        """
        # TODO: Implementar a busca do produto

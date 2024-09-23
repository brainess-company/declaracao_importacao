from odoo import api, models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    def _compute_custom_subtotal(self):
        """
        Função personalizada para calcular o subtotal da fatura, somando valores
        como ii_value, ipi_value, cofins_value, freight_value, e price_unit * quantity.
        Este cálculo será aplicado apenas para faturas de importação.
        """
        for move in self:
            if move.fiscal_operation_id and move.fiscal_operation_id.import_operation:
                # Apenas para faturas de importação
                for line in move.line_ids:
                    fiscal_line = line.fiscal_document_line_id
                    if fiscal_line:
                        # Somar os campos desejados da tabela l10n_br_fiscal_document_line
                        subtotal = (
                            fiscal_line.amount_tax_included +  # Valor de impostos
                            fiscal_line.freight_value +  # Valor do frete
                            fiscal_line.other_value +  # Outros valores adicionais
                            (line.price_unit * line.quantity)  # Preço unitário * quantidade
                        )
                        # Atualizar o campo price_subtotal da linha de fatura
                        line.price_subtotal = subtotal

    @api.model
    def create(self, vals):
        """
        Sobrescreve o método create para calcular o subtotal customizado
        quando a fatura for criada.
        """
        move = super(AccountMove, self).create(vals)
        move._compute_custom_subtotal()
        return move

    def write(self, vals):
        """
        Sobrescreve o método write para recalcular o subtotal customizado
        sempre que a fatura for atualizada.
        """
        result = super(AccountMove, self).write(vals)
        self._compute_custom_subtotal()
        return result

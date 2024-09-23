from odoo import api, models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    def _compute_custom_subtotal(self):
        """
        Função personalizada para calcular o subtotal da fatura, somando valores
        como ii_value, ipi_value, cofins_value, freight_value e price_unit * quantity.
        TODO: FAZER ISSO SÓ PARA FATURAS DE IMPORTAÇÃO
        """
        for move in self:
            for line in move.line_ids:
                fiscal_line = line.fiscal_document_line_id
                if fiscal_line:
                    # Somar os campos desejados da tabela l10n_br_fiscal_document_line
                    subtotal = (
                        fiscal_line.amount_tax_included +
                        fiscal_line.freight_value +
                        (line.price_unit * line.quantity)
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

# flake8: noqa: B950
# Copyright 2024 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
"""
Este módulo define a classe `L10nBrDiMixin`, que serve como um mixin para facilitar
operações relacionadas à Declaração de Importação (DI) no Odoo.

Classes:
    - L10nBrDiMixin: Um modelo abstrato que implementa funcionalidades comuns para
      integração com a DI.

Métodos:
    - _s_currency(siscomex_code): Retorna a moeda correspondente ao código SISCOMEX fornecido.

Detalhamento dos métodos:
    - _s_currency: Este método realiza uma busca no modelo `res.currency` para localizar
      a moeda que corresponde ao código SISCOMEX (Sistema Integrado de Comércio Exterior) 
      informado como parâmetro. Ele retorna o primeiro registro encontrado, se houver.

    Uso:
    Este mixin pode ser utilizado por outros modelos que necessitam realizar operações
    relacionadas à Declaração de Importação, como converter valores baseados na moeda 
    vinculada ao código SISCOMEX.
"""

from odoo import models


class L10nBrDiMixin(models.AbstractModel):

    _name = "l10n_br_di.mixin"
    _description = "Declaração Importação Mixin"

    def _s_currency(self, siscomex_code):
        return self.env["res.currency"].search(
            [("siscomex_code", "=", siscomex_code)],
            limit=1,
        )

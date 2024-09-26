import base64
from datetime import datetime
from xsdata.formats.dataclass.parsers import XmlParser
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tests.common import Form  # Importação correta do Form
import logging

_logger = logging.getLogger(__name__)

# Função auxiliar para converter data
def c_data(data):
    return datetime.strptime(str(data), "%Y%m%d").date()

class L10nBrDiDeclaracao(models.Model):
    _name = "declaracao_importacao.declaracao"
    _description = "Declaração Importação"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    _rec_name = "numero_di"

    # Campos principais
    state = fields.Selection(
        selection=[("draft", "Draft"), ("open", "Open"), ("locked", "Locked"), ("canceled", "Canceled")],
        default="draft",
        required=True,
        tracking=True,
    )

    fiscal_operation_id = fields.Many2one("l10n_br_fiscal.operation", domain=[("state", "=", "approved")], required=True)
    account_move_id = fields.Many2one("account.move", readonly=True)

    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.ref("base.BRL").id, readonly=True)
    dolar_currency_id = fields.Many2one("res.currency", default=lambda self: self.env.ref("base.USD").id, readonly=True)

    # Relacionamentos com outros modelos (Adição, Mercadoria, Despacho, etc.)
    di_adicao_ids = fields.One2many("declaracao_importacao.adicao", "declaracao_id")
    di_mercadoria_ids = fields.One2many("declaracao_importacao.mercadoria", "declaracao_id")
    di_pagamento_ids = fields.One2many("declaracao_importacao.pagamento", "declaracao_id")

    # Importação de arquivo XML
    arquivo_declaracao = fields.Binary(attachment=True)

    # Campos XML
    numero_di = fields.Char()
    data_registro = fields.Date()
    data_desembaraco = fields.Date()
    carga_peso_bruto = fields.Float(digits=(12, 7))
    carga_peso_liquido = fields.Float(digits=(12, 7))

    # Método para processar a declaração de importação a partir do XML
    def importa_declaracao(self, arquivo=False):
        if not self.arquivo_declaracao:
            raise UserError(_("Nenhum arquivo de declaração foi carregado."))

        file_content = base64.b64decode(self.arquivo_declaracao)
        parser = XmlParser()
        declaration_list = parser.from_string(file_content.decode("utf-8"), ListaDeclaracoes)
        vals = self._importa_declaracao(declaration_list)

        if self:
            self.di_adicao_ids.unlink()
            self.di_mercadoria_ids.unlink()
            self.update(vals)
        else:
            vals["arquivo_declaracao"] = self.arquivo_declaracao
            self.create(vals)

        self.calcular_declaracao()

    # Função interna que processa os dados do XML e os converte em valores para os campos Odoo
    def _importa_declaracao(self, declaracoes):
        if not declaracoes.declaracao_importacao:
            raise UserError(_("Nenhuma declaração de importação encontrada no XML."))

        di = declaracoes.declaracao_importacao

        # Processar adições, mercadorias e pagamentos
        adicoes = [self.di_adicao_ids._importa_declaracao(adicao) for adicao in di.adicao]
        mercadorias = [self.di_mercadoria_ids._importa_declaracao(mercadoria) for mercadoria in di.mercadoria]
        pagamentos = [self.di_pagamento_ids._importa_declaracao(pagamento) for pagamento in di.pagamento]

        vals = {
            "numero_di": di.numero_di,
            "data_registro": c_data(di.data_registro),
            "data_desembaraco": c_data(di.data_desembaraco),
            "carga_peso_bruto": int(di.carga_peso_bruto) / 10**7,
            "carga_peso_liquido": int(di.carga_peso_liquido) / 10**7,
            "di_adicao_ids": [(0, 0, adicao) for adicao in adicoes],
            "di_mercadoria_ids": [(0, 0, mercadoria) for mercadoria in mercadorias],
            "di_pagamento_ids": [(0, 0, pagamento) for pagamento in pagamentos],
        }

        _logger.info('Importação da Declaração de Importação: %s', vals)
        return vals

    # Método para calcular totais após a importação
    def calcular_declaracao(self):
        for record in self:
            record.di_adicao_ids.calcular_adicao_totals()

    # Gerar fatura com base na declaração de importação
    def gerar_fatura(self):
        self.ensure_one()
        self._validate_invoice_fields()
        return self._generate_invoice()

    # Validação para garantir que existem linhas de mercadoria antes de gerar a fatura
    def _validate_invoice_fields(self):
        if not any(self.di_mercadoria_ids):
            raise UserError(_("A declaração de importação precisa de ao menos uma linha de mercadoria."))
        if any(not line.product_id for line in self.di_mercadoria_ids):
            raise UserError(_("Alguma linha de mercadoria está sem produto vinculado."))

    # Gerar a fatura com base nos dados importados
    def _generate_invoice(self):
        move_form = Form(self.env["account.move"].with_context(default_move_type="in_invoice"))

        move_form.invoice_date = fields.Date.today()
        move_form.partner_id = self.di_adicao_ids[0].fornecedor_partner_id
        move_form.document_type_id = self.env.ref("l10n_br_fiscal.document_55")
        move_form.document_serie_id = self.env.ref("l10n_br_fiscal.document_55_serie_1")
        move_form.issuer = "company"
        move_form.fiscal_operation_id = self.fiscal_operation_id

        for mercadoria in self.di_mercadoria_ids:
            with move_form.invoice_line_ids.new() as line_form:
                adicao = self.di_adicao_ids.filtered(lambda a: mercadoria in a.di_adicao_mercadoria_ids).ensure_one()
                line_form.product_id = mercadoria.product_id
                line_form.quantity = mercadoria.quantidade
                line_form.price_unit = mercadoria.final_price_unit

        invoice = move_form.save()
        self.write({"account_move_id": invoice.id, "state": "locked"})
        return invoice

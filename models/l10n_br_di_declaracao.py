import base64
from datetime import datetime
from xsdata.formats.dataclass.parsers import XmlParser
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tests.common import Form  # Importação correta do Form
from ..utils.lista_declaracoes import ListaDeclaracoes
import logging

_logger = logging.getLogger(__name__)
D7 = 10**7
D5 = 10**5
D4 = 10**4
D3 = 10**3
D2 = 10**2

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

    # Campos Extras

    arquivo_declaracao = fields.Binary(
        attachment=True,
    )

    @api.model
    def _default_fiscal_operation(self):
        return self.env.company.import_trade_fiscal_operation_id

    @api.model
    def _fiscal_operation_domain(self):
        domain = [("state", "=", "approved")]
        return domain

    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("open", "Open"),
            ("locked", "Loked"),
            ("canceled", "Canceled"),
        ],
        default="draft",
        required=True,
        copy=False,
        tracking=True,
    )

    fiscal_operation_id = fields.Many2one(
        comodel_name="l10n_br_fiscal.operation",
        readonly=True,
        states={"draft": [("readonly", False)]},
        default=_default_fiscal_operation,
        domain=lambda self: self._fiscal_operation_domain(),
    )

    account_move_id = fields.Many2one(
        comodel_name="account.move",
        readonly=True,
    )

    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
    )

    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.ref("base.BRL").id,
        readonly=True,
    )

    dolar_currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.ref("base.USD").id,
        readonly=True,
    )

    freight_currency_id = fields.Many2one(
        "res.currency",
    )

    insurance_currency_id = fields.Many2one(
        "res.currency",
    )

    # Relacionais XML

    di_adicao_ids = fields.One2many("declaracao_importacao.adicao", "declaracao_id")
    di_despacho_ids = fields.One2many("declaracao_importacao.despacho", "declaracao_id")
    di_mercadoria_ids = fields.One2many("declaracao_importacao.mercadoria", "declaracao_id")
    di_pagamento_ids = fields.One2many("declaracao_importacao.pagamento", "declaracao_id")
    di_valor_ids = fields.One2many("declaracao_importacao.valor", "declaracao_id")

    # Campos do arquivo XML

    numero_di = fields.Char()
    data_registro = fields.Date()
    sequencial_retificacao = fields.Char()

    armazenamento_recinto_aduaneiro_codigo = fields.Char()
    armazenamento_recinto_aduaneiro_nome = fields.Char()
    armazenamento_setor = fields.Char()

    canal_selecao_parametrizada = fields.Char()
    caracterizacao_operacao_codigo_tipo = fields.Char()
    caracterizacao_operacao_descricao_tipo = fields.Char()

    carga_data_chegada = fields.Date()
    carga_numero_agente = fields.Char()
    carga_pais_procedencia_codigo = fields.Char()
    carga_pais_procedencia_nome = fields.Char()
    carga_peso_bruto = fields.Float(digits=(12, 7))
    carga_peso_liquido = fields.Float(digits=(12, 7))
    carga_urf_entrada_codigo = fields.Char()
    carga_urf_entrada_nome = fields.Char()

    conhecimento_carga_embarque_data = fields.Date()
    conhecimento_carga_embarque_local = fields.Char()
    conhecimento_carga_id = fields.Char()
    conhecimento_carga_tipo_codigo = fields.Char()
    conhecimento_carga_tipo_nome = fields.Char()
    conhecimento_carga_utilizacao = fields.Char()
    conhecimento_carga_utilizacao_nome = fields.Char()

    documento_chegada_carga_codigo_tipo = fields.Char()
    documento_chegada_carga_nome = fields.Char()
    documento_chegada_carga_numero = fields.Char()

    data_desembaraco = fields.Date()

    frete_collect = fields.Float()
    frete_em_territorio_nacional = fields.Monetary(currency_field="dolar_currency_id")
    frete_moeda_negociada_codigo = fields.Char()
    frete_moeda_negociada_nome = fields.Char()
    frete_prepaid = fields.Monetary(currency_field="dolar_currency_id")
    frete_total_dolares = fields.Monetary(currency_field="dolar_currency_id")
    frete_total_moeda = fields.Monetary(currency_field="freight_currency_id")
    frete_total_reais = fields.Monetary()

    icms = fields.Char()

    agencia_icms = fields.Char()
    banco_icms = fields.Char()
    codigo_tipo_recolhimento_icms = fields.Char()
    cpf_responsavel_registro = fields.Char()
    data_pagamento_icms = fields.Char()
    data_registro_icms = fields.Char()
    hora_registro_icms = fields.Char()
    nome_tipo_recolhimento_icms = fields.Char()
    numero_sequencial_icms = fields.Char()
    uf_icms = fields.Char()
    valor_total_icms = fields.Char()


    importador_codigo_tipo = fields.Char()
    importador_cpf_representante_legal = fields.Char()
    importador_endereco_bairro = fields.Char()
    importador_endereco_cep = fields.Char()
    importador_endereco_complemento = fields.Char()
    importador_endereco_logradouro = fields.Char()
    importador_endereco_municipio = fields.Char()
    importador_endereco_numero = fields.Char()
    importador_endereco_uf = fields.Char()
    importador_nome = fields.Char()
    importador_nome_representante_legal = fields.Char()
    importador_numero = fields.Char()
    importador_numero_telefone = fields.Char()

    local_descarga_total_dolares = fields.Monetary(currency_field="dolar_currency_id")
    local_descarga_total_reais = fields.Monetary()
    local_embarque_total_dolares = fields.Monetary(currency_field="dolar_currency_id")
    local_embarque_total_reais = fields.Monetary()

    modalidade_despacho_codigo = fields.Char()
    modalidade_despacho_nome = fields.Char()

    operacao_fundap = fields.Char()

    seguro_moeda_negociada_codigo = fields.Char()
    seguro_moeda_negociada_nome = fields.Char()
    seguro_total_dolares = fields.Monetary(currency_field="dolar_currency_id")
    seguro_total_moeda_negociada = fields.Monetary(
        currency_field="insurance_currency_id"
    )
    seguro_total_reais = fields.Monetary()

    situacao_entrega_carga = fields.Char()
    tipo_declaracao_codigo = fields.Char()
    tipo_declaracao_nome = fields.Char()
    total_adicoes = fields.Char()

    urf_despacho_codigo = fields.Char()
    urf_despacho_nome = fields.Char()

    valor_total_multa_arecolher_ajustado = fields.Float()

    via_transporte_codigo = fields.Char()
    via_transporte_multimodal = fields.Char()
    via_transporte_nome = fields.Char()
    via_transporte_nome_transportador = fields.Char()
    via_transporte_numero_veiculo = fields.Char()
    via_transporte_pais_transportador_codigo = fields.Char()

    informacao_complementar = fields.Text()

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

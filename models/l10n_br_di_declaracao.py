# flake8: noqa: B950
# Copyright 2024 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import base64
from datetime import datetime

from xsdata.formats.dataclass.parsers import XmlParser
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tests.common import Form

from ..utils.lista_declaracoes import ListaDeclaracoes
import logging
_logger = logging.getLogger(__name__)

D7 = 10**7
D5 = 10**5
D4 = 10**4
D3 = 10**3
D2 = 10**2


def c_data(data):
    return datetime.strptime(str(data), "%Y%m%d").date()


def process_icms_data(self, icms_data):
    if icms_data:
        self.agencia_icms = icms_data.agencia_icms
        self.banco_icms = icms_data.banco_icms
        self.codigo_tipo_recolhimento_icms = icms_data.codigo_tipo_recolhimento_icms
        self.cpf_responsavel_registro = icms_data.cpf_responsavel_registro
        self.data_pagamento_icms = icms_data.data_pagamento_icms
        self.data_registro_icms = icms_data.data_registro
        self.hora_registro_icms = icms_data.hora_registro
        self.nome_tipo_recolhimento_icms = icms_data.nome_tipo_recolhimento_icms
        self.numero_sequencial_icms = icms_data.numero_sequencial_icms
        self.uf_icms = icms_data.uf_icms
        self.valor_total_icms = icms_data.valor_total_icms
    else:
        _logger.warning("Nenhum dado de ICMS encontrado no XML")





class L10nBrDiDeclaracao(models.Model):

    _name = "declaracao_importacao.declaracao"
    _description = "Declaração Importação"
    _inherit = ["mail.thread", "mail.activity.mixin", "declaracao_importacao.mixin"]

    _rec_name = "numero_di"

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

    def importa_declaracao(self, arquivo=False):
        if self.arquivo_declaracao:
            arquivo = self.arquivo_declaracao

        file_content = base64.b64decode(arquivo)
        parser = XmlParser()
        declaration_list = parser.from_string(
            file_content.decode("utf-8"), ListaDeclaracoes
        )
        vals = self._importa_declaracao(declaration_list)

        if self:
            self.di_adicao_ids.unlink()
            self.di_despacho_ids.unlink()
            self.di_pagamento_ids.unlink()
            self.update(vals)
            self.calcular_declaracao()
        else:
            vals["arquivo_declaracao"] = arquivo
            res = self.create(vals)
            res.calcular_declaracao()

            return res

    def _importa_declaracao(self, declaracoes):
        """
        uma função que só pode ser usada aqui, que recebe declaracoes
        di recebe o metodo declaracao_importacao do arquivo recebido (declaracoes)
        o arquivo recebido na verdade é o declaration_list tratado pela classse ListaDeclaracoes
        ListaDeclaracoes é um mapeamento que recebe a classe inteira declaracaoImportacao DeclaracaoImportacao
        """
        if not declaracoes.declaracao_importacao:
            raise UserError(_("Nenhuma declaração de importação encontrada"))

        di = declaracoes.declaracao_importacao

        insurance_currency_id = self._s_currency(di.seguro_moeda_negociada_codigo)
        freight_currency_id = self._s_currency(di.frete_moeda_negociada_codigo)

        adicoes = []
        despachos = []
        pagamentos = []

        for adicao in di.adicao:
            adicoes.append(self.di_adicao_ids._importa_declaracao(adicao))
        for despacho in di.documento_instrucao_despacho:
            despachos.append(self.di_despacho_ids._importa_declaracao(despacho))
        for pagamento in di.pagamento:
            pagamentos.append(self.di_pagamento_ids._importa_declaracao(pagamento))

        # Fornecedor: adicao.fornecedorNome

        vals = {
            "di_adicao_ids": [(0, 0, x) for x in adicoes],
            "di_despacho_ids": [(0, 0, x) for x in despachos],
            "di_pagamento_ids": [(0, 0, x) for x in pagamentos],
            #
            "insurance_currency_id": (
                insurance_currency_id.id if insurance_currency_id else False
            ),
            "freight_currency_id": (
                freight_currency_id.id if freight_currency_id else False
            ),
            "numero_di": di.numero_di,
            "data_registro": c_data(di.data_registro),
            "data_desembaraco": c_data(di.data_desembaraco),
            "carga_data_chegada": c_data(di.carga_data_chegada),
            "armazenamento_recinto_aduaneiro_codigo": di.armazenamento_recinto_aduaneiro_codigo,
            "armazenamento_recinto_aduaneiro_nome": di.armazenamento_recinto_aduaneiro_nome,
            "armazenamento_setor": di.armazenamento_setor,
            "canal_selecao_parametrizada": di.canal_selecao_parametrizada,
            "caracterizacao_operacao_codigo_tipo": di.caracterizacao_operacao_codigo_tipo,
            "caracterizacao_operacao_descricao_tipo": di.caracterizacao_operacao_descricao_tipo,
            "carga_numero_agente": di.carga_numero_agente,
            "carga_pais_procedencia_codigo": di.carga_pais_procedencia_codigo,
            "carga_pais_procedencia_nome": di.carga_pais_procedencia_nome,
            "carga_peso_bruto": int(di.carga_peso_bruto) / D7,
            "carga_peso_liquido": int(di.carga_peso_liquido) / D7,
            "carga_urf_entrada_codigo": di.carga_urf_entrada_codigo,
            "carga_urf_entrada_nome": di.carga_urf_entrada_nome,
            "conhecimento_carga_embarque_data": c_data(
                di.conhecimento_carga_embarque_data
            ),
            "conhecimento_carga_embarque_local": di.conhecimento_carga_embarque_local,
            "conhecimento_carga_id": di.conhecimento_carga_id,
            "conhecimento_carga_tipo_codigo": di.conhecimento_carga_tipo_codigo,
            "conhecimento_carga_tipo_nome": di.conhecimento_carga_tipo_nome,
            "conhecimento_carga_utilizacao": di.conhecimento_carga_utilizacao,
            "conhecimento_carga_utilizacao_nome": di.conhecimento_carga_utilizacao_nome,
            "documento_chegada_carga_codigo_tipo": di.documento_chegada_carga_codigo_tipo,
            "documento_chegada_carga_nome": di.documento_chegada_carga_nome,
            "documento_chegada_carga_numero": di.documento_chegada_carga_numero,
            "frete_moeda_negociada_codigo": di.frete_moeda_negociada_codigo,
            "frete_moeda_negociada_nome": di.frete_moeda_negociada_nome,
            "frete_collect": int(di.frete_collect) / D2,
            "frete_em_territorio_nacional": int(di.frete_em_territorio_nacional) / D2,
            "frete_prepaid": int(di.frete_prepaid) / D2,
            "frete_total_dolares": int(di.frete_total_dolares) / D2,
            "frete_total_moeda": int(di.frete_total_moeda) / D2,
            "frete_total_reais": int(di.frete_total_reais) / D2,
            "icms": di.icms,


            "agencia_icms": di.icms.agencia_icms,
            "banco_icms": di.icms.banco_icms,
            "codigo_tipo_recolhimento_icms": di.icms.codigo_tipo_recolhimento_icms,
            "cpf_responsavel_registro": di.icms.cpf_responsavel_registro,
            "data_pagamento_icms": di.icms.data_pagamento_icms,
            "data_registro_icms": di.icms.data_registro_icms,
            "hora_registro_icms": di.icms.hora_registro_icms,
            "nome_tipo_recolhimento_icms": di.icms.nome_tipo_recolhimento_icms,
            "numero_sequencial_icms":di.icms.numero_sequencial_icms,
            "uf_icms": di.icms.uf_icms,
            "valor_total_icms": di.icms.valor_total_icms,

            "importador_codigo_tipo": di.importador_codigo_tipo,
            "importador_cpf_representante_legal": di.importador_cpf_representante_legal,
            "importador_endereco_bairro": di.importador_endereco_bairro,
            "importador_endereco_cep": di.importador_endereco_cep,
            "importador_endereco_complemento": di.importador_endereco_complemento,
            "importador_endereco_logradouro": di.importador_endereco_logradouro,
            "importador_endereco_municipio": di.importador_endereco_municipio,
            "importador_endereco_numero": di.importador_endereco_numero,
            "importador_endereco_uf": di.importador_endereco_uf,
            "importador_nome": di.importador_nome,
            "importador_nome_representante_legal": di.importador_nome_representante_legal,
            "importador_numero": di.importador_numero,
            "importador_numero_telefone": di.importador_numero_telefone,
            "informacao_complementar": di.informacao_complementar,
            "local_descarga_total_dolares": int(di.local_descarga_total_dolares) / D2,
            "local_descarga_total_reais": int(di.local_descarga_total_reais) / D2,
            "local_embarque_total_dolares": int(di.local_embarque_total_dolares) / D2,
            "local_embarque_total_reais": int(di.local_embarque_total_reais) / D2,
            "modalidade_despacho_codigo": di.modalidade_despacho_codigo,
            "modalidade_despacho_nome": di.modalidade_despacho_nome,
            "operacao_fundap": di.operacao_fundap,
            "seguro_moeda_negociada_codigo": di.seguro_moeda_negociada_codigo,
            "seguro_moeda_negociada_nome": di.seguro_moeda_negociada_nome,
            "seguro_total_dolares": int(di.seguro_total_dolares) / D2,
            "seguro_total_moeda_negociada": int(di.seguro_total_moeda_negociada) / D2,
            "seguro_total_reais": int(di.seguro_total_reais) / D2,
            "sequencial_retificacao": di.sequencial_retificacao,
            "situacao_entrega_carga": di.situacao_entrega_carga,
            "tipo_declaracao_codigo": di.tipo_declaracao_codigo,
            "tipo_declaracao_nome": di.tipo_declaracao_nome,
            "total_adicoes": int(di.total_adicoes) / D2,
            "urf_despacho_codigo": di.urf_despacho_codigo,
            "urf_despacho_nome": di.urf_despacho_nome,
            "valor_total_multa_arecolher_ajustado": int(
                di.valor_total_multa_arecolher_ajustado
            )
            / D2,
            "via_transporte_codigo": di.via_transporte_codigo,
            "via_transporte_multimodal": di.via_transporte_multimodal,
            "via_transporte_nome": di.via_transporte_nome,
            "via_transporte_nome_transportador": di.via_transporte_nome_transportador,
            "via_transporte_numero_veiculo": di.via_transporte_numero_veiculo,
            "via_transporte_pais_transportador_codigo": di.via_transporte_pais_transportador_codigo,
        }
        _logger.info('Vals declaracao: %s', vals)
        return vals

    def calcular_declaracao(self):
        for record in self:
            record.di_adicao_ids.calcular_declaracao()

    def gerar_fatura(self):
        self.ensure_one()
        self._validate_invoice_fields()
        # if self.state != "open":
        #     raise UserError(_("Only open declarations can generate invoices."))
        return self._generate_invoice()


    def _validate_invoice_fields(self):
        if not any(self.di_mercadoria_ids):
            raise UserError(_("Imported document must have at least one line."))
        if any(not line_id.product_id for line_id in self.di_mercadoria_ids):
            raise UserError(_("One or more import lines is missing a product ID."))

    def _generate_invoice(self):
        # Criar a fatura de fornecedor no Form com contexto específico
        move_form = Form(self.env["account.move"].with_context(default_move_type="in_invoice"))

        # Definir os campos principais
        move_form.partner_id = self.partner_id  # Parceiro fornecedor
        move_form.invoice_date = fields.Date.today()  # Data da fatura
        move_form.date = fields.Date.today()  # Data de lançamento
        move_form.ref = self.name  # Referência interna

        # Informações fiscais
        move_form.fiscal_operation_id = self.fiscal_operation_id  # Operação fiscal
        move_form.document_type_id = self.env.ref(
            "l10n_br_fiscal.document_55")  # Tipo de documento (NF-e)
        move_form.document_serie_id = self.env.ref(
            "l10n_br_fiscal.document_55_serie_1")  # Série do documento
        move_form.fiscal_position_id = self.fiscal_position_id  # Posição fiscal do fornecedor

        # Outras informações
        move_form.currency_id = self.env.user.company_id.currency_id  # Moeda
        move_form.company_id = self.env.user.company_id  # Empresa atual

        # Adicionar as linhas de fatura (produtos/serviços)
        for line in self.invoice_line_ids:
            with move_form.invoice_line_ids.new() as line_form:
                line_form.product_id = line.product_id  # Produto/Serviço
                line_form.quantity = line.quantity  # Quantidade
                line_form.price_unit = line.price_unit  # Preço unitário
                line_form.account_id = line.account_id  # Conta contábil
                line_form.name = line.name  # Descrição da linha

                # Informações fiscais por linha
                line_form.tax_ids.clear()  # Limpar impostos predefinidos
                for tax in line.tax_ids:
                    line_form.tax_ids.add(tax)  # Adicionar os impostos correspondentes
                line_form.fiscal_operation_line_id = line.fiscal_operation_line_id  # Operação fiscal por linha
                line_form.cfop_id = line.cfop_id  # CFOP

        # Salvar a fatura de fornecedor
        invoice = move_form.save()

    def _get_invoice_action(self, invoice):
        action = self.env.ref("account.action_move_in_invoice_type").read()[0]
        action["domain"] = [("id", "=", invoice.id)]
        return action

    def action_view_invoice(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "account.action_move_out_invoice_type"
        )
        form_view = [(self.env.ref("account.view_move_form").id, "form")]

        action["views"] = form_view
        action["res_id"] = self.account_move_id.id
        return action

    def action_view_de_para(self):
        if self.state not in ["draft", "open"]:
            return

        action = (
            self.env.ref("declaracao_importacao.l10n_br_di_mercadoria_de_para_act_window")
            .sudo()
            .read([])[0]
        )
        tree_view = [
            (
                self.env.ref("declaracao_importacao.l10n_br_di_mercadoria_tree_de_para_view").id,
                "tree",
            )
        ]

        action["views"] = tree_view
        domain = [("declaracao_id", "=", self.id)]
        action["domain"] = domain
        return action

# -*- coding: utf-8 -*-
import tempfile
import binascii
import xlrd
from odoo import models, fields, exceptions, api, _
from xlsxwriter.workbook import Workbook
import csv
from odoo.exceptions import UserError


import logging

_logger = logging.getLogger(__name__)

try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')
try:
    import cStringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')


class Template(models.Model):
    _inherit = "product.template"

    to_be = fields.Boolean('To Be')


class ImportWizard(models.TransientModel):
    _name = "import.wizard"
    _description = 'Import Wizard'
    
    file = fields.Binary('File')

    def import_data(self):
        try:
            fp = tempfile.NamedTemporaryFile(suffix=".csv")
            fp.write(binascii.a2b_base64(self.file))
            fp.seek(0)

            workbook = Workbook(fp.name[:-4] + '.xlsx')
            worksheet = workbook.add_worksheet()

            with open(fp.name, 'rt', encoding='utf8') as f:
                reader = csv.reader(f)
                for r, row in enumerate(reader):
                    for c, col in enumerate(row):
                        worksheet.write(r, c, col)

            workbook.close()

            workbook = xlrd.open_workbook(fp.name[:-4] + '.xlsx')
            sheet = workbook.sheet_by_index(0)

            not_imported_list = []
            survey_id = self.env['survey.survey'].browse(self.env.context.get('active_id'))
            question_type = {
                'multiple-choice': 'multiple_choice',
                'multi-select': 'simple_choice',
            }
            for row_num in range(1, sheet.nrows):
                row = sheet.row_values(row_num)
                question_id = self.env['survey.question'].search([('title', '=', row[0]), ('survey_id', '=', survey_id.id)])
                if not question_id:
                    values = {
                        'title': row[0],
                        'survey_id': survey_id.id,
                        'question_type': question_type[row[1]] or False,
                        'description': row[9] or False,
                    }
                    question_id = self.env['survey.question'].create(values)
                correct_ans = row[8].split(',')
                for i in range(2, 8):
                    answer_id = self.env['survey.question.answer'].search([('question_id', '=', question_id.id), ('value', '=', row[i])])
                    if not answer_id:
                        ans_values = {
                            'question_id': question_id.id,
                            'value': row[i],
                            'is_correct': (str(i-1) in correct_ans),
                        }
                        answer_id = self.env['survey.question.answer'].create(ans_values)
        except Exception as e:
            raise UserError(_('Error in importing data. %s') % e)

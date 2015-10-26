# -*- coding: utf-8 -*-
#----------------------------------------------
# Jose Hernandez josehernandezc@gmail.com 
#----------------------------------------------

# imports
import netsvc
import time
import logging
import decimal_precision as dp
from osv import osv, fields
from tools.translate import _

_logger = logging.getLogger(__name__)

class purchase_order(osv.osv):

    _inherit = 'purchase.order'

    _description = u"Calcula peso neto compras"

    def wkf_confirm_order(self, cr, uid, ids, context=None):
        message = "Estamos en el metodo nuevo"
        self.log(cr, uid, 1, message)
        for po in self.browse(cr, uid, ids, context=context):
            for line in po.order_line:
                if line and line.verificado=='draft':
                    raise osv.except_osv(_('Error !'), 'No puedes confirmar una compra sin validar las lineas.')
            message = _("Lista para confirmar la compra '%s") % (po.name,)
            self.log(cr, uid, po.id, message)

        return  super(purchase_order, self).wkf_confirm_order(cr, uid, ids, context)

purchase_order()


class purchase_order_line(osv.osv):

    _inherit = 'purchase.order.line'

    _description = u"Calcula peso neto compras"

    def _get_weight(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('purchase.order.line.weight').browse(cr, uid, ids, context=context):
            result[line.orderline_id.id] = True
        return result.keys()

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        cur_obj=self.pool.get('res.currency')
        _logger.info("_amount_all %r", field_name)
        for linea in self.browse(cr, uid, ids, context=context):
            res[linea.id] = {'empty_total_weight_packaging': 0.0, 'net_qty_product': 0.0, 'product_qty': 0.0}
            val = 0.0
            for line_weight in linea.order_line_weight:
               val += line_weight.weight * line_weight.qty
            cur = linea.order_id.pricelist_id.currency_id
            res[linea.id]['empty_total_weight_packaging']=cur_obj.round(cr, uid, cur, val)
            neto = linea.total_net_weight_product - val
            res[linea.id]['net_qty_product']=cur_obj.round(cr, uid, cur, neto)
            res[linea.id]['product_qty']=cur_obj.round(cr, uid, cur, neto)

        return res

    _columns = {
        'product_qty': fields.function(_amount_all, digits_compute= dp.get_precision('Product UoM'), string='Quantity',store={'purchase.order.line.weight': (_get_weight, None, 10)}, multi="pesos", required=True),
        'order_line_weight': fields.one2many('purchase.order.line.weight', 'orderline_id', 'Order Lines'),
        'total_net_weight_product': fields.float('Kg Peso bruto recibido (Lectura del display)',digits=(12,4)),
        'empty_total_weight_packaging': fields.function(_amount_all, digits_compute= dp.get_precision('Purchase Price'), 
            string='Kg Peso de material de empaquetado y carga',store=True, multi="pesos", method=True, required=True), #{'purchase.order.line.weight': (_get_weight, ['subtotal'], 10)}, multi="pesos", method = True,),
        'net_qty_product': fields.function(_amount_all, digits_compute= dp.get_precision('Purchase Price'), string='Kg Producto neto recibido', 
            store=True, multi="pesos", method=True, required=True),  #purchase.order.line.weight': (_get_weight, ['subtotal'], 10)}, multi="pesos", method = True, ),
	    'verificado': fields.selection([('draft', 'Sin Verificar'), ('done', 'Verificado')], 'State', required=True, readonly=True, ),
    }

    _defaults = {
        #'year': lambda self, cr, uid, ids: datetime.now().year,
	'verificado':lambda *args: 'draft',
    }

    def cal(self, cr, uid, ids,context=None):
        raise osv.except_osv(("JHC"), ('Resultado %s', "HOLA" ))

    #def calcula(self, cr, uid, ids,product_id, product_uom=False, name=False, date_planned=False, price_unit=False, company_id=False, account_analytic_id=False, total_net_weight_product=False, empty_total_weight_packaging=False, order_id=False):

    def calcula(self, cr, uid, ids, context=None):
        values = {'product_id':context['product_id'], \
            'product_uom': context['product_uom'], 'name': context['name'], \
             'date_planned': context['date_planned'], 'price_unit': context['price_unit'], \
             'company_id': context['company_id'], 'account_analytic_id': context['account_analytic_id'], \
             'total_net_weight_product': context['total_net_weight_product'], \
             'empty_total_weight_packaging': context['empty_total_weight_packaging'], \
              'order_id': context['order_id'],}
        
        _logger.info("Total producto %r", values['total_net_weight_product'])
        if(values['total_net_weight_product'] > 0.0):
            net_qty_product = values['total_net_weight_product'] - values['empty_total_weight_packaging']
            values.update({'net_qty_product': net_qty_product, 'product_qty':net_qty_product})
        
        _logger.info("ID %s", ids)
        _logger.info("Order ID %s", values['order_id'])
        #raise osv.except_osv(("JHC"), ('Resultado %s', values ))
        # if not (ids and ids[0]): 
        #     newid = self.create(cr, uid, values)
        #     values.update({'id': newid})
        #     #raise osv.except_osv(("JHC"), ('Resultado %s', values ))
        # else:
        #     self.write(cr, uid, ids, values, context)
        return {'value': values}

    def cambia_estado(self, cr, uid, ids, context=None):
        values = {}
        verificado = context["verificado"]
        #raise osv.except_osv(("JHC"), ("verificado antes: %s", verificado))
        _logger.info("verificado antes: %s", verificado)
        if(verificado == 'done'):
            values.update({'verificado': 'draft'})
        else:
            values.update({'verificado': 'done'})
        _logger.info("verificado despues: %s", values)
        self.write(cr, uid, ids, {'verificado': values['verificado']}, context)
        return {'value': values}

    def button_dummy(self, cr, uid, ids, context=None):
        _logger.info("DUMMY: %s", "jhc")
        return True

purchase_order_line()

#--------------------------------------------------------------------------------------------------

class purchase_order_line_weight(osv.osv):
    _name = "purchase.order.line.weight"

    _description = u"peso de elementos para peso neto en compras"

    def _amount_line(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        cur_obj=self.pool.get('res.currency')
        for line in self.browse(cr, uid, ids, context=context):
            cur = line.orderline_id.order_id.pricelist_id.currency_id
            res[line.id] = line.qty * line.weight
        return res

    _columns = {
        'orderline_id': fields.many2one('purchase.order.line', 'Orderline Reference', select=True, required=True, ondelete='cascade'),
        'name': fields.selection([('tarima', 'Tarima'), ('caja', 'Cajas'), ('otro', 'Otro')], 'Empaque', required=True, readonly=False, ),
        'weight': fields.float('Peso',digits=(12,4)),
        'qty': fields.float('Cantidad', digits=(12,4)),
        'subtotal': fields.function(_amount_line, string='Subtotal', digits_compute= dp.get_precision('Purchase Price')),
    }

    _defaults = {
        #'year': lambda self, cr, uid, ids: datetime.now().year,
	   'name':lambda *args: 'caja',
    }


    def write(self, cr, uid, ids, values, context=None):
        _logger.info("JHC write %s", values)
        osv.osv.write(self, cr, uid, ids, values, context)
        return True

    def create(self, cr, uid, values, context=None):
        _logger.info("JHC create: %s", values)
        newid = osv.osv.create(self, cr, uid, values, context)
        return newid


    def unlink(self, cr, uid, ids, context=None):
        _logger.info("JHC unlink: %s", ids)
        osv.osv.unlink(self, cr, uid, ids, context)
        return True

purchase_order_line_weight()



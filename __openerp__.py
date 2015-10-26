# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Compras peso neto',
    'version': '1.0',
    'author': 'Softcom Sistemas',
    'category': 'Compras',
    'description':
    """
net_weight_calc
====================================

Contenido:
--------------------------------------------
    * 
    * 
    * 


Otros:
--------------------------------------------------

    Elaborado por softcomsistemas
    

Descrición detallada:
Este módulo calcula el costo neto de un producto comprado en kilos, 
descuenta del peso bruto los elementos de empaque.
    """,
    'website': 'http://www.softcomsistemas.com.mx',
    'depends': ['base_setup', 'purchase',],
    'data': ['net_weight_calc_view.xml', ],
    'demo': [#'demo/media_demo.xml',
    ],
    'installable': True,
    'auto_install': False,
}


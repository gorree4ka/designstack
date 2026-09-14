/**
 * Редактор блока «Список ресурсов».
 *
 * Обычный JS без сборки: зависимости перечислены в editor.asset.php.
 * Превью — серверный рендер, поэтому в редакторе видно ровно то, что на сайте.
 */
( function ( blocks, element, components, blockEditor, ServerSideRender, i18n ) {
	'use strict';

	var el = element.createElement;
	var __ = i18n.__;
	var data = window.designstackCoreBlocks || {};

	function options( map, empty ) {
		var list = [ { label: empty, value: '' } ];

		Object.keys( map || {} ).forEach( function ( key ) {
			list.push( { label: map[ key ], value: key } );
		} );

		return list;
	}

	blocks.registerBlockType( 'designstack/resource-list', {
		edit: function ( props ) {
			var attributes = props.attributes;

			function set( key ) {
				return function ( value ) {
					var patch = {};
					patch[ key ] = value;
					props.setAttributes( patch );
				};
			}

			var manual = ( attributes.ids || [] ).length > 0;

			var controls = [
				el( components.TextControl, {
					key: 'ids',
					label: __( 'Номера записей через запятую', 'designstack-core' ),
					help: __( 'Заполнено — список собирается вручную, отборы ниже не работают.', 'designstack-core' ),
					value: ( attributes.ids || [] ).join( ', ' ),
					onChange: function ( value ) {
						var ids = value
							.split( ',' )
							.map( function ( item ) {
								return parseInt( item.trim(), 10 );
							} )
							.filter( function ( item ) {
								return ! isNaN( item ) && item > 0;
							} );

						props.setAttributes( { ids: ids } );
					}
				} ),
				el( components.SelectControl, {
					key: 'resource_type',
					label: __( 'Тип', 'designstack-core' ),
					value: attributes.resource_type,
					options: options( data.types, __( 'Все типы', 'designstack-core' ) ),
					disabled: manual,
					onChange: set( 'resource_type' )
				} ),
				el( components.SelectControl, {
					key: 'topic',
					label: __( 'Тема', 'designstack-core' ),
					value: attributes.topic,
					options: options( data.topics, __( 'Все темы', 'designstack-core' ) ),
					disabled: manual,
					onChange: set( 'topic' )
				} ),
				el( components.SelectControl, {
					key: 'level',
					label: __( 'Грейд', 'designstack-core' ),
					value: attributes.level,
					options: options( data.levels, __( 'Любой грейд', 'designstack-core' ) ),
					disabled: manual,
					onChange: set( 'level' )
				} ),
				el( components.SelectControl, {
					key: 'pricing',
					label: __( 'Цена', 'designstack-core' ),
					value: attributes.pricing,
					options: options( data.pricing, __( 'Любая цена', 'designstack-core' ) ),
					disabled: manual,
					onChange: set( 'pricing' )
				} ),
				el( components.SelectControl, {
					key: 'ru_open',
					label: __( 'Доступ из РФ', 'designstack-core' ),
					value: attributes.ru_open,
					options: options( data.ru_open, __( 'Неважно', 'designstack-core' ) ),
					disabled: manual,
					onChange: set( 'ru_open' )
				} ),
				el( components.SelectControl, {
					key: 'ru_payment',
					label: __( 'Оплата из РФ', 'designstack-core' ),
					value: attributes.ru_payment,
					options: options( data.ru_payment, __( 'Неважно', 'designstack-core' ) ),
					disabled: manual,
					onChange: set( 'ru_payment' )
				} ),
				el( components.RangeControl, {
					key: 'limit',
					label: __( 'Сколько карточек', 'designstack-core' ),
					value: attributes.limit,
					min: 6,
					max: 24,
					onChange: set( 'limit' )
				} ),
				el( components.SelectControl, {
					key: 'orderby',
					label: __( 'Порядок', 'designstack-core' ),
					value: attributes.orderby,
					options: [
						{ label: __( 'Свежая проверка сверху', 'designstack-core' ), value: 'checked_at' },
						{ label: __( 'Новые сверху', 'designstack-core' ), value: 'date' },
						{ label: __( 'По названию', 'designstack-core' ), value: 'title' }
					],
					disabled: manual,
					onChange: set( 'orderby' )
				} ),
				el( components.SelectControl, {
					key: 'layout',
					label: __( 'Раскладка', 'designstack-core' ),
					value: attributes.layout,
					options: [
						{ label: __( 'Сетка', 'designstack-core' ), value: 'grid' },
						{ label: __( 'Список', 'designstack-core' ), value: 'list' }
					],
					onChange: set( 'layout' )
				} )
			];

			return el(
				element.Fragment,
				{},
				el(
					blockEditor.InspectorControls,
					{},
					el( components.PanelBody, { title: __( 'Что показываем', 'designstack-core' ) }, controls )
				),
				el(
					'div',
					blockEditor.useBlockProps(),
					el( ServerSideRender, {
						block: 'designstack/resource-list',
						attributes: attributes
					} )
				)
			);
		},
		save: function () {
			return null;
		}
	} );
} )(
	window.wp.blocks,
	window.wp.element,
	window.wp.components,
	window.wp.blockEditor,
	window.wp.serverSideRender,
	window.wp.i18n
);

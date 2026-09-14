/**
 * Редактор блока «Доступ и оплата из РФ».
 */
( function ( blocks, element, components, blockEditor, ServerSideRender, i18n ) {
	'use strict';

	var el = element.createElement;
	var __ = i18n.__;

	blocks.registerBlockType( 'designstack/ru-status', {
		edit: function ( props ) {
			var attributes = props.attributes;

			function toggle( key, label ) {
				return el( components.ToggleControl, {
					key: key,
					label: label,
					checked: !! attributes[ key ],
					onChange: function ( value ) {
						var patch = {};
						patch[ key ] = value;
						props.setAttributes( patch );
					}
				} );
			}

			return el(
				element.Fragment,
				{},
				el(
					blockEditor.InspectorControls,
					{},
					el(
						components.PanelBody,
						{ title: __( 'Что показываем', 'designstack-core' ) },
						toggle( 'showState', __( 'Состояние записи', 'designstack-core' ) ),
						toggle( 'showChecked', __( 'Дата проверки', 'designstack-core' ) )
					)
				),
				el(
					'div',
					blockEditor.useBlockProps(),
					el( ServerSideRender, {
						block: 'designstack/ru-status',
						attributes: attributes,
						urlQueryArgs: { post_id: props.context && props.context.postId }
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
